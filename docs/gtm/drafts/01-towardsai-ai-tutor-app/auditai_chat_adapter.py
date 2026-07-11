#!/usr/bin/env python3
"""Thin JSON adapter for AuditAI against towardsai/ai-tutor-app.

Their production endpoint POST /api/chat is SSE (Vercel AI SDK).
AuditAI expects a simple JSON body with an answer string.

This adapter is a *sketch* you refine when forking upstream:

Option 1 (preferred if available): call an internal non-stream helper
from app.chat_service if one exists for tests.

Option 2: POST to /api/chat, parse SSE text events, return JSON.

Default below is Option 2 (best-effort SSE text extraction).

Usage:
  AI_TUTOR_API_BASE=http://127.0.0.1:8000 python auditai_chat_adapter.py
  # listens on http://127.0.0.1:18080/chat
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx

UPSTREAM = os.environ.get("AI_TUTOR_API_BASE", "http://127.0.0.1:8000").rstrip("/")
PORT = int(os.environ.get("AUDITAI_ADAPTER_PORT", "18080"))


def call_tutor(question: str) -> tuple[str, list[str]]:
    """Return (answer, contexts). Contexts may be empty if not exposed."""
    # Minimal UI-message style payload; adjust if upstream schema drifts.
    payload = {
        "query": question,
        "threadId": "",
        "includeReasoning": False,
    }
    answer_parts: list[str] = []
    contexts: list[str] = []

    with httpx.Client(timeout=120.0) as client:
        with client.stream(
            "POST",
            f"{UPSTREAM}/api/chat",
            json=payload,
            headers={"Accept": "text/event-stream"},
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data in ("[DONE]", ""):
                    continue
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    answer_parts.append(data)
                    continue
                # Best-effort parse of common stream shapes
                if isinstance(obj, str):
                    answer_parts.append(obj)
                elif isinstance(obj, dict):
                    if "delta" in obj and isinstance(obj["delta"], str):
                        answer_parts.append(obj["delta"])
                    elif "text" in obj:
                        answer_parts.append(str(obj["text"]))
                    elif "content" in obj and isinstance(obj["content"], str):
                        answer_parts.append(obj["content"])

    answer = "".join(answer_parts).strip() or "(empty stream — refine adapter parsing)"
    return answer, contexts


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/chat":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        question = str(body.get("question") or body.get("query") or "")
        try:
            answer, contexts = call_tutor(question)
            status = 200
            payload = {"answer": answer, "contexts": contexts}
        except Exception as e:  # noqa: BLE001
            status = 502
            payload = {"answer": "", "error": str(e), "contexts": []}

        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"AuditAI adapter on http://127.0.0.1:{PORT}/chat -> {UPSTREAM}/api/chat")
    server.serve_forever()


if __name__ == "__main__":
    main()
