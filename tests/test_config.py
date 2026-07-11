from pathlib import Path

import pytest

from auditai.config import load_config
from auditai.errors import ConfigError
from auditai.util.env import expand_env, redact_secrets
from auditai.util.jsonpath import get_by_path


FIXTURES = Path(__file__).parent / "fixtures"


def test_load_sample_config(monkeypatch):
    cfg = load_config(FIXTURES / "sample.yml")
    assert cfg.version == "0.1"
    assert cfg.judge.provider == "mock"
    assert cfg.metrics.faithfulness.threshold == 0.80


def test_expand_env(monkeypatch):
    monkeypatch.setenv("FOO_URL", "http://example.com")
    assert expand_env("${FOO_URL}/v1") == "http://example.com/v1"
    assert expand_env("${MISSING:-fallback}") == "fallback"


def test_redact_secrets():
    assert "***" in redact_secrets("Bearer sk-abc123456789")
    assert "sk-***" in redact_secrets("key=sk-abcdefghijklmnop")


def test_jsonpath():
    data = {"data": {"answer": "hi", "contexts": ["a"]}}
    assert get_by_path(data, "data.answer") == "hi"
    assert get_by_path(data, "data.missing") is None


def test_missing_config():
    with pytest.raises(ConfigError):
        load_config("/tmp/does-not-exist-auditai.yml")
