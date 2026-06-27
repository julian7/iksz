"""
IKSZ Build System - Tests for book module.

Tests for book building, chapter management, and YAML configuration.
"""

from pathlib import Path

import pytest
import yaml

from build.book import Book, BookBuilder, Chapter, Section


class TestChapter:
    """Tests for Chapter dataclass."""

    def test_creates_from_string(self) -> None:
        """Test creates Chapter from simple string."""
        chapter = Chapter.from_dict("core/chapter1.md")
        assert chapter.file == "core/chapter1.md"
        assert chapter.title is None

    def test_creates_from_dict(self) -> None:
        """Test creates Chapter from dictionary."""
        data = {"file": "core/chapter1.md", "title": "Introduction"}
        chapter = Chapter.from_dict(data)
        assert chapter.file == "core/chapter1.md"
        assert chapter.title == "Introduction"

    def test_creates_from_dict_without_title(self) -> None:
        """Test creates Chapter from dict without title."""
        data = {"file": "core/chapter1.md"}
        chapter = Chapter.from_dict(data)
        assert chapter.file == "core/chapter1.md"
        assert chapter.title is None


class TestSection:
    """Tests for Section dataclass."""

    def test_creates_from_dict(self) -> None:
        """Test creates Section from dictionary."""
        data = {
            "section": "Introduction",
            "pages": [
                "core/chapter1.md",
                {"file": "core/chapter2.md", "title": "Chapter 2"},
            ],
        }
        section = Section.from_dict(data)
        assert section.name == "Introduction"
        assert len(section.chapters) == 2
        assert section.chapters[0].file == "core/chapter1.md"
        assert section.chapters[1].title == "Chapter 2"

    def test_creates_empty_section(self) -> None:
        """Test creates Section with no chapters."""
        data = {"section": "Empty Section", "pages": []}
        section = Section.from_dict(data)
        assert section.name == "Empty Section"
        assert len(section.chapters) == 0


class TestBook:
    """Tests for Book dataclass."""

    def test_loads_from_yaml(self, sample_book_yaml: Path) -> None:
        """Test loads book from YAML file."""
        book = Book.from_yaml(sample_book_yaml)

        assert book.id == "test-book"
        assert book.title == "Test Book"
        assert book.subtitle == "A Test Subtitle"
        assert book.released == "1.0"
        assert book.language == "hu"
        assert book.author == "Test Author"
        assert book.publisher == "Test Publisher"
        assert book.rights == "Creative Commons BY-SA 4.0"

    def test_parses_sections(self, sample_book_yaml: Path) -> None:
        """Test parses sections from YAML."""
        book = Book.from_yaml(sample_book_yaml)

        assert len(book.sections) == 2
        assert book.sections[0].name == "Introduction"
        assert book.sections[1].name == "Main Content"

    def test_parses_chapters(self, sample_book_yaml: Path) -> None:
        """Test parses chapters from YAML."""
        book = Book.from_yaml(sample_book_yaml)

        # Introduction section has 2 chapters
        assert len(book.sections[0].chapters) == 2
        assert book.sections[0].chapters[0].file == "core/chapter1.md"
        assert book.sections[0].chapters[1].file == "core/chapter2.md"

        # Main Content section has 1 chapter
        assert len(book.sections[1].chapters) == 1
        assert book.sections[1].chapters[0].file == "core/chapter3.md"

    def test_get_all_chapters(self, sample_book_yaml: Path) -> None:
        """Test gets flat list of all chapters."""
        book = Book.from_yaml(sample_book_yaml)

        all_chapters = book.get_all_chapters()
        assert len(all_chapters) == 3
        assert all_chapters[0].file == "core/chapter1.md"
        assert all_chapters[1].file == "core/chapter2.md"
        assert all_chapters[2].file == "core/chapter3.md"

    def test_get_output_filename(self, sample_book_yaml: Path) -> None:
        """Test generates correct output filename."""
        book = Book.from_yaml(sample_book_yaml)

        assert book.get_output_filename("epub") == "test-book-v1.0.epub"
        assert book.get_output_filename("html") == "test-book-v1.0.html"
        assert book.get_output_filename("mobi") == "test-book-v1.0.mobi"
        assert book.get_output_filename("pdf") == "test-book-v1.0.pdf"

    def test_uses_default_values(self, temp_dir: Path) -> None:
        """Test uses default values when not specified in YAML."""
        yaml_content = """
book:
  title: "Minimal Book"

chapters:
  - section: "Content"
    pages:
      - file: "chapter1.md"
"""
        yaml_path = temp_dir / "minimal.yaml"
        yaml_path.write_text(yaml_content, encoding="utf-8")

        book = Book.from_yaml(yaml_path)

        assert book.id == "minimal"  # From filename
        assert book.released == "1.0"
        assert book.language == "hu"
        assert book.author == "IKSZ Fejlesztők"
        assert book.publisher == "IKSZ Projekt"

    def test_raises_on_missing_file(self, temp_dir: Path) -> None:
        """Test raises error when YAML file doesn't exist."""
        nonexistent = temp_dir / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            Book.from_yaml(nonexistent)

    def test_handles_invalid_yaml(self, temp_dir: Path) -> None:
        """Test handles invalid YAML gracefully."""
        yaml_path = temp_dir / "invalid.yaml"
        yaml_path.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(yaml.YAMLError):
            Book.from_yaml(yaml_path)


