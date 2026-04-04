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

# Handwriting worksheet components
from .handwriting import (
    HandwritingItem,
    HandwritingWorksheet,
    generate_handwriting_worksheet,
)

# Pixel copy worksheet components
from .pixel_copy import (
    PixelCopyWorksheet,
    generate_pixel_copy_worksheet,
)

# Matching worksheet components
from .matching import (
    MatchingItem,
    MatchingWorksheet,
    generate_matching_worksheet,
)

# Alphabet worksheet components
from .alphabet import (
    AlphabetWorksheet,
    generate_alphabet_worksheet,
)

# Sequencing worksheet components
from .sequencing import (
    SequencingStep,
    SequencingWorksheet,
    generate_sequencing_worksheet,
)

# T-Chart worksheet components
from .t_chart import (
    TChartColumn,
    TChartWorksheet,
    generate_t_chart_worksheet,
)

# Fill-in-the-blank worksheet components
from .fill_in_the_blank import (
    FillBlankSegment,
    FillBlankWorksheet,
    generate_fill_in_the_blank_worksheet,
)

# Word sort worksheet components
from .word_sort import (
    WordSortTile,
    WordSortWorksheet,
    generate_word_sort_worksheet,
)

# Story map worksheet components
from .story_map import (
    StoryMapField,
    StoryMapWorksheet,
    generate_story_map_worksheet,
)

# Labeled diagram worksheet components
from .labeled_diagram import (
    DiagramLabel,
    LabeledDiagramWorksheet,
    generate_labeled_diagram_worksheet,
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
    # Handwriting
    "HandwritingItem",
    "HandwritingWorksheet",
    "generate_handwriting_worksheet",
    # Alphabet
    "AlphabetWorksheet",
    "generate_alphabet_worksheet",
    # Pixel Copy
    "PixelCopyWorksheet",
    "generate_pixel_copy_worksheet",
    # Matching
    "MatchingItem",
    "MatchingWorksheet",
    "generate_matching_worksheet",
    # Sequencing
    "SequencingStep",
    "SequencingWorksheet",
    "generate_sequencing_worksheet",
    # T-Chart
    "TChartColumn",
    "TChartWorksheet",
    "generate_t_chart_worksheet",
    # Fill-in-the-blank
    "FillBlankSegment",
    "FillBlankWorksheet",
    "generate_fill_in_the_blank_worksheet",
    # Word sort
    "WordSortTile",
    "WordSortWorksheet",
    "generate_word_sort_worksheet",
    # Story map
    "StoryMapField",
    "StoryMapWorksheet",
    "generate_story_map_worksheet",
    # Labeled diagram
    "DiagramLabel",
    "LabeledDiagramWorksheet",
    "generate_labeled_diagram_worksheet",
    # Factory
    "WorksheetFactory",
]
