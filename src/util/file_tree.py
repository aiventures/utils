"""File objects as tree representation"""

import json
import logging
import os
from pathlib import Path

from model.model_persistence import ParamsFind
from util import constants as C
from util.persistence import Persistence
from util.tree import Tree
from util.utils import Utils

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

PARENT = "parent"
VALUE = "value"
ROOT = "root"
FILES = "files"
PATHS = "paths"

# TODO PRIO3 Add Progress Bar Indicator


class FileTree:
    """Files as tree representation"""

    def __init__(self, file_filter: ParamsFind = None, progress: bool = False):
        """Constructor"""
        self._file_filter: ParamsFind = file_filter
        self._file_filter.as_dict = True
        self._file_dict = {}
        self._tree_dict = {ROOT: {PARENT: None, VALUE: "root"}}
        self._stats = {FILES: 0, PATHS: 0}
        self._tree = None
        self._progress = progress
        self._read()

    def _add_file_dict_to_tree(self, path: str, files: list) -> None:
        """adding items to tree"""
        _parent_path = str(Path(path).parent)
        _hash_parent = Utils.get_hash(_parent_path)
        _hash_path = Utils.get_hash(path)
        if self._tree_dict.get(_hash_path) is None:
            self._tree_dict[_hash_path] = {PARENT: _hash_parent, VALUE: path}
            self._stats[PATHS] += 1
        for _file in files:
            self._stats[FILES] += 1
            _hash_file = Utils.get_hash(_file)
            self._tree_dict[_hash_file] = {PARENT: _hash_path, VALUE: _file}

    def _add_path_to_root(self, path: str) -> None:
        """add a path to the tree root"""
        _hash = Utils.get_hash(path)
        self._tree_dict[_hash] = {PARENT: ROOT, VALUE: path}

    def _read(self) -> None:
        """read all file objects and get the tree"""
        _paths = self._file_filter.p_root_paths
        if isinstance(_paths, str):
            _paths = _paths.split(",")

        for _p_root in _paths:
            if not os.path.isdir(_p_root):
                logger.warning(f"[FileTree] [{_p_root}] is not a valid path")
                continue
            _params = self._file_filter.model_dump()
            _params["p_root_paths"] = _p_root
            _file_dict = self._file_dict = Persistence.find(**_params)
            if _file_dict:
                self._file_dict.update(_file_dict)
                self._add_path_to_root(_p_root)
                for _path, _files in _file_dict.items():
                    self._add_file_dict_to_tree(_path, _files)

    @property
    def stats(self):
        """return statistics"""
        return self._stats

    @property
    def tree(self) -> Tree:
        """return the tree and create if needed"""
        if self._tree is None:
            self._tree = Tree()
            _ = self._tree.create_tree(self._tree_dict, name_field="value", parent_field="parent")
        return self._tree
