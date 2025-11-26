"""Base worksheet classes and interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseWorksheet(ABC):
    """Abstract base class for all worksheet types."""

    @abstractmethod
    def to_markdown(self) -> str:
        """Return a Markdown representation of the worksheet."""
        ...


__all__ = [
    "BaseWorksheet",
]
