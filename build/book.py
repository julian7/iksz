"""
IKSZ Build System - Book Building Module.

This module handles building complete books from YAML definitions.
It reads book configuration, combines chapters, and generates multiple output formats.
"""

import shutil
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from build.utils import ensure_dir, run_command


class Chapter(BaseModel):
    """Represents a single chapter in a book."""

    file: str
    title: str | None = None


class Section(BaseModel):
    """Represents a section containing multiple chapters."""

    name: str = Field(alias="section", default="")
    chapters: list[Chapter] = Field(default_factory=list, alias="pages")
    include_in_toc: bool = True


class BookInfo(BaseModel):
    """Represents a complete book with metadata and chapters."""

    id: str = ""
    title: str
    version: str = "1.0"
    released: str = ""
    language: str = "hu"
    author: str = "IKSZ Fejlesztők"
    compiled_by: str = ""
    subtitle: str = ""
    description: str = ""
    publisher: str = "IKSZ Projekt"
    rights: str = "Creative Commons BY-SA 4.0"
    sections: list[Section] = Field(default_factory=list)

    def get_output_filename(self, format: str) -> str:
        return f"{self.id}.{format}"


class Book(BaseModel):
    """Represents a publication containing multiple aspects of a book."""

    info: BookInfo = Field(alias="book")
    sections: list[Section] = Field(alias="chapters")

    def get_all_chapters(self) -> list[Chapter]:
        """Get flat list of all chapters from all sections."""
        all_chapters = []
        for section in self.sections:
            all_chapters.extend(section.chapters)
        return all_chapters

    def get_output_filename(self, format: str) -> str:
        return self.info.get_output_filename(format)


