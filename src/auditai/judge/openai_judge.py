"""OpenAI-compatible LLM-as-judge (OpenAI, xAI/Grok, OpenRouter, …)."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from auditai.config import JudgeConfig
from auditai.errors import JudgeError
from auditai.models import JudgeUsage

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
        # Widely available on current xAI catalogs; override in YAML if needed
        "model": "grok-4.3",
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
    if not model or (provider == "xai" and model in {"gpt-4o-mini", "mock"}):
        model = str(defaults.get("model") or "gpt-4o-mini")
    return api_key, base_url, model, provider


class OpenAIJudge:
    """Chat Completions judge via the OpenAI Python SDK (any compatible base_url)."""

    def __init__(self, config: JudgeConfig, *, provider_label: str | None = None) -> None:
        api_key, base_url, model, provider = resolve_judge_credentials(config)
        self.provider = provider_label or provider
        self.model = model
        self.call_count = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self._config = config
        client_kwargs: dict = {
            "api_key": api_key,
            "max_retries": config.max_retries,
        }
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**client_kwargs)
        self._base_url = base_url

    def usage_snapshot(self) -> JudgeUsage:
        return JudgeUsage(
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.prompt_tokens + self.completion_tokens,
            estimated=False,
            provider=self.provider,
            model=self.model,
        )

    def _record_usage(self, usage: object | None, *, prompt: str, system: str | None, content: str) -> None:
        """Accumulate API usage; fall back to char heuristic if provider omits usage."""
        pt = ct = None
        if usage is not None:
            pt = getattr(usage, "prompt_tokens", None)
            ct = getattr(usage, "completion_tokens", None)
            if pt is None and isinstance(usage, dict):
                pt = usage.get("prompt_tokens")
                ct = usage.get("completion_tokens")
        if pt is not None and ct is not None:
            self.prompt_tokens += int(pt)
            self.completion_tokens += int(ct)
            return
        # Fallback estimate (~4 chars/token)
        in_chars = len(system or "") + len(prompt)
        out_chars = len(content or "")
        self.prompt_tokens += max(1, in_chars // 4)
        self.completion_tokens += max(1, out_chars // 4)

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
            err = str(e)
            hint = ""
            if "model" in err.lower() and any(
                x in err.lower() for x in ("not found", "does not exist", "invalid", "404")
            ):
                hint = (
                    f" Hint: set judge.model to a model available on your account "
                    f"(current={self.model!r}). For xAI try grok-4.3 or grok-3-mini."
                )
            raise JudgeError(f"{self.provider} judge failed ({where}): {e}.{hint}") from e

        content = resp.choices[0].message.content
        if not content:
            raise JudgeError("empty judge response")
        text = content.strip()
        self._record_usage(getattr(resp, "usage", None), prompt=prompt, system=system, content=text)
        return text
