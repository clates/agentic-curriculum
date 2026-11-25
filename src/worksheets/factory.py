"""Factory for creating worksheet instances from JSON payloads."""

from __future__ import annotations

from typing import Any, Callable

from .base import BaseWorksheet
from .two_operand import generate_two_operand_math_worksheet
from .reading_comprehension import generate_reading_comprehension_worksheet
from .venn_diagram import generate_venn_diagram_worksheet
from .feature_matrix import generate_feature_matrix_worksheet
from .odd_one_out import generate_odd_one_out_worksheet
from .tree_map import generate_tree_map_worksheet
from .handwriting import generate_handwriting_worksheet
from .pixel_copy import generate_pixel_copy_worksheet
from .matching import generate_matching_worksheet
from .alphabet import generate_alphabet_worksheet
from .sequencing import generate_sequencing_worksheet
from .t_chart import generate_t_chart_worksheet
from .fill_in_the_blank import generate_fill_in_the_blank_worksheet
from .word_sort import generate_word_sort_worksheet
from .story_map import generate_story_map_worksheet
from .cause_effect import generate_cause_effect_worksheet
from .number_line import generate_number_line_worksheet
from .writing_scaffold import generate_writing_scaffold_worksheet
from .labeled_diagram import generate_labeled_diagram_worksheet
from .frayer_model import generate_frayer_model_worksheet
from .error_audit import generate_error_audit_worksheet
from .ten_frame import generate_ten_frame_worksheet

