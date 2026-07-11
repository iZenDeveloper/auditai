"""Environment variable expansion and secret redaction."""

from __future__ import annotations

import os
import re
from typing import Any

# ${VAR} or ${VAR:-default}
_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")

_SECRET_KEYS = re.compile(
    r"(authorization|api[_-]?key|token|password|secret|bearer)",
    re.IGNORECASE,
)
_BEARER_RE = re.compile(r"(Bearer\s+)(\S+)", re.IGNORECASE)
_SK_RE = re.compile(r"\b(sk-[A-Za-z0-9_-]{8,})\b")


def expand_env(value: str) -> str:
    """Expand ${VAR} and ${VAR:-default} in a string."""

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        env_val = os.environ.get(name)
        if env_val is not None and env_val != "":
            return env_val
        if default is not None:
            return default
        return match.group(0)  # leave unresolved for caller to detect

    return _ENV_PATTERN.sub(repl, value)


def expand_env_deep(obj: Any) -> Any:
    """Recursively expand env vars in strings within dicts/lists."""
    if isinstance(obj, str):
        return expand_env(obj)
    if isinstance(obj, dict):
        return {k: expand_env_deep(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env_deep(v) for v in obj]
    return obj


def has_unresolved_env(value: str) -> bool:
    return bool(_ENV_PATTERN.search(value))


def redact_secrets(text: str) -> str:
    text = _BEARER_RE.sub(r"\1***", text)
    text = _SK_RE.sub("sk-***", text)
    return text


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in data.items():
        if _SECRET_KEYS.search(str(k)):
            out[k] = "***"
        elif isinstance(v, dict):
            out[k] = redact_mapping(v)
        elif isinstance(v, str):
            out[k] = redact_secrets(v)
        else:
            out[k] = v
    return out
