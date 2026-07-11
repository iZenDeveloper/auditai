"""Orchestrate audit runs."""

from __future__ import annotations

import asyncio
import statistics
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from auditai.cloud import push_run, resolve_cloud_config
from auditai.config import AuditConfig, ensure_judge_auth
from auditai.dataset import load_dataset
from auditai.errors import TargetError
from auditai.evaluators.registry import build_evaluators
from auditai.judge.factory import create_judge
from auditai.models import (
    CaseResult,
    JudgeUsage,
    MetricAggregate,
    MetricScore,
    RunSummary,
    TopFailure,
)
from auditai.reporters.json_report import write_json_report
from auditai.reporters.markdown import write_markdown_report
from auditai.reporters.terminal import print_summary
from auditai.target.http import HttpTarget


async def run_audit(cfg: AuditConfig, *, base_dir: Path | None = None) -> tuple[RunSummary, list[CaseResult]]:
    ensure_judge_auth(cfg)
    cases = load_dataset(cfg, base_dir=base_dir)
    evaluators = build_evaluators(cfg)
    judge = create_judge(cfg.judge)

    started = datetime.now(timezone.utc)
    results: list[CaseResult] = []
    sem = asyncio.Semaphore(max(1, cfg.run.concurrency))

    async with HttpTarget(cfg.target) as target:

        async def one(case_idx: int, case) -> CaseResult:
            async with sem:
                t0 = time.perf_counter()
                try:
                    response = await target.invoke(case)
                except TargetError as e:
                    return CaseResult(
                        case_id=case.id,
                        question=case.question,
                        error=str(e),
                        duration_ms=(time.perf_counter() - t0) * 1000,
                    )

                metrics: list[MetricScore] = []
                for ev, threshold in evaluators:
                    if not ev.applicable(case, response):
                        continue
                    score = await ev.score(case, response, judge, threshold)
                    metrics.append(score)

                contexts_used = response.contexts or case.contexts
                return CaseResult(
                    case_id=case.id,
                    question=case.question,
                    answer=response.answer,
                    contexts_used=contexts_used,
                    metrics=metrics,
                    duration_ms=(time.perf_counter() - t0) * 1000,
                )

        # Process in chunks so we can abort on high target error rate
        # without leaving un-awaited coroutines.
        chunk_size = max(cfg.run.concurrency, 5)
        aborted = False
        for i in range(0, len(cases), chunk_size):
            batch = cases[i : i + chunk_size]
            chunk = await asyncio.gather(*[one(i + j, c) for j, c in enumerate(batch)])
            results.extend(chunk)
            done = len(results)
            if done >= 5:
                err_rate = sum(1 for r in results if r.error) / done
                if err_rate > cfg.run.stop_on_target_error_rate:
                    aborted = True
                    break

        if aborted:
            summary = _build_summary(
                cfg,
                results,
                started,
                overall_passed=False,
                exit_reason="target_unstable",
                judge_calls=judge.call_count,
                judge_usage=_judge_usage(judge),
            )
            _write_outputs(cfg, summary, results)
            _maybe_push_cloud(cfg, summary, results)
            return summary, results

    summary = _finalize(cfg, results, started, judge)
    _write_outputs(cfg, summary, results)
    _maybe_push_cloud(cfg, summary, results)
    return summary, results


def _judge_usage(judge: object) -> JudgeUsage:
    snap = getattr(judge, "usage_snapshot", None)
    if callable(snap):
        return snap()
    return JudgeUsage(
        prompt_tokens=int(getattr(judge, "prompt_tokens", 0) or 0),
        completion_tokens=int(getattr(judge, "completion_tokens", 0) or 0),
        total_tokens=int(getattr(judge, "prompt_tokens", 0) or 0)
        + int(getattr(judge, "completion_tokens", 0) or 0),
        estimated=getattr(judge, "provider", "") == "mock",
        provider=str(getattr(judge, "provider", "") or ""),
        model=str(getattr(judge, "model", "") or ""),
    )


def _maybe_push_cloud(cfg: AuditConfig, summary: RunSummary, results: list[CaseResult]) -> None:
    cloud = resolve_cloud_config(cfg)
    if cloud is None:
        return
    push_run(summary, results, cloud)


def _finalize(
    cfg: AuditConfig,
    results: list[CaseResult],
    started: datetime,
    judge: object,
) -> RunSummary:
    aggregates = _aggregate(cfg, results)
    overall, reason = _pass_fail(cfg, results, aggregates)
    return _build_summary(
        cfg,
        results,
        started,
        overall_passed=overall,
        exit_reason=reason,
        judge_calls=int(getattr(judge, "call_count", 0) or 0),
        judge_usage=_judge_usage(judge),
        aggregates=aggregates,
    )


