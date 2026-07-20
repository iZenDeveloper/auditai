from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _fake_auditai(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable = bin_dir / "auditai"
    executable.write_text(
        """#!/usr/bin/env bash
set -eu
if [[ "$1" == "run" ]]; then
  out="auditai-out"
  while [[ $# -gt 0 ]]; do
    if [[ "$1" == "--out" ]]; then out="$2"; shift 2; else shift; fi
  done
  mkdir -p "$out"
  printf '%s\n' '{"aggregates":{"faithfulness":{"mean":0.8}}}' > "$out/auditai-report.json"
  printf '%s\n' '## Audit report' > "$out/auditai-report.md"
  exit "${FAKE_AUDIT_EXIT:-0}"
fi
if [[ "$1" == "compare" ]]; then
  echo "fake regression comparison"
  exit "${FAKE_COMPARE_EXIT:-0}"
fi
exit 3
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return bin_dir


def _run_action(tmp_path: Path, *, audit_exit: int, compare_exit: int) -> tuple[str, str]:
    bin_dir = _fake_auditai(tmp_path)
    baseline = tmp_path / "baseline.json"
    baseline.write_text("{}", encoding="utf-8")
    github_output = tmp_path / "github-output.txt"
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "GITHUB_OUTPUT": str(github_output),
        "AUDITAI_BASELINE": str(baseline),
        "AUDITAI_OUT": "reports",
        "FAKE_AUDIT_EXIT": str(audit_exit),
        "FAKE_COMPARE_EXIT": str(compare_exit),
    }
    completed = subprocess.run(
        ["bash", str(ROOT / "action" / "run.sh")],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return github_output.read_text(encoding="utf-8"), completed.stdout


def test_action_runner_uses_regression_exit_code_after_audit_pass(tmp_path: Path):
    outputs, stdout = _run_action(tmp_path, audit_exit=0, compare_exit=1)

    assert "exit-code=1" in outputs
    assert "passed=false" in outputs
    assert "exit_code=1 passed=false" in stdout
    report = (tmp_path / "reports" / "auditai-report.md").read_text(encoding="utf-8")
    assert "## Baseline regression" in report
    assert "fake regression comparison" in report


def test_action_runner_preserves_original_audit_failure(tmp_path: Path):
    outputs, _stdout = _run_action(tmp_path, audit_exit=2, compare_exit=1)

    assert "exit-code=2" in outputs
    assert "passed=false" in outputs
