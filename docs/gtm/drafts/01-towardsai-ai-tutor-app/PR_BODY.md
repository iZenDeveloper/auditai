## Optional CI gate for RAG answer quality (AuditAI)

Hi Towards AI team 👋

You already have a serious eval program (`evals/`, batteries, faithfulness notes in `evals.md`). This contribution proposes an **optional, lightweight CI companion** that can fail a workflow when faithfulness / relevancy / basic prompt-injection checks regress — complementary to your offline batteries, not a replacement.

### Tool

[AuditAI](https://github.com/iZenDeveloper/auditai) — open-core CLI + GitHub Action:

- Runs **in the consumer’s CI** (BYOK: their `OPENAI_API_KEY` for LLM-as-judge)
- Metrics: **Faithfulness**, **Answer Relevancy**, **Prompt Injection**
- Exit code gate for PRs / manual workflows

### Why it might fit here

| Your stack | AuditAI role |
|------------|--------------|
| Offline batteries + human/judge grades | Deep experiment quality |
| Optional CI smoke on tutor answers | Fast regression signal on PRs |

### What’s in this PR

- [ ] `tests/auditai/dataset.json` — small **public educational** smoke set (no student private text)
- [ ] `tests/auditai/auditai.yml` — example config
- [ ] `scripts/auditai_chat_adapter.py` — thin JSON adapter (your `/api/chat` is SSE)
- [ ] Optional workflow: **workflow_dispatch only** (no surprise API spend)

### How maintainers run it

```bash
# terminal 1 — start tutor API as documented
uv run -m app.api

# terminal 2 — JSON adapter (collects a non-stream answer for AuditAI)
python scripts/auditai_chat_adapter.py  # listens on :18080

# terminal 3
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
export OPENAI_API_KEY=...   # judge only
auditai run --config tests/auditai/auditai.yml
```

### Ask

1. Are you open to an **optional** CI smoke gate, or prefer docs-only?
2. Should the workflow stay `workflow_dispatch`, or also run on `pull_request` for `app/**`?

Happy to rework thresholds, dataset size, or drop the workflow and keep docs only.

Thanks for open-sourcing a real production-shaped tutor 🙏
