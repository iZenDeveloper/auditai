import json
from pathlib import Path

from typer.testing import CliRunner

from auditai.cli import app

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.1" in result.stdout


def test_dry_run():
    result = runner.invoke(
        app,
        ["run", "--config", str(FIXTURES / "sample.yml"), "--dry-run"],
    )
    assert result.exit_code == 0
    assert "dry-run OK" in result.output


def test_validate_mock():
    result = runner.invoke(app, ["validate", "--config", str(FIXTURES / "sample.yml")])
    assert result.exit_code == 0
    assert "valid" in result.output


def _write_report(path: Path, **means: float) -> None:
    path.write_text(
        json.dumps({"aggregates": {name: {"mean": mean} for name, mean in means.items()}}),
        encoding="utf-8",
    )


def test_compare_passes_within_allowed_drop(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    _write_report(baseline, faithfulness=0.90, answer_relevancy=0.80)
    _write_report(current, faithfulness=0.85, answer_relevancy=0.83)

    result = runner.invoke(
        app,
        [
            "compare",
            "--baseline",
            str(baseline),
            "--current",
            str(current),
            "--max-drop",
            "0.05",
        ],
    )

    assert result.exit_code == 0
    assert "No metric regression" in result.output


def test_compare_fails_on_regression(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    _write_report(baseline, faithfulness=0.90)
    _write_report(current, faithfulness=0.82)

    result = runner.invoke(
        app,
        ["compare", "--baseline", str(baseline), "--current", str(current)],
    )

    assert result.exit_code == 1
    assert "Regression gate failed" in result.output
    assert "drop 0.0800 exceeds 0.0500" in " ".join(result.output.split())


def test_compare_fails_when_current_metric_is_missing(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    _write_report(baseline, faithfulness=0.90, prompt_injection=1.0)
    _write_report(current, faithfulness=0.91)

    result = runner.invoke(
        app,
        ["compare", "--baseline", str(baseline), "--current", str(current)],
    )

    assert result.exit_code == 1
    assert "prompt_injection" in result.output
    assert "missing from current report" in " ".join(result.output.split())


def test_compare_invalid_report_is_user_error(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    baseline.write_text("not json", encoding="utf-8")
    _write_report(current, faithfulness=0.91)

    result = runner.invoke(
        app,
        ["compare", "--baseline", str(baseline), "--current", str(current)],
    )

    assert result.exit_code == 2
    assert "invalid baseline report JSON" in result.output


def test_baseline_keeps_aggregates_but_removes_sensitive_results(tmp_path: Path):
    source = tmp_path / "report.json"
    output = tmp_path / "baseline.json"
    source.write_text(
        json.dumps(
            {
                "overall_passed": True,
                "run_id": "run-1",
                "finished_at": "2026-07-21T00:00:00Z",
                "total_cases": 2,
                "judge_usage": {"provider": "openai", "model": "gpt-test", "total_tokens": 9},
                "aggregates": {
                    "faithfulness": {"mean": 0.9, "threshold": 0.8, "n_scored": 2}
                },
                "results": [
                    {
                        "question": "private question",
                        "answer": "private answer",
                        "contexts_used": ["private context"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["baseline", "--from", str(source), "--out", str(output)],
    )

    assert result.exit_code == 0
    baseline = json.loads(output.read_text(encoding="utf-8"))
    assert baseline["kind"] == "auditai_baseline"
    assert baseline["aggregates"]["faithfulness"]["mean"] == 0.9
    assert baseline["source"]["judge"] == {"provider": "openai", "model": "gpt-test"}
    serialized = json.dumps(baseline)
    assert "private question" not in serialized
    assert "private answer" not in serialized
    assert "private context" not in serialized
    assert "total_tokens" not in serialized


def test_baseline_refuses_failed_report(tmp_path: Path):
    source = tmp_path / "report.json"
    output = tmp_path / "baseline.json"
    source.write_text(
        json.dumps(
            {
                "overall_passed": False,
                "aggregates": {"faithfulness": {"mean": 0.7}},
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["baseline", "--from", str(source), "--out", str(output)],
    )

    assert result.exit_code == 2
    assert "did not pass" in result.output
    assert not output.exists()


def test_baseline_does_not_overwrite_without_force(tmp_path: Path):
    source = tmp_path / "report.json"
    output = tmp_path / "baseline.json"
    source.write_text(
        json.dumps(
            {
                "overall_passed": True,
                "aggregates": {"faithfulness": {"mean": 0.9}},
            }
        ),
        encoding="utf-8",
    )
    output.write_text("keep me", encoding="utf-8")

    result = runner.invoke(
        app,
        ["baseline", "--from", str(source), "--out", str(output)],
    )

    assert result.exit_code == 2
    assert "already exists" in result.output
    assert output.read_text(encoding="utf-8") == "keep me"
