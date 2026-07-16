# Gợi ý retrieval / hybrid accuracy — qtuanph/chatbot-rag

**To:** @qtuanph · PR [#25](https://github.com/qtuanph/chatbot-rag/pull/25)  
**From:** iZenDeveloper / AuditAI  
**Date:** 2026-07-16  
**Scope:** Góp ý kỹ thuật dựa trên README + `docs/2.2_WORKFLOWS_CHAT.md` + `retrieval/pipeline.py` + config retrieval.  
**Không phải code review toàn repo.**

---

## 1. Những gì pipeline đã làm rất tốt

Stack hiện tại đã là production-grade cho multi-tenant ERP RAG:

| Thành phần | Nhận xét |
|------------|----------|
| Hybrid Qdrant + BM25 sparse | Đúng hướng cho thuật ngữ ERP / numbered sections |
| Section route + RecursiveRetriever + AutoMerging | Structure-aware — mạnh hơn “flat chunk RAG” |
| Latest-user-query retrieval | Tránh history làm loãng RAG expansion (hợp lý) |
| Adaptive rerank skip | Tiết kiệm latency/cost khi top-1 dominate |
| Section hydration từ Postgres | Context dài hơn sentence-window hit |
| Semantic cache (tenant-isolated) | Tốt cho FAQ lặp |
| Faithfulness / “chưa đủ căn cứ” rule | Đúng mindset anti-hallucination |
| Feedback API (`/v1/chat/feedback`) | Nền tảng gold set / online learning |

Phần dưới là **cách đo và tinh chỉnh** để hybrid + rerank “ăn” hơn, không phải rewrite kiến trúc.

---

## 2. Ưu tiên đo trước khi tune (2–3 ngày)

### 2.1 Golden set theo tenant / domain ERP

Tạo ~50–100 case **có ground truth section/article** (không chỉ free-text answer):

```json
{
  "id": "wh-receipt-01",
  "question": "How do I create a warehouse receipt?",
  "expected_section_codes": ["3.2.1", "3.2"],
  "expected_doc_ids": ["..."],
  "must_cite": true,
  "difficulty": "easy|medium|hard",
  "language": "en|vi"
}
```

**Metrics retrieval (trước LLM):**

| Metric | Ý nghĩa |
|--------|---------|
| **Recall@k** (section_id / section_code) | Context đúng có vào top-k candidate trước/sau rerank? |
| **MRR** | Rank của section đúng |
| **nDCG@k** | Nếu multi-relevant sections |
| **Citation precision** (post-LLM) | Answer có trỏ đúng section đã retrieve? |

**Ablations (bật/tắt 1 factor mỗi lần):**

1. hybrid ON vs dense-only  
2. rerank ON vs OFF vs skip-policy hiện tại  
3. section route priority ON vs OFF  
4. AutoMerging ON vs OFF  
5. section hydration ON vs OFF  

Ghi **latency p50/p95 + cost reranker** cùng bảng accuracy → trade-off rõ.

### 2.2 Dùng feedback đã có

`POST /v1/chat/feedback` + citations là gold thô:

- `thumbs_down` + citations → hard negatives / near-miss ranking  
- `thumbs_up` + query → hard positives cho semantic cache threshold  
- Log `rerank_skipped` reason (đã có trong code) → xem skip có đang “cướp” case khó không  

---

## 3. Hybrid retrieval — tinh chỉnh thực dụng

### 3.1 Tách score dense vs sparse khi debug

Hybrid fusion đôi khi che “BM25 thắng / dense thắng”. Khi eval:

- Log top-k **dense-only**, **sparse-only**, **hybrid** cho cùng query  
- Đặc biệt query **mã section** (`3.2.1`) vs **mô tả nghiệp vụ** (“tạo phiếu nhập kho”)  

Kỳ vọng:

| Query type | Ưu tiên |
|------------|---------|
| Section code / ERP SKU / form ID | Sparse / exact metadata filter |
| Ngôn ngữ tự nhiên VN/EN | Dense + rerank |
| Hỗn hợp | Hybrid, nhưng **boost metadata** `section_code` nếu regex match |

Code đã có `SECTION_CODE_QUERY_RE` — có thể harden: nếu match code → **bắt buộc** section route + filter `section_code` (không chỉ prioritize).

### 3.2 Hybrid top_k vs rerank top_k

Config hiện tại (gần đúng):

- `retrieval_hybrid_top_k` / `chunk_top_k` ≈ 20  
- `retrieval_rerank_top_k` ≈ 10  

Gợi ý experiment:

| Setting | Candidate | Rerank out | Khi nào |
|---------|-----------|------------|---------|
| A (baseline) | 20 | 10 | default |
| B | 40 | 10 | recall thấp, latency OK |
| C | 20 | 5 | context window chật / noise |
| D | 30 | 8 | balance |

**Rule:** nếu Recall@20 (pre-rerank) thấp → tăng candidate **trước** khi đổ lỗi reranker.

### 3.3 Sparse model & ERP tokenizer

BM25 (`Qdrant/bm25`) mặc định có thể kém với:

- mã không khoảng trắng (`WH-RCP-001`)  
- tiếng Việt không dấu vs có dấu  
- thuật ngữ mixed EN/VN  

Gợi ý:

- Chuẩn hóa query: giữ ERP tokens (đã có hướng normalize) + **variant có/không dấu** (dual query) nếu corpus lẫn  
- Index metadata fields: `section_code`, `heading`, `breadcrumb_text` với **keyword filter** song song vector  
- Cân nhắc sparse custom / text preprocessing cho product codes  

---

## 4. Adaptive rerank skip — đừng skip “âm thầm”

Logic skip (dominance ratio, short query, single result) rất hợp cost control.

**Rủi ro:** query ngắn nhưng **mơ hồ** (“xóa phiếu?”) → top-1 dense nhầm module → skip rerank → hallucination guard phải gánh.

Gợi ý:

1. **Metric dashboard:** % skip by reason × thumbs_down rate  
2. **Never-skip list:** query chứa verb rủi ro (`xóa`, `hủy`, `approve`, `post`, `void`) hoặc multi-intent  
3. Nới `retrieval_rerank_skip_dominance_ratio` (vd 1.35 → 1.5) nếu down-votes tập trung ở skip=true  
4. Khi skip: vẫn gắn debug `rerank_skipped=true` vào response metadata (nếu chưa expose) để eval offline  

---

## 5. Section route + AutoMerging

### 5.1 Section route

`_should_prioritize_section_route` (short query / numbered) là tốt.

Bổ sung:

- Query có **heading-like** quotes hoặc UI label (“nút Lưu & Đăng”) → ưu tiên section + breadcrumb match  
- Sau section hit: luôn expand children chunks (Recursive) — giữ invariant hiện tại  

### 5.2 AutoMerging threshold

`retrieval_auto_merge_ratio_threshold` (default 0.5):

- Quá thấp → merge sớm, context loãng  
- Quá cao → mất parent section, LLM chỉ thấy mảnh  

Eval: measure **citation section-level** vs **chunk-level** khi bật/tắt merge.

### 5.3 Hydration

Hydrate full section từ Postgres cho top nodes — mạnh cho faithfulness.

Rủi ro: top wrong section → hydrate “đúng section sai” → LLM tự tin sai.

Mitigation: hydration chỉ khi score ≥ τ **hoặc** sau rerank; log `hydrated_section_ids` trong audit trail.

---

## 6. Semantic cache

`retrieval_semantic_cache_threshold` (distance-like 0.08) nhạy cảm:

- Threshold lỏng → trả FAQ cũ sai tenant context (dù tag tenant)  
- Threshold chặt → cache miss liên tục  

Gợi ý:

- Cache key = tenant + **normalized query** + optional `document_scope`  
- Invalidate cache theo `document_id` khi re-ingest  
- Không cache khi `thinking_mode` / tool-ish queries  
- Track hit-rate × thumbs_down  

---

## 7. Generation-side (ảnh hưởng “cảm nhận accuracy”)

Retrieval tốt vẫn fail UX nếu prompt lỏng:

1. **Force cite:** yêu cầu model trích `section_code` / heading có trong context; cấm bước không có trong context (đã có safety rule — enforce trong system prompt + post-check).  
2. **Abstain threshold:** nếu max retrieval score < τ hoặc rerank scores phẳng → template “chưa đủ căn cứ / hỏi lại module”.  
3. **Latest-query only** là đúng default; cân nhắc **optional** rewrite nhẹ (không full multi-query) cho coreference: “còn bước nào nữa?” → cần previous user intent. Có thể giới hạn 1 rewrite LLM chỉ khi query < N chars và không có section code.  

---

## 8. Kết nối AuditAI (optional, low friction)

Khi API local/staging chạy:

```bash
export AUDITAI_TARGET_URL="https://api.qtuanph.dev/v1/chat/completions"  # hoặc local
# map OpenAI-compatible body nếu cần thin adapter
export XAI_API_KEY=...   # or OPENAI_API_KEY
# judge.provider: xai|openai trong tests/auditai/auditai.yml
auditai run --config tests/auditai/auditai.yml
```

Đề xuất dataset thật (không mock):

| Slice | Mục đích |
|-------|----------|
| Happy path ERP | Faithfulness cao kỳ vọng |
| Near-miss sections | Hybrid / rerank stress |
| Out-of-scope | Abstain + injection |
| Section-code lookup | Sparse / route stress |
| Ambiguous short VN | Rerank-skip policy stress |

Có thể thêm job `workflow_dispatch` so sánh **2 config retrieval** (A/B) export cùng format report.

---

## 9. Lộ trình gợi ý (không bắt buộc)

| Tuần | Việc | Output |
|------|------|--------|
| 1 | Golden set 50–100 + Recall@k / MRR harness | Bảng baseline hybrid/rerank |
| 1–2 | Ablation 5 switches | Config “recommended defaults” |
| 2 | Rerank-skip × feedback analysis | Policy never-skip / ratio |
| 3 | Dual-query VN diacritics + code boost | Lift trên ERP IDs |
| 3+ | AuditAI on staging against golden set | CI gate optional |

---

## 10. Offer

Mình có thể hỗ trợ theo hướng OSS:

1. **PR nhỏ:** script eval Recall@k trên export retrieval debug (offline, không đụng hot path).  
2. **PR nhỏ:** dataset AuditAI 20–40 case từ docs public ERP (nếu share được sample docs).  
3. **Design note:** A/B matrix config cho hybrid top_k / rerank skip.  

Không block merge #25 — đây là hướng optimize **sau** scaffold quality gate.

---

*Draft for posting as PR comment (short) + keep full memo in AuditAI repo.*
