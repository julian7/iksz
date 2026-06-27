"""
IKSZ Build System - Integration Tests.

End-to-end tests for the complete build pipeline.
"""

import subprocess
from pathlib import Path

import pytest


class TestEndToEndBuild:
    """End-to-end integration tests for the build system."""

    def test_complete_book_build_workflow(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test complete workflow from YAML to all output formats."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output files for pandoc
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])

                # Create appropriate dummy content based on format
                if output_file.suffix == ".epub":
                    output_file.write_bytes(b"EPUB content")
                elif output_file.suffix == ".html":
                    output_file.write_text("<html><body>HTML</body></html>", encoding="utf-8")
                elif output_file.suffix == ".pdf":
                    output_file.write_bytes(b"PDF content")
                elif output_file.suffix == ".mobi":
                    output_file.write_bytes(b"MOBI content")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        builder = BookBuilder(sources_dir=sources, results_dir=results)
        builder.templates_dir = templates

        # Build all formats
        for fmt in ["epub", "html", "pdf"]:
            output = builder.build_format("test-book", fmt)
            assert output.exists()
            assert output.suffix == f".{fmt}"

    def test_html_site_generation_workflow(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test complete HTML site generation workflow."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.site import SiteGenerator

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        # Verify complete site structure
        assert (site_dir / "index.html").exists()
        assert (site_dir / "chapter-1.html").exists()
        assert (site_dir / "chapter-2.html").exists()
        assert (site_dir / "chapter-3.html").exists()
        assert (site_dir / "style.css").exists()

    def test_book_load_combine_build_pipeline(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test the load → combine → build pipeline."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_bytes(b"Output content")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        builder = BookBuilder(sources_dir=sources, results_dir=results)
        builder.templates_dir = templates

        # Step 1: Load book
        book = builder.load_book("test-book")
        assert book.title == "Test Book"

        # Step 2: Combine chapters
        combined = builder.combine_chapters(book)
        assert "# Chapter 1" in combined
        assert "# Chapter 2" in combined
        assert "# Chapter 3" in combined

        # Step 3: Build format
        output = builder.build_format("test-book", "epub")
        assert output.exists()


class TestMultipleBooks:
    """Tests for handling multiple books."""

    def test_builds_multiple_books(
        self,
        full_mock_project: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test building multiple books in sequence."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_bytes(b"Content")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"

        # Create second book definition
        book2_yaml = """
book:
  id: test-book-2
  title: "Second Book"
  version: "2.0"

chapters:
  - section: "Content"
    pages:
      - file: "core/chapter1.md"
"""
        yaml_path = sources / "books" / "test-book-2.yaml"
        yaml_path.write_text(book2_yaml, encoding="utf-8")

        builder = BookBuilder(sources_dir=sources, results_dir=results)

        # Build both books
        output1 = builder.build_format("test-book", "epub")
        output2 = builder.build_format("test-book-2", "epub")

        assert output1.exists()
        assert output2.exists()
        assert output1.name == "test-book-v1.0.epub"
        assert output2.name == "test-book-2-v2.0.epub"


class TestErrorHandling:
    """Tests for error handling in the build pipeline."""

    def test_handles_missing_book_definition(self, full_mock_project: Path) -> None:
        """Test handles missing book definition gracefully."""
        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"

        builder = BookBuilder(sources_dir=sources, results_dir=results)

        with pytest.raises(FileNotFoundError, match="Book definition not found"):
            builder.load_book("nonexistent-book")

    def test_handles_missing_chapter_file(
        self, full_mock_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handles missing chapter file gracefully."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"

        # Create book with missing chapter
        bad_yaml = """
book:
  title: "Bad Book"

chapters:
  - section: "Content"
    pages:
      - file: "core/missing-chapter.md"
"""
        yaml_path = sources / "books" / "bad-book.yaml"
        yaml_path.write_text(bad_yaml, encoding="utf-8")

        builder = BookBuilder(sources_dir=sources, results_dir=results)
        book = builder.load_book("bad-book")

        with pytest.raises(FileNotFoundError, match="Chapter file not found"):
            builder.combine_chapters(book)

    def test_handles_pandoc_failure(
        self, full_mock_project: Path, sample_book_yaml: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handles pandoc failure gracefully."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if cmd[0] == "pandoc":
                raise subprocess.CalledProcessError(1, cmd, stderr="Pandoc error")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"

        builder = BookBuilder(sources_dir=sources, results_dir=results)

        with pytest.raises(RuntimeError, match="Command failed"):
            builder.build_format("test-book", "epub")


class TestUnicodeAndHungarianSupport:
    """Tests for Unicode and Hungarian character support."""

    def test_preserves_hungarian_characters_in_yaml(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test preserves Hungarian characters in YAML metadata."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import Book

        sources = temp_dir / "sources"
        sources.mkdir(parents=True)

        books_dir = sources / "books"
        books_dir.mkdir()

        chapters_dir = sources / "core"
        chapters_dir.mkdir()

        # Create chapter with Hungarian chars
        chapter1 = chapters_dir / "ch1.md"
        chapter1.write_text("# Fejezet: Karakteralkotás\n\náéíóöőúüű", encoding="utf-8")

        # Create book with Hungarian metadata
        yaml_content = """
book:
  title: "Magyar Könyv"
  subtitle: "Alapszabályok és Értékek"
  author: "Fejlesztők"

chapters:
  - section: "Bevezetés"
    pages:
      - file: "core/ch1.md"
"""
        yaml_path = books_dir / "hungarian-book.yaml"
        yaml_path.write_text(yaml_content, encoding="utf-8")

        # Load and verify
        book = Book.from_yaml(yaml_path)
        assert book.title == "Magyar Könyv"
        assert book.subtitle == "Alapszabályok és Értékek"

    def test_preserves_hungarian_characters_in_output(
        self, full_mock_project: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test preserves Hungarian characters in combined output."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        from build.book import BookBuilder

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"

        builder = BookBuilder(sources_dir=sources, results_dir=results)
        book = builder.load_book("test-book")
        combined = builder.combine_chapters(book)

        # Chapter 2 has Hungarian characters
        assert "áéíóöőúüű" in combined
        assert "ÁÉÍÓÖŐÚÜŰ" in combined
