"""Compare AuditAI report metrics against a saved baseline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auditai.errors import ConfigError


@dataclass(frozen=True)
class MetricComparison:
    name: str
    baseline: float
    current: float | None
    drop: float | None
    passed: bool
    reason: str = ""


@dataclass(frozen=True)
class ComparisonResult:
    comparisons: tuple[MetricComparison, ...]
    max_drop: float

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.comparisons)


def create_baseline_file(
    report_path: str | Path,
    output_path: str | Path,
    *,
    force: bool = False,
) -> Path:
    """Write a privacy-safe baseline containing aggregates and minimal provenance."""
    source = Path(report_path)
    output = Path(output_path)
    payload = _load_report_payload(source, label="source")
    if payload.get("overall_passed") is not True:
        raise ConfigError("source report did not pass; refusing to promote it as a baseline")
    if output.exists() and not force:
        raise ConfigError(f"baseline already exists: {output} (use --force to overwrite)")

    means = _aggregate_means(payload, label="source")
    aggregates = payload.get("aggregates") or payload.get("metric_aggregates") or {}
    safe_aggregates: dict[str, dict[str, Any]] = {}
    for name, mean in means.items():
        aggregate = aggregates.get(name, {})
        safe: dict[str, Any] = {"mean": mean}
        for key in ("threshold", "n_scored"):
            value = aggregate.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                safe[key] = value
        safe_aggregates[name] = safe

    judge_usage = payload.get("judge_usage")
    judge: dict[str, str] = {}
    if isinstance(judge_usage, dict):
        for key in ("provider", "model"):
            value = judge_usage.get(key)
            if isinstance(value, str) and value:
                judge[key] = value

    baseline = {
        "schema_version": "0.1",
        "kind": "auditai_baseline",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "run_id": str(payload.get("run_id") or ""),
            "finished_at": str(payload.get("finished_at") or ""),
            "total_cases": int(payload.get("total_cases") or 0),
            "judge": judge,
        },
        "aggregates": safe_aggregates,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def compare_report_files(
    baseline_path: str | Path,
    current_path: str | Path,
    *,
    max_drop: float,
) -> ComparisonResult:
    """Compare aggregate means and fail when a baseline metric regresses too far."""
    if not 0.0 <= max_drop <= 1.0:
        raise ConfigError("--max-drop must be between 0 and 1")

    baseline = _load_aggregate_means(Path(baseline_path), label="baseline")
    current = _load_aggregate_means(Path(current_path), label="current")

    comparisons: list[MetricComparison] = []
    for name, baseline_mean in sorted(baseline.items()):
        current_mean = current.get(name)
        if current_mean is None:
            comparisons.append(
                MetricComparison(
                    name=name,
                    baseline=baseline_mean,
                    current=None,
                    drop=None,
                    passed=False,
                    reason="missing from current report",
                )
            )
            continue

        drop = baseline_mean - current_mean
        passed = drop <= max_drop + 1e-12
        comparisons.append(
            MetricComparison(
                name=name,
                baseline=baseline_mean,
                current=current_mean,
                drop=drop,
                passed=passed,
                reason="" if passed else f"drop {drop:.4f} exceeds {max_drop:.4f}",
            )
        )

    return ComparisonResult(comparisons=tuple(comparisons), max_drop=max_drop)


def _load_aggregate_means(path: Path, *, label: str) -> dict[str, float]:
    return _aggregate_means(_load_report_payload(path, label=label), label=label)


def _load_report_payload(path: Path, *, label: str) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"{label} report not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"invalid {label} report JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigError(f"invalid {label} report: root must be an object")
    return payload


def _aggregate_means(payload: dict[str, Any], *, label: str) -> dict[str, float]:
    aggregates: Any = payload.get("aggregates") or payload.get("metric_aggregates")
    if not isinstance(aggregates, dict) or not aggregates:
        raise ConfigError(f"invalid {label} report: no metric aggregates")

    means: dict[str, float] = {}
    for name, aggregate in aggregates.items():
        if not isinstance(name, str) or not isinstance(aggregate, dict):
            raise ConfigError(f"invalid {label} report metric: {name!r}")
        value = aggregate.get("mean")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ConfigError(f"invalid {label} mean for metric '{name}'")
        mean = float(value)
        if not 0.0 <= mean <= 1.0:
            raise ConfigError(f"invalid {label} mean for metric '{name}': must be 0..1")
        means[name] = mean
    return means
