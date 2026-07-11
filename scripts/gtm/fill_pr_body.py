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
    }
    for k, v in repl.items():
        body = body.replace(k, v)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
