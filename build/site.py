"""
IKSZ Build System - HTML Site Generator Module.

This module handles generating multi-page HTML sites from book definitions.
"""

import shutil
from pathlib import Path
from typing import Any

from build.book import Book, BookBuilder
from build.utils import ensure_dir, run_command


class SiteGenerator:
    """Generates multi-page HTML sites from books."""

    def __init__(
        self,
        sources_dir: Path | None = None,
        results_dir: Path | None = None,
        templates_dir: Path | None = None,
    ):
        """
        Initialize SiteGenerator.

        Args:
            sources_dir: Directory containing source files. Defaults to 'sources'.
            results_dir: Directory for output files. Defaults to 'results'.
            templates_dir: Directory containing templates. Defaults to 'templates'.
        """
        self.sources_dir = sources_dir or Path("sources")
        self.results_dir = results_dir or Path("results")
        self.templates_dir = templates_dir or Path("templates")
        self.book_builder = BookBuilder(sources_dir, results_dir)

    def build_site(self, book_id: str) -> Path:
        """
        Generate multi-page HTML site for a book.

        Args:
            book_id: Book identifier.

        Returns:
            Path to generated site directory.

        Raises:
            FileNotFoundError: If book definition doesn't exist.
        """
        # Load book definition
        book = self.book_builder.load_book(book_id)

        # Prepare output directory
        site_dir = ensure_dir(self.results_dir / "html" / book_id)

        # Generate index page
        self._generate_index(book, site_dir)

        # Generate chapter pages
        chapter_num = 1
        for section in book.sections:
            print(section.name)
            for chapter in section.chapters:
                print(f"  {chapter.title}")
                self._generate_chapter_page(book, chapter, chapter_num, site_dir)
                chapter_num += 1

        # Copy CSS if it exists
        self._copy_css(site_dir)

        # Copy images directory if it exists
        self._copy_images(book, site_dir)

        return site_dir

    def _generate_index(self, book: Book, site_dir: Path) -> None:
        """
        Generate index.html for the site.

        Args:
            book: Book to generate index for.
            site_dir: Site output directory.
        """
        lines = []

        # HTML header
        lines.append("<!DOCTYPE html>")
        lines.append('<html lang="hu">')
        lines.append("<head>")
        lines.append('    <meta charset="UTF-8">')
        lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        lines.append(f"    <title>{book.info.title}</title>")
        lines.append('    <link rel="stylesheet" href="style.css">')
        lines.append("</head>")
        lines.append("<body>")

        # Title
        lines.append(f"    <h1>{book.info.title}</h1>")
        if book.info.subtitle:
            lines.append(f"    <p class='subtitle'>{book.info.subtitle}</p>")
        lines.append(f"    <p>Kiadás: {book.info.released}</p>")

        # Table of contents
        lines.append("    <h2>Tartalomjegyzék</h2>")
        lines.append("    <nav>")
        lines.append("        <ul>")

        chapter_num = 1
        for section in book.sections:
            if section.name:
                lines.append(f"            <li><strong>{section.name}</strong>")
                lines.append("                <ul>")

            for chapter in section.chapters:
                chapter_title = chapter.title or f"Chapter {chapter_num}"
                lines.append(
                    f'                    <li><a href="chapter-{chapter_num}.html">'
                    f"{chapter_title}</a></li>"
                )
                chapter_num += 1

            if section.name:
                lines.append("                </ul>")
                lines.append("            </li>")

        lines.append("        </ul>")
        lines.append("    </nav>")

        # Footer
        lines.append("    <footer>")
        lines.append(f"        <p>{book.info.author} • {book.info.publisher}</p>")
        lines.append(f"        <p>{book.info.rights}</p>")
        lines.append("    </footer>")

        lines.append("</body>")
        lines.append("</html>")

        # Write index.html
        index_file = site_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _generate_chapter_page(
        self, book: Book, chapter: Any, chapter_num: int, site_dir: Path
    ) -> None:
        """
        Generate HTML page for a single chapter.

        Args:
            book: Book containing the chapter.
            chapter: Chapter to generate page for.
            chapter_num: Chapter number (1-based).
            site_dir: Site output directory.
        """
        chapter_path = self.sources_dir / chapter.file

        if not chapter_path.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_path}")

        # Convert chapter markdown to HTML
        output_file = site_dir / f"chapter-{chapter_num}.html"

        cmd = [
            "pandoc",
            str(chapter_path),
            "-o",
            str(output_file),
            "--standalone",
            "--metadata",
            f"lang={book.info.language}",
            "--metadata",
            f"title={chapter.title or f'Chapter {chapter_num}'}",
        ]

        # Add CSS if it exists
        css_file = self.templates_dir / "style.css"
        if css_file.exists():
            cmd.extend(["--css", "style.css"])

        # Add Lua filter for floating tables and columns (same as PDF and single-page HTML)
        lua_filter = self.templates_dir / "columns-filter.lua"
        if lua_filter.exists():
            cmd.extend(["--lua-filter", str(lua_filter)])

        # Add resource path for images
        book_source_dir = self.sources_dir / book.info.id
        cmd.extend(["--resource-path", f"{book_source_dir}:{self.sources_dir}"])

        run_command(cmd)

        # Add navigation links to the generated HTML
        self._add_navigation(output_file, chapter_num, len(book.get_all_chapters()))

    def _add_navigation(self, html_file: Path, chapter_num: int, total_chapters: int) -> None:
        """
        Add navigation links to chapter HTML file.

        Args:
            html_file: Path to HTML file to modify.
            chapter_num: Current chapter number (1-based).
            total_chapters: Total number of chapters.
        """
        # Read existing HTML
        with open(html_file, encoding="utf-8") as f:
            content = f.read()

        # Build navigation HTML
        nav_html = ['<nav class="chapter-nav">']

        if chapter_num > 1:
            nav_html.append(f'    <a href="chapter-{chapter_num - 1}.html">← Previous</a>')
        else:
            nav_html.append('    <span class="disabled">← Previous</span>')

        nav_html.append('    <a href="index.html">↑ Contents</a>')

        if chapter_num < total_chapters:
            nav_html.append(f'    <a href="chapter-{chapter_num + 1}.html">Next →</a>')
        else:
            nav_html.append('    <span class="disabled">Next →</span>')

        nav_html.append("</nav>")

        nav_string = "\n".join(nav_html)

        # Insert navigation before </body>
        content = content.replace("</body>", f"{nav_string}\n</body>")

        # Write modified HTML
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(content)

    def _copy_css(self, site_dir: Path) -> None:
        """
        Copy CSS file to site directory.

        Args:
            site_dir: Site output directory.
        """
        css_source = self.templates_dir / "style.css"
        if css_source.exists():
            css_dest = site_dir / "style.css"
            shutil.copy2(css_source, css_dest)

    def _copy_images(self, book: Book, site_dir: Path) -> None:
        """
        Copy images directory to site directory.

        Args:
            book: Book to copy images for.
            site_dir: Site output directory.
        """
        # Check if book has an images directory
        images_dir = self.sources_dir / book.info.id / "images"

        if not images_dir.exists():
            return

        # Create images directory in site output
        output_images_dir = site_dir / "images"

        # Remove existing images directory if present
        if output_images_dir.exists():
            shutil.rmtree(output_images_dir)

        # Copy images directory
        shutil.copytree(images_dir, output_images_dir)
