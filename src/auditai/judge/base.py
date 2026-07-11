from __future__ import annotations

from typing import Protocol


class Judge(Protocol):
    provider: str
    model: str
    call_count: int

    async def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Return raw text completion from the judge model."""
        ...
