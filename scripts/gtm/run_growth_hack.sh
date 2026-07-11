#!/usr/bin/env bash
# One-shot helper: scan → (optional) prep first hit
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

OUT_DIR="${OUT_DIR:-docs/gtm/out}"
mkdir -p "$OUT_DIR"

echo "== Bước 1: scan =="
python3 scripts/gtm/scan_github.py \
  --keywords "langchain rag,rag chatbot,vietnam chatbot,vietnamese rag,zalo bot,zalo chatbot,chatbot tuyển sinh,topic:rag language:Python" \
  --min-stars 1 \
  --max-stars 800 \
  --out "$OUT_DIR/scan_results.jsonl" \
  --top 30 \
  --print-markdown | tee "$OUT_DIR/scan_top.md"

if [[ "${1:-}" == "--prep" && -n "${2:-}" ]]; then
  echo "== Bước 2: guerrilla prep $2 =="
  python3 scripts/gtm/guerrilla_prep.py --repo "$2" --workdir "${WORKDIR:-/tmp/auditai-guerrilla}" --questions 20
fi

echo "Done. Next: review $OUT_DIR/scan_top.md then guerrilla_prep + auditai run + PR."
