# AuditAI Cloud API (stub)

Lightweight FastAPI service that **stores audit run metrics** pushed by the CLI when `AUDITAI_PROJECT_KEY` is set.

## Design principles

| Principle | Implementation |
|-----------|----------------|
| Zero GPU / BYOK stays client-side | Server never calls OpenAI |
| Low privacy liability | Default CLI payload **strips answers** |
| Cheap ops | SQLite by default; `DATABASE_URL` for Postgres later |
| CI never blocked by cloud | CLI `fail_open: true` by default |

## Quick start

```bash
cd cloud/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

Or:

```bash
cd cloud
docker compose up --build
```

## Bootstrap a project key

```bash
curl -s -X POST http://127.0.0.1:8080/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-rag-app"}' | jq
# → { "id": "...", "api_key": "aai_...", ... }  # save api_key once
```

```bash
export AUDITAI_PROJECT_KEY='aai_...'
export AUDITAI_API_URL='http://127.0.0.1:8080'
auditai run --config auditai.yml
```

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness |
| POST | `/v1/projects` | optional admin | Create project + API key |
| GET | `/v1/projects/me` | project key | Project info |
| POST | `/v1/runs` | project key | Ingest run |
| GET | `/v1/runs` | project key | List runs |
| GET | `/v1/runs/{id}` | project key | Run detail + payload |
| GET | `/v1/runs/{id}/compliance.pdf` | project key | AI safety audit certificate PDF |

Auth header: `Authorization: Bearer <key>` or `X-AuditAI-Key: <key>`.

## Env

| Variable | Default | Notes |
|----------|---------|-------|
| `AUDITAI_CLOUD_DATABASE_URL` | `sqlite:///./auditai_cloud.db` | SQLAlchemy URL |
| `AUDITAI_CLOUD_ALLOW_PUBLIC_PROJECT_CREATE` | `true` | Set `false` in prod |
| `AUDITAI_CLOUD_ADMIN_TOKEN` | `` | Required for create when public is off |
| `AUDITAI_CLOUD_PORT` | `8080` | |

## Dashboard

Minimal Next.js UI lives in [`../dashboard`](../dashboard):

```bash
cd ../dashboard && npm install && npm run dev
```

## Not in this stub

- Multi-user login / teams
- Compliance PDF export
- Billing
- Long-term retention policies
