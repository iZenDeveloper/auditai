## Thêm AuditAI — tự kiểm tra hallucination / faithfulness cho chatbot SV

Chào @HiTrong (và mọi người maintain project) 👋

Mình đọc README và thấy phần so sánh **LLMChain vs RAG** rất hay — đặc biệt ví dụ thông tin đúng về **TMA** và việc model dễ “bịa” khi không có ngữ cảnh.  

Mình muốn góp một lớp **kiểm thử tự động** để mỗi lần sửa prompt / RAG có thể đo nhanh:

| Metric | Ý nghĩa (gọn) |
|--------|----------------|
| **Faithfulness** | Câu trả lời có bám context không (chống ảo giác) |
| **Answer relevancy** | Có đúng trọng tâm câu hỏi không |
| **Prompt injection** | Có bị thao túng lộ prompt không |

Tool: **[AuditAI](https://github.com/iZenDeveloper/auditai)** (MIT, CLI + GitHub Action, BYOK).

---

### PR này thêm gì?

```text
tests/auditai/
  auditai.yml              # cấu hình gate
  dataset.json             # câu hỏi về đoạn TMA (public trong README)
  seed_tma_context.txt     # ngữ cảnh TMA (copy từ README)
scripts/
  auditai_http_adapter.py  # bọc Streamlit → HTTP JSON cho AuditAI
.github/workflows/
  auditai.yml              # optional, chỉ workflow_dispatch + mock (không cần GPU)
```

**Adapter có 2 mode:**

1. **`mock` (mặc định)** — không cần file GGUF / CUDA; trả lời bám context TMA để **smoke wiring CI** và demo faithfulness (gồm câu bẫy “Đà Nẵng + 50.000 NV”).
2. **`live`** — gọi `llm_chain.load_rag_chain` như app Streamlit (khi máy đã setup model theo README).

GitHub Actions free **không** chạy Vinallama 7B thực tế → workflow chỉ chạy **mock smoke**, không tốn GPU, không bắt `OPENAI_API_KEY` (judge mock).

---

### Cách chạy local

```bash
# Terminal 1 — adapter mock
python scripts/auditai_http_adapter.py
# → http://127.0.0.1:18080/chat

# Terminal 2
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
# auditai.yml đang judge.provider=mock (free)
auditai run --config tests/auditai/auditai.yml
```

Live (máy có model):

```bash
export AUDITAI_ADAPTER_MODE=live
python scripts/auditai_http_adapter.py
# có thể đổi judge.provider=openai + OPENAI_API_KEY để chấm thật
auditai run --config tests/auditai/auditai.yml
```

---

### Dataset

Các câu hỏi bám đoạn TMA **đã public trong README** (năm 1997, >3000 kỹ sư, văn phòng HCM/Bình Định + 6 nước, top CNTT/Fintech/AI-IoT, khách 30 quốc gia) + 2 câu prompt-injection + 1 câu bẫy hallucination.

---

### Mong muốn từ maintainer

1. Merge được không, hay chỉ giữ docs/local script?
2. Workflow mock có OK không (mặc định off mọi PR, chỉ bấm tay)?

Mình sẵn sàng chỉnh path/threshold/prompt. Cảm ơn project — rất phù hợp sinh viên Việt Nam 🇻🇳

— góp ý từ [AuditAI](https://github.com/iZenDeveloper/auditai)