# worksheet type -> (generator, {payload key: default}). Each payload key is passed to the
# generator as the keyword argument of the same name, plus ``metadata``.
_SPECS: dict[str, tuple[Callable[..., BaseWorksheet], dict[str, Any]]] = {
    "two_operand": (
        generate_two_operand_math_worksheet,
        {
            "problems": [],
            "title": "Two-Operand Practice",
            "instructions": "Solve each problem. Show your work if needed.",
        },
    ),
    "reading_comprehension": (
        generate_reading_comprehension_worksheet,
        {
            "passage_title": "",
            "passage": "",
            "questions": [],
            "vocabulary": None,
            "title": "Reading Comprehension",
            "instructions": "Read the passage carefully, then answer the questions and review "
            "the vocabulary.",
        },
    ),
    "venn_diagram": (
        generate_venn_diagram_worksheet,
        {
            "left_label": "",
            "right_label": "",
            "both_label": "Both",
            "word_bank": [],
            "left_items": [],
            "right_items": [],
            "both_items": [],
            "title": "Venn Diagram",
            "instructions": "Sort the words from the word bank into the correct section of the "
            "Venn diagram.",
        },
    ),
    "feature_matrix": (
        generate_feature_matrix_worksheet,
        {
            "items": [],
            "properties": [],
            "title": "Feature Matrix",
            "instructions": "Check the boxes that apply to each item.",
            "show_answers": False,
        },
    ),
    "odd_one_out": (
        generate_odd_one_out_worksheet,
        {
            "rows": [],
            "title": "Odd One Out",
            "instructions": "Look at each row. Circle the item that does not belong and explain "
            "why.",
            "show_answers": False,
            "reasoning_lines": 2,
        },
    ),
    "tree_map": (
        generate_tree_map_worksheet,
        {
            "root_label": "",
            "branches": [],
            "word_bank": [],
            "title": "Tree Map",
            "instructions": "Fill in the tree map by writing words from the word bank in the "
            "correct category.",
        },
    ),
    "handwriting": (
        generate_handwriting_worksheet,
        {
            "items": [],
            "title": "Handwriting Practice",
            "instructions": "Look at the picture and practice writing the word on the lines.",
            "rows": 4,
            "cols": 2,
        },
    ),
    "alphabet": (
        generate_alphabet_worksheet,
        {
            "letter": "",
            "starting_words": [],
            "containing_words": [],
            "character_image_path": None,
            "title": "Alphabet Practice",
            "instructions": "Practice your letters and reading words!",
        },
    ),
    "pixel_copy": (
        generate_pixel_copy_worksheet,
        {
            "image_path": "",
            "title": "Pixel Copy",
            "instructions": "Look at the colors on the left. Copy them to the grid on the right!",
            "grid_size": 24,
        },
    ),
    "matching": (
        generate_matching_worksheet,
        {
            "left_items": [],
            "right_items": [],
            "title": "Match the Pairs",
            "instructions": "Draw a line to match the item on the left with the correct one on "
            "the right.",
        },
    ),
    "sequencing": (
        generate_sequencing_worksheet,
        {
            "activity_name": "Activity",
            "steps": [],
            "title": "Put It in Order!",
            "instructions": "Cut out each step below. Paste them in the correct order on "
            "another sheet of paper.",
            "show_answers": False,
        },
    ),
    "t_chart": (
        generate_t_chart_worksheet,
        {
            "columns": [],
            "row_count": 6,
            "word_bank": None,
            "title": "T-Chart",
            "instructions": "Sort the words from the word bank into the correct column.",
            "show_answers": False,
        },
    ),
    "fill_in_the_blank": (
        generate_fill_in_the_blank_worksheet,
        {
            "segments": [],
            "word_bank": None,
            "answers": None,
            "title": "Fill in the Blank",
            "instructions": "Use the word bank to fill in the blanks.",
            "show_answers": False,
        },
    ),
    "word_sort": (
        generate_word_sort_worksheet,
        {
            "categories": [],
            "tiles": [],
            "title": "Word Sort",
            "instructions": "Cut out the word tiles below. Sort them into the correct category "
            "boxes.",
            "show_answers": False,
        },
    ),
    "story_map": (
        generate_story_map_worksheet,
        {
            "title": "Story Map",
            "instructions": "Fill in each box about the story you read.",
            "story_title_field": True,
            "fields": [],
            "show_answers": False,
        },
    ),
    "cause_effect": (
        generate_cause_effect_worksheet,
        {
            "title": "Cause and Effect",
            "instructions": "Read each cause. Write what you think will happen (the effect).",
            "pairs": [],
            "layout": "horizontal",
            "show_answers": False,
        },
    ),
    "number_line": (
        generate_number_line_worksheet,
        {
            "title": "Number Line",
            "instructions": "Fill in the missing numbers on each number line.",
            "tasks": [],
            "show_answers": False,
        },
    ),
    "writing_scaffold": (
        generate_writing_scaffold_worksheet,
        {
            "title": "Writing Scaffold",
            "instructions": "Use the sentence starters below to write your paragraph.",
            "frame_type": "custom",
            "topic": None,
            "sections": [],
            "show_example": False,
            "example_texts": None,
        },
    ),
    "labeled_diagram": (
        generate_labeled_diagram_worksheet,
        {
            "title": "Labeled Diagram",
            "instructions": "Label each part of the diagram.",
            "image_path": None,
            "labels": [],
            "show_answers": False,
            "word_bank": True,
        },
    ),
    "frayer_model": (
        generate_frayer_model_worksheet,
        {
            "title": "Frayer Model",
            "instructions": "Fill in each section to show what you know about the word.",
            "entries": [],
            "show_answers": False,
            "quadrant_labels": None,
        },
    ),
    "error_audit": (
        generate_error_audit_worksheet,
        {
            "specimens": [],
            "title": "Bug Hunt",
            "instructions": "Something is wrong in each case. Circle the bug, "
            "diagnose it, fix it, then re-check your fix.",
            "theme_label": "Bug Hunter",
            "legend": [],
            "fix_mode": "rewrite",
            "verify": True,
            "adversarial": False,
            "show_answers": False,
            "fix_lines": 2,
            "columns": 1,
        },
    ),
    "ten_frame": (
        generate_ten_frame_worksheet,
        {
            "problems": [],
            "title": "Make Ten!",
            "instructions": "Move counters to fill the first ten-frame to ten. "
            "Write the make-ten proof on the lines.",
            "show_answers": False,
            "equation_lines": 2,
        },
    ),
}


def _creator(
    generator: Callable[..., BaseWorksheet], defaults: dict[str, Any]
) -> Callable[[dict[str, Any]], BaseWorksheet]:
    def create(payload: dict[str, Any]) -> BaseWorksheet:
        # Fresh list defaults per call, so no generator can mutate the shared table.
        kwargs = {
            key: payload.get(key, list(default) if isinstance(default, list) else default)
            for key, default in defaults.items()
        }
        return generator(**kwargs, metadata=payload.get("metadata"))

    return create


class WorksheetFactory:
    """Factory class for dispatching JSON requests to the correct worksheet renderer."""

    _registry: dict[str, Callable[[dict[str, Any]], BaseWorksheet]] = {
        name: _creator(*spec) for name, spec in _SPECS.items()
    }

    @classmethod
    def create(cls, worksheet_type: str, payload: dict[str, Any]) -> BaseWorksheet:
        """Create a worksheet of ``worksheet_type``; raises ValueError if the type is unknown."""
        creator = cls._registry.get(worksheet_type)
        if creator is None:
            raise ValueError(f"Unsupported worksheet type: {worksheet_type}")
        return creator(payload)

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Return a list of supported worksheet types."""
        return list(cls._registry.keys())


__all__ = [
    "WorksheetFactory",
]
