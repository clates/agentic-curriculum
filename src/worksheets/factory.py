"""Factory for creating worksheet instances from JSON payloads."""
from __future__ import annotations

from typing import Any, Callable

from .base import BaseWorksheet
from .two_operand import (
    Worksheet,
    generate_two_operand_math_worksheet,
)
from .reading_comprehension import (
    ReadingWorksheet,
    generate_reading_comprehension_worksheet,
)


def _create_two_operand(payload: dict[str, Any]) -> Worksheet:
    """Create a two-operand math worksheet from payload."""
    return generate_two_operand_math_worksheet(
        problems=payload.get("problems", []),
        title=payload.get("title", "Two-Operand Practice"),
        instructions=payload.get("instructions", "Solve each problem. Show your work if needed."),
        metadata=payload.get("metadata"),
    )


def _create_reading_comprehension(payload: dict[str, Any]) -> ReadingWorksheet:
    """Create a reading comprehension worksheet from payload."""
    return generate_reading_comprehension_worksheet(
        passage_title=payload.get("passage_title", ""),
        passage=payload.get("passage", ""),
        questions=payload.get("questions", []),
        vocabulary=payload.get("vocabulary"),
        title=payload.get("title", "Reading Comprehension"),
        instructions=payload.get(
            "instructions",
            "Read the passage carefully, then answer the questions and review the vocabulary.",
        ),
        metadata=payload.get("metadata"),
    )


class WorksheetFactory:
    """Factory class for dispatching JSON requests to the correct worksheet renderer."""

    _registry: dict[str, Callable[[dict[str, Any]], BaseWorksheet]] = {
        "two_operand": _create_two_operand,
        "reading_comprehension": _create_reading_comprehension,
    }

    @classmethod
    def create(cls, worksheet_type: str, payload: dict[str, Any]) -> BaseWorksheet:
        """Create a worksheet instance based on the type field in the payload.

        Args:
            worksheet_type: The type of worksheet to create ("two_operand" or "reading_comprehension").
            payload: Dictionary containing worksheet configuration.

        Returns:
            A worksheet instance (Worksheet or ReadingWorksheet).

        Raises:
            ValueError: If the worksheet type is not supported.
        """
        creator = cls._registry.get(worksheet_type)
        if creator is None:
            raise ValueError(f"Unsupported worksheet type: {worksheet_type}")
        return creator(payload)

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Return a list of supported worksheet types."""
        return list(cls._registry.keys())

    @classmethod
    def register(
        cls, worksheet_type: str, creator: Callable[[dict[str, Any]], BaseWorksheet]
    ) -> None:
        """Register a new worksheet type.

        Args:
            worksheet_type: The type identifier for the worksheet.
            creator: A callable that takes a payload dict and returns a worksheet.
        """
        cls._registry[worksheet_type] = creator


__all__ = [
    "WorksheetFactory",
]
