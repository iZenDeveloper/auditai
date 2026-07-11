from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.db import init_db
from app.routes import health, projects, runs
from app.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Stub Cloud API for AuditAI. Ingest CI/local audit run metrics "
        "(no model files, no customer secrets). BYOK stays on the client."
    ),
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(runs.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "auditai-cloud-api",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
