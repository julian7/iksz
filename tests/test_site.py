"""
IKSZ Build System - Tests for site module.

Tests for multi-page HTML site generation.
"""

import subprocess
from pathlib import Path

import pytest

from build.site import SiteGenerator


class TestSiteGenerator:
    """Tests for SiteGenerator class."""

    def test_initializes_with_defaults(self) -> None:
        """Test initializes with default directories."""
        generator = SiteGenerator()
        assert generator.sources_dir == Path("sources")
        assert generator.results_dir == Path("results")
        assert generator.templates_dir == Path("templates")

    def test_initializes_with_custom_dirs(self, temp_dir: Path) -> None:
        """Test initializes with custom directories."""
        sources = temp_dir / "custom_sources"
        results = temp_dir / "custom_results"
        templates = temp_dir / "custom_templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )
        assert generator.sources_dir == sources
        assert generator.results_dir == results
        assert generator.templates_dir == templates


class TestBuildSite:
    """Tests for build_site method."""

    def test_creates_site_directory(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test creates site output directory."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output file if pandoc is called
            if cmd[0] == "pandoc" and "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        assert site_dir.exists()
        assert site_dir.is_dir()
        assert site_dir == results / "html" / "test-book"

    def test_generates_index_page(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test generates index.html."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output file if pandoc is called
            if cmd[0] == "pandoc" and "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")
        index_file = site_dir / "index.html"

        assert index_file.exists()

        # Check index content
        content = index_file.read_text(encoding="utf-8")
        assert "Test Book" in content
        assert "Tartalomjegyzék" in content  # Table of contents
        assert "chapter-1.html" in content
        assert "chapter-2.html" in content
        assert "chapter-3.html" in content

    def test_generates_chapter_pages(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test generates individual chapter pages."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy HTML output
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        # Should have 3 chapter pages
        assert (site_dir / "chapter-1.html").exists()
        assert (site_dir / "chapter-2.html").exists()
        assert (site_dir / "chapter-3.html").exists()

    def test_copies_css_if_exists(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test copies CSS file to site directory."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")
        css_file = site_dir / "style.css"

        assert css_file.exists()


class TestGenerateIndex:
    """Tests for _generate_index method."""

    def test_includes_book_metadata(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test index includes book metadata."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output file if pandoc is called
            if cmd[0] == "pandoc" and "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")
        index_file = site_dir / "index.html"
        content = index_file.read_text(encoding="utf-8")

        assert "Test Book" in content
        assert "A Test Subtitle" in content
        assert "Verzió: 1.0" in content

    def test_includes_table_of_contents(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test index includes table of contents."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output file if pandoc is called
            if cmd[0] == "pandoc" and "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")
        index_file = site_dir / "index.html"
        content = index_file.read_text(encoding="utf-8")

        # Should have section names
        assert "Introduction" in content
        assert "Main Content" in content

        # Should have chapter links
        assert 'href="chapter-1.html"' in content
        assert 'href="chapter-2.html"' in content
        assert 'href="chapter-3.html"' in content

    def test_includes_footer(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test index includes footer with author and rights."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy output file if pandoc is called
            if cmd[0] == "pandoc" and "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")
        index_file = site_dir / "index.html"
        content = index_file.read_text(encoding="utf-8")

        assert "Test Author" in content
        assert "Test Publisher" in content
        assert "Creative Commons BY-SA 4.0" in content


class TestGenerateChapterPage:
    """Tests for _generate_chapter_page method."""

    def test_calls_pandoc_for_each_chapter(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test calls pandoc for each chapter."""
        pandoc_calls = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if cmd[0] == "pandoc":
                pandoc_calls.append(cmd)
                # Create dummy output
                if "-o" in cmd:
                    output_idx = cmd.index("-o") + 1
                    output_file = Path(cmd[output_idx])
                    output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        generator.build_site("test-book")

        # Should have called pandoc 3 times (one for each chapter)
        assert len(pandoc_calls) == 3

    def test_includes_css_reference(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test chapter pages include CSS reference."""
        captured_cmds: list[list[str]] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if cmd[0] == "pandoc":
                captured_cmds.append(cmd)
                if "-o" in cmd:
                    output_idx = cmd.index("-o") + 1
                    output_file = Path(cmd[output_idx])
                    output_file.write_text("<html><body>Test</body></html>", encoding="utf-8")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        generator.build_site("test-book")

        # All pandoc calls should include CSS
        for cmd in captured_cmds:
            assert "--css" in cmd
            assert "style.css" in " ".join(cmd)


class TestAddNavigation:
    """Tests for _add_navigation method."""

    def test_adds_navigation_to_html(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test adds navigation links to chapter HTML."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text(
                    "<html><body>Chapter content</body></html>", encoding="utf-8"
                )
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        # Check middle chapter (should have prev and next)
        chapter2 = site_dir / "chapter-2.html"
        content = chapter2.read_text(encoding="utf-8")

        assert "chapter-nav" in content
        assert 'href="chapter-1.html"' in content  # Previous
        assert 'href="index.html"' in content  # Contents
        assert 'href="chapter-3.html"' in content  # Next

    def test_first_chapter_has_no_previous(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test first chapter has no previous link."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text(
                    "<html><body>Chapter content</body></html>", encoding="utf-8"
                )
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        chapter1 = site_dir / "chapter-1.html"
        content = chapter1.read_text(encoding="utf-8")

        assert "disabled" in content  # Previous link should be disabled
        assert 'href="chapter-2.html"' in content  # Next should work

    def test_last_chapter_has_no_next(
        self,
        full_mock_project: Path,
        sample_book_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test last chapter has no next link."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if "-o" in cmd:
                output_idx = cmd.index("-o") + 1
                output_file = Path(cmd[output_idx])
                output_file.write_text(
                    "<html><body>Chapter content</body></html>", encoding="utf-8"
                )
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        sources = full_mock_project / "sources"
        results = full_mock_project / "results"
        templates = full_mock_project / "templates"

        generator = SiteGenerator(
            sources_dir=sources,
            results_dir=results,
            templates_dir=templates,
        )

        site_dir = generator.build_site("test-book")

        chapter3 = site_dir / "chapter-3.html"
        content = chapter3.read_text(encoding="utf-8")

        assert 'href="chapter-2.html"' in content  # Previous should work
        # Next should be disabled (check for disabled class or no href to chapter-4)
        assert 'href="chapter-4.html"' not in content
