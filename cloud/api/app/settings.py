from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUDITAI_CLOUD_", env_file=".env", extra="ignore")

    app_name: str = "AuditAI Cloud"
    # sqlite:///./auditai_cloud.db  |  postgresql+psycopg://user:pass@host/db
    database_url: str = "sqlite:///./auditai_cloud.db"
    # If true, POST /v1/projects is open (local dev). Disable in production.
    allow_public_project_create: bool = True
    # Optional bootstrap admin token for project creation when public create is off
    admin_token: str = ""
    cors_origins: str = "*"
    host: str = "0.0.0.0"
    port: int = 8080


settings = Settings()
