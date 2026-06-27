"""
IKSZ Build System - Tests for formats module.

Tests for format generation (EPUB, HTML, MOBI, PDF).
"""

import subprocess
from pathlib import Path

import pytest

from build.formats import FormatGenerator


class TestFormatGenerator:
    """Tests for FormatGenerator class."""

    def test_initializes_with_defaults(self) -> None:
        """Test initializes with default templates directory."""
        generator = FormatGenerator()
        assert generator.templates_dir == Path("templates")

    def test_initializes_with_custom_dir(self, temp_dir: Path) -> None:
        """Test initializes with custom templates directory."""
        custom_templates = temp_dir / "custom_templates"
        generator = FormatGenerator(templates_dir=custom_templates)
        assert generator.templates_dir == custom_templates


class TestGenerateEPUB:
    """Tests for generate_epub method."""

    def test_calls_pandoc_with_correct_args(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test calls pandoc with correct arguments."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.epub"

        # Create dummy input file
        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_epub(input_file, output_file)

        assert "pandoc" in captured_cmd
        assert str(input_file) in captured_cmd
        assert str(output_file) in captured_cmd
        assert "--toc" in captured_cmd
        assert "--toc-depth=3" in captured_cmd

    def test_includes_metadata(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test includes metadata in pandoc command."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.epub"

        input_file.write_text("# Test", encoding="utf-8")

        metadata = {
            "title": "Test Book",
            "author": "Test Author",
            "lang": "hu",
        }

        generator.generate_epub(input_file, output_file, metadata)

        assert any("title=Test Book" in arg for arg in captured_cmd)
        assert any("author=Test Author" in arg for arg in captured_cmd)
        assert any("lang=hu" in arg for arg in captured_cmd)


class TestGenerateHTML:
    """Tests for generate_html method."""

    def test_calls_pandoc_with_correct_args(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test calls pandoc with correct arguments."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.html"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_html(input_file, output_file)

        assert "pandoc" in captured_cmd
        assert str(input_file) in captured_cmd
        assert str(output_file) in captured_cmd
        assert "--toc" in captured_cmd
        assert "--standalone" in captured_cmd

    def test_includes_css_if_exists(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test includes CSS file if it exists."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create CSS file
        css_file = templates_dir / "style.css"
        css_file.write_text("body { margin: 0; }", encoding="utf-8")

        generator = FormatGenerator(templates_dir=templates_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.html"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_html(input_file, output_file)

        assert "--css" in captured_cmd
        assert any("style.css" in arg for arg in captured_cmd)

    def test_does_not_include_css_if_missing(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test does not include CSS if file doesn't exist."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.html"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_html(input_file, output_file)

        assert "--css" not in captured_cmd

    def test_can_generate_non_standalone(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test can generate non-standalone HTML."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.html"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_html(input_file, output_file, standalone=False)

        assert "--standalone" not in captured_cmd


class TestGeneratePDF:
    """Tests for generate_pdf method."""

    def test_calls_pandoc_with_correct_args(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test calls pandoc with correct arguments for PDF."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.pdf"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_pdf(input_file, output_file)

        assert "pandoc" in captured_cmd
        assert str(input_file) in captured_cmd
        assert str(output_file) in captured_cmd
        assert "--pdf-engine=pdflatex" in captured_cmd
        assert "--toc" in captured_cmd

    def test_includes_latex_options(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test includes LaTeX-specific options."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.pdf"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_pdf(input_file, output_file)

        assert any("geometry:margin=1in" in arg for arg in captured_cmd)
        assert any("papersize=a4" in arg for arg in captured_cmd)
        assert any("documentclass=book" in arg for arg in captured_cmd)

    def test_includes_latex_header_if_exists(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test includes LaTeX header if it exists."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create LaTeX header
        latex_header = templates_dir / "latex-header.tex"
        latex_header.write_text(r"\usepackage[utf8]{inputenc}", encoding="utf-8")

        generator = FormatGenerator(templates_dir=templates_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.pdf"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_pdf(input_file, output_file)

        assert "--include-in-header" in captured_cmd
        assert any("latex-header.tex" in arg for arg in captured_cmd)

    def test_includes_lua_filter_if_exists(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test includes Lua filter if it exists."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        # Create Lua filter
        lua_filter = templates_dir / "columns-filter.lua"
        lua_filter.write_text("-- Lua filter", encoding="utf-8")

        generator = FormatGenerator(templates_dir=templates_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.pdf"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_pdf(input_file, output_file)

        assert "--lua-filter" in captured_cmd
        assert any("columns-filter.lua" in arg for arg in captured_cmd)

    def test_uses_custom_pdf_engine(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test can use custom PDF engine."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_cmd.extend(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.pdf"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_pdf(input_file, output_file, pdf_engine="xelatex")

        assert "--pdf-engine=xelatex" in captured_cmd


class TestGenerateMOBI:
    """Tests for generate_mobi method."""

    def test_generates_epub_first(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generates EPUB before converting to MOBI."""
        calls: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(cmd[0])
            # Create dummy files so conversion can proceed
            if cmd[0] == "pandoc" and cmd[-1].endswith(".epub"):
                # Create the temp EPUB file
                Path(cmd[-1]).touch()
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.mobi"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_mobi(input_file, output_file)

        # First call should be pandoc (for EPUB), second should be ebook-convert
        assert calls[0] == "pandoc"
        assert calls[1] == "ebook-convert"

    def test_cleans_up_temp_epub(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cleans up temporary EPUB file."""

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            # Create dummy files so conversion can proceed
            if cmd[0] == "pandoc" and cmd[-1].endswith(".epub"):
                # Create the temp EPUB file
                Path(cmd[-1]).touch()
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.mobi"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_mobi(input_file, output_file)

        # Temp EPUB should be cleaned up
        temp_epub = output_file.parent / f"{output_file.stem}-temp.epub"
        assert not temp_epub.exists()

    def test_calls_ebook_convert(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test calls ebook-convert with correct arguments."""
        captured_cmd: list[str] = []

        def mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if cmd[0] == "ebook-convert":
                captured_cmd.extend(cmd)
            # Create dummy files
            if cmd[0] == "pandoc" and cmd[-1].endswith(".epub"):
                Path(cmd[-1]).touch()
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        monkeypatch.setattr("subprocess.run", mock_run)

        generator = FormatGenerator(templates_dir=temp_dir)
        input_file = temp_dir / "input.md"
        output_file = temp_dir / "output.mobi"

        input_file.write_text("# Test", encoding="utf-8")

        generator.generate_mobi(input_file, output_file)

        assert "ebook-convert" in captured_cmd
        assert any(".epub" in arg for arg in captured_cmd)
        assert str(output_file) in captured_cmd
