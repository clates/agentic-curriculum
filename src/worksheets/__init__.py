"""Worksheet generation module.

This module provides utilities for generating printable worksheet data structures.
It includes support for two-operand math worksheets and reading comprehension worksheets.
"""
from __future__ import annotations

# Base classes
from .base import BaseWorksheet

# Two-operand math worksheet components
from .two_operand import (
    Operator,
    TwoOperandProblem,
    Worksheet,
    generate_two_operand_math_worksheet,
    format_vertical_problem,
)

# Reading comprehension worksheet components
from .reading_comprehension import (
    ReadingQuestion,
    VocabularyEntry,
    ReadingWorksheet,
    generate_reading_comprehension_worksheet,
)

# Factory for creating worksheets from JSON payloads
from .factory import WorksheetFactory

__all__ = [
    # Base
    "BaseWorksheet",
    # Two-operand
    "Operator",
    "TwoOperandProblem",
    "Worksheet",
    "generate_two_operand_math_worksheet",
    "format_vertical_problem",
    # Reading comprehension
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheet",
    "generate_reading_comprehension_worksheet",
    # Factory
    "WorksheetFactory",
]
