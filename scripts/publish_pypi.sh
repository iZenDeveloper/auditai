#!/usr/bin/env bash
# Local one-shot: build + upload auditai to PyPI.
# Auth: ~/.config/pypi_token  OR  $PYPI_API_TOKEN  OR  $UV_PUBLISH_TOKEN
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

token="${PYPI_API_TOKEN:-${UV_PUBLISH_TOKEN:-}}"
if [[ -z "$token" && -f "${HOME}/.config/pypi_token" ]]; then
  token="$(tr -d ' \n\r' <"${HOME}/.config/pypi_token")"
fi
if [[ -z "$token" ]]; then
  echo "ERROR: set PYPI_API_TOKEN or write ~/.config/pypi_token (pypi-…)." >&2
  echo "See docs/PYPI.md for Trusted Publishing (no local token)." >&2
  exit 1
fi

echo "== tests =="
if [[ -x .venv/bin/pytest ]]; then
  .venv/bin/pytest -q
else
  python3 -m pytest -q
fi

echo "== build =="
rm -rf dist
if command -v uv >/dev/null 2>&1; then
  uv build
else
  python3 -m pip install -q build
  python3 -m build
fi

echo "== smoke wheel =="
smoke="$(mktemp -d)"
python3 -m venv "$smoke/v"
"$smoke/v/bin/pip" -q install dist/auditai-*-py3-none-any.whl
ver="$("$smoke/v/bin/auditai" --version)"
echo "installed auditai $ver"
rm -rf "$smoke"

echo "== publish =="
if command -v uv >/dev/null 2>&1; then
  uv publish --token "$token"
else
  python3 -m pip install -q twine
  TWINE_USERNAME=__token__ TWINE_PASSWORD="$token" python3 -m twine upload dist/*
fi

echo "OK → https://pypi.org/project/auditai/"
