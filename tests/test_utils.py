"""
IKSZ Build System - Tests for utils module.

Tests for utility functions used across the build system.
"""

import subprocess
from pathlib import Path

import pytest

from build.utils import (
    check_dependencies,
    detect_pdf_engine,
    ensure_dir,
    find_book_definitions,
    find_chapters,
    format_duration,
    format_size,
    get_file_size,
    get_project_root,
    run_command,
    slugify,
)


class TestFindBookDefinitions:
    """Tests for find_book_definitions function."""

    def test_finds_yaml_files(self, mock_sources_dir: Path) -> None:
        """Test finding YAML book definition files."""
        books_dir = mock_sources_dir / "books"

        # Create some YAML files
        (books_dir / "book1.yaml").write_text("test", encoding="utf-8")
        (books_dir / "book2.yaml").write_text("test", encoding="utf-8")
        (books_dir / "not-yaml.txt").write_text("test", encoding="utf-8")

        results = find_book_definitions(books_dir)

        assert len(results) == 2
        assert all(p.suffix == ".yaml" for p in results)
        assert sorted([p.stem for p in results]) == ["book1", "book2"]

    def test_returns_empty_for_nonexistent_dir(self, temp_dir: Path) -> None:
        """Test returns empty list when directory doesn't exist."""
        nonexistent = temp_dir / "nonexistent"
        results = find_book_definitions(nonexistent)
        assert results == []

    def test_uses_default_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test uses default sources/books path when not specified."""
        # This test verifies the function doesn't crash with default path
        # even if directory doesn't exist
        results = find_book_definitions()
        assert isinstance(results, list)


class TestFindChapters:
    """Tests for find_chapters function."""

    def test_finds_markdown_files(self, mock_sources_dir: Path) -> None:
        """Test finding markdown chapter files."""
        chapters_dir = mock_sources_dir / "core"

        # Create some markdown files
        (chapters_dir / "chapter1.md").write_text("test", encoding="utf-8")
        (chapters_dir / "chapter2.md").write_text("test", encoding="utf-8")
        (chapters_dir / "readme.txt").write_text("test", encoding="utf-8")

        # Create subdirectory with markdown
        subdir = chapters_dir / "subdir"
        subdir.mkdir()
        (subdir / "chapter3.md").write_text("test", encoding="utf-8")

        results = find_chapters(chapters_dir)

        assert len(results) == 3
        assert all(p.suffix == ".md" for p in results)

    def test_returns_empty_for_nonexistent_dir(self, temp_dir: Path) -> None:
        """Test returns empty list when directory doesn't exist."""
        nonexistent = temp_dir / "nonexistent"
        results = find_chapters(nonexistent)
        assert results == []


class TestRunCommand:
    """Tests for run_command function."""

    def test_runs_successful_command(self) -> None:
        """Test running a successful command."""
        result = run_command(["echo", "test"])
        assert result.returncode == 0
        assert "test" in result.stdout

    def test_raises_on_failed_command(self) -> None:
        """Test raises RuntimeError on failed command."""
        with pytest.raises(RuntimeError, match="Command failed"):
            run_command(["false"])

    def test_can_disable_error_checking(self) -> None:
        """Test can disable error checking."""
        result = run_command(["false"], check=False)
        assert result.returncode != 0

    def test_handles_missing_command(self) -> None:
        """Test handles missing command gracefully."""
        with pytest.raises(RuntimeError):
            run_command(["nonexistent-command-xyz"])


