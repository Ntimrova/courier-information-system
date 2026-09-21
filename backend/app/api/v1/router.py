"""Збірка всіх роутерів версії v1."""

from __future__ import annotations

from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.dashboard.router import router as dashboard_router
from app.orders.router import router as orders_router
from app.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(orders_router)
api_router.include_router(dashboard_router)
