# tests/test_generate_phonics_blends.py
import os
import subprocess
import pytest

OUTPUT_DIR = "output/phonics_blends"
EXPECTED_FILES = [
    "01_l_blends.html",
    "02_r_blends.html",
    "03_s_blends.html",
    "04_final_blends.html",
]


@pytest.fixture(scope="module", autouse=True)
def run_script():
    result = subprocess.run(
        ["python", "scripts/generate_phonics_blends_series.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"


def test_all_files_created():
    for fname in EXPECTED_FILES:
        path = os.path.join(OUTPUT_DIR, fname)
        assert os.path.exists(path), f"Missing output file: {path}"


def test_word_count_per_file():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        count = content.count('class="word"')
        assert count >= 25, f"{fname}: expected >=25 words, got {count}"


def test_grapheme_chunks_present():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert 'class="blend-part"' in content, f"{fname}: missing grapheme chunks"
        chunk_count = content.count('class="blend-part"')
        word_count = content.count('class="word"')
        assert (
            chunk_count / word_count >= 0.10
        ), f"{fname}: chunk ratio {chunk_count}/{word_count} is below 10%"


def test_opendyslexic_referenced():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert "OpenDyslexic" in content, f"{fname}: OpenDyslexic font not referenced"


def test_auto_print_present():
    for fname in EXPECTED_FILES:
        content = open(os.path.join(OUTPUT_DIR, fname)).read()
        assert "window.print()" in content, f"{fname}: missing auto-print trigger"
