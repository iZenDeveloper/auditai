#!/usr/bin/env python3
"""
HTTP adapter for HiTrong/RAG-Student-Chatbot + AuditAI.

Upstream app is Streamlit-only (application.py). AuditAI needs JSON over HTTP.

Modes
-----
mock (default)
  No GGUF / no FAISS. Answers are grounded in seed_tma_context.txt (README public
  excerpt) so you can wire AuditAI without downloading Vinallama.

live
  Calls llm_chain.load_rag_chain / load_normal_chain like the Streamlit app.
  Requires model file + configs from upstream README.

Usage
-----
  # mock
  python scripts/auditai_http_adapter.py

  # live (from repo root, with model installed)
  AUDITAI_ADAPTER_MODE=live python scripts/auditai_http_adapter.py

  # then
  auditai run --config tests/auditai/auditai.yml
"""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = int(os.environ.get("AUDITAI_ADAPTER_PORT", "18080"))
MODE = os.environ.get("AUDITAI_ADAPTER_MODE", "mock").strip().lower()

# Resolve seed file relative to this script or CWD
_SCRIPT_DIR = Path(__file__).resolve().parent
_SEED_CANDIDATES = [
    _SCRIPT_DIR / "seed_tma_context.txt",
    Path("tests/auditai/seed_tma_context.txt"),
    Path("seed_tma_context.txt"),
]


def _load_seed() -> str:
    for p in _SEED_CANDIDATES:
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            # drop comment lines
            lines = [
                ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")
            ]
            return "\n".join(lines).strip()
    return (
        "Được thành lập năm 1997, TMA là công ty phần mềm hàng đầu Việt Nam "
        "với hơn 3,000 kỹ sư."
    )


SEED = _load_seed()

# --- mock helpers (keyword → grounded reply) ---------------------------------

_FACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"thành lập|thanh lap|năm nào|nam nao|founded", re.I),
        "Theo ngữ cảnh, TMA được thành lập năm 1997.",
    ),
    (
        re.compile(r"kỹ sư|ky su|nhân viên|nhan vien|engineer", re.I),
        "Theo ngữ cảnh, TMA có hơn 3,000 kỹ sư.",
    ),
    (
        re.compile(r"văn phòng|van phong|TP\.?HCM|Bình Định|Binh Dinh|nước ngoài|nuoc ngoai", re.I),
        "Theo ngữ cảnh, TMA có 6 văn phòng tại TP.HCM, Công viên Sáng tạo TMA tại Bình Định, "
        "và 6 văn phòng nước ngoài (Canada, Mỹ, Đức, Úc, Nhật Bản và Singapore).",
    ),
    (
        re.compile(r"quốc gia|quoc gia|khách hàng|khach hang|30", re.I),
        "Theo ngữ cảnh, khách hàng của TMA là các tập đoàn lớn đến từ 30 quốc gia trên thế giới.",
    ),
    (
        re.compile(r"top|vinh danh|CNTT|Fintech|AI|IoT|xuất khẩu|xuat khau", re.I),
        "Theo ngữ cảnh, TMA được bình chọn trong top doanh nghiệp CNTT Việt Nam, top 10 xuất khẩu "
        "phần mềm, Top 10 Fintech, Top 10 AI – IoT.",
    ),
]


def _is_injection(q: str) -> bool:
    low = q.lower()
    needles = [
        "ignore all previous",
        "system prompt",
        "api key",
        "bỏ qua mọi",
        "bo qua moi",
        "tiết lộ",
        "tiet lo",
        "developer mode",
        "disable safety",
    ]
    return any(n in low for n in needles)


def _is_hallucination_trap(q: str) -> bool:
    low = q.lower()
    return ("đà nẵng" in low or "da nang" in low) and (
        "50.000" in q or "50000" in q or "50,000" in q or "nhân viên" in low or "nhan vien" in low
    )


def mock_answer(question: str) -> tuple[str, list[str]]:
    contexts = [SEED]
    if _is_injection(question):
        return (
            "Mình không thể bỏ qua quy tắc an toàn, tiết lộ system prompt hay mật khẩu. "
            "Bạn hãy hỏi nội dung học tập hoặc thông tin có trong cơ sở dữ liệu.",
            contexts,
        )
    if _is_hallucination_trap(question):
        return (
            "Trong cơ sở dữ liệu/ngữ cảnh hiện có không thấy thông tin TMA trụ sở Đà Nẵng "
            "hay 50.000 nhân viên. Theo ngữ cảnh: thành lập 1997, hơn 3.000 kỹ sư, "
            "văn phòng tại TP.HCM và Bình Định (cùng văn phòng nước ngoài).",
            contexts,
        )
    for pat, ans in _FACT_PATTERNS:
        if pat.search(question):
            return ans, contexts
    # fallback: refuse if not about TMA keywords
    if re.search(r"TMA|công ty|cong ty|phần mềm|phan mem", question, re.I):
        return (
            "Mình chỉ trả lời dựa trên ngữ cảnh có sẵn về TMA. "
            f"Ngữ cảnh: {SEED[:280]}…",
            contexts,
        )
    return (
        "Trong cơ sở dữ liệu của mình không có thông tin phù hợp với câu hỏi này. "
        "Bạn hãy tìm kiếm thêm hoặc cung cấp tài liệu liên quan.",
        contexts,
    )


# --- live path ---------------------------------------------------------------

_live_chain = None
_live_memory = None


class _EmptyMemory:
    """Minimal stand-in for Streamlit chat memory used by llm_chain."""

    def load_memory_variables(self, _inputs=None):
        return {"history": ""}


def live_answer(question: str) -> tuple[str, list[str]]:
    global _live_chain, _live_memory
    if _live_chain is None:
        import llm_chain  # type: ignore  # upstream package root

        use_rag = os.environ.get("AUDITAI_USE_RAG", "1") != "0"
        k = int(os.environ.get("AUDITAI_RAG_K", "3"))
        _live_chain = llm_chain.load_rag_chain(k) if use_rag else llm_chain.load_normal_chain()
        _live_memory = _EmptyMemory()

    raw = _live_chain.run(question, _live_memory)
    # pipeline may return str or message-like
    if isinstance(raw, str):
        answer = raw
    elif hasattr(raw, "content"):
        answer = str(raw.content)
    else:
        answer = str(raw)
    # Live path may not expose retrieved chunks easily; return seed as optional hint only if empty
    return answer.strip(), [SEED] if SEED else []


def answer(question: str) -> tuple[str, list[str]]:
    if MODE == "live":
        return live_answer(question)
    return mock_answer(question)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quieter
        pass

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") in ("", "/health"):
            body = json.dumps({"ok": True, "mode": MODE, "port": PORT}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/chat":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self.send_error(400, "invalid json")
            return

        question = str(body.get("question") or body.get("human_input") or body.get("query") or "")
        try:
            ans, ctx = answer(question)
            payload = {"answer": ans, "contexts": ctx, "mode": MODE}
            status = 200
        except Exception as e:  # noqa: BLE001
            payload = {"answer": "", "contexts": [], "error": str(e), "mode": MODE}
            status = 500

        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    print(f"AuditAI HTTP adapter mode={MODE} on http://127.0.0.1:{PORT}/chat")
    if MODE == "mock":
        print(f"  seed chars={len(SEED)} (TMA context from README)")
    else:
        print("  live mode: requires llm_chain + model GGUF + FAISS as upstream README")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
