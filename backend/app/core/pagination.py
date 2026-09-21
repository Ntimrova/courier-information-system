"""Загальні структури для серверної пагінації та сортування."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass(slots=True)
class PageParams:
    """Параметри сторінки, що приходять із query string."""

    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass(slots=True)
class SortParams:
    """Поле і напрямок сортування."""

    sort_by: str
    sort_order: str = "desc"

    @property
    def descending(self) -> bool:
        return self.sort_order.lower() == "desc"


@dataclass(slots=True)
class Page(Generic[T]):
    """Сторінка результатів разом із загальною кількістю записів."""

    items: Sequence[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
