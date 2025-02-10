"""Rendering the CLI."""

import logging
import os
from typing import Any

from rich.color import ANSI_COLOR_NAMES
from rich.console import Console
from rich.logging import RichHandler

import util.constants as C
from cli.bootstrap_env import CLI_LOG_LEVEL

# TODO MOVE THIS TO A CONFIG FILE

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

# switch to 256 Colors as default
console = Console(color_system="256")

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=CLI_LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
