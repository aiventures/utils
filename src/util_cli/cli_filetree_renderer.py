"""Rendering the File Tree"""

import logging
import os
import re
from pathlib import Path
from datetime import datetime as DateTime
from enum import StrEnum
from typing import List, Dict

from rich.logging import RichHandler
from rich.tree import Tree as RichTree
from rich.console import Console

from cli.bootstrap_env import LOG_LEVEL
from util import constants as C
from util.file_tree import FileTree
from model.model_file_tree import ParamsFileTree
from model.model_persistence import ParamsFind
from util.file_tree import PARENT, VALUE, ROOT, FILES, PATHS, SIZE, CHDATE, IS_FILE, TOTAL_SIZE


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class FileTreeRenderer:
    """Rendering A File Tree"""

    def __init__(self, params_file_tree: ParamsFileTree):
        """render a file Tree object"""
        self._params_file_tree: ParamsFileTree = params_file_tree
        self._file_tree: FileTree = FileTree(params_file_tree)
        # gets the tree dictionary
        self._file_tree_dict: Dict[str, dict] = self._file_tree.tree_dict
        # rich tree refs
        self._rich_tree_dict: Dict[str, RichTree] = {}
        self._create_rich_tree()
        self._rich_tree: RichTree = None

    def _create_rich_tree(self):
        """creates the rich tree"""
        _root = self._file_tree_dict.pop(ROOT)
        self._rich_tree = RichTree(
            f"QUERY - {_root[TOTAL_SIZE]}",
            guide_style="bold bright_blue",
        )
        self._rich_tree_dict[ROOT] = self._rich_tree
        _details_node = self._rich_tree.add("QUERY_DETAILS", guide_style="Purple")
        _details_node.add("INFO HUGO 2")
        _details_node.add("INFO HUGO 3")

        pass

        for _node_id, _node_info in self._file_tree_dict.items():
            # render the item

            _parent = _node_info[PARENT]
            _rich_tree_parent = self._rich_tree_dict.get(_parent)
            if _rich_tree_parent is None:
                continue
            # _name = _node_info[VALUE].split("\\")[-1]

            if _parent == ROOT:
                _name = _node_info[VALUE]
            else:
                _name = _node_info[VALUE].split("\\")[-1]
            _size = _node_info.get(SIZE)
            _size = _node_info.get(TOTAL_SIZE)
            _rich_tree = _rich_tree_parent.add(_name)
            self._rich_tree_dict[_node_id] = _rich_tree
            pass

        console = Console()
        console.print(self._rich_tree)

    # self._file_tree_dict['29876b4d08cf16b1a1c597dc8c274932']["value"].split("\\")[-1]


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    # get the test folder for display
    p = str(Path(__file__).parents[2].joinpath("test_data", "test_path"))
    show_progress = True
    add_filesize = True
    file_filter = ParamsFind(p_root_paths=p, show_progress=show_progress)
    add_metadata = True
    params_file_tree = ParamsFileTree(
        file_filter_params=file_filter, add_metadata=add_metadata, add_filesize=add_filesize
    )
    file_tree_renderer = FileTreeRenderer(params_file_tree)
