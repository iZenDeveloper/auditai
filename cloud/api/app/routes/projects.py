from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import generate_api_key, get_current_project, hash_api_key
from app.db import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectCreated, ProjectInfo
from app.settings import settings

router = APIRouter(prefix="/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectCreated, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> ProjectCreated:
    if not settings.allow_public_project_create:
        if not settings.admin_token or x_admin_token != settings.admin_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project create disabled")

    raw_key = generate_api_key()
    project = Project(
        name=body.name.strip(),
        api_key_hash=hash_api_key(raw_key),
        api_key_prefix=raw_key[:12],
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectCreated(
        id=project.id,
        name=project.name,
        api_key=raw_key,
        api_key_prefix=project.api_key_prefix,
        created_at=project.created_at,
    )


@router.get("/me", response_model=ProjectInfo)
def project_me(project: Project = Depends(get_current_project)) -> ProjectInfo:
    return ProjectInfo(
        id=project.id,
        name=project.name,
        api_key_prefix=project.api_key_prefix,
        created_at=project.created_at,
    )
