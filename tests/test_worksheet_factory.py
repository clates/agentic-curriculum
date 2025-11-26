"""Tests for WorksheetFactory in the new worksheets module."""
import pytest
from src.worksheets import WorksheetFactory, Worksheet, ReadingWorksheet, BaseWorksheet


def test_factory_creates_two_operand_worksheet():
    """Factory correctly creates a two-operand math worksheet."""
    worksheet = WorksheetFactory.create('two_operand', {
        'problems': [{'operand_one': 2, 'operand_two': 3, 'operator': '+'}],
        'title': 'Factory Math Test',
    })
    assert isinstance(worksheet, Worksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert worksheet.title == 'Factory Math Test'
    assert len(worksheet.problems) == 1


def test_factory_creates_reading_comprehension_worksheet():
    """Factory correctly creates a reading comprehension worksheet."""
    worksheet = WorksheetFactory.create('reading_comprehension', {
        'passage_title': 'Factory Passage',
        'passage': 'This is a test passage.',
        'questions': [{'prompt': 'What is this?'}],
    })
    assert isinstance(worksheet, ReadingWorksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert worksheet.passage_title == 'Factory Passage'
    assert len(worksheet.questions) == 1


def test_factory_raises_on_unsupported_type():
    """Factory raises ValueError for unsupported worksheet types."""
    with pytest.raises(ValueError, match="Unsupported worksheet type"):
        WorksheetFactory.create('unsupported_type', {})


def test_factory_supported_types():
    """Factory returns correct list of supported types."""
    supported = WorksheetFactory.get_supported_types()
    assert 'two_operand' in supported
    assert 'reading_comprehension' in supported
