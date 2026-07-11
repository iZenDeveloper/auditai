"""Re-export / thin adapter — cloud uses same certificate layout as CLI."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.models import Project, Run

# Inline import path: prefer vendored copy logic identical to CLI module
# Implemented here so the cloud API package stays self-contained.


def build_run_certificate_pdf(project: Project, run: Run) -> bytes:
    from app._pdf_cert import CertificateData, MetricLine, build_compliance_pdf

    payload: dict[str, Any] = {}
    try:
        payload = json.loads(run.payload_json or "{}")
    except json.JSONDecodeError:
        payload = {}

    metrics: list[MetricLine] = []
    aggregates = payload.get("aggregates") or {}
    name_to_mean = {
        "faithfulness": run.faithfulness_mean,
        "answer_relevancy": run.answer_relevancy_mean,
        "prompt_injection": run.prompt_injection_mean,
    }
    for name, mean in name_to_mean.items():
        agg = aggregates.get(name) if isinstance(aggregates, dict) else None
        if isinstance(agg, dict):
            metrics.append(
                MetricLine(
                    name=name,
                    mean=float(agg["mean"]) if agg.get("mean") is not None else mean,
                    threshold=float(agg["threshold"]) if agg.get("threshold") is not None else None,
                    passed=agg.get("passed"),
                    n_scored=agg.get("n_scored"),
                )
            )
        elif mean is not None:
            metrics.append(MetricLine(name=name, mean=mean))

    issued = run.created_at
    if issued.tzinfo is None:
        issued = issued.replace(tzinfo=timezone.utc)

    cert = CertificateData(
        project_name=project.name,
        run_id=run.id,
        overall_passed=run.overall_passed,
        exit_reason=run.exit_reason or "",
        issued_at=issued if isinstance(issued, datetime) else datetime.now(timezone.utc),
        metrics=metrics,
        total_cases=run.total_cases,
        failed_cases=run.failed_cases,
        judge_calls=run.judge_calls,
        client_run_id=run.client_run_id,
        git_sha=run.git_sha,
        git_ref=run.git_ref,
        repo=run.repo,
        client_version=run.client_version,
        top_failures=list(payload.get("top_failures") or [])[:5],
    )
    return build_compliance_pdf(cert)
