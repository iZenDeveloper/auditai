# GTM target list — AuditAI

**Updated:** 2026-07-18  
**Cadence:** after first wins → **≤1–2 quality PRs/week** (not 2–3/day). Prefer harvest + depth over spray.  
**Install in PR bodies:** `pip install auditai-cli` (CLI/import still `auditai`).

Prioritize **open license**, **recent activity**, **HTTP chat/RAG API or clear adapter path**, **maintainer likely to accept small opt-in CI**.

---

## Fit filter (must pass before PR)

| # | Rule | Notes |
|---|------|--------|
| 1 | License MIT / Apache / BSD / MPL | Skip no-license |
| 2 | **Generation path** | Chat / RAG / agent answers — not pure ETL |
| 3 | Public docs enough for dataset | README / docs only |
| 4 | Push in last ~90 days preferred | Older only if strong fit + draft |
| 5 | Size: avoid monorepos ★500+ process-heavy | e.g. full LibreChat/Dify |
| 6 | Not already in portfolio | See `STATUS.md` / `out/pr_log.jsonl` |

### Prefer

- FastAPI / Flask / clear `POST /chat` JSON  
- Repo already mentions evals / quality / hallucination  
- Vietnamese legal / education RAG (proven path: chatbot-rag)  
- Draft already prepared under `drafts/`

### Avoid (learned in field)

