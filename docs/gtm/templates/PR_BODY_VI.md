## ci: thêm AuditAI — gate chống ảo giác (RAG)

Chào bạn, dự án RAG/chatbot của bạn rất thú vị!

Mình đã chạy thử **[AuditAI](https://github.com/iZenDeveloper/auditai)** (`pip install auditai-cli`) — CLI + GitHub Action mã nguồn mở — để đánh giá chống ảo giác (hallucination) và vài kiểm tra an toàn cơ bản.

### Kết quả baseline (máy local)

| Metric | Mean | Threshold | Pass |
|--------|------|-----------|------|
| Faithfulness | {{FAITHFULNESS}} | {{FAITHFULNESS_THR}} | {{FAITHFULNESS_PASS}} |
| Answer relevancy | {{RELEVANCY}} | {{RELEVANCY_THR}} | {{RELEVANCY_PASS}} |
| Prompt injection | {{INJECTION}} | {{INJECTION_THR}} | {{INJECTION_PASS}} |

- Tổng case: **{{TOTAL_CASES}}** · Target errors: **{{FAILED_CASES}}**  
- Exit reason: `{{EXIT_REASON}}` · judge calls: **{{JUDGE_CALLS}}**  
- {{JUDGE_USAGE_LINE}}  
- Chi tiết: file report trong PR (`tests/auditai/auditai-out/` hoặc artifact CI)

> Lưu ý: Đây là **kiểm thử kỹ thuật** với dataset lấy từ README/docs **public**, không phải đánh giá toàn bộ sản phẩm của bạn.

### PR này thêm gì?

- `tests/auditai/auditai.yml` — cấu hình gate  
- `tests/auditai/dataset.json` — ~{{TOTAL_CASES}} câu hỏi smoke  
- `.github/workflows/auditai.yml` — chạy AuditAI (mặc định có thể chỉ `workflow_dispatch` để tránh tốn API bất ngờ)  
- (nếu có) adapter HTTP nếu app chưa expose JSON API  

Từ nay mỗi lần bạn (hoặc CI) chạy workflow, pipeline sẽ tự test bảo vệ chất lượng trả lời.

### Cách chạy lại

```bash
pip install auditai-cli
# fallback: pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.1"
export OPENAI_API_KEY=...   # hoặc XAI_API_KEY + judge.provider=xai
# start app / adapter nếu cần
auditai run --config tests/auditai/auditai.yml
```

### Badge (tuỳ chọn — chỉ khi bạn muốn)

```markdown
[![Audited by AuditAI](https://img.shields.io/badge/🛡️_Audited_by-AuditAI-7c5cfc?style=flat-square)](https://github.com/iZenDeveloper/auditai)
```

Mình sẵn sàng chỉnh threshold, dataset, hoặc bỏ workflow nếu bạn chỉ muốn CLI local.

Cảm ơn bạn đã open-source! 🙏
