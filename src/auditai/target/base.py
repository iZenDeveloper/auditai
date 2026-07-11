from __future__ import annotations

from typing import Protocol

from auditai.models import AuditCase, TargetResponse


class Target(Protocol):
    async def invoke(self, case: AuditCase) -> TargetResponse:
        """Call the system under test for a single case."""
        ...
