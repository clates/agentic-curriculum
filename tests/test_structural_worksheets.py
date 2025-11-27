"""Tests for structural relationship worksheets (Venn diagram, feature matrix, odd-one-out, tree map)."""
import pytest
from src.worksheets import (
    WorksheetFactory,
    BaseWorksheet,
    # Venn diagram
    VennDiagramEntry,
    VennDiagramWorksheet,
    generate_venn_diagram_worksheet,
    # Feature matrix
    FeatureMatrixItem,
    FeatureMatrixWorksheet,
    generate_feature_matrix_worksheet,
    # Odd one out
    OddOneOutRow,
    OddOneOutWorksheet,
    generate_odd_one_out_worksheet,
    # Tree map
    TreeMapSlot,
    TreeMapBranch,
    TreeMapWorksheet,
    generate_tree_map_worksheet,
)


# ============ Venn Diagram Tests ============


def test_venn_diagram_entry_from_mapping():
    """VennDiagramEntry correctly parses from dict."""
    entry = VennDiagramEntry.from_mapping({"text": "apple", "category": "left"})
    assert entry.text == "apple"
    assert entry.category == "left"


def test_venn_diagram_entry_requires_text():
    """VennDiagramEntry raises on missing text."""
    with pytest.raises(ValueError, match="requires a text field"):
        VennDiagramEntry.from_mapping({})


def test_generate_venn_diagram_basic():
    """generate_venn_diagram_worksheet creates valid worksheet."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="Mammals",
        right_label="Reptiles",
        word_bank=["dog", "lizard", "whale"],
    )
    assert isinstance(worksheet, VennDiagramWorksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert worksheet.left_label == "Mammals"
    assert worksheet.right_label == "Reptiles"
    assert len(worksheet.word_bank) == 3


def test_generate_venn_diagram_with_prefilled_items():
    """Venn diagram supports pre-filled items in sections."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="Hot",
        right_label="Cold",
        left_items=["fire", "sun"],
        right_items=["ice", "snow"],
        both_items=["water"],
    )
    assert worksheet.left_items == ["fire", "sun"]
    assert worksheet.right_items == ["ice", "snow"]
    assert worksheet.both_items == ["water"]


def test_generate_venn_diagram_requires_labels():
    """Venn diagram requires left and right labels."""
    with pytest.raises(ValueError, match="Left label is required"):
        generate_venn_diagram_worksheet(left_label="", right_label="Right")
    with pytest.raises(ValueError, match="Right label is required"):
        generate_venn_diagram_worksheet(left_label="Left", right_label="")


def test_venn_diagram_to_markdown():
    """Venn diagram generates valid markdown."""
    worksheet = generate_venn_diagram_worksheet(
        left_label="Even",
        right_label="Odd",
        word_bank=["2", "3", "4"],
    )
    md = worksheet.to_markdown()
    assert "Venn Diagram" in md
    assert "Even" in md
    assert "Odd" in md
    assert "Word Bank" in md


def test_factory_creates_venn_diagram():
    """Factory correctly creates Venn diagram worksheet."""
    worksheet = WorksheetFactory.create('venn_diagram', {
        'left_label': 'Animals',
        'right_label': 'Plants',
        'word_bank': ['dog', 'tree'],
    })
    assert isinstance(worksheet, VennDiagramWorksheet)
    assert worksheet.left_label == 'Animals'


# ============ Feature Matrix Tests ============


def test_feature_matrix_item_from_mapping():
    """FeatureMatrixItem correctly parses from dict."""
    item = FeatureMatrixItem.from_mapping({"name": "Dog", "checked_properties": ["has fur", "has legs"]})
    assert item.name == "Dog"
    assert item.checked_properties == ["has fur", "has legs"]


def test_feature_matrix_item_requires_name():
    """FeatureMatrixItem raises on missing name."""
    with pytest.raises(ValueError, match="requires a name field"):
        FeatureMatrixItem.from_mapping({})


