from datetime import datetime, timezone

from auditai.cloud import build_payload, resolve_cloud_config
from auditai.config import AuditConfig, CloudConfig, DatasetConfig, TargetConfig
from auditai.models import CaseResult, MetricAggregate, MetricScore, RunSummary, TopFailure


def _summary() -> RunSummary:
    return RunSummary(
        run_id="r1",
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        config_path="x.yml",
        total_cases=1,
        failed_cases=0,
        metric_aggregates={
            "faithfulness": MetricAggregate(
                name="faithfulness",
                mean=0.9,
                min=0.9,
                max=0.9,
                threshold=0.8,
                passed=True,
                n_scored=1,
            )
        },
        overall_passed=True,
        exit_reason="all_metrics_passed",
        top_failures=[
            TopFailure(
                case_id="c1",
                metric="faithfulness",
                score=0.2,
                question="secret customer question",
                answer="secret answer text",
                reason="bad",
            )
        ],
        judge_calls=1,
    )


def test_build_payload_redacts_answers():
    cloud = CloudConfig(include_answers=False, include_results=True)
    results = [
        CaseResult(
            case_id="c1",
            question="q",
            answer="CONFIDENTIAL",
            contexts_used=["doc"],
            metrics=[
                MetricScore(name="faithfulness", score=0.9, threshold=0.8, passed=True)
            ],
        )
    ]
    payload = build_payload(_summary(), results, cloud)
    assert payload["top_failures"][0]["answer"] == ""
    assert payload["results"][0]["answer"] == ""
    assert payload["results"][0]["contexts_used"] == []
    assert payload["aggregates"]["faithfulness"]["mean"] == 0.9


def test_resolve_cloud_auto_with_key(monkeypatch):
    monkeypatch.setenv("AUDITAI_PROJECT_KEY", "aai_test")
    monkeypatch.setenv("AUDITAI_API_URL", "http://localhost:9999")
    cfg = AuditConfig(
        target=TargetConfig(url="http://x"),
        dataset=DatasetConfig(path="d.json"),
        cloud=CloudConfig(enabled=None, api_url="http://localhost:9999"),
    )
    resolved = resolve_cloud_config(cfg)
    assert resolved is not None
    assert resolved.api_url == "http://localhost:9999"


def test_resolve_cloud_skip_without_key(monkeypatch):
    monkeypatch.delenv("AUDITAI_PROJECT_KEY", raising=False)
    cfg = AuditConfig(
        target=TargetConfig(url="http://x"),
        dataset=DatasetConfig(path="d.json"),
        cloud=CloudConfig(enabled=None),
    )
    assert resolve_cloud_config(cfg) is None
