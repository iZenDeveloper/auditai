"""Optional Cloud push client (fail-open by default)."""

from __future__ import annotations

import os
from typing import Any

import httpx
from rich.console import Console

from auditai import __version__
from auditai.config import AuditConfig, CloudConfig
from auditai.models import CaseResult, RunSummary

console = Console(stderr=True)


def resolve_cloud_config(cfg: AuditConfig) -> CloudConfig | None:
    """Return cloud config if push should run; else None."""
    cloud = cfg.cloud
    key = os.environ.get("AUDITAI_PROJECT_KEY", "").strip()
    url = (cloud.api_url or os.environ.get("AUDITAI_API_URL") or "").strip()

    # Auto-enable when key is present unless explicitly disabled
    enabled = cloud.enabled
    if enabled is None:
        enabled = bool(key)
    if not enabled:
        return None
    if not key:
        console.print(
            "[yellow]cloud:[/yellow] enabled but AUDITAI_PROJECT_KEY is missing — skip push"
        )
        return None
    if not url:
        console.print("[yellow]cloud:[/yellow] AUDITAI_API_URL / cloud.api_url missing — skip push")
        return None

    # materialize resolved values on a copy-like object
    return CloudConfig(
        enabled=True,
        api_url=url.rstrip("/"),
        include_answers=cloud.include_answers,
        include_results=cloud.include_results,
        fail_open=cloud.fail_open,
        timeout_seconds=cloud.timeout_seconds,
    )


def build_payload(
    summary: RunSummary,
    results: list[CaseResult],
    cloud: CloudConfig,
) -> dict[str, Any]:
    aggregates = {k: v.model_dump() for k, v in summary.metric_aggregates.items()}
    top = []
    for t in summary.top_failures:
        item = t.model_dump()
        if not cloud.include_answers:
            item["answer"] = ""
            # keep question truncated for debugging charts
            item["question"] = (item.get("question") or "")[:200]
        top.append(item)

    payload: dict[str, Any] = {
        "schema_version": summary.schema_version,
        "client_version": __version__,
        "run_id": summary.run_id,
        "overall_passed": summary.overall_passed,
        "exit_reason": summary.exit_reason,
        "total_cases": summary.total_cases,
        "failed_cases": summary.failed_cases,
        "judge_calls": summary.judge_calls,
        "aggregates": aggregates,
        "top_failures": top,
        "metadata": _ci_metadata(),
    }

    if cloud.include_results:
        cases = []
        for r in results:
            row = r.model_dump()
            if not cloud.include_answers:
                row["answer"] = ""
                row["contexts_used"] = []
            cases.append(row)
        payload["results"] = cases

    return payload


def _ci_metadata() -> dict[str, Any]:
    """Best-effort CI metadata from common env vars (no secrets)."""
    meta: dict[str, Any] = {}
    mapping = {
        "git_sha": ["GITHUB_SHA", "CI_COMMIT_SHA", "GIT_COMMIT"],
        "git_ref": ["GITHUB_REF", "CI_COMMIT_REF_NAME", "GIT_BRANCH"],
        "repo": ["GITHUB_REPOSITORY", "CI_PROJECT_PATH"],
        "run_url": ["GITHUB_SERVER_URL"],  # incomplete alone; ok as hint
        "ci": ["CI", "GITHUB_ACTIONS", "GITLAB_CI"],
    }
    for key, envs in mapping.items():
        for e in envs:
            val = os.environ.get(e)
            if val:
                meta[key] = val
                break
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY"):
        run_id = os.environ.get("GITHUB_RUN_ID")
        if run_id:
            meta["ci_run_url"] = (
                f"{os.environ['GITHUB_SERVER_URL'].rstrip('/')}/"
                f"{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}"
            )
    meta["source"] = "auditai-cli"
    return meta


def push_run(
    summary: RunSummary,
    results: list[CaseResult],
    cloud: CloudConfig,
    *,
    project_key: str | None = None,
) -> dict[str, Any] | None:
    """POST run to cloud. Returns response JSON or None on fail-open skip."""
    key = (project_key or os.environ.get("AUDITAI_PROJECT_KEY") or "").strip()
    if not key:
        return None

    url = f"{cloud.api_url.rstrip('/')}/v1/runs"
    payload = build_payload(summary, results, cloud)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": f"auditai-cli/{__version__}",
    }

    try:
        with httpx.Client(timeout=cloud.timeout_seconds) as client:
            resp = client.post(url, json=payload, headers=headers)
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        console.print(
            f"[green]cloud:[/green] pushed run id={data.get('id')} "
            f"passed={data.get('overall_passed')}"
        )
        return data
    except Exception as e:
        msg = f"cloud push failed: {e}"
        if cloud.fail_open:
            console.print(f"[yellow]cloud:[/yellow] {msg} (fail_open=true — CI continues)")
            return None
        console.print(f"[red]cloud:[/red] {msg}")
        raise
