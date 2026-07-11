# GTM v0.1 — Growth via useful PRs

Goal: first **10–50 developers** discover AuditAI through high-signal open-source PRs (no ads).

## Prerequisites (done)

- [x] Public repo: https://github.com/iZenDeveloper/auditai
- [x] Tag `v0.1.0` installable via pip
- [x] GitHub Action `iZenDeveloper/auditai@v0.1`
- [x] CI green

## Rules

1. **Only public repos.** Never clone private code.
2. **Value first.** PR must include a real baseline report (or a clear path to run it).
3. **No spam.** 2–3 quality PRs/day max; prefer Vietnamese RAG/chatbot projects early.
4. **Opt-in badge.** Only add README badge if maintainer wants it after merge.
5. **Tone:** helpful peer, not sales.

## Workflow (per target repo)

1. Find repo (`langchain` + `rag` + `vietnam` / `chatbot` / `zalo` …).
2. Read README; draft **10–20** test questions from public docs only.
3. Locally:

```bash
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
# add auditai.yml pointing at their API or a mock if no public endpoint
auditai run --config auditai.yml
```

4. Open PR that adds:
   - `auditai.yml` (or `tests/auditai/…`)
   - optional `.github/workflows/auditai.yml` using `iZenDeveloper/auditai@v0.1`
   - short note in PR body with metrics table + PDF/artifact if available

## PR body template

```markdown
## AuditAI baseline for this project

Hi! I ran a small LLM/RAG quality check with [AuditAI](https://github.com/iZenDeveloper/auditai)
(open-source CI gate for faithfulness / relevancy / prompt-injection).

### Results (baseline)
| Metric | Score | Threshold |
|--------|-------|-----------|
| Faithfulness | X.XX | 0.80 |
| Answer relevancy | X.XX | 0.75 |
| Prompt injection | X.XX | 0.90 |

### What this PR adds
- `auditai.yml` + sample dataset (from public README only)
- Optional GitHub Action so every PR re-runs the audit (BYOK: your `OPENAI_API_KEY`)

Happy to adjust thresholds or remove the workflow if you prefer CLI-only.
```

## Workflow file to propose

```yaml
name: AuditAI
on:
  pull_request:
    paths: ["**/*.py", "**/*.ts", "**/prompt*", "auditai.yml"]
permissions:
  contents: read
  pull-requests: write
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: iZenDeveloper/auditai@v0.1
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        with:
          config: auditai.yml
          install: git+https://github.com/iZenDeveloper/auditai.git@v0.1.0
```

## Tracking

Full target list: [gtm/TARGETS.md](./gtm/TARGETS.md)

| # | Repo | PR | Status | Notes |
|---|------|-----|--------|-------|
| 1 | towardsai/ai-tutor-app | | draft ready | [drafts/01-…](./gtm/drafts/01-towardsai-ai-tutor-app/) |
| 2 | chatvector-ai/chatvector-ai | | queued | JSON `/chat` |
| 3 | HiTrong/RAG-Student-Chatbot | | **full draft** | [02-…](./gtm/drafts/02-hitrong-rag-student-chatbot/) · mock PASS |
| 4–10 | see TARGETS.md | | | |

## Success criteria (2 weeks)

- ≥10 meaningful PRs opened
- ≥3 merges or “thanks, we’ll try”
- ≥1 external issue/star from people who found the tool via PR