class TestBookBuilder:
    """Tests for BookBuilder class."""

    def test_initializes_with_defaults(self) -> None:
        """Test initializes with default directories."""
        builder = BookBuilder()
        assert builder.sources_dir == Path("sources")
        assert builder.results_dir == Path("results")
        assert builder.templates_dir == Path("templates")

    def test_initializes_with_custom_dirs(self, temp_dir: Path) -> None:
        """Test initializes with custom directories."""
        sources = temp_dir / "custom_sources"
        results = temp_dir / "custom_results"

        builder = BookBuilder(sources_dir=sources, results_dir=results)
        assert builder.sources_dir == sources
        assert builder.results_dir == results

    def test_loads_book(self, full_mock_project: Path, sample_book_yaml: Path) -> None:
        """Test loads book definition by ID."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        book = builder.load_book("test-book")
        assert book.id == "test-book"
        assert book.title == "Test Book"

    def test_load_book_raises_on_missing(
        self, full_mock_project: Path, sample_book_yaml: Path
    ) -> None:
        """Test raises error when book definition doesn't exist."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        with pytest.raises(FileNotFoundError, match="Book definition not found"):
            builder.load_book("nonexistent-book")

    def test_combines_chapters(self, full_mock_project: Path, sample_book_yaml: Path) -> None:
        """Test combines chapters into single markdown."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        book = builder.load_book("test-book")
        combined = builder.combine_chapters(book)

        # Check YAML frontmatter
        assert "---" in combined
        assert 'title: "Test Book"' in combined
        assert 'subtitle: "A Test Subtitle"' in combined
        assert 'author: "Test Author"' in combined
        assert "lang: hu" in combined

        # Check title page
        assert "# Test Book" in combined
        assert "**A Test Subtitle**" in combined
        assert "**Verzió:** 1.0" in combined

        # Check chapters are included
        assert "# Chapter 1: Introduction" in combined
        assert "# Chapter 2: Basics" in combined
        assert "# Chapter 3: Advanced" in combined

        # Check page breaks
        assert "\\newpage" in combined

    def test_combine_chapters_includes_hungarian_chars(
        self, full_mock_project: Path, sample_book_yaml: Path
    ) -> None:
        """Test combined markdown preserves Hungarian characters."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        book = builder.load_book("test-book")
        combined = builder.combine_chapters(book)

        # Chapter 2 has Hungarian characters
        assert "áéíóöőúüű" in combined
        assert "ÁÉÍÓÖŐÚÜŰ" in combined

    def test_combine_chapters_raises_on_missing_chapter(
        self, full_mock_project: Path, temp_dir: Path
    ) -> None:
        """Test raises error when chapter file doesn't exist."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        # Create book with nonexistent chapter
        yaml_content = """
book:
  title: "Bad Book"
chapters:
  - section: "Content"
    pages:
      - file: "nonexistent.md"
"""
        yaml_path = sources / "books" / "bad-book.yaml"
        yaml_path.write_text(yaml_content, encoding="utf-8")

        book = builder.load_book("bad-book")

        with pytest.raises(FileNotFoundError, match="Chapter file not found"):
            builder.combine_chapters(book)

    def test_build_format_raises_on_unsupported_format(
        self, full_mock_project: Path, sample_book_yaml: Path
    ) -> None:
        """Test raises error for unsupported format."""
        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        with pytest.raises(ValueError, match="Unsupported format"):
            builder.build_format("test-book", "invalid")

    def test_build_format_creates_temp_file(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test creates temporary combined markdown file."""
        import subprocess

        # Mock pandoc
        def mock_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        builder.build_format("test-book", "epub")

        # Check temp file was created
        temp_md = results / "temp" / "test-book-combined.md"
        assert temp_md.exists()

    def test_build_format_creates_output_directory(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test creates output directory structure."""
        import subprocess

        # Mock pandoc
        def mock_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        builder.build_format("test-book", "html")

        # Check output directory exists
        output_dir = results / "books" / "test-book"
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_epub_build_uses_correct_pandoc_options(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test EPUB build uses correct pandoc options."""
        import subprocess

        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        builder = BookBuilder(sources_dir=sources, results_dir=results)

        builder.build_format("test-book", "epub")

        # Check pandoc command
        assert "pandoc" in captured_cmd
        assert "--toc" in captured_cmd
        assert "--toc-depth=3" in captured_cmd
        assert any("lang=hu" in arg for arg in captured_cmd)
        assert any("title=Test Book" in arg for arg in captured_cmd)
        assert any("author=Test Author" in arg for arg in captured_cmd)

    def test_html_build_includes_css(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test HTML build includes CSS if available."""
        import subprocess

        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"
        builder = BookBuilder(sources_dir=sources, results_dir=results)
        builder.templates_dir = templates

        builder.build_format("test-book", "html")

        # Check CSS is included
        assert any("--css" in arg for arg in captured_cmd)

    def test_pdf_build_includes_latex_header(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test PDF build includes LaTeX header if available."""
        import subprocess

        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"
        builder = BookBuilder(sources_dir=sources, results_dir=results)
        builder.templates_dir = templates

        builder.build_format("test-book", "pdf")

        # Check LaTeX header is included
        assert any("--include-in-header" in arg for arg in captured_cmd)
        assert "--pdf-engine=pdflatex" in captured_cmd
