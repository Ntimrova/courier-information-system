"""Налаштування застосунку, що читаються зі змінних середовища."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфігурація backend.

    Усі значення беруться зі змінних середовища або з файлу `.env`.
    Жодних секретів у коді.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Застосунок ---
    app_name: str = "Courier Information System API"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    api_v1_prefix: str = "/api/v1"

    # --- База даних ---
    database_url: str = Field(
        default="postgresql+psycopg://courier:courier@localhost:5432/courier_db",
        description="SQLAlchemy DSN, наприклад postgresql+psycopg://user:pass@host:5432/db",
    )

    # --- Безпека ---
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 8)

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        description="Список дозволених origin через кому.",
    )

    # --- Початковий адміністратор для seed-скрипта ---
    seed_admin_email: str = Field(default="admin@courier.ua")
    seed_default_password: str = Field(default="Password123!")

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Дозволяє писати в .env звичайний `postgresql://` DSN.

        SQLAlchemy 2 із драйвером psycopg 3 очікує схему
        `postgresql+psycopg://`, тож доповнюємо її автоматично.
        """
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins у вигляді списку."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Кешований доступ до налаштувань."""
    return Settings()


settings = get_settings()
