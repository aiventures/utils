"""recursive iteration through a dict"""

import copy
import json
import logging

# from datetime import datetime as DateTime
import os
import sys

# using the tree util to create a tree
from tools.util.tree import (
    Tree,
    ID,
    PARENT,
    CHILDREN,
    IS_LEAF,
    KEY,
    ROOT,
    LIST_IDX,
    LEVEL,
    OBJ_TYPE,
    OBJECT,
    PREDECESSORS,
    DICT_PATH,
)

from util import constants as C

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class DictParser:
    """parsing a dict into a tree structure"""

    def __init__(self, input_dict: dict) -> None:
        """constructor"""
        # number of elements (including counting list items)
        self._num_nodes = 0
        # level
        self._max_level = 0
        # always add a root node
        self._dict = {ROOT: copy.deepcopy(input_dict)}
        # root element has id of 0
        self._hierarchy = {}
        self._hierarchy[0] = {ID: 0, PARENT: None, CHILDREN: [], IS_LEAF: None, KEY: ROOT, LIST_IDX: None}
        # traverse the dict and create hierarchy
        self._traverse_dict(self._dict, None)
        # get the tree object
        self._tree = Tree()
        self._tree.create_tree(self._hierarchy, name_field=KEY, parent_field=PARENT)
        # get the key map from the hierarchy
        self._get_key_maps()
        # create the tree (including children, etc)

    def _parse_object(self, obj: object, parent_id: int = None, key: object = None, list_idx: int = None) -> dict:
        """parse the object and return the item"""
        out = {}
        _type = str(type(obj).__name__)
        out[ID] = self._num_nodes
        out[PARENT] = parent_id
        out[CHILDREN] = []
        out[IS_LEAF] = None
        out[KEY] = key
        if list_idx is not None:
            out[OBJECT] = obj[list_idx]
        else:
            out[OBJECT] = obj
        out[OBJ_TYPE] = _type
        out[LIST_IDX] = list_idx
        logger.debug(
            f"[DictParser] {self._num_nodes}: Key {key} type {_type}, parent {parent_id}, list index: [{list_idx}]"
        )

        return out

    def _traverse_iterable(self, d: iter, parent_id: int):
        try:
            iter(d)
            _parent_id = parent_id
            for _idx, _item in enumerate(d):
                self._traverse_dict(d, parent_id=parent_id, list_idx=_idx)
        except TypeError:
            return

    def _traverse_dict(self, d: object, parent_id: int, list_idx: int = None) -> None:
        """turns lists into dicts, each list item gets an index"""
        logging.debug(f"Iteration {self._num_nodes}")

        # when traversing a list, there is no key
        if not isinstance(d, dict):
            self._num_nodes += 1
            # treat iterables
            self._hierarchy[self._num_nodes] = self._parse_object(obj=d, parent_id=parent_id, list_idx=list_idx)
            return

        # traverse the dict
        for k, v in d.items():
            if parent_id is not None:
                self._num_nodes += 1
                self._hierarchy[self._num_nodes] = self._parse_object(
                    obj=v, parent_id=parent_id, key=k, list_idx=list_idx
                )
            else:
                _obj_id = 0

            if isinstance(v, (str, bool, float, int)):
                continue
            elif isinstance(v, dict):  # For DICT
                self._traverse_dict(d=v, parent_id=self._num_nodes, list_idx=list_idx)
            else:
                self._traverse_iterable(d=v, parent_id=self._num_nodes)

    def _get_dict_path(self, node_id: int) -> list:
        """calculate the dict path from predecessors"""
        out = []
        _hierarchy = self._hierarchy.get(node_id)
        _predecessors = _hierarchy[PREDECESSORS]
        for _predecessor in _predecessors:
            if _predecessor == 0:
                continue
            _pred_hierarchy = self._hierarchy[_predecessor]
            _key = _pred_hierarchy[KEY]
            _index = _pred_hierarchy[LIST_IDX]
            # we either get a dict key or an index of a list
            if _key is not None:
                out.append(_key)
            if _index is not None:
                out.append(_index)
        return out

    def _get_key_maps(self):
        """creates map of keys"""
        # get the hierarchy
        for _hier_id, _hier_info in self._hierarchy.items():
            _predecessors = self._tree.get_predecessors(_hier_id)
            # add the root elementa and add the current element
            if not _hier_id == 0:
                _predecessors.append(0)
            _predecessors.reverse()
            _predecessors.append(_hier_id)
            _hier_info[PREDECESSORS] = _predecessors
            _hier_info[DICT_PATH] = self._get_dict_path(_hier_id)
            _hier_info[LEVEL] = len(_predecessors) - 1
            if _hier_info[LEVEL] > self._max_level:
                self._max_level = _hier_info[LEVEL]
            # add as child item
            if _hier_info[PARENT] is not None:
                self._hierarchy[_hier_info[PARENT]][CHILDREN].append(_hier_id)
        # set the info whether it is a leaf or a node
        for _hier_id, _hier_info in self._hierarchy.items():
            if len(_hier_info[CHILDREN]) == 0:
                _hier_info[IS_LEAF] = True
            else:
                _hier_info[IS_LEAF] = False

    @property
    def tree(self):
        """tree object"""
        return self._tree


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    test_struc = '{"k1":"value1",' '"test_key":500,' '"k2":{"k2.1":5,"k2.2":"v2.2",' '"k2.3":["l1","test value","l3"]}}'
    test_dict = json.loads(test_struc)
    dict_parser = DictParser(test_dict)
    pass
