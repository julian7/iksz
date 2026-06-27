"""
IKSZ Build System - Test Configuration and Fixtures.

This module provides pytest fixtures and configuration for the test suite.
"""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """
    Create a temporary directory for tests.

    Yields:
        Path to temporary directory.

    Cleans up the directory after the test.
    """
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)


@pytest.fixture
def mock_sources_dir(temp_dir: Path) -> Path:
    """
    Create a mock sources directory structure.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to mock sources directory.
    """
    sources = temp_dir / "sources"
    sources.mkdir(parents=True)

    # Create books directory
    books_dir = sources / "books"
    books_dir.mkdir()

    # Create chapters directory
    chapters_dir = sources / "core"
    chapters_dir.mkdir()

    return sources


@pytest.fixture
def mock_templates_dir(temp_dir: Path) -> Path:
    """
    Create a mock templates directory.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to mock templates directory.
    """
    templates = temp_dir / "templates"
    templates.mkdir(parents=True)

    # Create basic CSS file
    css_file = templates / "style.css"
    css_file.write_text(
        """
body {
    font-family: sans-serif;
    margin: 2em;
}
h1 {
    color: #333;
}
""",
        encoding="utf-8",
    )

    # Create basic LaTeX header
    latex_header = templates / "latex-header.tex"
    latex_header.write_text(
        r"""
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[magyar]{babel}
""",
        encoding="utf-8",
    )

    return templates


@pytest.fixture
def mock_results_dir(temp_dir: Path) -> Path:
    """
    Create a mock results directory.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Path to mock results directory.
    """
    results = temp_dir / "results"
    results.mkdir(parents=True)
    return results


@pytest.fixture
def sample_book_yaml(mock_sources_dir: Path) -> Path:
    """
    Create a sample book YAML definition.

    Args:
        mock_sources_dir: Mock sources directory fixture.

    Returns:
        Path to created YAML file.
    """
    yaml_content = """
book:
  id: test-book
  title: "Test Book"
  subtitle: "A Test Subtitle"
  version: "1.0"
  language: "hu"
  author: "Test Author"
  publisher: "Test Publisher"
  rights: "Creative Commons BY-SA 4.0"

chapters:
  - section: "Introduction"
    pages:
      - file: "core/chapter1.md"
      - file: "core/chapter2.md"
  - section: "Main Content"
    pages:
      - file: "core/chapter3.md"
"""

    yaml_path = mock_sources_dir / "books" / "test-book.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")

    return yaml_path


@pytest.fixture
def sample_chapters(mock_sources_dir: Path) -> list[Path]:
    """
    Create sample chapter markdown files.

    Args:
        mock_sources_dir: Mock sources directory fixture.

    Returns:
        List of paths to created chapter files.
    """
    chapters_dir = mock_sources_dir / "core"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    chapters = []

    # Chapter 1
    chapter1 = chapters_dir / "chapter1.md"
    chapter1.write_text(
        """# Chapter 1: Introduction

This is the first chapter of the test book.

## Section 1.1

Some content here.

## Section 1.2

More content.
""",
        encoding="utf-8",
    )
    chapters.append(chapter1)

    # Chapter 2
    chapter2 = chapters_dir / "chapter2.md"
    chapter2.write_text(
        """# Chapter 2: Basics

This is the second chapter.

## Section 2.1

Hungarian characters: áéíóöőúüű ÁÉÍÓÖŐÚÜŰ

## Section 2.2

Tables:

| Name | Value |
|------|-------|
| Test | 123   |
""",
        encoding="utf-8",
    )
    chapters.append(chapter2)

    # Chapter 3
    chapter3 = chapters_dir / "chapter3.md"
    chapter3.write_text(
        """# Chapter 3: Advanced

This is the third chapter.

## Section 3.1

Some advanced content.
""",
        encoding="utf-8",
    )
    chapters.append(chapter3)

    return chapters


@pytest.fixture
def full_mock_project(
    temp_dir: Path,
    mock_sources_dir: Path,
    mock_templates_dir: Path,
    mock_results_dir: Path,
    sample_book_yaml: Path,
    sample_chapters: list[Path],
) -> Path:
    """
    Create a complete mock project with all necessary files.

    Args:
        temp_dir: Temporary directory fixture.
        mock_sources_dir: Mock sources directory.
        mock_templates_dir: Mock templates directory.
        mock_results_dir: Mock results directory.
        sample_book_yaml: Sample book YAML file.
        sample_chapters: Sample chapter files.

    Returns:
        Path to project root (temp_dir).
    """
    return temp_dir


@pytest.fixture
def mock_pandoc_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock pandoc as being available.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    import subprocess

    def mock_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        """Mock subprocess.run for pandoc."""
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def mock_calibre_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock ebook-convert (Calibre) as being available.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    import subprocess

    def mock_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        """Mock subprocess.run for ebook-convert."""
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)
