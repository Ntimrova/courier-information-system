"""Спільні схеми: пагінація, помилки, валідатори полів."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

T = TypeVar("T")

#: Телефон у міжнародному форматі: необов'язковий "+" і 10-15 цифр.
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")

#: Символи, які люди вставляють для краси і які ми прибираємо перед перевіркою.
_PHONE_NOISE = re.compile(r"[\s()\-.]")


def normalize_phone(value: Any) -> Any:
    """Прибирає пробіли й дужки, залишаючи чистий номер.

    Приклад: "+38 (067) 123-45-67" перетворюється на "+380671234567".
    """
    if not isinstance(value, str):
        return value
    cleaned = _PHONE_NOISE.sub("", value.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    return cleaned


def strip_text(value: Any) -> Any:
    """Прибирає зайві пробіли по краях тексту."""
    if isinstance(value, str):
        return value.strip()
    return value


def validate_phone(value: Any) -> Any:
    """Перевіряє формат телефону після нормалізації."""
    value = normalize_phone(value)
    if isinstance(value, str) and not PHONE_PATTERN.match(value):
        raise ValueError("Телефон має містити від 10 до 15 цифр, наприклад +380671234567")
    return value


Phone = Annotated[str, BeforeValidator(validate_phone), Field(max_length=32)]
TrimmedStr = Annotated[str, BeforeValidator(strip_text)]


class PageMeta(BaseModel):
    """Метадані сторінки для серверної пагінації."""

    page: int = Field(ge=1, examples=[1])
    page_size: int = Field(ge=1, examples=[20])
    total: int = Field(ge=0, examples=[137])
    total_pages: int = Field(ge=0, examples=[7])


class PaginatedResponse(BaseModel, Generic[T]):
    """Стандартна відповідь для списків."""

    items: Sequence[T]
    meta: PageMeta

    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str = Field(examples=["VALIDATION_ERROR"])
    message: str = Field(examples=["Дані не пройшли перевірку"])
    details: Any = None


class ErrorResponse(BaseModel):
    """Єдиний формат помилки API."""

    error: ErrorDetail


class MessageResponse(BaseModel):
    """Проста текстова відповідь."""

    message: str


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    version: str
    database: str = Field(examples=["ok"])
