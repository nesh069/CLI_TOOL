"""Output formatting utilities for the CLI tool.

Uses rich for colored terminal output and pretty tables.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text

# Global console instance - we just use one for the whole app
_console = Console()
_ERROR_STYLE = "bold red"
_SUCCESS_STYLE = "bold green"
_WARN_STYLE = "bold yellow"
_INFO_STYLE = "cyan"


def print_success(message: str):
    """Print a success message in green."""
    _console.print(f"[{_SUCCESS_STYLE}]✓ {message}[/{_SUCCESS_STYLE}]")


def print_error(message: str):
    """Print an error message in red."""
    _console.print(f"[{_ERROR_STYLE}]✗ ERROR: {message}[/{_ERROR_STYLE}]")


def print_warning(message: str):
    """Print a warning message in yellow."""
    _console.print(f"[{_WARN_STYLE}]⚠ {message}[/{_WARN_STYLE}]")


def print_info(message: str):
    """Print an info message in cyan."""
    _console.print(f"[{_INFO_STYLE}]ℹ {message}[/{_INFO_STYLE}]")


def print_header(title: str):
    """Print a section header with some padding."""
    _console.print()
    _console.rule(f"[bold]{title}[/bold]")
    _console.print()


def format_table(data: list[dict]) -> None:
    """Format a list of dicts into a rich Table and print it.

    Each dict key becomes a column header. Expects at least one row.
    If data is empty this just prints nothing.
    """
    if not data:
        return

    headers = list(data[0].keys())
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")

    for h in headers:
        # Make header names look nicer - replace underscores with spaces and title case
        display = h.replace("_", " ").title()
        table.add_column(display, overflow="fold")

    for row in data:
        vals = []
        for h in headers:
            v = row.get(h, "")
            # Make sure everything is string
            vals.append(str(v) if v is not None else "")
        table.add_row(*vals)

    _console.print(table)
