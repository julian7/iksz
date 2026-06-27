"""
IKSZ Build System - CLI Entry Point.

This module provides the command-line interface for the IKSZ build system.
Uses Click for argument parsing and Rich for beautiful terminal output.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from build import __version__
from build.book import BookBuilder
from build.site import SiteGenerator
from build.utils import find_book_definitions, format_duration

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """
    IKSZ Build System - Build ebooks in multiple formats.

    Convert IKSZ markdown sources to EPUB, HTML, MOBI, and PDF formats.
    """
    if version:
        console.print(f"[bold cyan]IKSZ Build System[/bold cyan] v{__version__}")
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        # No subcommand provided, show help
        console.print(ctx.get_help())


@main.command()
@click.argument("book_id", required=False)
@click.option(
    "--format",
    "-f",
    multiple=True,
    type=click.Choice(["epub", "html", "mobi", "pdf"], case_sensitive=False),
    help="Build specific format(s). Can be specified multiple times.",
)
@click.option("--all-formats", is_flag=True, help="Build all formats (default)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress verbose output")
def book(
    book_id: str | None,
    format: tuple[str, ...],
    all_formats: bool,
    quiet: bool,
) -> None:
    """
    Build a single book or all books.

    BOOK_ID is the book identifier (e.g., 'core-rulebook').
    If omitted, builds all books.

    Examples:

        iksz-build book core-rulebook          # Build one book, all formats

        iksz-build book core-rulebook -f epub  # Build just EPUB

        iksz-build book                        # Build all books
    """
    try:
        if book_id:
            _build_single_book(book_id, format or (), all_formats, quiet)
        else:
            _build_all_books(format or (), all_formats, quiet)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.argument("book_id", required=False)
@click.option("--quiet", "-q", is_flag=True, help="Suppress verbose output")
def site(book_id: str | None, quiet: bool) -> None:
    """
    Generate multi-page HTML site for a book.

    BOOK_ID is the book identifier (e.g., 'core-rulebook').
    If omitted, generates sites for all books.

    Examples:

        iksz-build site core-rulebook  # Generate one site

        iksz-build site                # Generate all sites
    """
    try:
        if book_id:
            _build_single_site(book_id, quiet)
        else:
            _build_all_sites(quiet)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--format",
    "-f",
    multiple=True,
    type=click.Choice(["epub", "html", "mobi", "pdf"], case_sensitive=False),
    help="Build specific format(s)",
)
@click.option("--books/--no-books", default=True, help="Build books (default: yes)")
@click.option("--sites/--no-sites", default=True, help="Build HTML sites (default: yes)")
@click.option("--parallel", "-p", is_flag=True, help="Build books in parallel")
@click.option("--clean", is_flag=True, help="Clean results directory first")
@click.option("--quiet", "-q", is_flag=True, help="Suppress verbose output")
def all(
    format: tuple[str, ...],
    books: bool,
    sites: bool,
    parallel: bool,
    clean: bool,
    quiet: bool,
) -> None:
    """
    Build everything - all books and HTML sites.

    This is the master build command that orchestrates building all books
    in all formats and generating HTML sites.

    Examples:

        iksz-build all                 # Build everything

        iksz-build all --clean         # Clean rebuild

        iksz-build all --books --no-sites  # Just books

        iksz-build all -f epub -f pdf  # Just EPUB and PDF
    """
    import time

    start_time = time.time()

    try:
        if clean:
            _clean_results(quiet)

        if not quiet:
            console.print(
                Panel.fit(
                    "[bold cyan]IKSZ Build System[/bold cyan]\n"
                    f"Building: {'books' if books else ''} "
                    f"{'sites' if sites else ''}\n"
                    f"Parallel: {parallel}",
                    title="Master Build",
                )
            )

        stats = {"books": 0, "sites": 0, "failed": 0}

        if books:
            stats["books"] = _build_all_books(format or (), True, quiet, parallel)

        if sites:
            stats["sites"] = _build_all_sites(quiet)

        duration = time.time() - start_time

        # Show summary
        _show_summary(stats, duration)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def _build_single_book(
    book_id: str, formats: tuple[str, ...], all_formats: bool, quiet: bool
) -> None:
    """Build a single book."""
    builder = BookBuilder()

    if not quiet:
        console.print(f"[bold cyan]Building book:[/bold cyan] {book_id}")

    formats_to_build = list(formats) if formats else ["epub", "html", "mobi", "pdf"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task(f"Building {book_id}...", total=len(formats_to_build))

        for fmt in formats_to_build:
            progress.update(task, description=f"Building {fmt.upper()}...")
            builder.build_format(book_id, fmt)
            progress.advance(task)

    if not quiet:
        console.print(f"[bold green]✓[/bold green] {book_id} built successfully")


def _build_all_books(
    formats: tuple[str, ...], all_formats: bool, quiet: bool, parallel: bool = False
) -> int:
    """Build all books. Returns count of books built."""
    book_defs = find_book_definitions()

    if not book_defs:
        console.print("[yellow]No book definitions found[/yellow]")
        return 0

    if not quiet:
        console.print(f"[cyan]Found {len(book_defs)} book(s)[/cyan]")

    for book_path in book_defs:
        book_id = book_path.stem
        _build_single_book(book_id, formats, all_formats, quiet)

    return len(book_defs)


def _build_single_site(book_id: str, quiet: bool) -> None:
    """Build HTML site for a single book."""
    generator = SiteGenerator()

    if not quiet:
        console.print(f"[bold cyan]Building HTML site:[/bold cyan] {book_id}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Generating site...", total=None)
        generator.build_site(book_id)
        progress.update(task, completed=True)

    if not quiet:
        console.print(f"[bold green]✓[/bold green] {book_id} site generated")


def _build_all_sites(quiet: bool) -> int:
    """Build HTML sites for all books. Returns count of sites built."""
    book_defs = find_book_definitions()

    if not book_defs:
        console.print("[yellow]No book definitions found[/yellow]")
        return 0

    for book_path in book_defs:
        book_id = book_path.stem
        _build_single_site(book_id, quiet)

    return len(book_defs)


def _clean_results(quiet: bool) -> None:
    """Clean the results directory."""
    import shutil

    results_dir = Path("results")

    if results_dir.exists():
        if not quiet:
            console.print("[yellow]Cleaning results directory...[/yellow]")
        shutil.rmtree(results_dir)

    results_dir.mkdir(parents=True, exist_ok=True)

    if not quiet:
        console.print("[green]✓ Results directory cleaned[/green]")


def _show_summary(stats: dict[str, int], duration: float) -> None:
    """Show build summary."""
    table = Table(title="Build Summary")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")

    table.add_row("Duration", format_duration(int(duration)))
    table.add_row("Books Built", str(stats["books"]))
    table.add_row("Sites Generated", str(stats["sites"]))

    if stats["failed"] > 0:
        table.add_row("Failed", str(stats["failed"]), style="red")

    console.print(table)

    if stats["failed"] == 0:
        console.print("\n[bold green]✓ All builds completed successfully![/bold green]")
    else:
        console.print(
            f"\n[bold yellow]⚠ Build completed with {stats['failed']} error(s)[/bold yellow]"
        )


if __name__ == "__main__":
    main()
