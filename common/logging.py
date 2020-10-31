import logging
import os
import sys
from typing import TypedDict, List

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table


class TableColumnInput(TypedDict):
    """
    Helper typed dict for table column input
    """

    header: str
    no_wrap: bool


def create_table(columns: List[TableColumnInput], **kwargs) -> Table:
    """
    Helper function to create table object
    :param columns: column data
    :return: rich table object
    """
    table = Table(show_header=True, expand=True, **kwargs)
    for column in columns:
        table.add_column(**column)
    return table


FORMAT = "%(message)s"
logging.basicConfig(
    **{
        "level": ("DEBUG" if os.getenv("ENV", "dev") == "dev" else "INFO"),
        "format": FORMAT,
        "datefmt": "[%X]",
        "handlers": [RichHandler(rich_tracebacks=True, show_level=True)],
    },
)

logger = logging.getLogger("rich")
console = Console(file=sys.stdout)
error_console = Console(file=sys.stderr)
OUTPUT_DIVIDER = "================================================================================"
