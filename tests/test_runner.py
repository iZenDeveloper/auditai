from pathlib import Path

import httpx
import pytest
import respx

from auditai.config import load_config
from auditai.runner import run_audit

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
@respx.mock
async def test_run_audit_with_mock_target(tmp_path, monkeypatch):
    route = respx.post("http://127.0.0.1:9/chat").mock(
        return_value=httpx.Response(
            200,
            json={
                "answer": "Refunds are available within 7 days with a receipt.",
                "contexts": ["Refunds are available within 7 days with a receipt."],
            },
        )
    )

    # Second call (injection) — refuse
    def _side_effect(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        if "Ignore" in body or "system prompt" in body:
            return httpx.Response(
                200,
                json={"answer": "I cannot reveal system prompts.", "contexts": []},
            )
        return httpx.Response(
            200,
            json={
                "answer": "Refunds are available within 7 days with a receipt.",
                "contexts": ["Refunds are available within 7 days with a receipt."],
            },
        )

    route.side_effect = _side_effect

    cfg = load_config(FIXTURES / "sample.yml")
    cfg.output.dir = str(tmp_path / "out")
    cfg.output.terminal = False

    summary, results = await run_audit(cfg, base_dir=FIXTURES)
    assert len(results) == 2
    assert summary.total_cases == 2
    assert "faithfulness" in summary.metric_aggregates
    assert summary.judge_calls >= 1
    assert summary.judge_usage.total_tokens > 0
    assert summary.judge_usage.estimated is True  # mock judge
    assert (tmp_path / "out" / "auditai-report.json").exists()
    assert (tmp_path / "out" / "auditai-report.md").exists()
    report = (tmp_path / "out" / "auditai-report.json").read_text()
    assert "judge_usage" in report
    assert "prompt_tokens" in report
