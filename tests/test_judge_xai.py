"""xAI / OpenAI-compatible judge config and factory."""

from __future__ import annotations

from pathlib import Path

import pytest

from auditai.config import JudgeConfig, load_config, ensure_judge_auth
from auditai.errors import AuthError, JudgeError
from auditai.judge.factory import create_judge
from auditai.judge.openai_judge import OpenAIJudge, resolve_judge_credentials

FIXTURES = Path(__file__).parent / "fixtures"


def test_xai_auth_requires_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    cfg = load_config(FIXTURES / "sample.yml")
    # force xai on a copy of judge
    cfg.judge.provider = "xai"
    cfg.judge.model = "grok-3-mini"
    with pytest.raises(AuthError, match="XAI_API_KEY"):
        ensure_judge_auth(cfg)


def test_xai_auth_ok(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test-key-not-real")
    cfg = load_config(FIXTURES / "sample.yml")
    cfg.judge.provider = "xai"
    ensure_judge_auth(cfg)  # no raise


def test_xai_resolve_defaults(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    cfg = JudgeConfig(provider="xai")  # model defaults to gpt-4o-mini in schema
    key, base_url, model, provider = resolve_judge_credentials(cfg)
    assert provider == "xai"
    assert key == "xai-test"
    assert base_url == "https://api.x.ai/v1"
    assert model == "grok-4.3"


def test_xai_explicit_model(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    cfg = JudgeConfig(provider="xai", model="grok-3")
    _, _, model, _ = resolve_judge_credentials(cfg)
    assert model == "grok-3"


def test_openai_custom_base_url(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    cfg = JudgeConfig(
        provider="openai",
        model="my-proxy-model",
        base_url="https://proxy.example/v1",
        api_key_env="OPENAI_API_KEY",
    )
    key, base_url, model, provider = resolve_judge_credentials(cfg)
    assert provider == "openai"
    assert base_url == "https://proxy.example/v1"
    assert model == "my-proxy-model"
    assert key == "sk-test"


def test_custom_api_key_env(monkeypatch):
    monkeypatch.setenv("MY_GROK_KEY", "custom-secret")
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    cfg = JudgeConfig(
        provider="xai",
        model="grok-3-mini",
        api_key_env="MY_GROK_KEY",
    )
    key, _, _, _ = resolve_judge_credentials(cfg)
    assert key == "custom-secret"

    # ensure_judge_auth uses same env name
    from auditai.config import AuditConfig, TargetConfig, DatasetConfig

    audit = AuditConfig(
        target=TargetConfig(url="http://localhost/chat"),
        dataset=DatasetConfig(path="./d.json"),
        judge=cfg,
    )
    ensure_judge_auth(audit)


def test_create_judge_xai(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    judge = create_judge(JudgeConfig(provider="xai", model="grok-4.3"))
    assert isinstance(judge, OpenAIJudge)
    assert judge.provider == "xai"
    assert judge.model == "grok-4.3"
    assert judge._base_url == "https://api.x.ai/v1"
    snap = judge.usage_snapshot()
    assert snap.total_tokens == 0
    assert snap.estimated is False


def test_missing_key_raises_judge_error(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(JudgeError, match="XAI_API_KEY"):
        OpenAIJudge(JudgeConfig(provider="xai"))
