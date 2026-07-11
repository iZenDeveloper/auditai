"""Typed exceptions and exit-code mapping."""

from __future__ import annotations


class AuditAIError(Exception):
    """Base error for AuditAI."""


class ConfigError(AuditAIError):
    """Invalid configuration or missing files (exit 2)."""


class AuthError(AuditAIError):
    """Missing or invalid judge API credentials (exit 2)."""


class DatasetError(AuditAIError):
    """Dataset load/parse failures (exit 2)."""


class TargetError(AuditAIError):
    """Per-case target invocation failure."""


class JudgeError(AuditAIError):
    """LLM-as-judge call failure."""


class InternalError(AuditAIError):
    """Unexpected internal failure (exit 3)."""


# Exit codes (stable contract for CI / GitHub Action)
EXIT_PASS = 0
EXIT_AUDIT_FAILED = 1
EXIT_USER_ERROR = 2
EXIT_INTERNAL = 3
