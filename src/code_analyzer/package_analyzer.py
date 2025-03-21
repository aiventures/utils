"""analyzing packages"""

# from pathlib import Path
import os
import logging
import sys

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


def main():
    """do something"""
    pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=CLI_LOG_LEVEL,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
