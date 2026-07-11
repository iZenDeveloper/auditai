from __future__ import annotations

from rich.console import Console
from rich.table import Table

from auditai.models import RunSummary

console = Console(stderr=True)


def print_summary(summary: RunSummary) -> None:
    status = "[green]PASSED[/green]" if summary.overall_passed else "[red]FAILED[/red]"
    console.print(f"\n[bold]AuditAI[/bold] {status} · {summary.exit_reason}")

    table = Table(title="Metrics")
    table.add_column("Metric")
    table.add_column("Mean", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Pass")
    table.add_column("n", justify="right")

    for name, agg in summary.metric_aggregates.items():
        mark = "✓" if agg.passed else "✗"
        style = "green" if agg.passed else "red"
        table.add_row(
            name,
            f"{agg.mean:.3f}",
            f"{agg.threshold:.2f}",
            f"[{style}]{mark}[/{style}]",
            str(agg.n_scored),
        )

    console.print(table)
    u = summary.judge_usage
    est = " (est.)" if u.estimated else ""
    console.print(
        f"cases={summary.total_cases} target_errors={summary.failed_cases} "
        f"judge_calls={summary.judge_calls} "
        f"tokens_in={u.prompt_tokens} tokens_out={u.completion_tokens} "
        f"tokens_total={u.total_tokens}{est}"
        + (f" · {u.provider}/{u.model}" if u.provider else "")
    )
