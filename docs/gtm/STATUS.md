# GTM / project status — AuditAI

**Snapshot:** 2026-07-16 (live re-check)  
**Last synced:** 2026-07-16  
**Owner account:** [iZenDeveloper](https://github.com/iZenDeveloper)  
**Product repo:** https://github.com/iZenDeveloper/auditai  

Update this file when opening PRs, getting maintainer replies, or shipping releases.  
Machine log: [`out/pr_log.jsonl`](./out/pr_log.jsonl).

---

## 1. Product (engineering)

| Item | Status |
|------|--------|
| Public repo | https://github.com/iZenDeveloper/auditai |
| Stars / forks | **0 / 0** |
| Releases | **v0.1.0**, **v0.1.1** (latest); floating tag `v0.1` → v0.1.1 |
| CLI | `auditai run` / `validate` / `init` / `report --pdf` |
| Judge BYOK | `openai` · `xai` (Grok) · `mock` |
| Reports | JSON / Markdown / terminal · **`judge_usage`** tokens |
| GitHub Action | `iZenDeveloper/auditai@v0.1` |
| Cloud API + dashboard | Stub present (not GTM-critical yet) |

Install:

```bash
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"
```

---

## 2. Guerrilla PRs (acquisition)

**Rules:** public docs only · honest metrics · ~2–3 quality PRs/day · badge only if maintainer opts in.

| # | Target | PR | State | Baseline | Maintainer | Notes |
|---|--------|-----|-------|----------|------------|-------|
| 1 | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#25](https://github.com/qtuanph/chatbot-rag/pull/25) | **CLOSED** (not merged) | PASS (mock cũ) | **qtuanph — positive** (2026-07-16): thanks + intends merge + invites RAG accuracy help | We replied: reopen/merge tip + offer hybrid eval help |
| 2 | [vietnam-labor-law-rag](https://github.com/ducdanh2304/vietnam-labor-law-rag) | [#1](https://github.com/ducdanh2304/vietnam-labor-law-rag/pull/1) | OPEN | FAIL Grok | none | Follow-up done |
| 3 | [Traffic-law-chatbot](https://github.com/tontide1/Traffic-law-chatbot) | [#9](https://github.com/tontide1/Traffic-law-chatbot/pull/9) | OPEN | FAIL Grok | none (Sourcery bot only) | Sourcery addressed |
| 4 | [BIN9721/Chatbot](https://github.com/BIN9721/Chatbot) | [#1](https://github.com/BIN9721/Chatbot/pull/1) | OPEN | FAIL Grok | none | Follow-up done |
| 5 | [SimpleRAG](https://github.com/quyen244/SimpleRAG) | [#1](https://github.com/quyen244/SimpleRAG/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 6 | [rag-traffic-vn](https://github.com/congmnguyen/rag-traffic-vn) | [#1](https://github.com/congmnguyen/rag-traffic-vn/pull/1) | OPEN | FAIL Grok | none | Opened 2026-07-13; follow-up 2026-07-16 |
| 7 | [LexMind](https://github.com/hnamyud/LexMind) | [#2](https://github.com/hnamyud/LexMind/pull/2) | OPEN | FAIL Grok | none | Opened 2026-07-13; follow-up 2026-07-16 |
| 8 | [TubeNote](https://github.com/buitrongtrinh/TubeNote) | [#1](https://github.com/buitrongtrinh/TubeNote/pull/1) | OPEN | FAIL Grok | none | Opened 2026-07-13; follow-up 2026-07-16 |

### KPI snapshot (2026-07-16)

| KPI | Current | Early target |
|-----|--------:|--------------|
| PRs opened | **8** | ≥10 |
| Open now | **7** | — |
| Closed (no merge yet) | **1** (#25) | — |
| Merged | **0** | ≥1–3 |
| Human maintainer replies | **1** (qtuanph — positive) | ≥3 |
| AuditAI stars | **0** | organic after merge/badge |
| Follow-ups | **8/8** | — |

**Milestone:** first positive maintainer reply on chatbot-rag #25.  
**Action:** wait for reopen/merge; optional follow-up on retrieval accuracy contribution.

---

## 3. GTM tooling

| Tool | Path |
|------|------|
| Scan | `scripts/gtm/scan_github.py` |
| Prep | `scripts/gtm/guerrilla_prep.py` |
| One-shot | `scripts/gtm/open_guerrilla_pr.py` / `run_growth_hack.sh --open-pr` |
| PR body | `scripts/gtm/fill_pr_body.py` |
| Playbook | [`GROWTH_HACK.md`](./GROWTH_HACK.md) · [`TARGETS.md`](./TARGETS.md) |

---

## 4. Principles in force

1. Public docs only.  
2. Weak mock adapter — honest FAIL under real judge.  
3. Committed yml: **`judge.provider: mock`** + **`AUDITAI_TARGET_URL`**.  
4. Badge only if maintainer opts in.  
5. No second ping for ≥5–7 days after follow-up.  
6. No secrets in repo/chat.

---

## 5. Backlog

| Priority | Item |
|:--------:|------|
| **P0** | Watch #25: reopen/merge by qtuanph; reply if they want retrieval help |
| Wait | Replies on remaining 7 OPEN PRs |
| P1 | Optional deeper contribution on chatbot-rag hybrid accuracy |
| P1 | HiTrong draft PR when cadence allows |
| P2 | About/topics on auditai · optional PyPI |

---

## 6. Scorecard

| Layer | /10 | Note |
|-------|----:|------|
| Product build | 8 | v0.1.x shippable |
| GTM execution | 7 | 8 PRs + first positive reply |
| Outcomes | 3 | Still 0 merge / 0 stars |

---

## 7. Changelog of this status file

| Date | Change |
|------|--------|
| 2026-07-12 | Initial export |
| 2026-07-12 | Live re-sync 5 OPEN |
| 2026-07-16 | 8 PRs; #25 CLOSED + positive qtuanph reply; follow-ups on 4 newest |

*Refresh with `gh pr view` before major decisions.*
