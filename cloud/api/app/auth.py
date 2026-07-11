from __future__ import annotations

import hashlib
import secrets

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project


def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    # aai_ + 32 bytes urlsafe
    return "aai_" + secrets.token_urlsafe(32)


def extract_bearer(authorization: str | None, x_auditai_key: str | None) -> str:
    if x_auditai_key:
        return x_auditai_key.strip()
    if authorization:
        parts = authorization.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip()
        # allow raw key in Authorization
        return authorization.strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API key. Use Authorization: Bearer <AUDITAI_PROJECT_KEY> or X-AuditAI-Key.",
    )


def get_current_project(
    authorization: str | None = Header(default=None),
    x_auditai_key: str | None = Header(default=None, alias="X-AuditAI-Key"),
    db: Session = Depends(get_db),
) -> Project:
    raw = extract_bearer(authorization, x_auditai_key)
    key_hash = hash_api_key(raw)
    project = db.query(Project).filter(Project.api_key_hash == key_hash).one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid project key")
    return project
