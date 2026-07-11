"""Unit tests for guerrilla_prep helpers (no network)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "guerrilla_prep", ROOT / "scripts" / "gtm" / "guerrilla_prep.py"
)
assert SPEC and SPEC.loader
gp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gp)


SAMPLE_README = """
# Vietnam Labor Law RAG

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about
Vietnam's 2019 Labor Code (Bộ luật Lao động 2019), built with a hybrid
retrieval pipeline, query rewriting, semantic routing, and Self-RAG.

## Architecture

Instead of a single embed retrieve generate step, the pipeline adds three layers
of reasoning to improve accuracy on legal text, where precision matters.

## Features

| Component | Purpose |
|---|---|
| Query Rewriting | Converts colloquial questions into precise legal queries |
| Semantic Router | Filters out-of-scope questions before retrieval |
| Hybrid Retrieval | Combines BM25 and vector search for legal terminology |

## Tech Stack

- LLM: Groq (Llama 3.1 8B)
- Framework: LangChain
- Vector Store: ChromaDB
- Embeddings: vietnamese-sbert
"""


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
    chunks = gp.extract_text_snippets(readme, max_chunks=8)
    assert chunks
    blob = " ".join(chunks).lower()
    assert "shields.io" not in blob
    assert "multi-tenant" in blob or "rag" in blob


def test_extract_tables_and_many_chunks():
    chunks = gp.extract_text_snippets(SAMPLE_README, max_chunks=40)
    assert len(chunks) >= 4
    blob = " ".join(chunks).lower()
    assert "labor" in blob or "lao động" in blob or "hybrid" in blob
    assert "query rewriting" in blob or "bm25" in blob or "chromadb" in blob


def test_suggest_questions_no_todo_by_default():
    chunks = gp.extract_text_snippets(SAMPLE_README, max_chunks=40)
    cases = gp.suggest_questions(chunks, 20, pad_todos=False, max_per_chunk=3)
    todos = [c for c in cases if str(c.get("id", "")).startswith("todo")]
    assert not todos
    assert len(cases) >= 8  # 2 injection + several real
    assert any(c.get("category") == "prompt_injection" for c in cases)
    # all non-injection have real contexts from docs
    for c in cases:
        if c.get("category") == "prompt_injection":
            continue
        assert c.get("contexts")
        assert "TODO" not in c["question"]


def test_suggest_questions_pad_todos_optional():
    cases = gp.suggest_questions(["short chunk about rag only once"], 10, pad_todos=True)
    assert any(str(c["id"]).startswith("todo") for c in cases)


def test_mock_adapter_emits_empty_contexts(tmp_path):
    out = tmp_path / "mock_adapter.py"
    gp.write_mock_adapter(out, "seed context about refunds within 7 days")
    src = out.read_text(encoding="utf-8")
    assert '"contexts": []' in src or '"contexts":[]' in src
    assert "weak" in src.lower() or "intentionally" in src.lower() or "empty" in src.lower()


def test_collect_public_docs(tmp_path):
    (tmp_path / "README.md").write_text(SAMPLE_README, encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text(
        "Extra guide about indexing labor code articles into Chroma for retrieval.\n" * 3,
        encoding="utf-8",
    )
    corpus = gp.collect_public_docs(tmp_path)
    assert "FILE: README.md" in corpus or "Labor" in corpus
    assert "guide.md" in corpus or "indexing labor" in corpus.lower()
