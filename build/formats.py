"""
IKSZ Build System - Format Generator Module.

This module handles generating different output formats from markdown sources.
"""

from pathlib import Path

from build.utils import run_command


class FormatGenerator:
    """Generates various output formats from markdown sources."""

    def __init__(self, templates_dir: Path | None = None):
        """
        Initialize FormatGenerator.

        Args:
            templates_dir: Directory containing templates. Defaults to 'templates'.
        """
        self.templates_dir = templates_dir or Path("templates")

    def generate_epub(
        self,
        input_file: Path,
        output_file: Path,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Generate EPUB format from markdown.

        Args:
            input_file: Path to input markdown file.
            output_file: Path to output EPUB file.
            metadata: Optional metadata dictionary (title, author, lang, etc.).
        """
        metadata = metadata or {}

        cmd = [
            "pandoc",
            str(input_file),
            "-o",
            str(output_file),
            "--toc",
            "--toc-depth=3",
        ]

        # Add metadata
        for key, value in metadata.items():
            cmd.extend(["--metadata", f"{key}={value}"])

        run_command(cmd)

    def generate_html(
        self,
        input_file: Path,
        output_file: Path,
        metadata: dict[str, str] | None = None,
        standalone: bool = True,
    ) -> None:
        """
        Generate HTML format from markdown.

        Args:
            input_file: Path to input markdown file.
            output_file: Path to output HTML file.
            metadata: Optional metadata dictionary.
            standalone: Whether to generate standalone HTML with headers.
        """
        metadata = metadata or {}

        cmd = [
            "pandoc",
            str(input_file),
            "-o",
            str(output_file),
            "--toc",
            "--toc-depth=3",
        ]

        if standalone:
            cmd.append("--standalone")

        # Add metadata
        for key, value in metadata.items():
            cmd.extend(["--metadata", f"{key}={value}"])

        # Add CSS if it exists
        css_file = self.templates_dir / "style.css"
        if css_file.exists():
            cmd.extend(["--css", str(css_file)])

        run_command(cmd)

    def generate_pdf(
        self,
        input_file: Path,
        output_file: Path,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Generate PDF format from markdown.

        Args:
            input_file: Path to input markdown file.
            output_file: Path to output PDF file.
            metadata: Optional metadata dictionary.
        """
        metadata = metadata or {}
        temp_typ = output_file.with_suffix(".typ")

        cmd = [
            "pandoc",
            str(input_file),
            "-o",
            str(temp_typ),
            "--to=typst",
            "--toc",
            "--toc-depth=3",
        ]

        # Add metadata
        for key, value in metadata.items():
            cmd.extend(["--metadata", f"{key}={value}"])

        typst_template = self.templates_dir / "template.typ"
        if typst_template.exists():
            cmd.extend(["--template", str(typst_template)])

        typst_filter = self.templates_dir / "typst-filter.lua"
        if typst_filter.exists():
            cmd.extend(["--lua-filter", str(typst_filter)])

        run_command(cmd)
        run_command(["typst", "compile", str(temp_typ), str(output_file)])

    def generate_mobi(
        self,
        input_file: Path,
        output_file: Path,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Generate MOBI format from markdown (via EPUB conversion).

        Args:
            input_file: Path to input markdown file.
            output_file: Path to output MOBI file.
            metadata: Optional metadata dictionary.
        """
        # First generate EPUB with .epub extension so ebook-convert recognizes it
        temp_epub = output_file.parent / f"{output_file.stem}-temp.epub"
        self.generate_epub(input_file, temp_epub, metadata)

        # Convert EPUB to MOBI using calibre
        cmd = ["ebook-convert", str(temp_epub), str(output_file)]
        run_command(cmd)

        # Clean up temporary EPUB
        if temp_epub.exists():
            temp_epub.unlink()
