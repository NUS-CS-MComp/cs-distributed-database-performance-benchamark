import logging
import logging.handlers as handlers
import os
import sys
from typing import TypedDict, List

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from common.path import WORKSPACE_PATH


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


LOG_FILE_PATH = WORKSPACE_PATH / "common/logs"
FORMAT = "%(message)s"
logging.basicConfig(
    **{
        "level": ("DEBUG" if os.getenv("ENV", "dev") == "dev" else "INFO"),
        "format": FORMAT,
        "datefmt": "[%X]",
        "handlers": [RichHandler(rich_tracebacks=True, show_level=True)],
    },
)

if not LOG_FILE_PATH.exists():
    LOG_FILE_PATH.mkdir(parents=True)

logger = logging.getLogger("rich")

file_handler = handlers.TimedRotatingFileHandler(
    filename=WORKSPACE_PATH / "common/logs" / "application.log"
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
file_handler.suffix = "%Y%m%d%H%M"
logger.addHandler(file_handler)

console = Console(file=sys.stdout)
error_console = Console(file=sys.stderr)
OUTPUT_DIVIDER = "================================================================================"
