# GTM / project status — AuditAI

**Snapshot:** 2026-07-12  
**Owner account:** [iZenDeveloper](https://github.com/iZenDeveloper)  
**Product repo:** https://github.com/iZenDeveloper/auditai  

Update this file when opening PRs, getting maintainer replies, or shipping releases.  
Machine log: [`out/pr_log.jsonl`](./out/pr_log.jsonl).

---

## 1. Product (engineering)

| Item | Status |
|------|--------|
| Public repo | https://github.com/iZenDeveloper/auditai |
| Stars / forks | 0 / 0 *(update live on GitHub)* |
| Releases | **v0.1.0**, **v0.1.1** (latest); floating tag `v0.1` → v0.1.1 |
| CLI | `auditai run` / `validate` / `init` / `report --pdf` |
| Judge BYOK | `openai` · `xai` (Grok) · `mock` |
| Reports | JSON / Markdown / terminal · **`judge_usage`** tokens (v0.1.1) |
| GitHub Action | `iZenDeveloper/auditai@v0.1` |
| Cloud API + dashboard | Stub present (not GTM-critical yet) |
| Tests | Green on last local runs (~33) |

### Recent product commits (high level)

- v0.1.0 — open-core CLI + Action + cloud stub  
- v0.1.1 — judge token usage, xAI judge, guerrilla prep improvements  
- One-shot `open_guerrilla_pr.py` · no PAT in git remotes · commit **mock judge** + `AUDITAI_TARGET_URL` by default  

Install:

```bash
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"
```

---

## 2. Guerrilla PRs (acquisition)

**Rules:** public repos only · docs-public datasets · honest metrics (no greenwash) · ~2–3 quality PRs/day · badge only if maintainer opts in.

| # | Target | PR | State | Baseline metrics | Notes |
|---|--------|-----|-------|------------------|-------|
| 1 | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#25](https://github.com/qtuanph/chatbot-rag/pull/25) | OPEN | PASS (older mock-judge run) | Follow-up posted; Vercel bot only; URL env fix pushed |
| 2 | [ducdanh2304/vietnam-labor-law-rag](https://github.com/ducdanh2304/vietnam-labor-law-rag) | [#1](https://github.com/ducdanh2304/vietnam-labor-law-rag/pull/1) | OPEN | FAIL (Grok) | Honest fail; follow-up; mock default fix |
| 3 | [tontide1/Traffic-law-chatbot](https://github.com/tontide1/Traffic-law-chatbot) | [#9](https://github.com/tontide1/Traffic-law-chatbot/pull/9) | OPEN | FAIL (Grok) | Sourcery review → fixed URL/env + mock default + reply |
| 4 | [BIN9721/Chatbot](https://github.com/BIN9721/Chatbot) | [#1](https://github.com/BIN9721/Chatbot/pull/1) | OPEN | FAIL (Grok) · 0 TODO dataset | Follow-up; mock default fix |
| 5 | [quyen244/SimpleRAG](https://github.com/quyen244/SimpleRAG) | [#1](https://github.com/quyen244/SimpleRAG/pull/1) | OPEN | FAIL (Grok) · 0 TODO dataset | Newest; mock + `AUDITAI_TARGET_URL` in commit |

### KPI snapshot (2026-07-12)

| KPI | Current | Early target (see GROWTH_HACK) |
|-----|--------:|--------------------------------|
| PRs opened | **5** | ≥10 |
| Merged | **0** | ≥1–3 |
| Human maintainer replies | **0** | ≥3 |
| AuditAI stars | **0** | organic after merge/badge |
| Follow-ups sent | **4/5** (SimpleRAG pending T+2–3d) | — |

**Bottleneck:** maintainer response rate — not missing CLI features.

---

## 3. GTM tooling

| Tool | Path | Role |
|------|------|------|
| Scan | `scripts/gtm/scan_github.py` | Find RAG/chatbot targets |
| Prep | `scripts/gtm/guerrilla_prep.py` | Clone + dataset (0 TODO default) + weak mock |
| One-shot PR | `scripts/gtm/open_guerrilla_pr.py` | prep → audit → body → fork/push → PR → log |
| Wrapper | `scripts/gtm/run_growth_hack.sh` | scan / prep / `--open-pr` |
| PR body fill | `scripts/gtm/fill_pr_body.py` | Metrics + token placeholders |
| Templates | `docs/gtm/templates/` | PR_BODY_VI, badge |
| Drafts | `docs/gtm/drafts/` | HiTrong, towardsai (not all shipped as PRs yet) |
| Targets list | [`TARGETS.md`](./TARGETS.md) | Priority A/B |
| Playbook | [`GROWTH_HACK.md`](./GROWTH_HACK.md) | 4-step viral PR loop |

### One-shot usage

```bash
export GITHUB_TOKEN="$(tr -d ' \n' < ~/.config/github_token)"
# optional real judge for baseline numbers only (committed yml stays mock):
# export XAI_API_KEY=...

./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge xai --yes
./scripts/gtm/run_growth_hack.sh --open-pr owner/name --dry-run
```

---

## 4. Principles in force

1. Dataset only from **public** README/docs.  
2. Mock adapter is **intentionally weak** — real LLM judge may FAIL; do not “smart mock” for vanity greens.  
3. Committed `auditai.yml`: **`judge.provider: mock`** + **`AUDITAI_TARGET_URL`**.  
4. No badge unless maintainer wants it.  
5. No second follow-up ping for ≥5–7 days after first follow-up.  
6. Never commit secrets; PAT in `~/.config/github_token` only.

---

## 5. Backlog

| Priority | Item |
|:--------:|------|
| Wait | Maintainer reply / merge on open PRs |
| P1 | Follow-up **SimpleRAG #1** after T+2–3 days |
| P1 | Open HiTrong / other TARGETS drafts when cadence allows |
| P2 | GitHub About + topics on auditai |
| P2 | Optional PyPI publish |
| P3 | Cloud multi-tenant / paid path |

---

## 6. Scorecard (qualitative)

| Layer | Score /10 | Note |
|-------|----------:|------|
| Product build | 8 | v0.1.x shippable CLI + Action + xAI |
| GTM execution | 6 | 5 PRs + automation; no social proof yet |
| Outcomes (merge/stars) | 2 | Funnel stuck at “PR open” |

---

## 7. Changelog of this status file

| Date | Change |
|------|--------|
| 2026-07-12 | Initial export from session progress review |

*Refresh metrics/PR states with `gh pr view` before major decisions.*
