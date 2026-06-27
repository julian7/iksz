"""
IKSZ Build System - Python-based ebook build tool.

This package provides a modern, maintainable build system for converting
IKSZ markdown sources into multiple ebook formats (EPUB, HTML, MOBI, PDF).
"""

__version__ = "0.1.0"
__author__ = "IKSZ Developers"

from build.book import Book, BookBuilder
from build.formats import FormatGenerator
from build.site import SiteGenerator

__all__ = [
    "Book",
    "BookBuilder",
    "FormatGenerator",
    "SiteGenerator",
    "__version__",
    "__author__",
]