def _aggregate(cfg: AuditConfig, results: list[CaseResult]) -> dict[str, MetricAggregate]:
    buckets: dict[str, list[float]] = {}
    errors: dict[str, int] = {}
    thresholds: dict[str, float] = {
        "faithfulness": cfg.metrics.faithfulness.threshold,
        "answer_relevancy": cfg.metrics.answer_relevancy.threshold,
        "prompt_injection": cfg.metrics.prompt_injection.threshold,
    }
    enabled = {
        "faithfulness": cfg.metrics.faithfulness.enabled,
        "answer_relevancy": cfg.metrics.answer_relevancy.enabled,
        "prompt_injection": cfg.metrics.prompt_injection.enabled,
    }

    for name, on in enabled.items():
        if on:
            buckets[name] = []
            errors[name] = 0

    for r in results:
        for m in r.metrics:
            if m.name not in buckets:
                continue
            if m.reason and m.reason.startswith("judge_error"):
                errors[m.name] = errors.get(m.name, 0) + 1
            buckets[m.name].append(m.score)

    aggregates: dict[str, MetricAggregate] = {}
    for name, scores in buckets.items():
        thr = thresholds[name]
        if not scores:
            aggregates[name] = MetricAggregate(
                name=name,
                mean=0.0,
                min=0.0,
                max=0.0,
                threshold=thr,
                passed=False,
                n_scored=0,
                n_errors=errors.get(name, 0),
            )
            continue
        mean = statistics.fmean(scores)
        aggregates[name] = MetricAggregate(
            name=name,
            mean=mean,
            min=min(scores),
            max=max(scores),
            threshold=thr,
            passed=mean >= thr,
            n_scored=len(scores),
            n_errors=errors.get(name, 0),
        )
    return aggregates


def _pass_fail(
    cfg: AuditConfig,
    results: list[CaseResult],
    aggregates: dict[str, MetricAggregate],
) -> tuple[bool, str]:
    if not results:
        return False, "no_cases"

    target_failures = sum(1 for r in results if r.error)
    if target_failures == len(results):
        return False, "all_targets_failed"

    for name, agg in aggregates.items():
        if agg.n_scored == 0:
            return False, f"no_scores_for:{name}"

    if cfg.run.fail_on == "average":
        for name, agg in aggregates.items():
            if not agg.passed:
                return False, f"metric_below_threshold:{name}"
        return True, "all_metrics_passed"

    # fail_on: any
    if target_failures:
        return False, "target_errors"
    for r in results:
        for m in r.metrics:
            if not m.passed:
                return False, f"case_metric_failed:{r.case_id}:{m.name}"
    return True, "all_cases_passed"


def _top_failures(results: list[CaseResult], n: int) -> list[TopFailure]:
    fails: list[TopFailure] = []
    for r in results:
        for m in r.metrics:
            if not m.passed:
                fails.append(
                    TopFailure(
                        case_id=r.case_id,
                        metric=m.name,
                        score=m.score,
                        question=r.question,
                        answer=r.answer,
                        reason=m.reason,
                    )
                )
        if r.error:
            fails.append(
                TopFailure(
                    case_id=r.case_id,
                    metric="target",
                    score=0.0,
                    question=r.question,
                    answer="",
                    reason=r.error,
                )
            )
    fails.sort(key=lambda x: x.score)
    return fails[:n]


def _build_summary(
    cfg: AuditConfig,
    results: list[CaseResult],
    started: datetime,
    *,
    overall_passed: bool,
    exit_reason: str,
    judge_calls: int,
    judge_usage: JudgeUsage | None = None,
    aggregates: dict[str, MetricAggregate] | None = None,
) -> RunSummary:
    if aggregates is None:
        aggregates = _aggregate(cfg, results)
    finished = datetime.now(timezone.utc)
    return RunSummary(
        run_id=str(uuid.uuid4()),
        started_at=started,
        finished_at=finished,
        config_path=cfg.config_path,
        total_cases=len(results),
        failed_cases=sum(1 for r in results if r.error),
        metric_aggregates=aggregates,
        overall_passed=overall_passed,
        exit_reason=exit_reason,
        top_failures=_top_failures(results, cfg.output.top_failures),
        judge_calls=judge_calls,
        judge_usage=judge_usage or JudgeUsage(),
    )


def _write_outputs(cfg: AuditConfig, summary: RunSummary, results: list[CaseResult]) -> Path:
    out_dir = Path(cfg.output.dir)
    if not out_dir.is_absolute() and cfg.config_path:
        out_dir = Path(cfg.config_path).parent / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if cfg.output.write_json:
        write_json_report(out_dir / "auditai-report.json", summary, results)
    if cfg.output.write_markdown:
        write_markdown_report(out_dir / "auditai-report.md", summary)
    if cfg.output.terminal:
        print_summary(summary)
    return out_dir
