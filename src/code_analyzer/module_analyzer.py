"""analyzing modules"""

# from pathlib import Path
import os
import logging
import sys
import ast

logger = logging.getLogger(__name__)

# get log level from environment if given
DEFAULT_LOGLEVEL = int(os.environ.get("CLI_LOG_LEVEL", logging.INFO))
logger.setLevel(DEFAULT_LOGLEVEL)


class ModuleAnalyzer:
    """Module to analyse python code"""

    def __init__(self):
        pass


def main():
    """do something"""
    pass


if __name__ == "__main__":
    loglevel = DEFAULT_LOGLEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
