"""Compare AuditAI report metrics against a saved baseline."""

from __future__ import annotations

import json
from dataclasses import dataclass
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
    if not path.exists():
        raise ConfigError(f"{label} report not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"invalid {label} report JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigError(f"invalid {label} report: root must be an object")

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
