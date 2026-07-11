from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("AUDITAI_CLOUD_DATABASE_URL", f"sqlite:///{db_path}")
    # Re-import app with new settings is hard; patch engine after import
    from app import db as dbmod
    from app import settings as settings_mod
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    settings_mod.settings.database_url = f"sqlite:///{db_path}"
    engine = create_engine(
        settings_mod.settings.database_url,
        connect_args={"check_same_thread": False},
    )
    dbmod.engine = engine
    dbmod.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    dbmod.Base.metadata.create_all(bind=engine)

    from app.main import app

    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_project_and_run_flow(client: TestClient):
    r = client.post("/v1/projects", json={"name": "demo"})
    assert r.status_code == 201
    data = r.json()
    key = data["api_key"]
    assert key.startswith("aai_")

    headers = {"Authorization": f"Bearer {key}"}
    me = client.get("/v1/projects/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["name"] == "demo"

    ingest = {
        "schema_version": "0.1",
        "client_version": "0.1.0",
        "run_id": "run-abc",
        "overall_passed": False,
        "exit_reason": "metric_below_threshold:faithfulness",
        "total_cases": 6,
        "failed_cases": 0,
        "judge_calls": 10,
        "aggregates": {
            "faithfulness": {"mean": 0.72, "threshold": 0.8, "passed": False, "n_scored": 4},
            "answer_relevancy": {"mean": 0.85, "threshold": 0.75, "passed": True, "n_scored": 4},
            "prompt_injection": {"mean": 1.0, "threshold": 0.9, "passed": True, "n_scored": 2},
        },
        "top_failures": [
            {
                "case_id": "hallucinate",
                "metric": "faithfulness",
                "score": 0.2,
                "question": "refund?",
                "answer": "",
            }
        ],
        "metadata": {"git_sha": "deadbeef", "repo": "acme/rag"},
    }
    r2 = client.post("/v1/runs", json=ingest, headers=headers)
    assert r2.status_code == 201
    run = r2.json()
    assert run["overall_passed"] is False
    assert run["faithfulness_mean"] == pytest.approx(0.72)
    assert run["client_run_id"] == "run-abc"

    # idempotent on same client run_id
    r3 = client.post("/v1/runs", json=ingest, headers=headers)
    assert r3.status_code == 201
    assert r3.json()["id"] == run["id"]

    listed = client.get("/v1/runs", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(f"/v1/runs/{run['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["payload"]["exit_reason"].startswith("metric_below")


def test_unauthorized(client: TestClient):
    r = client.get("/v1/runs")
    assert r.status_code == 401


def test_compliance_pdf(client: TestClient):
    r = client.post("/v1/projects", json={"name": "pdf-demo"})
    key = r.json()["api_key"]
    headers = {"Authorization": f"Bearer {key}"}
    ingest = {
        "run_id": "run-pdf",
        "overall_passed": False,
        "exit_reason": "metric_below_threshold:faithfulness",
        "total_cases": 4,
        "aggregates": {
            "faithfulness": {"mean": 0.7, "threshold": 0.8, "passed": False, "n_scored": 4},
        },
        "top_failures": [
            {"case_id": "x", "metric": "faithfulness", "score": 0.1, "question": "q"}
        ],
        "metadata": {"git_sha": "abc123", "repo": "acme/bot"},
    }
    run = client.post("/v1/runs", json=ingest, headers=headers).json()
    pdf = client.get(f"/v1/runs/{run['id']}/compliance.pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content[:4] == b"%PDF"
    assert len(pdf.content) > 500
