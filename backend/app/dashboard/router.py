"""Ендпоінт dashboard."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Зведення для головної сторінки",
    description="Для ADMIN і DISPATCHER рахуються всі замовлення, "
    "для CUSTOMER - лише власні. Дані беруться напряму з PostgreSQL.",
)
def dashboard_summary(session: DbSession, current_user: CurrentUser) -> DashboardSummary:
    return DashboardService(session).summary(current_user)
