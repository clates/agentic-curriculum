"""Base worksheet classes and interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


class BaseWorksheet(ABC):
    """Abstract base class for all worksheet types."""

    @abstractmethod
    def to_markdown(self) -> str:
        """Return a Markdown representation of the worksheet."""
        ...


def normalize_entries(
    items: Iterable[Any],
    cls: type[T],
    error: str,
    from_str: Callable[[str], T] | None = None,
) -> list[T]:
    """Coerce items to ``cls``: instances pass through, dicts go through ``cls.from_mapping``,
    strings through ``from_str`` when given. Anything else raises ``TypeError(error)``."""
    normalized: list[T] = []
    for item in items:
        if isinstance(item, cls):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(cls.from_mapping(item))  # type: ignore[attr-defined]
        elif from_str is not None and isinstance(item, str):
            normalized.append(from_str(item))
        else:
            raise TypeError(error)
    return normalized


__all__ = [
    "BaseWorksheet",
]
