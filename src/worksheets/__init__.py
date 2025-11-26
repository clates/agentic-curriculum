"""Worksheet generation module.

This module provides utilities for generating printable worksheet data structures.
It includes support for two-operand math worksheets, reading comprehension worksheets,
and structural relationship worksheets (Venn diagrams, feature matrices, odd-one-out, tree maps).
"""
from __future__ import annotations

# Base classes
from .base import BaseWorksheet

# Two-operand math worksheet components
from .two_operand import (
    Operator,
    TwoOperandProblem,
    MathWorksheet,
    Worksheet,  # Backward compatibility alias
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

# Venn diagram worksheet components
from .venn_diagram import (
    VennDiagramEntry,
    VennDiagramWorksheet,
    generate_venn_diagram_worksheet,
)

# Feature matrix worksheet components
from .feature_matrix import (
    FeatureMatrixItem,
    FeatureMatrixWorksheet,
    generate_feature_matrix_worksheet,
)

# Odd one out worksheet components
from .odd_one_out import (
    OddOneOutRow,
    OddOneOutWorksheet,
    generate_odd_one_out_worksheet,
)

# Tree map worksheet components
from .tree_map import (
    TreeMapSlot,
    TreeMapBranch,
    TreeMapWorksheet,
    generate_tree_map_worksheet,
)

# Factory for creating worksheets from JSON payloads
from .factory import WorksheetFactory

__all__ = [
    # Base
    "BaseWorksheet",
    # Two-operand
    "Operator",
    "TwoOperandProblem",
    "MathWorksheet",
    "Worksheet",  # Backward compatibility alias
    "generate_two_operand_math_worksheet",
    "format_vertical_problem",
    # Reading comprehension
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheet",
    "generate_reading_comprehension_worksheet",
    # Venn diagram
    "VennDiagramEntry",
    "VennDiagramWorksheet",
    "generate_venn_diagram_worksheet",
    # Feature matrix
    "FeatureMatrixItem",
    "FeatureMatrixWorksheet",
    "generate_feature_matrix_worksheet",
    # Odd one out
    "OddOneOutRow",
    "OddOneOutWorksheet",
    "generate_odd_one_out_worksheet",
    # Tree map
    "TreeMapSlot",
    "TreeMapBranch",
    "TreeMapWorksheet",
    "generate_tree_map_worksheet",
    # Factory
    "WorksheetFactory",
]
