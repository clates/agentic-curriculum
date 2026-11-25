"""Worksheet generation module.

This module provides utilities for generating printable worksheet data structures.
It includes support for two-operand math worksheets, reading comprehension worksheets,
and structural relationship worksheets (Venn diagrams, feature matrices, odd-one-out, tree maps).
"""

from __future__ import annotations

from .base import BaseWorksheet
from .two_operand import (
    Operator,
    TwoOperandProblem,
    MathWorksheet,
    Worksheet,  # Backward compatibility alias
    generate_two_operand_math_worksheet,
    format_vertical_problem,
)
from .reading_comprehension import (
    ReadingQuestion,
    VocabularyEntry,
    ReadingWorksheet,
    generate_reading_comprehension_worksheet,
)
from .venn_diagram import VennDiagramEntry, VennDiagramWorksheet, generate_venn_diagram_worksheet
from .feature_matrix import (
    FeatureMatrixItem,
    FeatureMatrixWorksheet,
    generate_feature_matrix_worksheet,
)
from .odd_one_out import OddOneOutRow, OddOneOutWorksheet, generate_odd_one_out_worksheet
from .tree_map import TreeMapSlot, TreeMapBranch, TreeMapWorksheet, generate_tree_map_worksheet
from .handwriting import HandwritingItem, HandwritingWorksheet, generate_handwriting_worksheet
from .pixel_copy import PixelCopyWorksheet, generate_pixel_copy_worksheet
from .matching import MatchingItem, MatchingWorksheet, generate_matching_worksheet
from .alphabet import AlphabetWorksheet, generate_alphabet_worksheet
from .sequencing import SequencingStep, SequencingWorksheet, generate_sequencing_worksheet
from .t_chart import TChartColumn, TChartWorksheet, generate_t_chart_worksheet
from .fill_in_the_blank import (
    FillBlankSegment,
    FillBlankWorksheet,
    generate_fill_in_the_blank_worksheet,
)
from .word_sort import WordSortTile, WordSortWorksheet, generate_word_sort_worksheet
from .story_map import StoryMapField, StoryMapWorksheet, generate_story_map_worksheet
from .cause_effect import CauseEffectPair, CauseEffectWorksheet, generate_cause_effect_worksheet
from .number_line import NumberLineTask, NumberLineWorksheet, generate_number_line_worksheet
from .writing_scaffold import (
    ScaffoldSection,
    WritingScaffoldWorksheet,
    generate_writing_scaffold_worksheet,
)
from .labeled_diagram import (
    DiagramLabel,
    LabeledDiagramWorksheet,
    generate_labeled_diagram_worksheet,
)
from .frayer_model import FrayerModelEntry, FrayerModelWorksheet, generate_frayer_model_worksheet
from .error_audit import (
    ErrorAuditSpecimen,
    ErrorAuditWorksheet,
    generate_error_audit_worksheet,
    decimal_stack_rows,
    FIX_MODES,
)
from .ten_frame import TenFrameProblem, TenFrameWorksheet, generate_ten_frame_worksheet
from .factory import WorksheetFactory

__all__ = [
    "BaseWorksheet",
    "Operator",
    "TwoOperandProblem",
    "MathWorksheet",
    "Worksheet",  # Backward compatibility alias
    "generate_two_operand_math_worksheet",
    "format_vertical_problem",
    "ReadingQuestion",
    "VocabularyEntry",
    "ReadingWorksheet",
    "generate_reading_comprehension_worksheet",
    "VennDiagramEntry",
    "VennDiagramWorksheet",
    "generate_venn_diagram_worksheet",
    "FeatureMatrixItem",
    "FeatureMatrixWorksheet",
    "generate_feature_matrix_worksheet",
    "OddOneOutRow",
    "OddOneOutWorksheet",
    "generate_odd_one_out_worksheet",
    "TreeMapSlot",
    "TreeMapBranch",
    "TreeMapWorksheet",
    "generate_tree_map_worksheet",
    "HandwritingItem",
    "HandwritingWorksheet",
    "generate_handwriting_worksheet",
    "AlphabetWorksheet",
    "generate_alphabet_worksheet",
    "PixelCopyWorksheet",
    "generate_pixel_copy_worksheet",
    "MatchingItem",
    "MatchingWorksheet",
    "generate_matching_worksheet",
    "SequencingStep",
    "SequencingWorksheet",
    "generate_sequencing_worksheet",
    "TChartColumn",
    "TChartWorksheet",
    "generate_t_chart_worksheet",
    "FillBlankSegment",
    "FillBlankWorksheet",
    "generate_fill_in_the_blank_worksheet",
    "WordSortTile",
    "WordSortWorksheet",
    "generate_word_sort_worksheet",
    "StoryMapField",
    "StoryMapWorksheet",
    "generate_story_map_worksheet",
    "CauseEffectPair",
    "CauseEffectWorksheet",
    "generate_cause_effect_worksheet",
    "NumberLineTask",
    "NumberLineWorksheet",
    "generate_number_line_worksheet",
    "ScaffoldSection",
    "WritingScaffoldWorksheet",
    "generate_writing_scaffold_worksheet",
    "DiagramLabel",
    "LabeledDiagramWorksheet",
    "generate_labeled_diagram_worksheet",
    "FrayerModelEntry",
    "FrayerModelWorksheet",
    "generate_frayer_model_worksheet",
    "ErrorAuditSpecimen",
    "ErrorAuditWorksheet",
    "generate_error_audit_worksheet",
    "decimal_stack_rows",
    "FIX_MODES",
    "TenFrameProblem",
    "TenFrameWorksheet",
    "generate_ten_frame_worksheet",
    "WorksheetFactory",
]
