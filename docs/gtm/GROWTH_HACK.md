# Chiến lược Growth Hack qua Pull Request

Cách tìm **1,000 user đầu tiên** không tốn quảng cáo — đúng playbook PRD v2.0.

| Bước | Việc | Tool trong repo |
|------|------|-----------------|
| 1 | Quét OSS GitHub | `scripts/gtm/scan_github.py` |
| 2 | Audit du kích (clone + dataset + run) | `scripts/gtm/guerrilla_prep.py` + `auditai run` |
| 3 | PR hữu ích | `templates/PR_BODY_VI.md` + workflow scaffold |
| 4 | Viral loop (badge) | `templates/README_BADGE.md` |

**Nguyên tắc sống còn**

1. Chỉ **public** repo.  
2. Dataset chỉ từ **README/docs public**.  
3. **2–3 PR chất lượng/ngày**, không spam.  
4. Badge chỉ khi maintainer **opt-in** (sau merge hoặc họ yêu cầu).  
5. Tone: peer kỹ thuật, số liệu thật — không “repo bạn dở”.

---

## Bước 1 — Quét hệ sinh thái Open-Source

```bash
cd /path/to/auditai
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"  # hoặc editable

# Optional: GITHUB_TOKEN=ghp_... để tránh rate limit
export GITHUB_TOKEN=...   # recommended

python scripts/gtm/scan_github.py \
  --keywords langchain,rag,chatbot,vietnam,vietnamese,zalo,zalo-bot \
  --min-stars 1 \
  --max-stars 500 \
  --out docs/gtm/out/scan_results.jsonl
```

Script:

- Gọi GitHub Search API với từng keyword / combo VN.  
- Lọc: không archived, có description, ưu tiên Python/TS, ưu tiên signal VN.  
- Ghi JSONL + bảng tóm tắt ra stdout.  
- Cập nhật gợi ý vào `docs/gtm/TARGETS.md` (thủ công hoặc `--print-markdown`).

---

## Bước 2 — Audit “du kích”

Với mỗi repo shortlist:

```bash
python scripts/gtm/guerrilla_prep.py \
  --repo HiTrong/RAG-Student-Chatbot \
  --workdir /tmp/auditai-guerrilla \
  --questions 20

cd /tmp/auditai-guerrilla/HiTrong_RAG-Student-Chatbot

# 1) Điền/sửa tests/auditai/dataset.json (script đã seed từ README)
# 2) Cấu hình target HTTP hoặc mock adapter
# 3) Chạy audit
export OPENAI_API_KEY=sk-...   # hoặc judge.provider=mock trong yml
auditai run --config tests/auditai/auditai.yml

# 4) (optional) PDF
pip install "auditai[pdf] @ git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
auditai report --pdf \
  --from tests/auditai/auditai-out/auditai-report.json \
  --out tests/auditai/auditai-out/compliance.pdf \
  --project-name HiTrong/RAG-Student-Chatbot
```

`guerrilla_prep.py` sẽ:

1. `git clone --depth 1` public repo.  
2. Đọc **README + docs/**/*.md**, trích đoạn prose/table (lọc badge/noise).  
3. Sinh `dataset.json` từ docs thật (mặc định **0 TODO**; `--pad-todos` nếu cần legacy).  
4. Nhiều câu hỏi / chunk (templates EN/VI) + 2 probe injection.  
5. Sinh `auditai.yml` + workflow example + **mock adapter yếu** (một SEED — không greenwash).  
6. In checklist; expect **FAIL** với LLM judge + mock target.

**Quan trọng:** Điểm Faithfulness trong PR **phải lấy từ report thật** sau `auditai run`, không bịa số. Mock “thông minh” để điểm xanh = greenwash — **không làm**.

---

## Bước 3 — Mở Pull Request “Hữu ích”

PR **có value**:

- `tests/auditai/auditai.yml`  
- `tests/auditai/dataset.json` (đã review)  
- `.github/workflows/auditai.yml` (nên `workflow_dispatch` trước)  
- Adapter nếu app không có HTTP JSON  
- (Tuỳ chọn) đính report markdown / PDF

Template tiếng Việt: [`templates/PR_BODY_VI.md`](./templates/PR_BODY_VI.md)

Điền số liệu từ report:

```bash
python scripts/gtm/fill_pr_body.py \
  --report tests/auditai/auditai-out/auditai-report.json \
  --template docs/gtm/templates/PR_BODY_VI.md \
  --out /tmp/pr_body.md
```

Mở PR (sau khi fork + push branch):

```bash
# trên máy đã gh auth
gh pr create --title "ci: add AuditAI RAG quality gate (optional)" --body-file /tmp/pr_body.md
```

### One-shot (khuyến nghị)

```bash
export GITHUB_TOKEN="$(tr -d ' \n' < ~/.config/github_token)"
# optional real judge:
# export XAI_API_KEY=...

# dry-run: prep + audit + pr_body (không push)
./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge mock --dry-run

# full: fork + push + gh pr create + log docs/gtm/out/pr_log.jsonl
./scripts/gtm/run_growth_hack.sh --open-pr owner/name --judge xai --model grok-4.3 --yes

# hoặc gọi Python trực tiếp
python scripts/gtm/open_guerrilla_pr.py --repo owner/name --judge openai --yes
```

Flags hữu ích: `--skip-prep`, `--skip-audit`, `--workflow-example-only` / `--no-workflow-example-only`, `--branch`, `--title`.

---

## Bước 4 — Viral loop (badge)

**Chỉ sau khi maintainer đồng ý** (merge + họ muốn, hoặc comment “cho badge nhé”).

Thêm vào README của **họ**:

```markdown
[![Audited by AuditAI](https://img.shields.io/badge/🛡️_Audited_by-AuditAI-7c5cfc?style=flat-square)](https://github.com/iZenDeveloper/auditai)
```

Chi tiết: [`templates/README_BADGE.md`](./templates/README_BADGE.md)

Loop:

```text
Merge PR → CI chạy / badge trên README
  → dev khác click badge → AuditAI repo
  → cài CLI / add Action → organic users
```

---

## Nhịp độ đề xuất (2 tuần)

| Ngày | Việc |
|------|------|
| 1 | `scan_github.py` → shortlist 20 |
| 2–3 | Guerrilla 5 repo (dataset + run) |
| 4–14 | 2 PR/ngày chất lượng (không 5 spam) |
| Cuối tuần | Review merge rate, chỉnh template |

Success: ≥10 PR mở, ≥3 phản hồi tích cực, ≥1 star/issue từ người lạ.

---

## Đạo đức / pháp lý

- Không scrape private data, không dox.  
- Không claim “chứng nhận Luật AI” trên PR — chỉ technical audit.  
- Không force-push / không bot mass-PR.  
- Tôn trọng `CONTRIBUTING` và code of conduct của họ.
