# GTM / project status — AuditAI

**Snapshot:** 2026-07-18 (#25 + #26 both MERGED)  
**Last synced:** 2026-07-18  
**Owner account:** [iZenDeveloper](https://github.com/iZenDeveloper)  
**Product repo:** https://github.com/iZenDeveloper/auditai  

Update this file when opening PRs, getting maintainer replies, or shipping releases.  
Machine log: [`out/pr_log.jsonl`](./out/pr_log.jsonl) (gitignored under `out/`).

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
| Tests | **34+** unit (incl. GTM helpers) |

Install:

```bash
pip install auditai-cli                # PyPI package name (CLI still: auditai)
# pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"  # fallback
```

---

## 2. Guerrilla PRs (acquisition)

**Rules:** public docs only · honest metrics · ~2–3 quality PRs/day · badge only if maintainer opts in · no second ping &lt;5–7 days after follow-up.

| # | Target | PR | State | Baseline | Maintainer | Notes |
|---|--------|-----|-------|----------|------------|-------|
| 1 | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#25](https://github.com/qtuanph/chatbot-rag/pull/25) | **MERGED** 2026-07-16 | PASS (mock cũ) | **qtuanph — positive + merge** | First guerrilla merge · thank-you posted |
| 1b | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#26](https://github.com/qtuanph/chatbot-rag/pull/26) | **MERGED** 2026-07-18 | n/a (Recall@k) | **qtuanph** | Offline Recall@k / MRR harness · thank-you + badge ask [posted](https://github.com/qtuanph/chatbot-rag/pull/26#issuecomment-5009416099) |
| 2 | [vietnam-labor-law-rag](https://github.com/ducdanh2304/vietnam-labor-law-rag) | [#1](https://github.com/ducdanh2304/vietnam-labor-law-rag/pull/1) | OPEN | FAIL Grok | none | 2nd soft FU 2026-07-18 (PyPI + #25) |
| 3 | [Traffic-law-chatbot](https://github.com/tontide1/Traffic-law-chatbot) | [#9](https://github.com/tontide1/Traffic-law-chatbot/pull/9) | OPEN | FAIL Grok | none (Sourcery) | 2nd soft FU 2026-07-18 |
| 4 | [BIN9721/Chatbot](https://github.com/BIN9721/Chatbot) | [#1](https://github.com/BIN9721/Chatbot/pull/1) | OPEN | FAIL Grok | none | 2nd soft FU 2026-07-18 |
| 5 | [SimpleRAG](https://github.com/quyen244/SimpleRAG) | [#1](https://github.com/quyen244/SimpleRAG/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 6 | [rag-traffic-vn](https://github.com/congmnguyen/rag-traffic-vn) | [#1](https://github.com/congmnguyen/rag-traffic-vn/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 7 | [LexMind](https://github.com/hnamyud/LexMind) | [#2](https://github.com/hnamyud/LexMind/pull/2) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 8 | [TubeNote](https://github.com/buitrongtrinh/TubeNote) | [#1](https://github.com/buitrongtrinh/TubeNote/pull/1) | OPEN | FAIL Grok | **buitrongtrinh — positive** (2026-07-18): will review; RAG reference useful | Thank-you reply posted |
| 9 | [viparse](https://github.com/minhtridinh-kayden/viparse) | [#54](https://github.com/minhtridinh-kayden/viparse/pull/54) | MERGED then **reverted #59** | FAIL Grok | **minhtridinh-kayden**: wrong fit (loader≠RAG) + supply-chain | Graceful ack posted; avoid pure loaders |
| 10 | [VietNam-CyberLaw-RAG-](https://github.com/QuangVu404/VietNam-CyberLaw-RAG-) | [#1](https://github.com/QuangVu404/VietNam-CyberLaw-RAG-/pull/1) | OPEN | FAIL Grok | none | 2026-07-16 |
| 11 | [Edu_Omni_MyMind](https://github.com/khang3004/Edu_Omni_MyMind) | [#2](https://github.com/khang3004/Edu_Omni_MyMind/pull/2) | OPEN | FAIL Grok | none | force-add `tests/` |
| 12 | [Chatbot_tuyen_sinh_FPTU_2026](https://github.com/HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026) | [#1](https://github.com/HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026/pull/1) | OPEN | FAIL Grok | none | MIT · VN |
| 13 | [local-rag-pdf-assistant](https://github.com/SagarCodes03/local-rag-pdf-assistant) | [#1](https://github.com/SagarCodes03/local-rag-pdf-assistant/pull/1) | OPEN | FAIL Grok | none | 2026-07-16 |
| 14 | [banhmi](https://github.com/dannyota/banhmi) | [#1](https://github.com/dannyota/banhmi/pull/1) | OPEN | FAIL Grok | none | base=`master` · VN banking |
| 15 | [RAG-Student-Chatbot](https://github.com/HiTrong/RAG-Student-Chatbot) | [#1](https://github.com/HiTrong/RAG-Student-Chatbot/pull/1) | OPEN | FAIL Grok | none | MIT · draft was ready |
| 16 | [hybrid-search-eval](https://github.com/kunal4040/hybrid-search-eval) | [#1](https://github.com/kunal4040/hybrid-search-eval/pull/1) | OPEN | FAIL Grok | none | eval-adjacent target |
| 17 | [Agentic-RAG-Anime-…](https://github.com/drae1712/Agentic-RAG-Anime-Recommender-System) | [#1](https://github.com/drae1712/Agentic-RAG-Anime-Recommender-System/pull/1) | OPEN | FAIL Grok | none | git-lfs; finished after LFS-off |

### KPI snapshot (2026-07-18)

| KPI | Current | Early target |
|-----|--------:|--------------|
| Quality-gate PRs opened | **16** (+#26 harness) | ≥10 ✓ |
| Open quality-gate | **~15** | — |
| **Merged** | **2** (#25 quality-gate + #26 Recall@k) | ≥1–3 ✓ |
| #26 | **MERGED** 2026-07-18T01:40:53Z | — |
| Human maintainer replies | **3** (qtuanph · TubeNote · viparse) | ≥3 ✓ |
| AuditAI stars | **0** | after badge / social proof |
| PyPI | **`auditai-cli` 0.1.1** live | ✓ |
| Follow-ups | older set 2nd soft FU ×3 | no spam on 07-16 batch |

**Milestone:** **two merges** on chatbot-rag (#25 + #26) · PyPI `auditai-cli` live · champion maintainer qtuanph.

---

## 3. GTM tooling

| Tool | Path |
|------|------|
| Scan | `scripts/gtm/scan_github.py` |
| Prep | `scripts/gtm/guerrilla_prep.py` |
| One-shot | `scripts/gtm/open_guerrilla_pr.py` |
| PR body | `scripts/gtm/fill_pr_body.py` |
| Playbook | [`GROWTH_HACK.md`](./GROWTH_HACK.md) · [`TARGETS.md`](./TARGETS.md) |
| **Codex / agent handoff** | [`HANDOFF_CODEX.md`](./HANDOFF_CODEX.md) · root [`AGENTS.md`](../../AGENTS.md) |
| PyPI | [`docs/PYPI.md`](../PYPI.md) · `publish-pypi.yml` |

**Script harden:** `git add -f` · default branch · LFS-off · no PAT in remotes.

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
| **P0** | **#25 + #26 MERGED** ✓ · **PyPI live** ✓ |
| P1 | Badge ask on #26 — wait ≥7d; no re-ping |
| P1 | Case study on README ✓ · optional social repost |
| Wait | TubeNote review · no re-ping |
| Wait | Soft FU batch 16/07 ~**21–23/07** only |
| **Next PR** | **towardsai/ai-tutor-app** (see [`TARGETS.md`](./TARGETS.md) shortlist) — max 1 |
| P2 | About/topics ✓ · avoid loaders (viparse lesson in TARGETS) |

---

## 6. Scorecard

| Layer | /10 | Note |
|-------|----:|------|
| Product build | 8 | v0.1.x shippable · tests green |
| GTM execution | 8 | 16+ PRs + first merge |
| Outcomes | **7** | **2 merges** (same champion) · **PyPI** · 0 stars |

---

## 7. Changelog of this status file

| Date | Change |
|------|--------|
| 2026-07-12 | Initial export |
| 2026-07-16 | Portfolio → #17; LFS; PyPI prep |
| 2026-07-17 | **#25 MERGED**; #26 closed + reopen tip; thank-you on #25; KPI outcomes ↑ |
| 2026-07-17 | **PyPI:** published `auditai-cli==0.1.1` (bare `auditai` blocked vs `audit-ai`) |
| 2026-07-18 | #26 reopened by qtuanph; conflicts resolved → MERGEABLE; 2nd soft FU ×3 oldest PRs |
| 2026-07-18 | **#26 MERGED** 01:40 UTC — 2nd merge; champion qtuanph |
| 2026-07-18 | TubeNote positive review intent; viparse revert+lesson; replies posted |
| 2026-07-18 | TARGETS: fit filter + avoid loaders + shortlist next = towardsai |
| 2026-07-18 | README case study: chatbot-rag #25 + #26 |
| 2026-07-18 | GitHub About + topics set (PyPI homepage) |
| 2026-07-18 | HANDOFF_CODEX.md + AGENTS.md for next agent |

*Refresh with `gh pr view` / search before major decisions.*
