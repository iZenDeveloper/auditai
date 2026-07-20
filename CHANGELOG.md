# Changelog

All notable changes to AuditAI are documented in this file.

## [Unreleased]

### Added

- Guerrilla: LFS-safe clone (`git add -f`, default branch detect, skip git-lfs filters)
- `auditai compare` regression gate for comparing current metric means with a saved baseline

### Changed

- README install leads with `pip install auditai-cli`

## [0.1.1] — PyPI distribution note

Published on PyPI as **`auditai-cli==0.1.1`** (2026-07-17).  
Bare name `auditai` is rejected by PyPI as too similar to existing `audit-ai`.  
Import package and console script remain **`auditai`**.

## [0.1.1] - 2026-07-11

### Added

- **Judge token usage** in run reports: `judge_usage.prompt_tokens` / `completion_tokens` / `total_tokens` (API-reported for OpenAI/xAI; estimated for mock)
- Terminal + Markdown report lines for tokens; cloud payload includes `judge_usage`
- Guerrilla prep: README noise filter (badges/URLs), mock adapter returns **empty contexts**, `--workflow-example-only`, default `judge: mock`
- `fill_pr_body.py`: token/judge placeholders + auto mock-judge disclaimer
- Model-not-found hint on xAI/OpenAI judge errors
- **xAI / Grok judge** (`judge.provider: xai`) — BYOK via `XAI_API_KEY`, base URL `https://api.x.ai/v1`
- OpenAI-compatible overrides on judge: `base_url`, `api_key_env` (proxies / OpenRouter-style gateways)
- Example: `examples/xai_judge/auditai.yml`

### Changed

- Default xAI model → `grok-4.3` (override in YAML; `grok-3-mini` still valid when set explicitly)
- `OpenAIJudge` is the shared OpenAI-compatible client for both `openai` and `xai`
- Package version `0.1.1`

### Install

```bash
pip install auditai
# fallback:
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"
```

## [0.1.0] - 2026-07-11

First public open-core release.

### Added

- **CLI** (`auditai`): `run`, `validate`, `init`, `report --pdf`
- YAML config v0.1 (`auditai.yml`), dataset JSON/JSONL/CSV
- Metrics: Faithfulness, Answer Relevancy, Prompt Injection
- BYOK OpenAI judge + offline `mock` judge; optional DeepEval backend
- Reports: terminal table, Markdown (PR-ready), JSON (`schema_version: 0.1`)
- CI exit codes: `0` pass · `1` audit fail · `2` config · `3` internal
- **GitHub composite Action**: gate PRs, upsert report comment, upload artifacts
- **Cloud API stub** (FastAPI/SQLite): projects, run ingest, list/detail, compliance PDF
- **Next.js dashboard**: project key login, sparklines, run history, PDF download
- Compliance PDF certificate (technical evidence + legal disclaimer)
- Examples: `rag_demo` (mock server + intentional hallucination), GitHub/GitLab CI samples

### Install (v0.1)

```bash
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
pip install "auditai[pdf] @ git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
```

```yaml
- uses: iZenDeveloper/auditai@v0.1
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```
