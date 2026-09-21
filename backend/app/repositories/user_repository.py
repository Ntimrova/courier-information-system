"""Доступ до таблиці користувачів. Тільки запити, без бізнес-правил."""

from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.pagination import Page, PageParams, SortParams
from app.models.user import User

#: Поля, за якими дозволено сортувати список користувачів.
USER_SORT_FIELDS: dict[str, object] = {
    "id": User.id,
    "first_name": User.first_name,
    "last_name": User.last_name,
    "email": User.email,
    "phone": User.phone,
    "role": User.role,
    "is_active": User.is_active,
    "created_at": User.created_at,
    "updated_at": User.updated_at,
}


class UserRepository:
    """Репозиторій користувачів."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Читання ---

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.session.execute(stmt).scalar_one_or_none()

    def email_exists(self, email: str, *, exclude_user_id: int | None = None) -> bool:
        stmt = select(func.count()).select_from(User).where(
            func.lower(User.email) == email.strip().lower()
        )
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        return bool(self.session.execute(stmt).scalar_one())

    def count_all(self) -> int:
        return int(self.session.execute(select(func.count()).select_from(User)).scalar_one())

    def count_active(self) -> int:
        stmt = select(func.count()).select_from(User).where(User.is_active.is_(True))
        return int(self.session.execute(stmt).scalar_one())

    def _apply_filters(
        self,
        stmt: Select,
        *,
        search: str | None,
        role: UserRole | None,
        is_active: bool | None,
    ) -> Select:
        if search:
            pattern = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.first_name).like(pattern),
                    func.lower(User.last_name).like(pattern),
                    func.lower(User.email).like(pattern),
                    func.lower(User.phone).like(pattern),
                )
            )
        if role is not None:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active.is_(is_active))
        return stmt

    def list_users(
        self,
        *,
        page: PageParams,
        sort: SortParams,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> Page[User]:
        """Сторінка користувачів із пошуком, фільтрами й сортуванням."""
        count_stmt = self._apply_filters(
            select(func.count()).select_from(User),
            search=search,
            role=role,
            is_active=is_active,
        )
        total = int(self.session.execute(count_stmt).scalar_one())

        column = USER_SORT_FIELDS.get(sort.sort_by, User.created_at)
        order_by = column.desc() if sort.descending else column.asc()  # type: ignore[union-attr]

        stmt = self._apply_filters(
            select(User), search=search, role=role, is_active=is_active
        )
        stmt = stmt.order_by(order_by, User.id.desc()).offset(page.offset).limit(page.limit)
        items = list(self.session.execute(stmt).scalars().all())
        return Page(items=items, total=total, page=page.page, page_size=page.page_size)

    # --- Запис ---

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def commit(self) -> None:
        self.session.commit()
