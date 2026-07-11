"""Minimal dot-path extraction (no external JSONPath dep for v0.1)."""

from __future__ import annotations

from typing import Any


def get_by_path(data: Any, path: str) -> Any:
    """Get value by dotted path, e.g. 'data.answer' or 'choices.0.message'."""
    if not path:
        return data
    cur: Any = data
    for part in path.split("."):
        if cur is None:
            return None
        if isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if idx < 0 or idx >= len(cur):
                return None
            cur = cur[idx]
            continue
        if isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur[part]
            continue
        return None
    return cur
