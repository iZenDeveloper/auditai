from __future__ import annotations

from auditai.config import JudgeConfig
from auditai.errors import ConfigError
from auditai.judge.base import Judge
from auditai.judge.mock_judge import MockJudge
from auditai.judge.openai_judge import OpenAIJudge


def create_judge(config: JudgeConfig) -> Judge:
    if config.provider == "mock":
        return MockJudge(config)
    if config.provider in ("openai", "xai"):
        return OpenAIJudge(config)
    if config.provider == "anthropic":
        raise ConfigError(
            "judge.provider=anthropic is reserved for a later release; "
            "use openai, xai (Grok), or mock"
        )
    raise ConfigError(f"unknown judge provider: {config.provider}")
