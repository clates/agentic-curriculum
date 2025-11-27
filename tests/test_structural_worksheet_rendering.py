"""Tests for rendering structural relationship worksheets to images and PDFs."""
import os
import tempfile
from pathlib import Path

import pytest

from src.worksheets import (
    generate_venn_diagram_worksheet,
    generate_feature_matrix_worksheet,
    generate_odd_one_out_worksheet,
    generate_tree_map_worksheet,
)
from src.worksheet_renderer import (
    render_venn_diagram_to_image,
    render_venn_diagram_to_pdf,
    render_feature_matrix_to_image,
    render_feature_matrix_to_pdf,
    render_odd_one_out_to_image,
    render_odd_one_out_to_pdf,
    render_tree_map_to_image,
    render_tree_map_to_pdf,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============ Venn Diagram Rendering Tests ============


def test_render_venn_diagram_to_image(temp_dir):
    """Venn diagram renders to PNG image."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="Mammals",
        right_label="Reptiles",
        word_bank=["dog", "lizard", "whale"],
    )
    output_path = Path(temp_dir) / "venn.png"
    result = render_venn_diagram_to_image(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_venn_diagram_to_pdf(temp_dir):
    """Venn diagram renders to PDF."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="Even",
        right_label="Odd",
        both_label="Prime",
        word_bank=["2", "3", "4", "5", "6"],
        left_items=["4", "6"],
        both_items=["2"],
        right_items=["3", "5"],
    )
    output_path = Path(temp_dir) / "venn.pdf"
    result = render_venn_diagram_to_pdf(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_venn_diagram_creates_parent_dirs(temp_dir):
    """Rendering creates parent directories if needed."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="A",
        right_label="B",
    )
    output_path = Path(temp_dir) / "nested" / "dir" / "venn.png"
    result = render_venn_diagram_to_image(worksheet, output_path)
    
    assert output_path.exists()


# ============ Feature Matrix Rendering Tests ============


def test_render_feature_matrix_to_image(temp_dir):
    """Feature matrix renders to PNG image."""
    worksheet = generate_feature_matrix_worksheet(
        items=["Dog", "Cat", "Fish"],
        properties=["Has Fur", "Has Legs", "Lives in Water"],
    )
    output_path = Path(temp_dir) / "matrix.png"
    result = render_feature_matrix_to_image(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_feature_matrix_to_pdf(temp_dir):
    """Feature matrix renders to PDF."""
    worksheet = generate_feature_matrix_worksheet(
        items=[
            {"name": "Apple", "checked_properties": ["Red", "Sweet"]},
            {"name": "Lemon", "checked_properties": ["Yellow", "Sour"]},
        ],
        properties=["Red", "Yellow", "Sweet", "Sour"],
        show_answers=True,
    )
    output_path = Path(temp_dir) / "matrix.pdf"
    result = render_feature_matrix_to_pdf(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_feature_matrix_handles_long_names(temp_dir):
    """Feature matrix handles items with long names gracefully."""
    worksheet = generate_feature_matrix_worksheet(
        items=["This is a very long item name that should be truncated", "Short"],
        properties=["Property A", "Property B"],
    )
    output_path = Path(temp_dir) / "matrix_long.png"
    result = render_feature_matrix_to_image(worksheet, output_path)
    
    assert output_path.exists()


# ============ Odd One Out Rendering Tests ============


def test_render_odd_one_out_to_image(temp_dir):
    """Odd one out renders to PNG image."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[
            {"items": ["dog", "cat", "car", "bird"]},
            {"items": ["red", "blue", "happy", "green"]},
        ],
    )
    output_path = Path(temp_dir) / "odd.png"
    result = render_odd_one_out_to_image(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_odd_one_out_to_pdf(temp_dir):
    """Odd one out renders to PDF."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[
            {"items": ["dog", "cat", "car", "bird"], "odd_item": "car", "explanation": "Not an animal"},
        ],
        show_answers=True,
    )
    output_path = Path(temp_dir) / "odd.pdf"
    result = render_odd_one_out_to_pdf(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_odd_one_out_with_reasoning_lines(temp_dir):
    """Odd one out renders correct number of reasoning lines."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[{"items": ["a", "b", "c", "d"]}],
        reasoning_lines=4,
    )
    output_path = Path(temp_dir) / "odd_lines.png"
    result = render_odd_one_out_to_image(worksheet, output_path)
    
    assert output_path.exists()


# ============ Tree Map Rendering Tests ============


def test_render_tree_map_to_image(temp_dir):
    """Tree map renders to PNG image."""
    worksheet = generate_tree_map_worksheet(
        root_label="Food Groups",
        branches=[
            {"label": "Fruits", "slots": ["apple", "banana"]},
            {"label": "Vegetables", "slots": ["carrot", "broccoli"]},
        ],
    )
    output_path = Path(temp_dir) / "tree.png"
    result = render_tree_map_to_image(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_tree_map_to_pdf(temp_dir):
    """Tree map renders to PDF."""
    worksheet = generate_tree_map_worksheet(
        root_label="Animals",
        branches=[
            {"label": "Mammals", "slot_count": 3},
            {"label": "Birds", "slot_count": 3},
            {"label": "Fish", "slot_count": 3},
        ],
        word_bank=["dog", "eagle", "salmon", "cat", "parrot", "tuna", "whale", "penguin", "shark"],
    )
    output_path = Path(temp_dir) / "tree.pdf"
    result = render_tree_map_to_pdf(worksheet, output_path)
    
    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_tree_map_with_empty_slots(temp_dir):
    """Tree map renders correctly with empty slots for student fill-in."""
    worksheet = generate_tree_map_worksheet(
        root_label="Categories",
        branches=[
            {"label": "Type A", "slot_count": 4},
            {"label": "Type B", "slot_count": 4},
        ],
    )
    output_path = Path(temp_dir) / "tree_empty.png"
    result = render_tree_map_to_image(worksheet, output_path)
    
    assert output_path.exists()


def test_render_tree_map_single_branch(temp_dir):
    """Tree map renders correctly with single branch."""
    worksheet = generate_tree_map_worksheet(
        root_label="Main Topic",
        branches=[
            {"label": "Subtopic", "slots": ["item1", "item2"]},
        ],
    )
    output_path = Path(temp_dir) / "tree_single.png"
    result = render_tree_map_to_image(worksheet, output_path)
    
    assert output_path.exists()
