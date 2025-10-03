"""Image Handling Meta Data Using Exif Tool
Prerequisite is to have EXIFTOOL installed and available in your program path: https://exiftool.org/

"""

import os
import logging
import shutil
import sys
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import json
from util.utils import CmdRunner
from typing import List


class ExifToolWrapper:
    """Exiftool Wrapper, performs operations on exif tool"""

    def __init__(self, p_root: str | Path, filetype: List[str] = ["jpg", "jpeg","tif"]):
        """Constructor"""
        # working dir of files to be modified / analyzed
        self._p_root = Path(p_root)
        pass


def main():
    """do something"""

    pass


if __name__ == "__main__":
    loglevel = logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
