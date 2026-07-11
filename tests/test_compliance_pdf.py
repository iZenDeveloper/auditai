from datetime import datetime, timezone
from pathlib import Path

from auditai.compliance_pdf import (
    CertificateData,
    MetricLine,
    build_compliance_pdf,
    certificate_from_report_json,
    write_compliance_pdf,
)


def test_build_pdf_bytes():
    cert = CertificateData(
        project_name="demo",
        run_id="run-1",
        overall_passed=False,
        exit_reason="metric_below_threshold:faithfulness",
        issued_at=datetime.now(timezone.utc),
        metrics=[
            MetricLine(name="faithfulness", mean=0.72, threshold=0.8, passed=False, n_scored=4),
            MetricLine(name="answer_relevancy", mean=0.85, threshold=0.75, passed=True, n_scored=4),
        ],
        total_cases=6,
        top_failures=[{"case_id": "h1", "metric": "faithfulness", "score": 0.2, "question": "refund?"}],
        git_sha="abcdef123456",
        repo="acme/rag",
    )
    data = build_compliance_pdf(cert)
    assert data[:4] == b"%PDF"
    assert len(data) > 500


def test_from_report_json_and_write(tmp_path: Path):
    report = {
        "run_id": "abc",
        "overall_passed": True,
        "exit_reason": "all_metrics_passed",
        "finished_at": "2026-07-11T10:00:00+00:00",
        "total_cases": 3,
        "failed_cases": 0,
        "judge_calls": 5,
        "aggregates": {
            "faithfulness": {"mean": 0.9, "threshold": 0.8, "passed": True, "n_scored": 2}
        },
        "top_failures": [],
        "metadata": {"git_sha": "deadbeef"},
    }
    cert = certificate_from_report_json(report, project_name="p")
    assert cert.overall_passed is True
    assert cert.metrics[0].mean == 0.9
    out = write_compliance_pdf(cert, tmp_path / "c.pdf")
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"