def test_generate_feature_matrix_basic():
    """generate_feature_matrix_worksheet creates valid worksheet."""
    worksheet = generate_feature_matrix_worksheet(
        items=["Dog", "Cat", "Fish"],
        properties=["Has Fur", "Has Legs", "Lives in Water"],
    )
    assert isinstance(worksheet, FeatureMatrixWorksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert len(worksheet.items) == 3
    assert len(worksheet.properties) == 3


def test_generate_feature_matrix_with_answers():
    """Feature matrix supports show_answers for answer key."""
    worksheet = generate_feature_matrix_worksheet(
        items=[
            {"name": "Dog", "checked_properties": ["Has Fur", "Has Legs"]},
            {"name": "Fish", "checked_properties": ["Lives in Water"]},
        ],
        properties=["Has Fur", "Has Legs", "Lives in Water"],
        show_answers=True,
    )
    assert worksheet.show_answers is True
    assert worksheet.items[0].checked_properties == ["Has Fur", "Has Legs"]


def test_generate_feature_matrix_requires_items_and_properties():
    """Feature matrix requires at least one item and property."""
    with pytest.raises(ValueError, match="At least one item is required"):
        generate_feature_matrix_worksheet(items=[], properties=["Prop"])
    with pytest.raises(ValueError, match="At least one property is required"):
        generate_feature_matrix_worksheet(items=["Item"], properties=[])


def test_feature_matrix_to_markdown():
    """Feature matrix generates valid markdown table."""
    worksheet = generate_feature_matrix_worksheet(
        items=["Apple", "Carrot"],
        properties=["Red", "Orange"],
    )
    md = worksheet.to_markdown()
    assert "Feature Matrix" in md
    assert "Apple" in md
    assert "Red" in md
    assert "|" in md  # Table formatting


def test_factory_creates_feature_matrix():
    """Factory correctly creates feature matrix worksheet."""
    worksheet = WorksheetFactory.create('feature_matrix', {
        'items': ['Dog', 'Cat'],
        'properties': ['Fur', 'Tail'],
    })
    assert isinstance(worksheet, FeatureMatrixWorksheet)
    assert len(worksheet.items) == 2


# ============ Odd One Out Tests ============


def test_odd_one_out_row_from_mapping():
    """OddOneOutRow correctly parses from dict."""
    row = OddOneOutRow.from_mapping({
        "items": ["dog", "cat", "car", "bird"],
        "odd_item": "car",
        "explanation": "Car is not an animal"
    })
    assert len(row.items) == 4
    assert row.odd_item == "car"
    assert row.explanation == "Car is not an animal"


def test_odd_one_out_row_requires_items():
    """OddOneOutRow raises on missing or insufficient items."""
    with pytest.raises(ValueError, match="requires an items list"):
        OddOneOutRow.from_mapping({})
    with pytest.raises(ValueError, match="at least 3 items"):
        OddOneOutRow.from_mapping({"items": ["a", "b"]})


def test_generate_odd_one_out_basic():
    """generate_odd_one_out_worksheet creates valid worksheet."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[
            {"items": ["apple", "banana", "car", "orange"]},
            {"items": ["red", "blue", "happy", "green"]},
        ],
    )
    assert isinstance(worksheet, OddOneOutWorksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert len(worksheet.rows) == 2


def test_generate_odd_one_out_with_answers():
    """Odd one out supports show_answers for answer key."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[
            {"items": ["dog", "cat", "car", "bird"], "odd_item": "car", "explanation": "Not an animal"},
        ],
        show_answers=True,
    )
    assert worksheet.show_answers is True
    assert worksheet.rows[0].odd_item == "car"


def test_generate_odd_one_out_requires_rows():
    """Odd one out requires at least one row."""
    with pytest.raises(ValueError, match="At least one row is required"):
        generate_odd_one_out_worksheet(rows=[])


def test_odd_one_out_to_markdown():
    """Odd one out generates valid markdown."""
    worksheet = generate_odd_one_out_worksheet(
        rows=[{"items": ["a", "b", "c", "d"]}],
        reasoning_lines=2,
    )
    md = worksheet.to_markdown()
    assert "Odd One Out" in md
    assert "Why?" in md
    assert "a" in md


