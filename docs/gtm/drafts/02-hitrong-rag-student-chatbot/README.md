# Draft PR đầy đủ — HiTrong/RAG-Student-Chatbot (#6 VN)

## Upstream

- https://github.com/HiTrong/RAG-Student-Chatbot  
- MIT · Streamlit + LangChain + FAISS + Vinallama GGUF (CTransformers)  
- README đã nêu rõ vấn đề **hallucination** của LLMChain và lợi ích RAG  

## Chiến lược đóng góp (an toàn, hữu ích)

| Thành phần | Mục đích |
|------------|----------|
| Dataset TMA | Câu hỏi dựa trên đoạn **public** trong README (không scrape private data) |
| `auditai.yml` | Cấu hình gate Faithfulness / Relevancy / Prompt injection |
| HTTP adapter | Streamlit không có API → bọc `llm_chain` thành JSON cho AuditAI |
| Seed context | File text TMA để index / mock retrieval |
| Workflow | `workflow_dispatch` only — **không** bắt GPU/GGUF trên mọi PR |

### Hai mode của adapter

| Mode | Env | Khi nào dùng |
|------|-----|----------------|
| `mock` | `AUDITAI_ADAPTER_MODE=mock` (default) | Smoke AuditAI **không** cần GGUF/GPU; trả lời bám context TMA |
| `live` | `AUDITAI_ADAPTER_MODE=live` | Máy dev đã có model + FAISS; gọi `llm_chain.load_rag_chain` |

CI GitHub free runner **không** realistic cho Vinallama 7B GGUF → workflow chỉ document + mock smoke optional.

## Map file → vị trí trên upstream fork

```text
# copy vào root repo HiTrong (hoặc giữ dưới tests/auditai/)
tests/auditai/auditai.yml          ← auditai.yml
tests/auditai/dataset.json         ← dataset.json
tests/auditai/seed_tma_context.txt ← seed_tma_context.txt
scripts/auditai_http_adapter.py    ← auditai_http_adapter.py
.github/workflows/auditai.yml      ← workflow-auditai.yml (optional)
```

## Chạy local (mock — 2 phút)

```bash
# trong fork HiTrong, sau khi copy files
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
pip install httpx  # adapter mock only needs stdlib+httpx if you extend later; mock uses stdlib only

# terminal 1
python scripts/auditai_http_adapter.py
# → http://127.0.0.1:18080/chat

# terminal 2
export OPENAI_API_KEY=sk-...   # judge; hoặc sửa auditai.yml judge.provider=mock
auditai run --config tests/auditai/auditai.yml
```

## Chạy live (cần GGUF + embedding như README)

```bash
export AUDITAI_ADAPTER_MODE=live
# model path theo model_config.yml; bật RAG DB trước
python scripts/auditai_http_adapter.py
auditai run --config tests/auditai/auditai.yml
```

## Checklist trước khi mở PR

- [ ] Tone thân thiện SV VN (dùng `PR_BODY.md`)
- [ ] Không commit model GGUF / `.env`
- [ ] Dataset chỉ dùng text public từ README
- [ ] Workflow không auto-run tốn GPU
- [ ] Test mock path ít nhất 1 lần

## Status

- [x] Full draft files
- [ ] Open PR upstream
