"""Typed validation for non-secret local platform configuration."""

from enum import StrEnum
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment-environment names."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class PlatformSettings(BaseSettings):
    """Validate configuration without storing or rendering credentials."""

    model_config = SettingsConfigDict(env_prefix="PLATFORM_", extra="forbid")

    environment: Environment
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_username: str
    redis_host: str
    redis_port: int

    @field_validator("postgres_host", "postgres_database", "postgres_username", "redis_host")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        """Reject missing and whitespace-only required values."""
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("postgres_port", "redis_port")
    @classmethod
    def require_network_port(cls, value: int) -> int:
        """Accept only valid TCP/UDP port ranges."""
        if not 1 <= value <= 65_535:
            raise ValueError("must be between 1 and 65535")
        return value

    def safe_summary(self) -> str:
        """Return a diagnostic summary that intentionally excludes credentials."""
        return (
            f"environment={self.environment}; log_level={self.log_level}; "
            f"postgres={self.postgres_host}:{self.postgres_port}/{self.postgres_database}; "
            f"redis={self.redis_host}:{self.redis_port}"
        )