class TestEnsureDir:
    """Tests for ensure_dir function."""

    def test_creates_directory(self, temp_dir: Path) -> None:
        """Test creates directory if it doesn't exist."""
        new_dir = temp_dir / "new" / "nested" / "dir"
        assert not new_dir.exists()

        result = ensure_dir(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir

    def test_does_not_fail_if_exists(self, temp_dir: Path) -> None:
        """Test doesn't fail if directory already exists."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        result = ensure_dir(existing_dir)

        assert existing_dir.exists()
        assert result == existing_dir


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_formats_seconds(self) -> None:
        """Test formats seconds only."""
        assert format_duration(30) == "30s"
        assert format_duration(59) == "59s"

    def test_formats_minutes_and_seconds(self) -> None:
        """Test formats minutes and seconds."""
        assert format_duration(60) == "1m 0s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(125) == "2m 5s"

    def test_formats_hours_and_minutes(self) -> None:
        """Test formats hours and minutes."""
        assert format_duration(3600) == "1h 0m"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(7325) == "2h 2m"

    def test_handles_zero(self) -> None:
        """Test handles zero seconds."""
        assert format_duration(0) == "0s"


class TestFormatSize:
    """Tests for format_size function."""

    def test_formats_bytes(self) -> None:
        """Test formats bytes."""
        assert format_size(100) == "100B"
        assert format_size(1023) == "1023B"

    def test_formats_kilobytes(self) -> None:
        """Test formats kilobytes."""
        assert format_size(1024) == "1KB"
        assert format_size(1536) == "2KB"
        assert format_size(10240) == "10KB"

    def test_formats_megabytes(self) -> None:
        """Test formats megabytes."""
        assert format_size(1024 * 1024) == "1.0MB"
        assert format_size(1024 * 1024 * 5) == "5.0MB"

    def test_formats_gigabytes(self) -> None:
        """Test formats gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.00GB"
        assert format_size(1024 * 1024 * 1024 * 2) == "2.00GB"


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_returns_path(self) -> None:
        """Test returns a Path object."""
        root = get_project_root()
        assert isinstance(root, Path)
        assert root.exists()


class TestDetectPDFEngine:
    """Tests for detect_pdf_engine function."""

    def test_returns_string_or_none(self) -> None:
        """Test returns string or None."""
        result = detect_pdf_engine()
        assert result is None or isinstance(result, str)

    def test_detects_pdflatex_if_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detects pdflatex if available."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if cmd[0] == "pdflatex":
                return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
            raise FileNotFoundError()

        monkeypatch.setattr("subprocess.run", mock_run)
        result = detect_pdf_engine()
        assert result == "pdflatex"


class TestCheckDependencies:
    """Tests for check_dependencies function."""

    def test_returns_dict(self) -> None:
        """Test returns dictionary of tool availability."""
        deps = check_dependencies()
        assert isinstance(deps, dict)
        assert "pandoc" in deps
        assert "ebook-convert" in deps
        assert "pdflatex" in deps

    def test_values_are_booleans(self) -> None:
        """Test all values are booleans."""
        deps = check_dependencies()
        assert all(isinstance(v, bool) for v in deps.values())


class TestGetFileSize:
    """Tests for get_file_size function."""

    def test_returns_size_for_existing_file(self, temp_dir: Path) -> None:
        """Test returns file size for existing file."""
        test_file = temp_dir / "test.txt"
        content = "Hello, World!"
        test_file.write_text(content, encoding="utf-8")

        size = get_file_size(test_file)
        assert size > 0
        assert size == len(content.encode("utf-8"))

    def test_returns_zero_for_nonexistent_file(self, temp_dir: Path) -> None:
        """Test returns 0 for nonexistent file."""
        nonexistent = temp_dir / "nonexistent.txt"
        size = get_file_size(nonexistent)
        assert size == 0

    def test_returns_zero_for_empty_file(self, temp_dir: Path) -> None:
        """Test returns 0 for empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        size = get_file_size(empty_file)
        assert size == 0


class TestSlugify:
    """Tests for slugify function."""

    def test_converts_to_lowercase(self) -> None:
        """Test converts text to lowercase."""
        assert slugify("HELLO WORLD") == "hello-world"
        assert slugify("Test Book") == "test-book"

    def test_replaces_spaces_with_hyphens(self) -> None:
        """Test replaces spaces with hyphens."""
        assert slugify("hello world") == "hello-world"
        assert slugify("one two three") == "one-two-three"

    def test_removes_accents(self) -> None:
        """Test removes Hungarian accents."""
        assert slugify("áéíóöőúüű") == "aeiooouuu"
        assert slugify("ÁÉÍÓÖŐÚÜŰ") == "aeiooouuu"

    def test_handles_hungarian_text(self) -> None:
        """Test handles Hungarian text correctly."""
        assert slugify("IKSZ Alapszabály") == "iksz-alapszabaly"
        assert slugify("Tárgyak és Értékek") == "targyak-es-ertekek"
        assert slugify("Könyv Címe") == "konyv-cime"

    def test_removes_special_characters(self) -> None:
        """Test removes special characters."""
        assert slugify("hello@world") == "helloworld"
        assert slugify("test!book#2") == "testbook2"
        assert slugify("book (v1.0)") == "book-v10"

    def test_removes_multiple_hyphens(self) -> None:
        """Test removes multiple consecutive hyphens."""
        assert slugify("hello  world") == "hello-world"
        assert slugify("one   two   three") == "one-two-three"

    def test_removes_leading_trailing_hyphens(self) -> None:
        """Test removes leading and trailing hyphens."""
        assert slugify("  hello world  ") == "hello-world"
        assert slugify("-test-") == "test"

    def test_handles_empty_string(self) -> None:
        """Test handles empty string."""
        assert slugify("") == ""
        assert slugify("   ") == ""

    def test_preserves_numbers(self) -> None:
        """Test preserves numbers."""
        assert slugify("Book 123") == "book-123"
        assert slugify("Version 2.0") == "version-20"

    def test_handles_complex_cases(self) -> None:
        """Test handles complex real-world cases."""
        assert slugify("IKSZ v1.1 - Alapszabályok") == "iksz-v11-alapszabalyok"
        assert slugify("2. Fejezet: Karakteralkotás") == "2-fejezet-karakteralkotas"
