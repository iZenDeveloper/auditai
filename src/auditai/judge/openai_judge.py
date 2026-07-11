"""OpenAI BYOK judge."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from auditai.config import JudgeConfig
from auditai.errors import JudgeError


class OpenAIJudge:
    def __init__(self, config: JudgeConfig) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise JudgeError("OPENAI_API_KEY missing")
        self.provider = "openai"
        self.model = config.model
        self.call_count = 0
        self._config = config
        self._client = AsyncOpenAI(api_key=api_key, max_retries=config.max_retries)

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            self.call_count += 1
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self._config.temperature,
                timeout=self._config.timeout_seconds,
            )
        except Exception as e:
            raise JudgeError(f"OpenAI judge failed: {e}") from e

        content = resp.choices[0].message.content
        if not content:
            raise JudgeError("empty judge response")
        return content.strip()
