"""Unit tests for open_guerrilla_pr helpers (no network)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "open_guerrilla_pr", ROOT / "scripts" / "gtm" / "open_guerrilla_pr.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_patch_judge_yml(tmp_path: Path):
    yml = tmp_path / "auditai.yml"
    yml.write_text(
        """version: "0.1"
target:
  type: http
  url: http://127.0.0.1:18080/chat
judge:
  provider: mock
  model: "mock"
  temperature: 0
run:
  concurrency: 2
""",
        encoding="utf-8",
    )
    mod.patch_judge_yml(yml, "xai", "grok-4.3")
    text = yml.read_text(encoding="utf-8")
    assert "provider: xai" in text
    assert 'model: "grok-4.3"' in text
    assert "concurrency: 2" in text
    # did not rewrite target type
    assert "type: http" in text


def test_repo_slug():
    assert mod.repo_slug("a/b") == ("a", "b")
    try:
        mod.repo_slug("bad")
        assert False
    except mod.StepError:
        pass


def test_default_model():
    assert mod.default_model("xai") == "grok-4.3"
    assert mod.default_model("openai") == "gpt-4o-mini"
    assert mod.default_model("mock") == "mock"


def test_prepare_yml_for_commit_resets_judge(tmp_path: Path):
    yml = tmp_path / "auditai.yml"
    yml.write_text(
        """version: "0.1"
target:
  type: http
  url: "http://127.0.0.1:18080/chat"
judge:
  provider: xai
  model: "grok-4.3"
run:
  concurrency: 2
""",
        encoding="utf-8",
    )
    mod.prepare_yml_for_commit(yml)
    text = yml.read_text(encoding="utf-8")
    assert "provider: mock" in text
    assert 'model: "mock"' in text
    assert "AUDITAI_TARGET_URL" in text
    assert "provider: xai" not in text or text.count("provider: xai") == 0

