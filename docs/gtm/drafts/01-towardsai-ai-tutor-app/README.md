# Draft PR — towardsai/ai-tutor-app

## Why this target

- Production-style **agentic RAG** with FastAPI + LangGraph.
- They already invest in **`evals/`** and `evals.md` — AuditAI is a **CI gate companion**, not a replacement.
- Active (pushed 2026-07), Apache-2.0, clear architecture docs.

## Constraint

`POST /api/chat` returns **SSE** (Vercel AI SDK protocol).  
AuditAI HTTP target expects **JSON** `{ "answer": "..." }`.

→ Draft includes a **tiny optional adapter** `scripts/auditai_chat_adapter.py` that:

1. Calls their existing chat service path **or** a documented internal helper once you run the app locally.
2. For CI: starts the adapter next to the API and points `auditai.yml` at it.

**Recommended contribution shape (minimal risk):**

- Add `auditai.yml` + `tests/auditai/dataset.json` only if they accept external gate.
- Prefer opening a **Discussion / Issue first** if the PR feels large: “Would you welcome a lightweight CI faithfulness gate?”

For the actual PR, **safer path for first contact:**

### Option A — Issue first (recommended)

Open issue linking AuditAI + their evals program; ask if they want a workflow.

### Option B — Small PR

Only:

1. `tests/auditai/dataset_smoke.json` — public course-themed questions (no student private data).
2. `auditai.yml` example under `tests/auditai/`.
3. Docs blurb in `evals/contributing.md` or `evals.md` section “CI gate (optional)”.
4. Optional workflow `workflow_dispatch` only (not on every PR) to avoid surprise OpenAI spend.

## Files in this folder

| File | Purpose |
|------|---------|
| `PR_BODY.md` | Copy-paste PR / issue body |
| `auditai.yml` | Example config |
| `dataset.json` | Smoke dataset (public educational topics only) |
| `workflow-auditai.yml` | Optional GitHub Action (manual trigger) |
| `auditai_chat_adapter.py` | Optional JSON adapter sketch |

## How to open the PR (you)

```bash
# fork + clone towardsai/ai-tutor-app
# copy files from this folder into the fork as described in PR_BODY.md
# do NOT force OPENAI spend on their default PR CI without consent
```

## Status

- [x] Research complete
- [x] Draft files written
- [ ] Human review of tone
- [ ] Issue or PR opened on upstream
