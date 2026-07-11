# Changelog

All notable changes to AuditAI are documented in this file.

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

### Known limitations

- Judge providers: OpenAI + mock only (no Anthropic yet)
- Cloud: SQLite, single project key auth, no multi-user billing
- Compliance PDF is **not** a government licence or legal opinion
- PyPI package name may be reserved — primary install path is git tag

### Links

- Repo: https://github.com/iZenDeveloper/auditai
- Release checklist: [docs/RELEASE_v0.1.md](docs/RELEASE_v0.1.md)
