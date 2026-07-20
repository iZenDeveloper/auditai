# Handoff for Codex — AuditAI GTM + product

**Audience:** Codex (or any coding agent) continuing work without prior chat context.  
**Owner GitHub:** [iZenDeveloper](https://github.com/iZenDeveloper)  
**Product repo:** https://github.com/iZenDeveloper/auditai  
**Handoff date:** 2026-07-18  
**Branch:** `main` (keep working here unless asked otherwise)

Read this file first, then open the linked sources of truth. **Do not invent merges, stars, or maintainer quotes** — re-check with `gh` before acting.

---

## 0. Mission (what “done” looks like)

**Product:** Open-core CLI **AuditAI** — CI quality gates for RAG/LLM (**faithfulness**, **answer relevancy**, **prompt injection**), BYOK judges (`openai` | `xai` | `mock`).

**GTM:** “Guerrilla” value PRs to public OSS RAG repos (honest metrics, public docs only) → merges → badge opt-in → installs (`auditai-cli`) → stars.

**Current phase:** **Harvest + selective depth** (not spray 3 PRs/day). Two merges landed; PyPI live; convert remaining OPEN PRs carefully; open **≤1** new high-fit PR/week when cadence allows.

---

## 1. Sources of truth (read in order)

| Priority | Path | Role |
|:--------:|------|------|
| 1 | **This file** | Cold-start handoff |
| 2 | [`STATUS.md`](./STATUS.md) | Live portfolio table + KPI + backlog |
| 3 | [`TARGETS.md`](./TARGETS.md) | Fit filter, avoid list, next shortlist |
| 4 | [`GROWTH_HACK.md`](./GROWTH_HACK.md) | Full guerrilla playbook |
| 5 | [`docs/PYPI.md`](../PYPI.md) | Publish notes (`auditai-cli`) |
| 6 | `docs/gtm/out/pr_log.jsonl` | Machine log (**gitignored** under `out/`) |
| 7 | `README.md` | Public install + **case study** chatbot-rag |

After any PR open/merge/comment: update **STATUS.md** + append **pr_log.jsonl**.

---

## 2. Product snapshot

| Item | Value |
|------|--------|
| Version | **0.1.1** (`pyproject.toml` + `src/auditai/__init__.py`) |
| PyPI name | **`auditai-cli`** (bare `auditai` rejected — similar to `audit-ai`) |
| CLI / import | Still **`auditai`** / `import auditai` |
| Install | `pip install auditai-cli` |
| Tag / Action | `v0.1.1` · `iZenDeveloper/auditai@v0.1` |
| Package layout | `src/auditai/` (hatchling) |
| Tests | `pytest -q` from repo root (expect green; ~35+) |
| Cloud | `cloud/api` + `cloud/dashboard` stubs — **not GTM-critical** |

### Key product commands

```bash
cd /path/to/auditai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,pdf]"
pytest -q
auditai --version
auditai run --config examples/rag_demo/auditai.yml --dry-run
```

Judge: `examples/xai_judge/auditai.yml` needs `XAI_API_KEY`. Mock offline: `examples/rag_demo/`.

---

## 3. Secrets & auth (never commit)

| Secret | Location / env | Used for |
|--------|----------------|----------|
| GitHub PAT | `~/.config/github_token` or `GITHUB_TOKEN` / `GH_TOKEN` | `gh`, fork, PR |
| xAI | `XAI_API_KEY` or `~/.config/xai_api_key` or Grok CLI `~/.grok/auth.json` | `--judge xai` baselines |
| OpenAI | `OPENAI_API_KEY` | optional judge |
| PyPI | `~/.config/pypi_token` or `PYPI_API_TOKEN` | `./scripts/publish_pypi.sh` |

**Rules:**

- Never put PAT in git remote URLs (scripts already public HTTPS remotes).  
- Never paste tokens into PR bodies, STATUS, or chat logs.  
- Guerrilla commits use **`judge.provider: mock`** + `AUDITAI_TARGET_URL` in yml — local audit may use xai, then `prepare_yml_for_commit` resets before push.

---

## 4. Guerrilla pipeline (how to open a PR)

### One-shot (preferred)

```bash
export GITHUB_TOKEN="$(cat ~/.config/github_token)"
# XAI optional for real baseline; mock-only if no key
python scripts/gtm/open_guerrilla_pr.py \
  --repo owner/name \
  --judge xai --model grok-4.3 \
  --yes
# Dry-run (no fork/PR):
#   ... --dry-run
```

### What the script does

1. `guerrilla_prep.py` — clone public repo → `tests/auditai/` dataset from **public docs only**  
2. Start weak mock adapter → `auditai run` (honest FAIL under Grok is OK)  
3. `fill_pr_body.py` + template `docs/gtm/templates/PR_BODY_VI.md`  
4. Fork, branch `ci/auditai-quality-gate`, **`git add -f`**, commit, push, `gh pr create`  
5. Append `docs/gtm/out/pr_log.jsonl`

### Script hardenings already in place

| Fix | Why |
|-----|-----|
| `git add -f` | Some repos gitignore `tests/` |
| Default branch via `gh repo view` | `main` vs `master` (e.g. banhmi) |
| LFS filters disabled | Missing `git-lfs` binary |
| No PAT in remotes | Secret hygiene |
| Workflow **example-only** by default | Supply-chain (viparse lesson) |

Workdirs: `/tmp/auditai-guerrilla/<owner>_<repo>/`.

### PR body install line (required)

```bash
pip install auditai-cli
# fallback: pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"
```

Optional social proof: link chatbot-rag **#25** + **#26**.

---

## 5. Wins & lessons (do not regress)

### Wins

| | |
|--|--|
| **#25** | https://github.com/qtuanph/chatbot-rag/pull/25 — AuditAI quality-gate **MERGED** |
| **#26** | https://github.com/qtuanph/chatbot-rag/pull/26 — Recall@k/MRR harness **MERGED** |
| Champion | **qtuanph** — positive, multi-message |
| PyPI | https://pypi.org/project/auditai-cli/ `0.1.1` |
| README | Case study section + Used-by style narrative |
| GitHub About | Description + homepage PyPI + topics (`rag`, `llm-eval`, …) |

### Human feedback map

| Maintainer | Repo | Sentiment | Action taken |
|------------|------|-----------|--------------|
| qtuanph | chatbot-rag | Very positive · 2 merges | Thank-you + **badge opt-in ask** on #26 — **wait ≥7d, no re-ping** |
| buitrongtrinh | TubeNote #1 | Positive · will review | Thank-you reply · **wait**, no re-ping |
| minhtridinh-kayden | viparse #54 | Professional **reject** | Merged then **revert #59**; graceful ack posted |

### Hard lessons

1. **No pure loaders/normalizers** — metrics score mock, not product (viparse).  
2. **Supply-chain sensitivity** — prefer `workflow-auditai.yml.example` / `workflow_dispatch`, not forced Actions with `pip install git+…` on day one.  
3. **Depth > spray** — two merges came from one champion + second valuable PR, not 15 silent quality-gates.  
4. Cadence now: **≤1–2 new PRs/week**, not 2–3/day.

Full avoid list: [`TARGETS.md`](./TARGETS.md).

---

## 6. Portfolio state (summary)

- **Merged (keep):** chatbot-rag #25, #26  
- **OPEN (~15):** labor-law, traffic-law, BIN9721, SimpleRAG, rag-traffic-vn, LexMind, TubeNote, CyberLaw, Edu, FPTU, local-rag-pdf, banhmi, HiTrong, hybrid-search-eval, Anime, …  
- **Dead path:** viparse (reverted) — do not re-open AuditAI there  
- Exact rows: always refresh via `STATUS.md` + `gh pr view`

### Follow-up policy

| Situation | Policy |
|-----------|--------|
| No reply yet, first FU done | Wait **≥5–7 days** before 2nd soft FU |
| 2nd FU already done (e.g. labor/traffic/BIN 2026-07-18) | **Stop** until they reply |
| Batch opened **2026-07-16** | Soft FU window ~**2026-07-21–23** (not before) |
| Badge ask qtuanph | No re-ask before **~2026-07-25**; if silent, drop |
| TubeNote | Wait for their review; no ping |

Soft FU tone: peer, opt-in, “merge or close đều ổn”, mention `auditai-cli` + #25/#26 only once if useful.

---

## 7. Ordered backlog for Codex

### Do next (P0 / P1)

1. **Before any new guerrilla:** `gh` re-check TubeNote #1 + qtuanph #26 comments for badge reply.  
2. **Soft FU batch 2026-07-16** only after **~2026-07-21** (FPTU, banhmi, HiTrong, hybrid-eval, Anime, CyberLaw, Edu, local-rag-pdf, …) — max **2–3 comments/day**, not all at once.  
3. **Next new PR (when allowed):**  
   - **Primary:** `towardsai/ai-tutor-app`  
   - Draft: `docs/gtm/drafts/01-towardsai-ai-tutor-app/`  
   - Refresh dataset from public docs; PR body uses `auditai-cli`; SSE may need thin JSON adapter (see draft README).  
   - Backups: `chatvector-ai/chatvector-ai` → `khanghoang123/vietnamese-legal-rag-portfolio`  
4. Keep STATUS/pr_log honest after each action.

### Do not

- Open 3+ new quality-gate PRs in one day.  
- Target loaders/PDF normalizers “because Vietnamese”.  
- Force-push or amend published commits without user ask.  
- Commit secrets, `docs/gtm/out/*` if policy is gitignore (out is gitignored).  
- Second-ping maintainers inside the quiet window.  
- Greenwash metrics (mock must stay weak).

### Optional product (only if user asks)

- Bump version / PyPI 0.1.2  
- Action/docs polish  
- Cloud dashboard — low priority  
- Golden encoding contrib to viparse — only if user wants non-AuditAI contribution

---

## 8. Common commands (copy-paste)

### Live PR feedback scan (pattern)

```bash
export GITHUB_TOKEN="$(cat ~/.config/github_token)"
gh pr view https://github.com/buitrongtrinh/TubeNote/pull/1 --json state,mergedAt,comments
gh pr view https://github.com/qtuanph/chatbot-rag/pull/26 --json state,mergedAt
# Issue comments:
gh api repos/OWNER/REPO/issues/N/comments --jq '.[] | {user:.user.login, at:.created_at, body:.body[0:200]}'
```

### Open one guerrilla (example)

```bash
export GITHUB_TOKEN="$(cat ~/.config/github_token)"
python scripts/gtm/open_guerrilla_pr.py \
  --repo towardsai/ai-tutor-app \
  --judge xai --model grok-4.3 \
  --yes
```

### After PR / comment

```bash
# append pr_log.jsonl (jsonl one object per line)
# edit docs/gtm/STATUS.md table + KPI
git add docs/gtm/STATUS.md   # not secrets
git commit -m "docs(gtm): ..."
git push origin main
```

### Publish PyPI (version bump required if 0.1.1 already live)

```bash
# bump pyproject + __init__; then:
./scripts/publish_pypi.sh   # needs ~/.config/pypi_token
```

---

## 9. Drafts index

| Path | Purpose |
|------|---------|
| `drafts/01-towardsai-ai-tutor-app/` | **Next PR** scaffold (yml, adapter, PR_BODY) |
| `drafts/02-hitrong-rag-student-chatbot/` | Historical; PR already opened |
| `drafts/03-qtuanph-…-retrieval-suggestions.md` | Memo that led to #26 |
| `drafts/04-qtuanph-thank-you-badge-ask.md` | Posted on #26 |

Templates: `templates/PR_BODY_VI.md`, `templates/README_BADGE.md`.

---

## 10. Definition of good work for the next agent

- Maintainer-facing comments: **peer tone**, Vietnamese or English matching their thread, short.  
- Metrics: **honest**; explain mock baseline in PR body.  
- Ethics: public docs only; badge **opt-in only**.  
- Sync STATUS + pr_log after every external action.  
- Prefer **unblocking merges** (conflicts, CI, clarifications) over opening new PRs.  
- When in doubt: re-read TARGETS fit filter and ask the user before spray.

---

## 11. Suggested first Codex session checklist

```text
[ ] Read HANDOFF_CODEX.md + STATUS.md + TARGETS.md
[ ] gh auth / token works: gh api user
[ ] pytest -q green on auditai
[ ] Scan: TubeNote #1 state; any qtuanph badge reply
[ ] If date >= 2026-07-21: plan 2–3 soft FUs for 16/07 batch (not all)
[ ] Else if user asks new PR: towardsai dry-run then --yes
[ ] Update STATUS + pr_log + commit
```

---

## 12. One-line state

**AuditAI v0.1.1 is shippable on PyPI as `auditai-cli`; GTM has a champion (chatbot-rag ×2 merges); pipeline is full of silent OPEN PRs — harvest and select, do not spray; next quality target is towardsai/ai-tutor-app when cadence allows.**