def test_factory_creates_odd_one_out():
    """Factory correctly creates odd-one-out worksheet."""
    worksheet = WorksheetFactory.create('odd_one_out', {
        'rows': [{'items': ['cat', 'dog', 'car', 'bird']}],
    })
    assert isinstance(worksheet, OddOneOutWorksheet)
    assert len(worksheet.rows) == 1


# ============ Tree Map Tests ============


def test_tree_map_slot_from_mapping():
    """TreeMapSlot correctly parses from dict."""
    slot = TreeMapSlot.from_mapping({"text": "apple"})
    assert slot.text == "apple"
    
    empty_slot = TreeMapSlot.from_mapping({})
    assert empty_slot.text is None


def test_tree_map_branch_from_mapping():
    """TreeMapBranch correctly parses from dict."""
    branch = TreeMapBranch.from_mapping({
        "label": "Fruits",
        "slots": ["apple", "banana", {"text": "orange"}],
    })
    assert branch.label == "Fruits"
    assert len(branch.slots) == 3
    assert branch.slots[0].text == "apple"


def test_tree_map_branch_requires_label():
    """TreeMapBranch raises on missing label."""
    with pytest.raises(ValueError, match="requires a label"):
        TreeMapBranch.from_mapping({})


def test_tree_map_branch_creates_empty_slots():
    """TreeMapBranch creates empty slots when none provided."""
    branch = TreeMapBranch.from_mapping({"label": "Category", "slot_count": 4})
    assert len(branch.slots) == 4
    assert all(slot.text is None for slot in branch.slots)


def test_generate_tree_map_basic():
    """generate_tree_map_worksheet creates valid worksheet."""
    worksheet = generate_tree_map_worksheet(
        root_label="Food Groups",
        branches=[
            {"label": "Fruits", "slots": ["apple", "banana"]},
            {"label": "Vegetables", "slots": ["carrot", "broccoli"]},
        ],
    )
    assert isinstance(worksheet, TreeMapWorksheet)
    assert isinstance(worksheet, BaseWorksheet)
    assert worksheet.root_label == "Food Groups"
    assert len(worksheet.branches) == 2


def test_generate_tree_map_with_word_bank():
    """Tree map supports word bank."""
    worksheet = generate_tree_map_worksheet(
        root_label="Animals",
        branches=[
            {"label": "Mammals", "slot_count": 2},
            {"label": "Birds", "slot_count": 2},
        ],
        word_bank=["dog", "cat", "eagle", "parrot"],
    )
    assert worksheet.word_bank == ["dog", "cat", "eagle", "parrot"]


def test_generate_tree_map_requires_root_and_branches():
    """Tree map requires root label and at least one branch."""
    with pytest.raises(ValueError, match="Root label is required"):
        generate_tree_map_worksheet(root_label="", branches=[{"label": "A"}])
    with pytest.raises(ValueError, match="At least one branch is required"):
        generate_tree_map_worksheet(root_label="Root", branches=[])


def test_tree_map_to_markdown():
    """Tree map generates valid markdown."""
    worksheet = generate_tree_map_worksheet(
        root_label="Shapes",
        branches=[{"label": "Round", "slots": ["circle"]}],
    )
    md = worksheet.to_markdown()
    assert "Tree Map" in md
    assert "Shapes" in md
    assert "Round" in md
    assert "circle" in md


def test_factory_creates_tree_map():
    """Factory correctly creates tree map worksheet."""
    worksheet = WorksheetFactory.create('tree_map', {
        'root_label': 'Categories',
        'branches': [{'label': 'Type A', 'slot_count': 3}],
    })
    assert isinstance(worksheet, TreeMapWorksheet)
    assert worksheet.root_label == 'Categories'


# ============ Factory Integration Tests ============


def test_factory_supports_all_new_types():
    """Factory lists all new worksheet types."""
    supported = WorksheetFactory.get_supported_types()
    assert 'venn_diagram' in supported
    assert 'feature_matrix' in supported
    assert 'odd_one_out' in supported
    assert 'tree_map' in supported
