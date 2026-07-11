#!/usr/bin/env bash
# Growth-hack helpers
#
#   # scan only
#   ./scripts/gtm/run_growth_hack.sh
#
#   # prep one repo (no PR)
#   ./scripts/gtm/run_growth_hack.sh --prep owner/name
#
#   # one-shot: prep → audit → open PR
#   ./scripts/gtm/run_growth_hack.sh --open-pr owner/name
#   ./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge xai --yes
#   ./scripts/gtm/run_growth_hack.sh --open-pr owner/name --dry-run
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

OUT_DIR="${OUT_DIR:-docs/gtm/out}"
WORKDIR="${WORKDIR:-/tmp/auditai-guerrilla}"
mkdir -p "$OUT_DIR"

usage() {
  cat <<'EOF'
Usage:
  run_growth_hack.sh                     # scan GitHub → docs/gtm/out/
  run_growth_hack.sh --prep owner/name   # guerrilla_prep only
  run_growth_hack.sh --open-pr owner/name [open_guerrilla_pr.py flags...]

Examples:
  export GITHUB_TOKEN="$(tr -d ' \n' < ~/.config/github_token)"
  export XAI_API_KEY=...

  ./scripts/gtm/run_growth_hack.sh --open-pr qtuanph/chatbot-rag --judge mock --dry-run
  ./scripts/gtm/run_growth_hack.sh --open-pr owner/rag-bot --judge xai --yes
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--open-pr" ]]; then
  shift
  if [[ -z "${1:-}" || "${1:-}" == -* ]]; then
    echo "ERROR: --open-pr requires owner/name" >&2
    usage
    exit 2
  fi
  REPO="$1"
  shift
  exec python3 scripts/gtm/open_guerrilla_pr.py --repo "$REPO" --workdir "$WORKDIR" "$@"
fi

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
  python3 scripts/gtm/guerrilla_prep.py --repo "$2" --workdir "$WORKDIR" --questions 20
  echo "Next: ./scripts/gtm/run_growth_hack.sh --open-pr $2 --judge mock --dry-run"
  exit 0
fi

echo "Done. Next:"
echo "  review $OUT_DIR/scan_top.md"
echo "  ./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge xai --dry-run"
echo "  ./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge xai --yes"
