from __future__ import annotations

from pathlib import Path

from auditai.models import RunSummary


def render_markdown(summary: RunSummary) -> str:
    status = "✅ PASSED" if summary.overall_passed else "❌ FAILED"
    lines = [
        "## 🛡️ AuditAI Report",
        f"**Status:** {status} · `{summary.exit_reason}`",
        "",
        "| Metric | Mean | Threshold | Pass | n |",
        "|--------|------|-----------|------|---|",
    ]
    for name, agg in summary.metric_aggregates.items():
        mark = "✅" if agg.passed else "❌"
        lines.append(
            f"| {name} | {agg.mean:.2f} | {agg.threshold:.2f} | {mark} | {agg.n_scored} |"
        )

    if summary.top_failures:
        lines.extend(["", "### Top failures", ""])
        for i, f in enumerate(summary.top_failures, start=1):
            q = f.question.replace("\n", " ")[:120]
            reason = (f.reason or "").replace("\n", " ")[:160]
            lines.append(
                f"{i}. **{f.case_id}** `{f.metric}`={f.score:.2f} — {q}"
                + (f" _{reason}_" if reason else "")
            )

    lines.extend(
        [
            "",
            f"_run_id={summary.run_id} · judge_calls={summary.judge_calls}_",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown_report(path: Path, summary: RunSummary) -> Path:
    path.write_text(render_markdown(summary), encoding="utf-8")
    return path
