"""File objects as tree representation"""

import logging
import os
from datetime import datetime as DateTime
from os import lstat
from pathlib import Path

from model.model_file_tree import ParamsFileTreeModel
from model.model_persistence import ParamsFind
from util import constants as C
from util.filter import DictFilter
from util.filter_set import FilterSet
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
SIZE = "size"
CHDATE = "chdate"
IS_FILE = "is_file"
TOTAL_SIZE = "total_size"

# TODO PRIO3 Add Progress Bar Indicator


class FileTree:
    """Files as tree representation"""

    def __init__(self, params_file_tree: ParamsFileTreeModel):
        """Constructor"""
        # file_filter: ParamsFind = None, metadata: bool = False, progress: bool = False

        self._file_filter_params: ParamsFind = params_file_tree.file_filter_params
        self._file_filter_params.as_dict = True
        self._add_metadata: bool = params_file_tree.add_metadata
        self._show_progress: bool = self._file_filter_params.show_progress
        self._filesize: bool = params_file_tree.add_filesize
        self._path_filterset = None
        self._file_filterset = None
        self._file_filter = None
        self._path_filter = None
        # a bit awkward but allow for quick access to Filter

        if isinstance(params_file_tree.file_filter, DictFilter):
            self._file_filter = params_file_tree.file_filter
        elif isinstance(params_file_tree.file_filter, FilterSet):
            self._file_filterset = params_file_tree.file_filters

        if isinstance(params_file_tree.path_filter, DictFilter):
            self._path_filter = params_file_tree.path_filter
        elif isinstance(params_file_tree.path_filter, FilterSet):
            self._path_filterset = params_file_tree.path_filter

        self._file_dict: dict = {}
        self._tree_dict: dict = {ROOT: {PARENT: None, VALUE: "root"}}
        self._stats: dict = {FILES: 0, PATHS: 0}
        self._tree: Tree = None
        self._read()
        if self._filesize:
            self._calc_total_sizes()

    def _add_file_dict_to_tree(self, path: str, files: list) -> None:
        """adding items to tree"""
        _parent_path = str(Path(path).parent)
        _hash_parent = Utils.get_hash(_parent_path)
        _hash_path = Utils.get_hash(path)
        if self._tree_dict.get(_hash_path) is None:
            _out = {PARENT: _hash_parent, VALUE: path}
            if self._add_metadata:
                _meta = lstat(path)
                _ch_time = DateTime.fromtimestamp(_meta.st_ctime)
                _metadict = {IS_FILE: False, SIZE: _meta.st_size, CHDATE: _ch_time}
                _out.update(_metadict)
            self._tree_dict[_hash_path] = _out
            self._stats[PATHS] += 1
        for _file in files:
            self._stats[FILES] += 1
            _hash_file = Utils.get_hash(_file)
            _out = {PARENT: _hash_path, VALUE: _file}
            if self._add_metadata:
                _meta = lstat(_file)
                _ch_time = DateTime.fromtimestamp(_meta.st_ctime)
                _metadict = {IS_FILE: True, SIZE: _meta.st_size, CHDATE: _ch_time}
                _out.update(_metadict)
            self._tree_dict[_hash_file] = _out

    def _add_path_to_root(self, path: str) -> None:
        """add a path to the tree root"""
        _hash = Utils.get_hash(path)
        _out = {PARENT: ROOT, VALUE: path}
        if self._add_metadata:
            _meta = lstat(path)
            _ch_time = DateTime.fromtimestamp(_meta.st_ctime)
            _metadict = {IS_FILE: False, SIZE: _meta.st_size, CHDATE: _ch_time}
            _out.update(_metadict)
        self._tree_dict[_hash] = _out

    def _read(self) -> None:
        """read all file objects and get the tree"""
        _paths = self._file_filter_params.p_root_paths
        if isinstance(_paths, str):
            _paths = _paths.split(",")

        for _p_root in _paths:
            if not os.path.isdir(_p_root):
                logger.warning(f"[FileTree] [{_p_root}] is not a valid path")
                continue
            _params = self._file_filter_params.model_dump()
            _params["p_root_paths"] = _p_root
            _file_dict = self._file_dict = Persistence.find(**_params)
            if _file_dict:
                self._file_dict.update(_file_dict)
                self._add_path_to_root(_p_root)
                for _path, _files in _file_dict.items():
                    self._add_file_dict_to_tree(_path, _files)

    def _calc_total_sizes(self, leaves: list = None) -> None:
        """Calculate subotal size of the whole tree or only for some leaf nodes"""
        # can't calculate size since no metadata were read
        if self._add_metadata is False:
            logger.info("[FileTree] Calculation of subtotal file sizes not possible since no metadata were read")
            return
        # get all children (=Files) and adf file size to each predecessor
        _tree = self.tree
        # get all leaves in case no leaf ids are transferred
        if leaves is None:
            _leaves = _tree.get_leaves()
        # can be used to calculate trees only for some sub trees
        else:
            _leaves = leaves

        for _leaf_id in _leaves:
            # get the info
            _info = self._tree_dict.get(_leaf_id)
            # only add size of files
            if _info[IS_FILE] is False:
                continue
            _size = _info.get(SIZE, 0)
            # get all predecessors and add size of leaf node (=file)
            _pred_ids = _tree.get_predecessors(_leaf_id)
            for _pred_id in _pred_ids:
                _info_pred = self._tree_dict.get(_pred_id)
                _pred_size = _info_pred.get(TOTAL_SIZE, 0) + _size
                _info_pred[TOTAL_SIZE] = _pred_size

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

    @property
    def tree_dict(self) -> Tree:
        """returns the tree dict"""
        _ = self.tree
        return self._tree_dict
