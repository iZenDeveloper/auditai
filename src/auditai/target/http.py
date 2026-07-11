"""HTTP target for user RAG/LLM endpoints."""

from __future__ import annotations

import copy
import time
from typing import Any

import httpx

from auditai.config import TargetConfig
from auditai.errors import TargetError
from auditai.models import AuditCase, TargetResponse
from auditai.util.jsonpath import get_by_path


def _render_value(value: Any, case: AuditCase) -> Any:
    if isinstance(value, str):
        return (
            value.replace("{{question}}", case.question)
            .replace("{{case_id}}", case.id)
            .replace("{{id}}", case.id)
        )
    if isinstance(value, dict):
        return {k: _render_value(v, case) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_value(v, case) for v in value]
    return value


def _as_context_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


class HttpTarget:
    def __init__(self, config: TargetConfig, client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> HttpTarget:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout_seconds)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def invoke(self, case: AuditCase) -> TargetResponse:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout_seconds)
            self._owns_client = True

        body = _render_value(copy.deepcopy(self.config.body_template), case)
        headers = dict(self.config.headers)
        started = time.perf_counter()

        try:
            resp = await self._client.request(
                self.config.method,
                self.config.url,
                headers=headers,
                json=body if self.config.method != "GET" else None,
                params=body if self.config.method == "GET" else None,
            )
        except httpx.TimeoutException as e:
            raise TargetError(f"timeout calling {self.config.url}") from e
        except httpx.HTTPError as e:
            raise TargetError(f"HTTP error calling {self.config.url}: {e}") from e

        latency_ms = (time.perf_counter() - started) * 1000

        if resp.status_code >= 500:
            # one retry on 5xx
            try:
                resp = await self._client.request(
                    self.config.method,
                    self.config.url,
                    headers=headers,
                    json=body if self.config.method != "GET" else None,
                    params=body if self.config.method == "GET" else None,
                )
                latency_ms = (time.perf_counter() - started) * 1000
            except httpx.HTTPError as e:
                raise TargetError(f"HTTP error on retry: {e}") from e

        if resp.status_code >= 400:
            raise TargetError(f"target returned HTTP {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
        except ValueError as e:
            raise TargetError("target response is not valid JSON") from e

        if not isinstance(data, dict):
            data = {"_root": data}

        answer_val = get_by_path(data, self.config.response_map.answer)
        if answer_val is None:
            raise TargetError(
                f"could not extract answer at path '{self.config.response_map.answer}'"
            )
        answer = str(answer_val).strip()
        if not answer:
            raise TargetError("empty answer from target")

        contexts: list[str] = []
        if self.config.response_map.contexts:
            contexts = _as_context_list(get_by_path(data, self.config.response_map.contexts))

        return TargetResponse(
            answer=answer,
            contexts=contexts,
            raw=data if isinstance(data, dict) else {"value": data},
            latency_ms=latency_ms,
            status_code=resp.status_code,
        )
