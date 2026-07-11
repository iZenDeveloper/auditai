#!/usr/bin/env python3
"""Fill PR_BODY_VI.md placeholders from auditai-report.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def pass_mark(ok) -> str:
    if ok is True:
        return "✅"
    if ok is False:
        return "❌"
    return "—"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.report.read_text(encoding="utf-8"))
    agg = data.get("aggregates") or {}

    def metric(name: str) -> tuple[str, str, str]:
        m = agg.get(name) or {}
        return fmt(m.get("mean")), fmt(m.get("threshold")), pass_mark(m.get("passed"))

    f_m, f_t, f_p = metric("faithfulness")
    r_m, r_t, r_p = metric("answer_relevancy")
    i_m, i_t, i_p = metric("prompt_injection")

    usage = data.get("judge_usage") or {}
    provider = usage.get("provider") or "—"
    model = usage.get("model") or "—"
    tok_in = usage.get("prompt_tokens")
    tok_out = usage.get("completion_tokens")
    tok_total = usage.get("total_tokens")
    est = " (est.)" if usage.get("estimated") else ""
    usage_line = (
        f"Judge: **{provider}/{model}** · "
        f"tokens in/out/total = **{tok_in}/{tok_out}/{tok_total}**{est}"
        if usage
        else ""
    )

    body = args.template.read_text(encoding="utf-8")
    repl = {
        "{{FAITHFULNESS}}": f_m,
        "{{FAITHFULNESS_THR}}": f_t,
        "{{FAITHFULNESS_PASS}}": f_p,
        "{{RELEVANCY}}": r_m,
        "{{RELEVANCY_THR}}": r_t,
        "{{RELEVANCY_PASS}}": r_p,
        "{{INJECTION}}": i_m,
        "{{INJECTION_THR}}": i_t,
        "{{INJECTION_PASS}}": i_p,
        "{{TOTAL_CASES}}": str(data.get("total_cases", "—")),
        "{{FAILED_CASES}}": str(data.get("failed_cases", "—")),
        "{{EXIT_REASON}}": str(data.get("exit_reason", "—")),
        "{{JUDGE_CALLS}}": str(data.get("judge_calls", "—")),
        "{{JUDGE_PROVIDER}}": str(provider),
        "{{JUDGE_MODEL}}": str(model),
        "{{TOKENS_IN}}": str(tok_in if tok_in is not None else "—"),
        "{{TOKENS_OUT}}": str(tok_out if tok_out is not None else "—"),
        "{{TOKENS_TOTAL}}": str(tok_total if tok_total is not None else "—"),
        "{{JUDGE_USAGE_LINE}}": usage_line,
    }
    for k, v in repl.items():
        body = body.replace(k, v)

    # Auto disclaimer for mock judge scores
    if provider == "mock" and "mock judge" not in body.lower():
        body += (
            "\n\n> **Note:** baseline used `judge.provider=mock` (offline). "
            "Re-run with `openai` or `xai` for LLM-as-judge numbers before citing as production evidence.\n"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
