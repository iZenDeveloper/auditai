"""Unit tests for guerrilla_prep helpers (no network)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "guerrilla_prep", ROOT / "scripts" / "gtm" / "guerrilla_prep.py"
)
assert SPEC and SPEC.loader
gp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gp)


def test_extract_skips_badge_noise():
    readme = """
# My RAG

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)

This project is a multi-tenant RAG platform for enterprise knowledge retrieval
with hybrid search and strict tenant isolation on shared infrastructure.

## Overview

More prose here about how the system routes browser traffic through a Next.js
proxy so tokens never sit in the client, then hits FastAPI for retrieval.
"""
    chunks = gp.extract_readme_snippets(readme, max_chunks=8)
    assert chunks
    blob = " ".join(chunks).lower()
    assert "shields.io" not in blob
    assert "multi-tenant" in blob or "rag" in blob


def test_mock_adapter_emits_empty_contexts(tmp_path):
    out = tmp_path / "mock_adapter.py"
    gp.write_mock_adapter(out, "seed context about refunds within 7 days")
    src = out.read_text(encoding="utf-8")
    assert '"contexts": []' in src or '"contexts":[]' in src
    assert "empty" in src.lower() or "dataset" in src.lower()
