"""analyzing modules"""

# from pathlib import Path
import os
import logging
import sys
import ast
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_persistence import ParamsFind
from typing import List

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class ModuleAnalyzer:
    """Module to analyse python code based on a root path"""

    def __init__(self, p_root: str):
        self._p_root = p_root
        pass


def main():
    """do something"""
    # ...\utils\test_data\sample_py_package
    pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=CLI_LOG_LEVEL,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
