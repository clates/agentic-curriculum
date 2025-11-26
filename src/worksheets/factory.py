"""Factory for creating worksheet instances from JSON payloads."""
from __future__ import annotations

from typing import Any

from .base import BaseWorksheet
from .two_operand import (
    Worksheet,
    generate_two_operand_math_worksheet,
)
from .reading_comprehension import (
    ReadingWorksheet,
    generate_reading_comprehension_worksheet,
)


class WorksheetFactory:
    """Factory class for dispatching JSON requests to the correct worksheet renderer."""

    _registry: dict[str, type] = {
        "two_operand": Worksheet,
        "reading_comprehension": ReadingWorksheet,
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
        if worksheet_type == "two_operand":
            return generate_two_operand_math_worksheet(
                problems=payload.get("problems", []),
                title=payload.get("title", "Two-Operand Practice"),
                instructions=payload.get("instructions", "Solve each problem. Show your work if needed."),
                metadata=payload.get("metadata"),
            )
        elif worksheet_type == "reading_comprehension":
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
        else:
            raise ValueError(f"Unsupported worksheet type: {worksheet_type}")

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Return a list of supported worksheet types."""
        return list(cls._registry.keys())

    @classmethod
    def register(cls, worksheet_type: str, worksheet_class: type) -> None:
        """Register a new worksheet type.

        Args:
            worksheet_type: The type identifier for the worksheet.
            worksheet_class: The worksheet class to register.
        """
        cls._registry[worksheet_type] = worksheet_class


__all__ = [
    "WorksheetFactory",
]
