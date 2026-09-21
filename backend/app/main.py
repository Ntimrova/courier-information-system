"""Точка входу FastAPI-застосунку."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.database.session import engine
from app.schemas.common import HealthResponse

DESCRIPTION = """
API інформаційної системи локальної кур'єрської компанії (частина 1).

Реалізовано: авторизація з ролями, управління користувачами, замовлення,
історія статусів і зведення для головної сторінки.

Авторизація: отримайте токен у `POST /api/v1/auth/login` і натисніть
**Authorize** угорі, ввівши сам токен.
"""


def create_app() -> FastAPI:
    """Створює і налаштовує застосунок."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", response_model=HealthResponse, tags=["Service"], summary="Перевірка стану")
    def health() -> HealthResponse:
        """Показує, що сервіс живий і бачить базу даних."""
        database_status = "ok"
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception:  # pragma: no cover - залежить від оточення
            database_status = "unavailable"
        return HealthResponse(
            status="ok", version=settings.app_version, database=database_status
        )

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
