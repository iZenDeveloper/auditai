## Gợi ý tích hợp AuditAI — gate chống ảo giác cho chatbot SV

Chào bạn,

Mình thấy README đã phân tích rất rõ hạn chế của LLMChain (hallucination / triple-H) và cách RAG + rule trong prompt giúp cải thiện.  

[AuditAI](https://github.com/iZenDeveloper/auditai) là CLI/GitHub Action mã nguồn mở để **tự động đo Faithfulness / Relevancy / Prompt injection** mỗi lần push (BYOK OpenAI cho LLM-as-judge).

### Mình muốn góp

- Dataset smoke (~6–10 câu) dựa trên **nội dung public trong README** (ví dụ đoạn TMA)
- `auditai.yml` mẫu
- (Tuỳ chọn) adapter HTTP mỏng nếu app đang là Streamlit-only
- Workflow `workflow_dispatch` (không ép tốn API trên mọi PR)

### Lợi ích

- Mỗi lần sửa prompt/RAG có **cờ đỏ CI** khi faithfulness tụt
- Phù hợp với narrative README về “generate wrong text”

Bạn có ổn nếu mình mở PR nhỏ theo hướng docs + config trước không?  
Cảm ơn project — rất hữu ích cho sinh viên VN 🇻🇳
