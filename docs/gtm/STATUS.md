# GTM / project status — AuditAI

**Snapshot:** 2026-07-16 (STATUS + LFS hygiene)  
**Last synced:** 2026-07-16  
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
pip install auditai                    # PyPI (after first upload — see docs/PYPI.md)
# pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"  # fallback
```

---

## 2. Guerrilla PRs (acquisition)

**Rules:** public docs only · honest metrics · ~2–3 quality PRs/day · badge only if maintainer opts in · no second ping &lt;5–7 days after follow-up.

| # | Target | PR | State | Baseline | Maintainer | Notes |
|---|--------|-----|-------|----------|------------|-------|
| 1 | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#25](https://github.com/qtuanph/chatbot-rag/pull/25) | **CLOSED** (not merged) | PASS (mock cũ) | **qtuanph — positive** (2026-07-16) | Reopen/merge tip + hybrid help offered |
| 1b | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | [#26](https://github.com/qtuanph/chatbot-rag/pull/26) | OPEN | n/a (Recall@k) | — | Offline retrieval harness |
| 2 | [vietnam-labor-law-rag](https://github.com/ducdanh2304/vietnam-labor-law-rag) | [#1](https://github.com/ducdanh2304/vietnam-labor-law-rag/pull/1) | OPEN | FAIL Grok | none | Follow-up done |
| 3 | [Traffic-law-chatbot](https://github.com/tontide1/Traffic-law-chatbot) | [#9](https://github.com/tontide1/Traffic-law-chatbot/pull/9) | OPEN | FAIL Grok | none (Sourcery) | Follow-up done |
| 4 | [BIN9721/Chatbot](https://github.com/BIN9721/Chatbot) | [#1](https://github.com/BIN9721/Chatbot/pull/1) | OPEN | FAIL Grok | none | Follow-up done |
| 5 | [SimpleRAG](https://github.com/quyen244/SimpleRAG) | [#1](https://github.com/quyen244/SimpleRAG/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 6 | [rag-traffic-vn](https://github.com/congmnguyen/rag-traffic-vn) | [#1](https://github.com/congmnguyen/rag-traffic-vn/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 7 | [LexMind](https://github.com/hnamyud/LexMind) | [#2](https://github.com/hnamyud/LexMind/pull/2) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 8 | [TubeNote](https://github.com/buitrongtrinh/TubeNote) | [#1](https://github.com/buitrongtrinh/TubeNote/pull/1) | OPEN | FAIL Grok | none | Follow-up 2026-07-16 |
| 9 | [viparse](https://github.com/minhtridinh-kayden/viparse) | [#54](https://github.com/minhtridinh-kayden/viparse/pull/54) | OPEN | FAIL Grok | none | 2026-07-16 |
| 10 | [VietNam-CyberLaw-RAG-](https://github.com/QuangVu404/VietNam-CyberLaw-RAG-) | [#1](https://github.com/QuangVu404/VietNam-CyberLaw-RAG-/pull/1) | OPEN | FAIL Grok | none | 2026-07-16 |
| 11 | [Edu_Omni_MyMind](https://github.com/khang3004/Edu_Omni_MyMind) | [#2](https://github.com/khang3004/Edu_Omni_MyMind/pull/2) | OPEN | FAIL Grok | none | force-add `tests/` |
| 12 | [Chatbot_tuyen_sinh_FPTU_2026](https://github.com/HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026) | [#1](https://github.com/HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026/pull/1) | OPEN | FAIL Grok | none | MIT · VN |
| 13 | [local-rag-pdf-assistant](https://github.com/SagarCodes03/local-rag-pdf-assistant) | [#1](https://github.com/SagarCodes03/local-rag-pdf-assistant/pull/1) | OPEN | FAIL Grok | none | 2026-07-16 |
| 14 | [banhmi](https://github.com/dannyota/banhmi) | [#1](https://github.com/dannyota/banhmi/pull/1) | OPEN | FAIL Grok | none | base=`master` · VN banking |
| 15 | [RAG-Student-Chatbot](https://github.com/HiTrong/RAG-Student-Chatbot) | [#1](https://github.com/HiTrong/RAG-Student-Chatbot/pull/1) | OPEN | FAIL Grok | none | MIT · draft was ready |
| 16 | [hybrid-search-eval](https://github.com/kunal4040/hybrid-search-eval) | [#1](https://github.com/kunal4040/hybrid-search-eval/pull/1) | OPEN | FAIL Grok | none | eval-adjacent target |
| 17 | [Agentic-RAG-Anime-…](https://github.com/drae1712/Agentic-RAG-Anime-Recommender-System) | [#1](https://github.com/drae1712/Agentic-RAG-Anime-Recommender-System/pull/1) | OPEN | FAIL Grok | none | git-lfs; finished after LFS-off |

### KPI snapshot (2026-07-16)

| KPI | Current | Early target |
|-----|--------:|--------------|
| Quality-gate PRs opened | **16** (+#26 harness; +#25 closed) | ≥10 ✓ |
| Open quality-gate | **16** | — |
| Open related (#26) | **1** | — |
| Closed not merged | **1** (#25) | — |
| Merged | **0** | ≥1–3 |
| Human maintainer replies | **1** (qtuanph) | ≥3 |
| AuditAI stars | **0** | after merge/badge |
| Follow-ups (older set) | **8/8** | no same-day re-ping on 07-16 batch |

**Milestone:** portfolio ≥16 + first positive human reply.  
**Bottleneck:** conversion (merge), not volume.

---

## 3. GTM tooling

| Tool | Path |
|------|------|
| Scan | `scripts/gtm/scan_github.py` |
| Prep | `scripts/gtm/guerrilla_prep.py` |
| One-shot | `scripts/gtm/open_guerrilla_pr.py` |
| PR body | `scripts/gtm/fill_pr_body.py` |
| Playbook | [`GROWTH_HACK.md`](./GROWTH_HACK.md) · [`TARGETS.md`](./TARGETS.md) |

**Script harden**

| Fix | Why |
|-----|-----|
| `git add -f` | Repos that gitignore `tests/` |
| Auto default branch | `main` vs `master` (e.g. banhmi) |
| **LFS-off** (`GIT_LFS_SKIP_SMUDGE` + `filter.lfs.*=`) | Missing `git-lfs` binary (e.g. Anime) |
| No PAT in remotes | Secret hygiene |

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
| **P0** | Watch #25 reopen/merge + #26 review |
| **P0** | STATUS/log hygiene ✓ · LFS harden ✓ |
| **P0** | **PyPI:** packaging ready · need Trusted Publisher or `~/.config/pypi_token` → see [`docs/PYPI.md`](../PYPI.md) |
| Wait | No spam follow-up on 2026-07-16 batch |
| P1 | After PyPI live: verify `pip install auditai`; refresh open PR comments if useful |
| P1 | First merge → badge + case study |
| P1 | Selective follow-up on ≥5–7 day open PRs only |
| P2 | GTVT only if license clarified |
| P2 | About/topics on auditai |

---

## 6. Scorecard

| Layer | /10 | Note |
|-------|----:|------|
| Product build | 8 | v0.1.x shippable · tests green |
| GTM execution | 8 | 16 PRs + tooling harden |
| Outcomes | 3 | 0 merge / 0 stars / 1 human reply |

---

## 7. Changelog of this status file

| Date | Change |
|------|--------|
| 2026-07-12 | Initial export |
| 2026-07-16 | 8 PRs; #25 CLOSED + qtuanph reply |
| 2026-07-16 | +#9–14 viparse…banhmi |
| 2026-07-16 | **Full sync #1–17** + #26; LFS harden; anime logged |
| 2026-07-16 | PyPI prep: wheel smoke 0.1.1, `publish-pypi.yml`, `docs/PYPI.md`, install docs → `pip install auditai` |

*Refresh with `gh pr view` / search before major decisions.*
