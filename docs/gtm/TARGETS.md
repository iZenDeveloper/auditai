# GTM target list — AuditAI v0.1 (2026-07-11)

Prioritize **open license**, **recent activity**, **reachable chat/API**, **maintainer likely to accept small CI PRs**.  
Do not spam. Max 2–3 PRs/day. Track outcomes in the table at the bottom.

## Priority A — ship first (good fit)

| # | Repo | Stars | Why | Fit notes | Priority |
|---|------|------:|----|-----------|----------|
| 1 | [towardsai/ai-tutor-app](https://github.com/towardsai/ai-tutor-app) | ~15 | Agentic RAG tutor, **already has `evals/`**, FastAPI `POST /api/chat` | SSE stream — need thin JSON adapter for AuditAI | **P0 first draft** |
| 2 | [chatvector-ai/chatvector-ai](https://github.com/chatvector-ai/chatvector-ai) | ~22 | RAG **engine**, FastAPI `POST /chat` JSON, CONTRIBUTING, CI | Needs API key + document_id secrets in CI | P0 |
| 3 | [kc-ml2/MARU-Lang](https://github.com/kc-ml2/MARU-Lang) | ~27 | OSS RAG chatbot engine, MIT, open issues | Inspect deploy path before PR | P1 |
| 4 | [amscotti/local-LLM-with-RAG](https://github.com/amscotti/local-LLM-with-RAG) | ~286 | Active local RAG + LangChain, MIT | Streamlit UI — may need small adapter | P1 |
| 5 | [schmitech/orbit](https://github.com/schmitech/orbit) | ~298 | OpenAI-compatible gateway + RAG, **ai-safety** topic | Larger project; careful, high quality only | P1 |

## Priority B — Việt Nam (community / portfolio)

| # | Repo | Stars | Why | Fit notes | Priority |
|---|------|------:|----|-----------|----------|
| 6 | [HiTrong/RAG-Student-Chatbot](https://github.com/HiTrong/RAG-Student-Chatbot) | ~2 | Chatbot SV VN, RAG vs hallucination **đã nêu trong README** | **Full draft ready** | P0 VN |
| 7 | [HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026](https://github.com/HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026) | ~1 | RAG tuyển sinh FPT, MIT, data public | CLI app — add FastAPI thin wrap for CI | P0 VN |
| 8 | [ngothanhnam0910/Vietnamese-Law-Question-Answering-system](https://github.com/ngothanhnam0910/Vietnamese-Law-Question-Answering-system) | ~56 | Q&A pháp lý VN | License unclear; check before PR | P1 VN |
| 9 | [Trinhvhao/TalentBridge](https://github.com/Trinhvhao/TalentBridge) | ~12 | LangChain + FastAPI, SV VN | Job matching > pure RAG chat; still LLM quality gate | P2 |
| 10 | [hoangtung386/Medical-RAG-System](https://github.com/hoangtung386/Medical-RAG-System) | ~1 | Medical RAG EN↔VI | Small / offline; friendly PR | P2 VN |

## Avoid / later

| Repo | Reason |
|------|--------|
| LibreChat / Dify-scale monorepos | Too large; process heavy |
| Repos without license | Legal grey area for patches |
| Archived / no push >18 months | Low merge chance |
| Pure notebooks with no app entry | Hard to CI |

## Draft artifacts

| Target | Folder |
|--------|--------|
| #1 towardsai/ai-tutor-app | [`drafts/01-towardsai-ai-tutor-app/`](./drafts/01-towardsai-ai-tutor-app/) |

## Tracking

| # | Repo | PR URL | Status | Notes |
|---|------|--------|--------|-------|
| 1 | towardsai/ai-tutor-app | | draft ready | |
| 2 | chatvector-ai/chatvector-ai | | | |
| 3 | HiTrong/RAG-Student-Chatbot | | **full draft** | [drafts/02-…](./drafts/02-hitrong-rag-student-chatbot/) mock smoke PASS |
| 4 | HoangLeminh17/Chatbot_tuyen_sinh_FPTU_2026 | | | |
| 5–10 | … | | | |
