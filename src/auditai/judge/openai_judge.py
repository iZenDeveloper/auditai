"""OpenAI-compatible LLM-as-judge (OpenAI, xAI/Grok, OpenRouter, …)."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from auditai.config import JudgeConfig
from auditai.errors import JudgeError

# Defaults for known providers (OpenAI SDK chat.completions shape).
_PROVIDER_DEFAULTS: dict[str, dict[str, str | None]] = {
    "openai": {
        "base_url": None,  # SDK default https://api.openai.com/v1
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
    },
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
        "model": "grok-3-mini",
    },
}


def resolve_judge_credentials(config: JudgeConfig) -> tuple[str, str | None, str, str]:
    """Return (api_key, base_url|None, model, provider_label).

    Raises JudgeError if the API key env is missing.
    """
    provider = config.provider
    defaults = _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["openai"])

    api_key_env = (config.api_key_env or defaults["api_key_env"] or "OPENAI_API_KEY").strip()
    api_key = os.environ.get(api_key_env) or ""
    if not api_key.strip():
        raise JudgeError(
            f"{api_key_env} is required for judge.provider={provider} (BYOK). "
            "Export the key or use judge.provider=mock for offline demos."
        )

    base_url = config.base_url if config.base_url is not None else defaults.get("base_url")
    if isinstance(base_url, str):
        base_url = base_url.strip() or None

    model = (config.model or "").strip()
    # Pydantic default model is openai-oriented; map to Grok when provider=xai
    # unless the user already set a non-default model name.
    if not model or (provider == "xai" and model == "gpt-4o-mini"):
        model = str(defaults.get("model") or "gpt-4o-mini")
    return api_key, base_url, model, provider


class OpenAIJudge:
    """Chat Completions judge via the OpenAI Python SDK (any compatible base_url)."""

    def __init__(self, config: JudgeConfig, *, provider_label: str | None = None) -> None:
        api_key, base_url, model, provider = resolve_judge_credentials(config)
        self.provider = provider_label or provider
        self.model = model
        self.call_count = 0
        self._config = config
        client_kwargs: dict = {
            "api_key": api_key,
            "max_retries": config.max_retries,
        }
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**client_kwargs)
        self._base_url = base_url

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
            where = self._base_url or "api.openai.com"
            raise JudgeError(f"{self.provider} judge failed ({where}): {e}") from e

        content = resp.choices[0].message.content
        if not content:
            raise JudgeError("empty judge response")
        return content.strip()
