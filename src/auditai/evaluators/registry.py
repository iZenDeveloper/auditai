from __future__ import annotations

from auditai.config import AuditConfig
from auditai.evaluators.base import Evaluator
from auditai.evaluators.faithfulness import FaithfulnessEvaluator
from auditai.evaluators.injection import PromptInjectionEvaluator
from auditai.evaluators.relevancy import AnswerRelevancyEvaluator


def build_evaluators(cfg: AuditConfig) -> list[tuple[Evaluator, float]]:
    """Return list of (evaluator, threshold) for enabled metrics."""
    out: list[tuple[Evaluator, float]] = []
    if cfg.metrics.faithfulness.enabled:
        out.append(
            (FaithfulnessEvaluator(cfg.metrics.faithfulness), cfg.metrics.faithfulness.threshold)
        )
    if cfg.metrics.answer_relevancy.enabled:
        out.append(
            (
                AnswerRelevancyEvaluator(cfg.metrics.answer_relevancy),
                cfg.metrics.answer_relevancy.threshold,
            )
        )
    if cfg.metrics.prompt_injection.enabled:
        out.append(
            (
                PromptInjectionEvaluator(cfg.metrics.prompt_injection),
                cfg.metrics.prompt_injection.threshold,
            )
        )
    return out
