"""Схеми користувачів."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.core.enums import UserRole
from app.schemas.common import Phone, TrimmedStr

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class UserBase(BaseModel):
    first_name: TrimmedStr = Field(min_length=2, max_length=80, examples=["Олена"])
    last_name: TrimmedStr = Field(min_length=2, max_length=80, examples=["Ковальчук"])
    email: EmailStr = Field(max_length=255, examples=["olena@example.com"])
    phone: Phone = Field(examples=["+380671234567"])


class UserCreate(UserBase):
    """Створення користувача адміністратором."""

    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_active: bool = True


class UserRegister(UserBase):
    """Самостійна реєстрація. Роль завжди CUSTOMER."""

    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class UserUpdate(BaseModel):
    """Часткове оновлення користувача."""

    first_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=80)
    last_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=80)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: Phone | None = None
    role: UserRole | None = None
    password: str | None = Field(
        default=None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class UserStatusUpdate(BaseModel):
    """Блокування або активація облікового запису."""

    is_active: bool


class UserProfileUpdate(BaseModel):
    """Редагування власного профілю (без зміни ролі)."""

    first_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=80)
    last_name: TrimmedStr | None = Field(default=None, min_length=2, max_length=80)
    phone: Phone | None = None
    password: str | None = Field(
        default=None, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class UserRead(BaseModel):
    """Публічне представлення користувача. Хеш пароля ніколи не віддається."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class UserShort(BaseModel):
    """Скорочений користувач для вкладення в інші відповіді."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: UserRole

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
