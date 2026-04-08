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
from .handwriting import (
    HandwritingWorksheet,
    generate_handwriting_worksheet,
)
from .pixel_copy import (
    PixelCopyWorksheet,
    generate_pixel_copy_worksheet,
)
from .matching import (
    MatchingWorksheet,
    generate_matching_worksheet,
)
from .alphabet import (
    AlphabetWorksheet,
    generate_alphabet_worksheet,
)
from .sequencing import (
    SequencingWorksheet,
    generate_sequencing_worksheet,
)
from .t_chart import (
    TChartWorksheet,
    generate_t_chart_worksheet,
)
from .fill_in_the_blank import (
    FillBlankWorksheet,
    generate_fill_in_the_blank_worksheet,
)
from .word_sort import (
    WordSortWorksheet,
    generate_word_sort_worksheet,
)
from .story_map import (
    StoryMapWorksheet,
    generate_story_map_worksheet,
)
from .number_line import (
    NumberLineWorksheet,
    generate_number_line_worksheet,
)
from .labeled_diagram import (
    LabeledDiagramWorksheet,
    generate_labeled_diagram_worksheet,
)
from .frayer_model import (
    FrayerModelWorksheet,
    generate_frayer_model_worksheet,
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


def _create_handwriting(payload: dict[str, Any]) -> HandwritingWorksheet:
    """Create a handwriting worksheet from payload."""
    return generate_handwriting_worksheet(
        items=payload.get("items", []),
        title=payload.get("title", "Handwriting Practice"),
        instructions=payload.get(
            "instructions", "Look at the picture and practice writing the word on the lines."
        ),
        rows=payload.get("rows", 4),
        cols=payload.get("cols", 2),
        metadata=payload.get("metadata"),
    )


def _create_pixel_copy(payload: dict[str, Any]) -> PixelCopyWorksheet:
    """Create a pixel copy worksheet from payload."""
    return generate_pixel_copy_worksheet(
        image_path=payload.get("image_path", ""),
        title=payload.get("title", "Pixel Copy"),
        instructions=payload.get(
            "instructions", "Look at the colors on the left. Copy them to the grid on the right!"
        ),
        grid_size=payload.get("grid_size", 24),
        metadata=payload.get("metadata"),
    )


def _create_matching(payload: dict[str, Any]) -> MatchingWorksheet:
    """Create a matching worksheet from payload."""
    return generate_matching_worksheet(
        left_items=payload.get("left_items", []),
        right_items=payload.get("right_items", []),
        title=payload.get("title", "Match the Pairs"),
        instructions=payload.get(
            "instructions",
            "Draw a line to match the item on the left with the correct one on the right.",
        ),
        metadata=payload.get("metadata"),
    )


def _create_alphabet(payload: dict[str, Any]) -> AlphabetWorksheet:
    """Create an alphabet worksheet from payload."""
    return generate_alphabet_worksheet(
        letter=payload.get("letter", ""),
        starting_words=payload.get("starting_words", []),
        containing_words=payload.get("containing_words", []),
        character_image_path=payload.get("character_image_path"),
        title=payload.get("title", "Alphabet Practice"),
        instructions=payload.get("instructions", "Practice your letters and reading words!"),
        metadata=payload.get("metadata"),
    )


def _create_sequencing(payload: dict[str, Any]) -> SequencingWorksheet:
    """Create a sequencing worksheet from payload."""
    return generate_sequencing_worksheet(
        activity_name=payload.get("activity_name", "Activity"),
        steps=payload.get("steps", []),
        title=payload.get("title", "Put It in Order!"),
        instructions=payload.get(
            "instructions",
            "Cut out each step below. Paste them in the correct order on another sheet of paper.",
        ),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_t_chart(payload: dict[str, Any]) -> TChartWorksheet:
    """Create a T-chart worksheet from payload."""
    return generate_t_chart_worksheet(
        columns=payload.get("columns", []),
        row_count=payload.get("row_count", 6),
        word_bank=payload.get("word_bank"),
        title=payload.get("title", "T-Chart"),
        instructions=payload.get(
            "instructions",
            "Sort the words from the word bank into the correct column.",
        ),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_fill_in_the_blank(payload: dict[str, Any]) -> FillBlankWorksheet:
    """Create a fill-in-the-blank worksheet from payload."""
    return generate_fill_in_the_blank_worksheet(
        segments=payload.get("segments", []),
        word_bank=payload.get("word_bank"),
        answers=payload.get("answers"),
        title=payload.get("title", "Fill in the Blank"),
        instructions=payload.get(
            "instructions",
            "Use the word bank to fill in the blanks.",
        ),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_word_sort(payload: dict[str, Any]) -> WordSortWorksheet:
    """Create a word sort worksheet from payload."""
    return generate_word_sort_worksheet(
        categories=payload.get("categories", []),
        tiles=payload.get("tiles", []),
        title=payload.get("title", "Word Sort"),
        instructions=payload.get(
            "instructions",
            "Cut out the word tiles below. Sort them into the correct category boxes.",
        ),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_story_map(payload: dict[str, Any]) -> StoryMapWorksheet:
    """Create a story map worksheet from payload."""
    return generate_story_map_worksheet(
        title=payload.get("title", "Story Map"),
        instructions=payload.get(
            "instructions",
            "Fill in each box about the story you read.",
        ),
        story_title_field=payload.get("story_title_field", True),
        fields=payload.get("fields", []),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_number_line(payload: dict[str, Any]) -> NumberLineWorksheet:
    """Create a number line worksheet from payload."""
    return generate_number_line_worksheet(
        title=payload.get("title", "Number Line"),
        instructions=payload.get(
            "instructions", "Fill in the missing numbers on each number line."
        ),
        tasks=payload.get("tasks", []),
        show_answers=payload.get("show_answers", False),
        metadata=payload.get("metadata"),
    )


def _create_labeled_diagram(payload: dict[str, Any]) -> LabeledDiagramWorksheet:
    """Create a labeled diagram worksheet from payload."""
    return generate_labeled_diagram_worksheet(
        title=payload.get("title", "Labeled Diagram"),
        instructions=payload.get("instructions", "Label each part of the diagram."),
        image_path=payload.get("image_path"),
        labels=payload.get("labels", []),
        show_answers=payload.get("show_answers", False),
        word_bank=payload.get("word_bank", True),
        metadata=payload.get("metadata"),
    )


def _create_frayer_model(payload: dict[str, Any]) -> FrayerModelWorksheet:
    """Create a Frayer model worksheet from payload."""
    return generate_frayer_model_worksheet(
        title=payload.get("title", "Frayer Model"),
        instructions=payload.get(
            "instructions", "Fill in each section to show what you know about the word."
        ),
        entries=payload.get("entries", []),
        show_answers=payload.get("show_answers", False),
        quadrant_labels=payload.get("quadrant_labels"),
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
        "handwriting": _create_handwriting,
        "alphabet": _create_alphabet,
        "pixel_copy": _create_pixel_copy,
        "matching": _create_matching,
        "sequencing": _create_sequencing,
        "t_chart": _create_t_chart,
        "fill_in_the_blank": _create_fill_in_the_blank,
        "word_sort": _create_word_sort,
        "number_line": _create_number_line,
        "labeled_diagram": _create_labeled_diagram,
        "frayer_model": _create_frayer_model,
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
