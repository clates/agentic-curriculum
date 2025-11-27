"""Factory for creating worksheet instances from JSON payloads."""

from __future__ import annotations

from typing import Any, Callable

from .base import BaseWorksheet
from .two_operand import (
    MathWorksheet,
    generate_two_operand_math_worksheet,
)
from .reading_comprehension import (
    ReadingWorksheet,
    generate_reading_comprehension_worksheet,
)
from .venn_diagram import (
    VennDiagramWorksheet,
    generate_venn_diagram_worksheet,
)
from .feature_matrix import (
    FeatureMatrixWorksheet,
    generate_feature_matrix_worksheet,
)
from .odd_one_out import (
    OddOneOutWorksheet,
    generate_odd_one_out_worksheet,
)
from .tree_map import (
    TreeMapWorksheet,
    generate_tree_map_worksheet,
)


def _create_two_operand(payload: dict[str, Any]) -> MathWorksheet:
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


def _create_venn_diagram(payload: dict[str, Any]) -> VennDiagramWorksheet:
    """Create a Venn diagram worksheet from payload."""
    return generate_venn_diagram_worksheet(
        left_label=payload.get("left_label", ""),
        right_label=payload.get("right_label", ""),
        both_label=payload.get("both_label", "Both"),
        word_bank=payload.get("word_bank", []),
        left_items=payload.get("left_items", []),
        right_items=payload.get("right_items", []),
        both_items=payload.get("both_items", []),
        title=payload.get("title", "Venn Diagram"),
        instructions=payload.get(
            "instructions",
            "Sort the words from the word bank into the correct section of the Venn diagram.",
        ),
        metadata=payload.get("metadata"),
    )


def _create_feature_matrix(payload: dict[str, Any]) -> FeatureMatrixWorksheet:
    """Create a feature matrix worksheet from payload."""
    return generate_feature_matrix_worksheet(
        items=payload.get("items", []),
        properties=payload.get("properties", []),
        title=payload.get("title", "Feature Matrix"),
        instructions=payload.get("instructions", "Check the boxes that apply to each item."),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_odd_one_out(payload: dict[str, Any]) -> OddOneOutWorksheet:
    """Create an odd-one-out worksheet from payload."""
    return generate_odd_one_out_worksheet(
        rows=payload.get("rows", []),
        title=payload.get("title", "Odd One Out"),
        instructions=payload.get(
            "instructions",
            "Look at each row. Circle the item that does not belong and explain why.",
        ),
        show_answers=payload.get("show_answers", False),
        reasoning_lines=payload.get("reasoning_lines", 2),
        metadata=payload.get("metadata"),
    )


def _create_tree_map(payload: dict[str, Any]) -> TreeMapWorksheet:
    """Create a tree map worksheet from payload."""
    return generate_tree_map_worksheet(
        root_label=payload.get("root_label", ""),
        branches=payload.get("branches", []),
        word_bank=payload.get("word_bank", []),
        title=payload.get("title", "Tree Map"),
        instructions=payload.get(
            "instructions",
            "Fill in the tree map by writing words from the word bank in the correct category.",
        ),
        metadata=payload.get("metadata"),
    )


class WorksheetFactory:
    """Factory class for dispatching JSON requests to the correct worksheet renderer."""

    _registry: dict[str, Callable[[dict[str, Any]], BaseWorksheet]] = {
        "two_operand": _create_two_operand,
        "reading_comprehension": _create_reading_comprehension,
        "venn_diagram": _create_venn_diagram,
        "feature_matrix": _create_feature_matrix,
        "odd_one_out": _create_odd_one_out,
        "tree_map": _create_tree_map,
    }

    @classmethod
    def create(cls, worksheet_type: str, payload: dict[str, Any]) -> BaseWorksheet:
        """Create a worksheet instance based on the type field in the payload.

        Args:
            worksheet_type: The type of worksheet to create.
            payload: Dictionary containing worksheet configuration.

        Returns:
            A worksheet instance.

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
