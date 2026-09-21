"""Єдиний формат помилок API та їх обробники.

Будь-яка помилка повертається в одному вигляді:

    {
      "error": {
        "code": "ORDER_NOT_FOUND",
        "message": "Замовлення не знайдено",
        "details": null
      }
    }

Так frontend завжди знає, де шукати текст для користувача, і не мусить
розбирати десяток різних форматів.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Базова помилка застосунку з кодом, повідомленням і HTTP-статусом."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "APP_ERROR"
    message: str = "Сталася помилка"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)

    def to_payload(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"
    message = "Ресурс не знайдено"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"
    message = "Конфлікт даних"


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Дані не пройшли перевірку"


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTHENTICATION_ERROR"
    message = "Потрібна авторизація"


class InvalidCredentialsError(AuthenticationError):
    code = "INVALID_CREDENTIALS"
    message = "Неправильний email або пароль"


class InactiveUserError(AuthenticationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "USER_INACTIVE"
    message = "Обліковий запис заблоковано. Зверніться до адміністратора"


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "PERMISSION_DENIED"
    message = "Недостатньо прав для цієї дії"


class BusinessRuleError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "BUSINESS_RULE_VIOLATION"
    message = "Дію заборонено правилами системи"


class InvalidStatusTransitionError(BusinessRuleError):
    code = "INVALID_STATUS_TRANSITION"
    message = "Такий перехід статусу заборонено"


class EmailAlreadyUsedError(ConflictError):
    code = "EMAIL_ALREADY_USED"
    message = "Користувач із таким email уже існує"


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"error": {"code": code, "message": message, "details": details}}),
    )


#: Людські назви типових HTTP-кодів українською.
_HTTP_MESSAGES: dict[int, tuple[str, str]] = {
    400: ("BAD_REQUEST", "Некоректний запит"),
    401: ("AUTHENTICATION_ERROR", "Потрібна авторизація"),
    403: ("PERMISSION_DENIED", "Недостатньо прав для цієї дії"),
    404: ("NOT_FOUND", "Ресурс не знайдено"),
    405: ("METHOD_NOT_ALLOWED", "Метод не підтримується"),
    409: ("CONFLICT", "Конфлікт даних"),
    422: ("VALIDATION_ERROR", "Дані не пройшли перевірку"),
    500: ("INTERNAL_ERROR", "Внутрішня помилка сервера"),
}


def register_exception_handlers(app: FastAPI) -> None:
    """Підключає обробники помилок до застосунку."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in err.get("loc", []) if part != "body"),
                "message": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in exc.errors()
        ]
        return _error_response(
            422,
            "VALIDATION_ERROR",
            "Дані не пройшли перевірку",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, default_message = _HTTP_MESSAGES.get(
            exc.status_code, ("HTTP_ERROR", "Помилка запиту")
        )
        message = exc.detail if isinstance(exc.detail, str) and exc.detail else default_message
        return _error_response(exc.status_code, code, message)

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "Внутрішня помилка сервера",
        )
