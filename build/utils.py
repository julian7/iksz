"""
IKSZ Build System - Utility Functions.

Common utility functions used across the build system.
"""

import subprocess
import unicodedata
from pathlib import Path


def find_book_definitions(books_dir: Path | None = None) -> list[Path]:
    """
    Find all YAML book definition files.

    Args:
        books_dir: Directory containing book definitions. Defaults to sources/books.

    Returns:
        List of paths to YAML book definition files.
    """
    if books_dir is None:
        books_dir = Path("sources/books")

    if not books_dir.exists():
        return []

    return sorted(books_dir.glob("*.yaml"))


def find_chapters(chapters_dir: Path | None = None) -> list[Path]:
    """
    Find all markdown chapter files.

    Args:
        chapters_dir: Directory containing chapters. Defaults to sources/core.

    Returns:
        List of paths to markdown files.
    """
    if chapters_dir is None:
        chapters_dir = Path("sources/core")

    if not chapters_dir.exists():
        return []

    return sorted(chapters_dir.rglob("*.md"))


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    capture_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """
    Run a shell command with proper error handling.

    Args:
        cmd: Command and arguments as list.
        cwd: Working directory for command.
        capture_output: Whether to capture stdout/stderr.
        check: Whether to raise exception on non-zero exit.

    Returns:
        CompletedProcess instance.

    Raises:
        subprocess.CalledProcessError: If command fails and check=True.
        RuntimeError: If command fails with stderr output.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result
    except FileNotFoundError as e:
        # Command not found
        error_msg = f"Command not found: {cmd[0]}"
        raise RuntimeError(error_msg) from e
    except subprocess.CalledProcessError as e:
        # Re-raise with stderr included in the error message
        error_msg = f"Command failed: {' '.join(cmd)}\n"
        if e.stderr:
            error_msg += f"Error output:\n{e.stderr}"
        raise RuntimeError(error_msg) from e


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists.

    Returns:
        The path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string (e.g., "1m 30s", "45s", "2h 15m").
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_size(bytes_count: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        bytes_count: Size in bytes.

    Returns:
        Formatted string (e.g., "1.5KB", "234MB").
    """
    if bytes_count < 1024:
        return f"{bytes_count}B"
    elif bytes_count < 1024 * 1024:
        kb = bytes_count / 1024
        return f"{kb:.0f}KB"
    elif bytes_count < 1024 * 1024 * 1024:
        mb = bytes_count / (1024 * 1024)
        return f"{mb:.1f}MB"
    else:
        gb = bytes_count / (1024 * 1024 * 1024)
        return f"{gb:.2f}GB"


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to project root.
    """
    # Assume we're in build/ module, project root is parent
    return Path(__file__).parent.parent


def detect_pdf_engine() -> str | None:
    """
    Detect available PDF engine.

    Returns:
        Name of available PDF engine or None if none found.
    """
    engines = ["typst"]

    for engine in engines:
        try:
            subprocess.run(
                [engine, "--version"],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return engine
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return None


def check_dependencies() -> dict[str, bool]:
    """
    Check if required external tools are available.

    Returns:
        Dictionary mapping tool names to availability status.
    """
    tools = {
        "pandoc": ["pandoc", "--version"],
        "ebook-convert": ["ebook-convert", "--version"],
        "typst": ["typst", "--version"],
    }

    status: dict[str, bool] = {}

    for tool, cmd in tools.items():
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=False,
                timeout=5,
            )
            status[tool] = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            status[tool] = False

    return status


def get_file_size(path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        path: Path to file.

    Returns:
        File size in bytes, or 0 if file doesn't exist.
    """
    if path.exists():
        return path.stat().st_size
    return 0


def slugify(text: str) -> str:
    """
    Convert text to a safe filename slug.

    Transliterates accented characters to ASCII equivalents,
    converts to lowercase, replaces spaces with hyphens,
    and removes non-alphanumeric characters.

    Args:
        text: Text to slugify.

    Returns:
        Safe filename string.

    Examples:
        >>> slugify("IKSZ Alapszabály")
        'iksz-alapszabaly'
        >>> slugify("Tárgyak és Értékek")
        'targyak-es-ertekek'
    """
    # Normalize to NFD (decomposed form) - splits accented chars into base + accent
    normalized = unicodedata.normalize("NFD", text)

    # Filter out combining characters (category Mn = Mark, nonspacing)
    # This removes the accent marks, leaving just the base characters
    ascii_text = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # Convert to lowercase and replace spaces with hyphens
    slug = ascii_text.lower().replace(" ", "-")

    # Keep only alphanumeric characters and hyphens
    slug = "".join(c for c in slug if c.isalnum() or c == "-")

    # Remove multiple consecutive hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug
