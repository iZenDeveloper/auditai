from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.schemas import HealthOut
from app.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    db_kind = "sqlite" if settings.database_url.startswith("sqlite") else "other"
    return HealthOut(status="ok", version=__version__, database=db_kind)
