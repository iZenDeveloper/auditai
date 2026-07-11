from __future__ import annotations

from typing import Protocol

from auditai.judge.base import Judge
from auditai.models import AuditCase, MetricScore, TargetResponse


class Evaluator(Protocol):
    name: str

    def applicable(self, case: AuditCase, response: TargetResponse) -> bool: ...

    async def score(
        self,
        case: AuditCase,
        response: TargetResponse,
        judge: Judge,
        threshold: float,
    ) -> MetricScore: ...
