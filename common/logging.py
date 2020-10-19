import logging
import os

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=("DEBUG" if os.getenv("ENV", "dev") == "dev" else "INFO"),
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_level=True)],
)

logger = logging.getLogger("rich")
