#!/usr/bin/env bash
# Thin runner used by action.yml — never swallows audit exit codes incorrectly.
set -uo pipefail

CONFIG="${AUDITAI_CONFIG:-auditai.yml}"
OUT="${AUDITAI_OUT:-auditai-out}"
FAIL_ON="${AUDITAI_FAIL_ON:-}"
BASELINE="${AUDITAI_BASELINE:-}"
MAX_DROP="${AUDITAI_MAX_DROP:-0.05}"

mkdir -p "$OUT"

ARGS=(run --config "$CONFIG" --out "$OUT")
if [[ -n "$FAIL_ON" ]]; then
  ARGS+=(--fail-on "$FAIL_ON")
fi

set +e
auditai "${ARGS[@]}"
EXIT_CODE=$?
set -e

REPORT_MD="${OUT}/auditai-report.md"
REPORT_JSON="${OUT}/auditai-report.json"

if [[ ! -f "$REPORT_MD" ]]; then
  # Still produce a minimal report so PR comment has content on config errors
  {
    echo "## 🛡️ AuditAI Report"
    echo "**Status:** ⚠️ NO REPORT · exit_code=${EXIT_CODE}"
    echo ""
    echo "_CLI exited before writing a full report (config/auth/target error)._"
  } > "$REPORT_MD"
fi

# A threshold pass can still regress relative to the project's known-good run.
# Preserve an existing audit failure; otherwise use the comparison exit code.
if [[ -n "$BASELINE" && -f "$REPORT_JSON" ]]; then
  set +e
  COMPARE_OUTPUT=$(auditai compare \
    --baseline "$BASELINE" \
    --current "$REPORT_JSON" \
    --max-drop "$MAX_DROP" 2>&1)
  COMPARE_EXIT=$?
  set -e

  {
    echo ""
    echo "## Baseline regression"
    echo '```text'
    printf '%s\n' "$COMPARE_OUTPUT"
    echo '```'
  } >> "$REPORT_MD"

  if [[ "$EXIT_CODE" -eq 0 && "$COMPARE_EXIT" -ne 0 ]]; then
    EXIT_CODE=$COMPARE_EXIT
  fi
fi

PASSED=false
if [[ "$EXIT_CODE" -eq 0 ]]; then
  PASSED=true
fi

# GitHub Actions step outputs
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "exit-code=${EXIT_CODE}"
    echo "passed=${PASSED}"
    echo "report-md=${REPORT_MD}"
    echo "report-json=${REPORT_JSON}"
  } >> "$GITHUB_OUTPUT"
fi

echo "AuditAI finished exit_code=${EXIT_CODE} passed=${PASSED}"
# Do not exit non-zero here — composite step must complete so comment/artifact run.
# Final fail is handled by the last step in action.yml.
exit 0
