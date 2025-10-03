"""analyzing package based on a root path"""

# from pathlib import Path
import os
import logging
import sys
from pathlib import Path
from model.model_persistence import ParamsFind
from typing import List

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class PackageAnalyzer:
    """Module to analyse python code based on a root path"""

    def _get_params_find(self) -> ParamsFind:
        """populates the ParamsFind"""

    def __init__(self, p_root: str, source_folder: str | None = "src"):
        self._p_root = Path(p_root)
        # subfolder
        if source_folder:
            source_subfolders = source_folder.split(os.sep)
            self._p_root = self._p_root.joinpath(*source_subfolders)
        logger.debug(f"Analyze Subfolders in {str(self._p_root)} ")

        pass


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
