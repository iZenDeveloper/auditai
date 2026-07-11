from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # Store only sha256 hash of API key
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    api_key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # for display
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    runs: Mapped[list[Run]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    client_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    schema_version: Mapped[str] = mapped_column(String(16), default="0.1")
    client_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    overall_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    exit_reason: Mapped[str] = mapped_column(String(200), default="")
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    judge_calls: Mapped[int] = mapped_column(Integer, default=0)
    # Metric means (denormalized for simple charts)
    faithfulness_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    answer_relevancy_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    prompt_injection_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Full payload (metrics + optional redacted cases) — no secrets by contract
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    # CI metadata
    git_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    git_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    repo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    project: Mapped[Project] = relationship(back_populates="runs")
