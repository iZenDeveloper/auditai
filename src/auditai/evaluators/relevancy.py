"""Answer relevancy evaluator."""

from __future__ import annotations

import json
import re

from auditai.config import MetricConfig
from auditai.errors import JudgeError
from auditai.judge.base import Judge
from auditai.models import AuditCase, CaseCategory, MetricScore, TargetResponse


class AnswerRelevancyEvaluator:
    name = "answer_relevancy"

    def __init__(self, config: MetricConfig) -> None:
        self.config = config

    def applicable(self, case: AuditCase, response: TargetResponse) -> bool:
        if case.category == CaseCategory.prompt_injection:
            return False
        if case.category == CaseCategory.faithfulness:
            return True  # optional dual score
        return case.category in {CaseCategory.general, CaseCategory.relevancy}

    async def score(
        self,
        case: AuditCase,
        response: TargetResponse,
        judge: Judge,
        threshold: float,
    ) -> MetricScore:
        deepeval_score = await _try_deepeval_relevancy(case, response, threshold)
        if deepeval_score is not None:
            return deepeval_score

        system = (
            "You grade answer relevancy to the question. "
            "Score 1.0 if fully on-topic, 0.0 if off-topic. "
            'Reply JSON only: {"score": 0.0-1.0, "reason": "..."}'
        )
        prompt = (
            "Grade answer relevancy.\n"
            f"Question: {case.question}\n"
            f"Answer: {response.answer}\n"
        )
        try:
            raw = await judge.complete(prompt, system=system)
            score, reason = _parse_score_json(raw)
        except JudgeError as e:
            return MetricScore(
                name=self.name,
                score=0.0,
                threshold=threshold,
                passed=False,
                reason=f"judge_error: {e}",
            )

        return MetricScore(
            name=self.name,
            score=score,
            threshold=threshold,
            passed=score >= threshold,
            reason=reason,
            details={"backend": "judge_prompt"},
        )


async def _try_deepeval_relevancy(
    case: AuditCase,
    response: TargetResponse,
    threshold: float,
) -> MetricScore | None:
    try:
        from deepeval.metrics import AnswerRelevancyMetric  # type: ignore
        from deepeval.test_case import LLMTestCase  # type: ignore
    except Exception:
        return None

    try:
        metric = AnswerRelevancyMetric(threshold=threshold, include_reason=True)
        tc = LLMTestCase(input=case.question, actual_output=response.answer)
        metric.measure(tc)
        score = float(metric.score or 0.0)
        reason = getattr(metric, "reason", None)
        return MetricScore(
            name="answer_relevancy",
            score=score,
            threshold=threshold,
            passed=score >= threshold,
            reason=reason,
            details={"backend": "deepeval"},
        )
    except Exception as e:
        return MetricScore(
            name="answer_relevancy",
            score=0.0,
            threshold=threshold,
            passed=False,
            reason=f"deepeval_error: {e}",
            details={"backend": "deepeval"},
        )


def _parse_score_json(raw: str) -> tuple[float, str]:
    raw = raw.strip()
    if "```" in raw:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            raw = m.group(0)
    try:
        data = json.loads(raw)
        score = float(data.get("score", 0.0))
        return max(0.0, min(1.0, score)), str(data.get("reason") or "")
    except (json.JSONDecodeError, TypeError, ValueError):
        m = re.search(r"([01](?:\.\d+)?)", raw)
        if m:
            return max(0.0, min(1.0, float(m.group(1)))), raw[:200]
        return 0.0, f"unparseable_judge_output: {raw[:200]}"
