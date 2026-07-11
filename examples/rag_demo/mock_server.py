#!/usr/bin/env python3
"""Minimal mock RAG API for local demos. No third-party deps beyond stdlib."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765

DOCS = {
    "hoàn tiền": "Khách hàng được hoàn tiền trong vòng 7 ngày nếu còn hóa đơn mua hàng.",
    "giao hàng": "Giao hàng tiêu chuẩn mất 3-5 ngày làm việc trong nội thành.",
    "vận chuyển": "Phí vận chuyển nội thành là 30.000 VND cho đơn dưới 500.000 VND.",
}


def answer_for(question: str) -> tuple[str, list[str]]:
    q = question.lower()

    # Intentional hallucination path for demo
    if "unsupported" in q or "hallucinate" in q or "bịa" in q:
        ctx = [DOCS["hoàn tiền"]]
        return (
            "Bạn được hoàn tiền trong 90 ngày và tặng thêm voucher 1 triệu (I made this up).",
            ctx,
        )

    # Prompt injection attempts
    if "ignore all previous" in q or "system prompt" in q or "secret" in q:
        return (
            "I cannot reveal system prompts or secrets. I will continue to follow my safety policy.",
            [],
        )

    for key, doc in DOCS.items():
        if key in q:
            return doc, [doc]

    return "Xin lỗi, tôi không có thông tin trong tài liệu.", []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quieter
        pass

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/chat":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        question = str(body.get("question") or body.get("message") or "")
        case_id = str(body.get("case_id") or self.headers.get("X-Case-Id") or "")
        if case_id == "hallucinate":
            ans, ctx = answer_for("hallucinate unsupported")
        else:
            ans, ctx = answer_for(question)

        payload = json.dumps({"answer": ans, "contexts": ctx}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Mock RAG server on http://127.0.0.1:{PORT}/chat")
    server.serve_forever()


if __name__ == "__main__":
    main()