class BookBuilder:
    """Builds books from YAML definitions into multiple formats."""

    def __init__(self, sources_dir: Path | None = None, results_dir: Path | None = None):
        """
        Initialize BookBuilder.

        Args:
            sources_dir: Directory containing source files. Defaults to 'sources'.
            results_dir: Directory for output files. Defaults to 'results'.
        """
        self.sources_dir = sources_dir or Path("sources")
        self.results_dir = results_dir or Path("results")
        self.templates_dir = Path("templates")

    def load_book(self, book_id: str) -> Book:
        """
        Load book definition by ID.

        Args:
            book_id: Book identifier (filename without .yaml extension).

        Returns:
            Book instance.

        Raises:
            FileNotFoundError: If book definition doesn't exist.
        """
        yaml_path = self.sources_dir / "books" / f"{book_id}.yaml"

        if not yaml_path.exists():
            raise FileNotFoundError(f"Book definition not found: {yaml_path}")

        with open(yaml_path, encoding="utf-8") as f:
            yaml_path = yaml.safe_load(f)

        if isinstance(yaml_path, dict):
            book_info = yaml_path.get("book")
            if isinstance(book_info, dict) and not book_info.get("id"):
                book_info["id"] = book_id

        return Book.model_validate(yaml_path)

    def combine_chapters(self, book: Book) -> str:
        """
        Combine all chapters into a single markdown document.

        Args:
            book: Book to combine chapters from.

        Returns:
            Combined markdown content as string.
        """
        lines = []

        # Add YAML frontmatter
        lines.append("---")
        lines.append(f'title: "{book.info.title}"')
        if book.info.subtitle:
            lines.append(f'subtitle: "{book.info.subtitle}"')
        lines.append(f'author: "{book.info.author}"')
        if book.info.compiled_by:
            lines.append(f'compiled_by: "{book.info.compiled_by}"')
        lines.append(f"lang: {book.info.language}")
        lines.append(f"version: {book.info.version}")
        lines.append(f"released: {book.info.released}")
        lines.append("---")
        lines.append("")

        # Add chapters from all sections
        chapter_num = 1
        for section in book.sections:
            # Add section header if it has a name
            if section.name:
                name = section.name
                if not section.include_in_toc:
                    name += " { .unlisted }"
                lines.append(f"# {name}")
                lines.append("")

            # Add chapters in this section
            for chapter in section.chapters:
                chapter_path = self.sources_dir / chapter.file

                if not chapter_path.exists():
                    raise FileNotFoundError(f"Chapter file not found: {chapter_path}")

                # Read chapter content
                with open(chapter_path, encoding="utf-8") as f:
                    content = f.read()

                # Add chapter content
                lines.append(content)
                lines.append("")

                chapter_num += 1

        return "\n".join(lines)

    def build_format(self, book_id: str, format: str) -> Path:
        """
        Build a book in a specific format.

        Args:
            book_id: Book identifier.
            format: Output format (epub, html, mobi, pdf).

        Returns:
            Path to generated file.

        Raises:
            ValueError: If format is not supported.
            subprocess.CalledProcessError: If build fails.
        """
        supported_formats = ["epub", "html", "mobi", "pdf"]
        if format not in supported_formats:
            raise ValueError(f"Unsupported format: {format}. Choose from {supported_formats}")

        # Load book definition
        book = self.load_book(book_id)

        # Prepare output directory
        output_dir = ensure_dir(self.results_dir / "books" / book_id)
        output_file = output_dir / book.get_output_filename(format)

        # Create temporary combined markdown file
        temp_dir = ensure_dir(self.results_dir / "temp")
        temp_md = temp_dir / f"{book_id}-combined.md"

        # Combine chapters
        combined_content = self.combine_chapters(book)

        # Write combined markdown
        with open(temp_md, "w", encoding="utf-8") as f:
            f.write(combined_content)

        # Build the format using pandoc
        if format == "epub":
            self._build_epub(temp_md, output_file, book)
        elif format == "html":
            self._build_html(temp_md, output_file, book)
        elif format == "mobi":
            self._build_mobi(temp_md, output_file, book)
        elif format == "pdf":
            self._build_pdf(temp_md, output_file, book)

        return output_file

    def _build_epub(self, input_md: Path, output_file: Path, book: Book) -> None:
        """Build EPUB format."""
        # Get the book's source directory for resource resolution
        book_source_dir = self.sources_dir / book.info.id

        cmd = [
            "pandoc",
            str(input_md),
            "-o",
            str(output_file),
            "--toc",
            "--toc-depth=2",
            "--resource-path",
            f"{book_source_dir}:{self.sources_dir}",
            "--metadata",
            f"lang={book.info.language}",
            "--metadata",
            f"title={book.info.title}",
            "--metadata",
            f"author={book.info.author}",
        ]

        run_command(cmd)

    def _build_html(self, input_md: Path, output_file: Path, book: Book) -> None:
        """Build single-page HTML format."""
        # Get the book's source directory for resource resolution
        book_source_dir = self.sources_dir / book.info.id

        cmd = [
            "pandoc",
            str(input_md),
            "-o",
            str(output_file),
            "--standalone",
            "--toc",
            "--toc-depth=2",
            "--resource-path",
            f"{book_source_dir}:{self.sources_dir}",
            "--metadata",
            f"lang={book.info.language}",
            "--metadata",
            f"title={book.info.title}",
            "--metadata",
            f"author={book.info.author}",
        ]

        # Add CSS if it exists
        css_file = self.templates_dir / "style.css"
        if css_file.exists():
            cmd.extend(["--css", str(css_file)])

        # Add Lua filter for floating tables and columns (same as PDF)
        lua_filter = self.templates_dir / "columns-filter.lua"
        if lua_filter.exists():
            cmd.extend(["--lua-filter", str(lua_filter)])

        run_command(cmd)

        # Copy images directory if it exists for HTML
        self._copy_images_for_html(book, output_file)

    def _copy_images_for_html(self, book: Book, output_file: Path) -> None:
        """Copy images directory to HTML output location."""
        # Check if book has an images directory
        images_dir = self.sources_dir / book.info.id / "images"

        if not images_dir.exists():
            return

        # Create images directory next to HTML output
        output_images_dir = output_file.parent / "images"

        # Remove existing images directory if present
        if output_images_dir.exists():
            shutil.rmtree(output_images_dir)

        # Copy images directory
        shutil.copytree(images_dir, output_images_dir)

    def _build_mobi(self, input_md: Path, output_file: Path, book: Book) -> None:
        """Build MOBI format (via EPUB conversion)."""
        # First build EPUB with .epub extension so ebook-convert recognizes it
        temp_epub = output_file.parent / f"{output_file.stem}-temp.epub"
        self._build_epub(input_md, temp_epub, book)

        # Convert EPUB to MOBI using calibre
        cmd = ["ebook-convert", str(temp_epub), str(output_file)]

        run_command(cmd)

        # Clean up temp EPUB
        if temp_epub.exists():
            temp_epub.unlink()

    def _build_pdf(self, input_md: Path, output_file: Path, book: Book) -> None:
        """Build PDF format."""
        # Get the book's source directory for resource resolution
        book_source_dir = self.sources_dir / book.info.id

        temp_typ = output_file.with_suffix(".typ")

        cmd = [
            "pandoc",
            str(input_md),
            "-o",
            str(temp_typ),
            "--to=typst",
            "--toc",
            "--toc-depth=2",
            "--resource-path",
            f"{book_source_dir}:{self.sources_dir}",
            "--metadata",
            f"lang={book.info.language}",
            "--metadata",
            f"title={book.info.title}",
            "--metadata",
            f"author={book.info.author}",
        ]

        typst_template = self.templates_dir / "template.typ"
        if typst_template.exists():
            cmd.extend(["--template", str(typst_template)])

        typst_filter = self.templates_dir / "typst-filter.lua"
        if typst_filter.exists():
            cmd.extend(["--lua-filter", str(typst_filter)])

        run_command(cmd)
        run_command(["typst", "compile", str(temp_typ), str(output_file)])
