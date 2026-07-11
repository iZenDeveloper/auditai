from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_project
from app.compliance_pdf import build_run_certificate_pdf
from app.db import get_db
from app.models import Project, Run
from app.schemas import RunDetailOut, RunIngest, RunSummaryOut

router = APIRouter(prefix="/v1/runs", tags=["runs"])


def _mean(aggregates: dict[str, Any], key: str) -> float | None:
    raw = aggregates.get(key)
    if raw is None:
        return None
    if isinstance(raw, dict):
        val = raw.get("mean")
        return float(val) if val is not None else None
    mean = getattr(raw, "mean", None)
    return float(mean) if mean is not None else None


@router.post("", response_model=RunSummaryOut, status_code=status.HTTP_201_CREATED)
def ingest_run(
    body: RunIngest,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> RunSummaryOut:
    meta = body.metadata or {}
    # Serialize payload; keep as stored history for dashboard later
    payload = body.model_dump(mode="json")

    # Idempotent-ish: if same client_run_id already stored for project, return existing
    if body.run_id:
        existing = (
            db.query(Run)
            .filter(Run.project_id == project.id, Run.client_run_id == body.run_id)
            .one_or_none()
        )
        if existing:
            return _to_summary(existing)

    run = Run(
        project_id=project.id,
        client_run_id=body.run_id,
        schema_version=body.schema_version,
        client_version=body.client_version,
        overall_passed=body.overall_passed,
        exit_reason=body.exit_reason[:200],
        total_cases=body.total_cases,
        failed_cases=body.failed_cases,
        judge_calls=body.judge_calls,
        faithfulness_mean=_mean(body.aggregates, "faithfulness"),
        answer_relevancy_mean=_mean(body.aggregates, "answer_relevancy"),
        prompt_injection_mean=_mean(body.aggregates, "prompt_injection"),
        payload_json=json.dumps(payload, ensure_ascii=False),
        git_sha=_as_str(meta.get("git_sha") or meta.get("commit")),
        git_ref=_as_str(meta.get("git_ref") or meta.get("branch") or meta.get("ref")),
        repo=_as_str(meta.get("repo") or meta.get("repository")),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _to_summary(run)


@router.get("", response_model=list[RunSummaryOut])
def list_runs(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[RunSummaryOut]:
    rows = (
        db.query(Run)
        .filter(Run.project_id == project.id)
        .order_by(Run.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_to_summary(r) for r in rows]


def _get_run_for_project(db: Session, project: Project, run_id: str) -> Run:
    run = db.query(Run).filter(Run.id == run_id, Run.project_id == project.id).one_or_none()
    if not run:
        run = (
            db.query(Run)
            .filter(Run.client_run_id == run_id, Run.project_id == project.id)
            .one_or_none()
        )
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.get("/{run_id}", response_model=RunDetailOut)
def get_run(
    run_id: str,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> RunDetailOut:
    run = _get_run_for_project(db, project, run_id)
    summary = _to_summary(run)
    try:
        payload = json.loads(run.payload_json)
    except json.JSONDecodeError:
        payload = {}
    return RunDetailOut(
        **summary.model_dump(),
        schema_version=run.schema_version,
        client_version=run.client_version,
        payload=payload,
    )


@router.get("/{run_id}/compliance.pdf")
def download_compliance_pdf(
    run_id: str,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> Response:
    """Download AI safety audit certificate PDF for a stored run."""
    run = _get_run_for_project(db, project, run_id)
    try:
        pdf_bytes = build_run_certificate_pdf(project, run)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    filename = f"auditai-compliance-{run.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s[:300] if s else None


def _to_summary(run: Run) -> RunSummaryOut:
    return RunSummaryOut(
        id=run.id,
        client_run_id=run.client_run_id,
        overall_passed=run.overall_passed,
        exit_reason=run.exit_reason,
        total_cases=run.total_cases,
        failed_cases=run.failed_cases,
        judge_calls=run.judge_calls,
        faithfulness_mean=run.faithfulness_mean,
        answer_relevancy_mean=run.answer_relevancy_mean,
        prompt_injection_mean=run.prompt_injection_mean,
        git_sha=run.git_sha,
        git_ref=run.git_ref,
        repo=run.repo,
        created_at=run.created_at,
    )
