"""Load test datasets from JSON / JSONL / CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from auditai.config import AuditConfig, CsvMapConfig
from auditai.errors import DatasetError
from auditai.models import AuditCase, CaseCategory


def load_dataset(cfg: AuditConfig, base_dir: Path | None = None) -> list[AuditCase]:
    base = base_dir or Path(cfg.config_path).parent
    path = Path(cfg.dataset.path)
    if not path.is_absolute():
        path = (base / path).resolve()

    if not path.exists():
        raise DatasetError(f"dataset not found: {path}")

    if path.stat().st_size > 5 * 1024 * 1024:
        raise DatasetError(f"dataset too large (>5MB): {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        cases = _load_json(path)
    elif suffix == ".jsonl":
        cases = _load_jsonl(path)
    elif suffix == ".csv":
        cases = _load_csv(path, cfg.dataset.csv)
    else:
        raise DatasetError(f"unsupported dataset format: {suffix} (use .json, .jsonl, .csv)")

    if not cases:
        raise DatasetError(f"dataset is empty: {path}")

    if len(cases) > cfg.run.max_cases:
        raise DatasetError(
            f"dataset has {len(cases)} cases; max is {cfg.run.max_cases} "
            "(raise run.max_cases if intentional)"
        )

    return cases


def _parse_case(raw: dict[str, Any], idx: int) -> AuditCase:
    if "question" not in raw and "input" not in raw:
        raise DatasetError(f"case #{idx} missing 'question'")

    cid = str(raw.get("id") or f"case-{idx}")
    question = str(raw.get("question") or raw.get("input"))
    contexts = raw.get("contexts") or raw.get("retrieval_context") or []
    if isinstance(contexts, str):
        contexts = _split_contexts(contexts)

    cat_raw = raw.get("category", "general")
    try:
        category = CaseCategory(str(cat_raw))
    except ValueError:
        category = CaseCategory.general

    should_refuse = raw.get("should_refuse", False)
    if isinstance(should_refuse, str):
        should_refuse = should_refuse.strip().lower() in {"1", "true", "yes", "y"}

    return AuditCase(
        id=cid,
        question=question,
        contexts=list(contexts) if contexts else [],
        expected_answer=raw.get("expected_answer"),
        expected_keywords=list(raw.get("expected_keywords") or []),
        category=category,
        should_refuse=bool(should_refuse),
        metadata=dict(raw.get("metadata") or {}),
    )


def _split_contexts(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except json.JSONDecodeError:
            pass
    if "|||" in value:
        return [p.strip() for p in value.split("|||") if p.strip()]
    return [value]


def _load_json(path: Path) -> list[AuditCase]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DatasetError(f"invalid JSON dataset: {e}") from e

    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    if not isinstance(data, list):
        raise DatasetError("JSON dataset must be a list of cases or {\"cases\": [...]}")

    return [_parse_case(item, i) for i, item in enumerate(data, start=1)]


def _load_jsonl(path: Path) -> list[AuditCase]:
    cases: list[AuditCase] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            raise DatasetError(f"invalid JSONL at line {i}: {e}") from e
        cases.append(_parse_case(item, i))
    return cases


def _load_csv(path: Path, mapping: CsvMapConfig) -> list[AuditCase]:
    cases: list[AuditCase] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            raw: dict[str, Any] = {
                "id": row.get(mapping.id) or f"case-{i}",
                "question": row.get(mapping.question, ""),
                "contexts": row.get(mapping.contexts, ""),
                "category": row.get(mapping.category, "general"),
                "should_refuse": row.get(mapping.should_refuse, False),
                "expected_answer": row.get(mapping.expected_answer),
            }
            cases.append(_parse_case(raw, i))
    return cases
