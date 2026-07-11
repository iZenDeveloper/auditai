from __future__ import annotations

import json
from pathlib import Path

from auditai.models import CaseResult, RunSummary


def write_json_report(path: Path, summary: RunSummary, results: list[CaseResult]) -> Path:
    payload = {
        "schema_version": summary.schema_version,
        "run_id": summary.run_id,
        "overall_passed": summary.overall_passed,
        "exit_reason": summary.exit_reason,
        "started_at": summary.started_at.isoformat(),
        "finished_at": summary.finished_at.isoformat(),
        "config_path": summary.config_path,
        "total_cases": summary.total_cases,
        "failed_cases": summary.failed_cases,
        "judge_calls": summary.judge_calls,
        "judge_usage": summary.judge_usage.model_dump(),
        "aggregates": {
            k: v.model_dump() for k, v in summary.metric_aggregates.items()
        },
        "top_failures": [t.model_dump() for t in summary.top_failures],
        "results": [r.model_dump() for r in results],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
