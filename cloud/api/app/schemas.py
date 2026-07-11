from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectCreated(BaseModel):
    id: str
    name: str
    api_key: str
    api_key_prefix: str
    created_at: datetime
    warning: str = (
        "Store api_key now — it is shown only once. "
        "Export as AUDITAI_PROJECT_KEY in CI."
    )


class ProjectInfo(BaseModel):
    id: str
    name: str
    api_key_prefix: str
    created_at: datetime


class MetricAggregateIn(BaseModel):
    name: str | None = None
    mean: float
    min: float | None = None
    max: float | None = None
    threshold: float | None = None
    passed: bool | None = None
    n_scored: int | None = None
    n_errors: int | None = None


class RunIngest(BaseModel):
    """Payload pushed by AuditAI CLI after a local/CI run."""

    schema_version: str = "0.1"
    client_version: str | None = None
    run_id: str | None = None
    overall_passed: bool
    exit_reason: str = ""
    total_cases: int = 0
    failed_cases: int = 0
    judge_calls: int = 0
    aggregates: dict[str, MetricAggregateIn | dict[str, Any]] = Field(default_factory=dict)
    top_failures: list[dict[str, Any]] = Field(default_factory=list)
    # Privacy: CLI may omit answers / full results
    results: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunSummaryOut(BaseModel):
    id: str
    client_run_id: str | None
    overall_passed: bool
    exit_reason: str
    total_cases: int
    failed_cases: int
    judge_calls: int
    faithfulness_mean: float | None
    answer_relevancy_mean: float | None
    prompt_injection_mean: float | None
    git_sha: str | None
    git_ref: str | None
    repo: str | None
    created_at: datetime


class RunDetailOut(RunSummaryOut):
    schema_version: str
    client_version: str | None
    payload: dict[str, Any]


class HealthOut(BaseModel):
    status: str
    version: str
    database: str