| Pattern | Why | Example |
|---------|-----|---------|
| **Document loader / normalizer only** | Faithfulness/relevancy score **mock adapter**, not product; maintainer will (rightly) reject/revert | [viparse](https://github.com/minhtridinh-kayden/viparse) #54 → reverted #59 |
| Pure encoding / PDF / OCR tooling | Same — no Q&A surface | — |
| Third-party Action + secrets without opt-in workflow | Supply-chain pushback | viparse feedback |
| No license | Legal grey | GTVT-class repos |
| Notebook-only, no app entry | Hard to CI | — |
| Archived / dead | Low merge | — |

**Correct quality signal for loaders:** golden fixtures (input bytes → expected NFC/Markdown) — out of scope for AuditAI smoke; do not force-fit.

---

## Shortlist — next window (2026-07-18+)

Open **at most one** until TubeNote settles and badge wait on qtuanph ends.

| Rank | Repo | Why | Prep | When |
|:----:|------|-----|------|------|
| **1** | [towardsai/ai-tutor-app](https://github.com/towardsai/ai-tutor-app) | Agentic RAG + **`evals/`** + FastAPI; Apache-2.0; P0 original | [`drafts/01-towardsai-ai-tutor-app/`](./drafts/01-towardsai-ai-tutor-app/) | **Next single PR** |
| **2** | [chatvector-ai/chatvector-ai](https://github.com/chatvector-ai/chatvector-ai) | RAG engine, FastAPI `POST /chat`, MIT, active issues | Inspect API + secrets for CI | If #1 blocked / declined |
| **3** | [khanghoang123/vietnamese-legal-rag-portfolio](https://github.com/khanghoang123/vietnamese-legal-rag-portfolio) | VN labor-law RAG + eval notebooks; MIT; fresh | Light scout | Domain follow-on to wins |
| Hold | [kc-ml2/MARU-Lang](https://github.com/kc-ml2/MARU-Lang) | OSS RAG engine MIT | Deploy path | P1 later |
| Hold | [amscotti/local-LLM-with-RAG](https://github.com/amscotti/local-LLM-with-RAG) | ★ high, Streamlit/local | Adapter | Prestige, lower merge odds |
| Skip now | [schmitech/orbit](https://github.com/schmitech/orbit) | Large gateway | — | Process heavy |

### Not for new PR (already in portfolio)

HiTrong, FPTU, labor-law, traffic-law, LexMind, TubeNote, CyberLaw, Edu, banhmi, hybrid-search-eval, Anime, SimpleRAG, BIN9721, viparse (closed path), chatbot-rag (**done** — champion).

---

## Priority A — original list (refresh)

| # | Repo | Stars | Why | Fit notes | Priority |
|---|------|------:|----|-----------|----------|
| 1 | [towardsai/ai-tutor-app](https://github.com/towardsai/ai-tutor-app) | ~17 | `evals/` + agentic RAG + FastAPI | SSE may need thin JSON adapter | **Next** |
| 2 | [chatvector-ai/chatvector-ai](https://github.com/chatvector-ai/chatvector-ai) | ~22 | RAG engine, JSON chat API | API key / document_id in CI | Backup |
| 3 | [kc-ml2/MARU-Lang](https://github.com/kc-ml2/MARU-Lang) | ~27 | OSS RAG chatbot engine | Inspect deploy | Later |
| 4 | [amscotti/local-LLM-with-RAG](https://github.com/amscotti/local-LLM-with-RAG) | ~286 | Local RAG sandbox | Streamlit | Later |
| 5 | [schmitech/orbit](https://github.com/schmitech/orbit) | ~300+ | Gateway + RAG | Large — careful only | Later |

## Priority B — Việt Nam

| # | Repo | Status | Notes |
|---|------|--------|-------|
| — | [qtuanph/chatbot-rag](https://github.com/qtuanph/chatbot-rag) | **#25 + #26 MERGED** | Champion; badge ask posted; no new spam |
| — | [buitrongtrinh/TubeNote](https://github.com/buitrongtrinh/TubeNote) | OPEN · positive human | Wait review; no re-ping |
| — | FPTU / labor / traffic / LexMind / Edu / CyberLaw / banhmi / HiTrong | OPEN or followed | Soft FU on schedule only |
| New scout | [khanghoang123/vietnamese-legal-rag-portfolio](https://github.com/khanghoang123/vietnamese-legal-rag-portfolio) | Shortlist #3 | Hybrid + eval notebooks |
| Skip | Loader-class VN tools | — | viparse lesson |

## Avoid / later (summary)

| Pattern | Reason |
|---------|--------|
| LibreChat / Dify-scale | Process heavy |
| No license | Legal grey |
| Archived / push &gt;18 mo | Low merge |
| Pure notebooks | Hard CI |
| **Loaders / normalizers / pure encoding** | Metrics don't measure product (viparse) |
| Re-PR same repo after clear reject/revert | Reputation |

---

## Draft artifacts

| Target | Folder |
|--------|--------|
| towardsai/ai-tutor-app | [`drafts/01-towardsai-ai-tutor-app/`](./drafts/01-towardsai-ai-tutor-app/) |
| HiTrong (done PR) | [`drafts/02-hitrong-…`](./drafts/02-hitrong-rag-student-chatbot/) |
| qtuanph retrieval memo | [`drafts/03-…`](./drafts/03-qtuanph-chatbot-rag-retrieval-suggestions.md) |
| qtuanph thank-you + badge | [`drafts/04-…`](./drafts/04-qtuanph-thank-you-badge-ask.md) posted on #26 |

---

## Tracking (shortlist)

| # | Repo | PR | Status | Notes |
|---|------|-----|--------|-------|
| 1 | towardsai/ai-tutor-app | — | **draft ready · next** | Refresh dataset before open; `auditai-cli` in body |
| 2 | chatvector-ai/chatvector-ai | — | backup | API-first |
| 3 | khanghoang123/vietnamese-legal-rag-portfolio | — | scout | VN legal domain |
| — | qtuanph/chatbot-rag | #25 #26 | **MERGED ×2** | Champion |
| — | minhtridinh-kayden/viparse | #54 | merged then **revert #59** | Wrong fit documented |
| — | buitrongtrinh/TubeNote | #1 | OPEN · positive | Wait |

Full portfolio: [`STATUS.md`](./STATUS.md) · machine log: `out/pr_log.jsonl`.

---

## Before opening any new PR

1. Pass fit filter (especially **not a loader**).  
2. Cadence: no same-day spam; prefer after FU window on 16/07 batch (~21–23/07) or isolated single.  
3. PR body: honest FAIL under Grok if mock weak; `pip install auditai-cli`; link chatbot-rag #25/#26 as optional social proof.  
4. Workflow **example-only** / `workflow_dispatch` default (supply-chain lesson).  
5. Log in `pr_log.jsonl` + STATUS row.
