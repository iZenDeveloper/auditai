"""Domain models for AuditAI CLI v0.1."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CaseCategory(str, Enum):
    general = "general"
    faithfulness = "faithfulness"
    relevancy = "relevancy"
    prompt_injection = "prompt_injection"


class AuditCase(BaseModel):
    """Single evaluation case (named AuditCase to avoid pytest Test* collection)."""

    id: str
    question: str
    contexts: list[str] = Field(default_factory=list)
    expected_answer: str | None = None
    expected_keywords: list[str] = Field(default_factory=list)
    category: CaseCategory = CaseCategory.general
    should_refuse: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


# Back-compat alias for docs / external imports
TestCase = AuditCase


class TargetResponse(BaseModel):
    answer: str
    contexts: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    status_code: int | None = None


class MetricScore(BaseModel):
    name: str
    score: float
    threshold: float
    passed: bool
    reason: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CaseResult(BaseModel):
    case_id: str
    question: str
    answer: str = ""
    contexts_used: list[str] = Field(default_factory=list)
    metrics: list[MetricScore] = Field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0


class MetricAggregate(BaseModel):
    name: str
    mean: float
    min: float
    max: float
    threshold: float
    passed: bool
    n_scored: int
    n_errors: int = 0


class TopFailure(BaseModel):
    case_id: str
    metric: str
    score: float
    question: str
    answer: str
    reason: str | None = None


class JudgeUsage(BaseModel):
    """Aggregated LLM-as-judge token usage for one run."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    # True when tokens are char-heuristic estimates (e.g. mock judge)
    estimated: bool = False
    provider: str = ""
    model: str = ""


class RunSummary(BaseModel):
    schema_version: str = "0.1"
    run_id: str
    started_at: datetime
    finished_at: datetime
    config_path: str
    total_cases: int
    failed_cases: int
    metric_aggregates: dict[str, MetricAggregate]
    overall_passed: bool
    exit_reason: str
    top_failures: list[TopFailure] = Field(default_factory=list)
    judge_calls: int = 0
    judge_usage: JudgeUsage = Field(default_factory=JudgeUsage)
