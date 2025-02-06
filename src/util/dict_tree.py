"""recursive iteration through a dict"""

import copy
import json
import logging
from functools import wraps

# from datetime import datetime as DateTime
import sys
from typing import List, Union, Dict

# using the tree util to create a tree
from model.model_tree import PARENT_ID, ROOT, DictTreeNodeModel, NodeType, OUTPUT
from util.tree import Tree

logger = logging.getLogger(__name__)

# get log level from environment if given
# logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def valid_node_id(func):
    """decorator / annotation to verify a valid node id was passed and returns None otherwise"""

    @wraps(func)
    def func_wrapper(self, node_id: int, *args, **kwargs):
        # check if valid key was passed, if not, skip function execution
        if not self._node_hierarchy.get(node_id):
            logger.info(f"[DictTree] valid_node_id decorator: node_id [{node_id}] invalid")
            return None
        # there is a key, execute function
        return func(self, node_id)

    return func_wrapper


class DictTree:
    """parsing a dict into a tree structure"""

    def __init__(self, input_dict: dict, copy_dict: bool = False, max_output_length: int = 20) -> None:
        """constructor"""
        # number of elements (including counting list items)
        self._num_nodes = 0
        # level
        self._max_level = 0
        # max output length for display
        self._max_output_length = max_output_length
        # always add a root node to avoid non tree structure when lists are passed
        _input_dict = copy.deepcopy(input_dict) if copy_dict else input_dict
        self._dict = {ROOT: _input_dict}
        # root element has id of 0
        self._node_hierarchy: Dict[int, DictTreeNodeModel] = {}
        self._node_hierarchy[0] = DictTreeNodeModel(id=0, obj="ROOT", obj_type="str")
        # traverse the dict and create hierarchy
        self._traverse_dict(self._dict, None)
        # special case: root output is not populated
        self._node_hierarchy[0].output = "ROOT"
        # get the tree object
        self._tree = Tree()
        self._tree.create_tree(self._node_hierarchy, name_field=OUTPUT, parent_field=PARENT_ID)
        self._index = {}
        # get the key map from the hierarchy
        self._get_key_maps()
        # create the key index
        self._create_index()

    def _render_output(self, dict_tree_node: DictTreeNodeModel) -> None:
        """renders the output field for later display (eg in Tree Viewer)"""
        s_out = f"[{dict_tree_node.obj_type}] "
        _key = ""
        _idx = ""
        if dict_tree_node.key is not None:
            _key = str(dict_tree_node.key)
        if dict_tree_node.list_idx is not None:
            _idx = f"({str(dict_tree_node.list_idx)})"
        # TODO PRIO3 render differently for complex object or only atomic type
        # TODO optionally offer wrapping of object
        _obj = str(dict_tree_node.obj)
        if len(_obj) > self._max_output_length:
            _obj = f"{_obj[:self._max_output_length]}..]\n({len(_obj)}) more "
        s_out = f"{_key}{_idx} {s_out}\n{_obj}"
        dict_tree_node.output = s_out

    def _parse_object(
        self, obj: object, parent_id: int = None, key: object = None, list_idx: int = None
    ) -> DictTreeNodeModel:
        """parse the object and return the item"""

        _id = self._num_nodes
        _parent_id = parent_id
        _children = []
        if list_idx is not None:
            _object = obj[list_idx]
        else:
            _object = obj
        _obj_type = str(type(_object).__name__)
        _key = key
        _list_idx = list_idx
        out = DictTreeNodeModel(
            id=_id,
            parent_id=_parent_id,
            children=_children,
            obj=_object,
            obj_type=_obj_type,
            key=_key,
            list_idx=_list_idx,
        )
        self._render_output(out)
        logger.debug(
            f"[DictTree] OBJECT Parent->Node [{parent_id}->{self._num_nodes}], key [{key}], index [{list_idx}], type [{_obj_type}]"
        )

        return out

    def _traverse_iterable(self, d: iter, parent_id: int):
        """traverse all items in a list / iterable"""
        try:
            iter(d)
            logger.debug(f"[DictTree] ITERABLE Parent [{parent_id}]")
            _parent_id = parent_id
            for _idx, _item in enumerate(d):
                self._traverse_dict(d, parent_id=parent_id, list_idx=_idx)
        except TypeError:
            return

    def _traverse_dict(self, d: object, parent_id: int, list_idx: int = None) -> None:
        """turns lists into dicts, each list item gets an index"""
        logger.debug(f"[DictTree] DICT Parent->Node [{parent_id}->{self._num_nodes}], index [{list_idx}]")
        _list_idx = list_idx
        # process list item with an inner iterable type
        _inner_iterable = None
        if list_idx is not None:
            _list_item = d[list_idx]
            # check whether it is an inner iterable
            if not isinstance(_list_item, str):
                try:
                    _ = iter(d[list_idx])
                    _inner_iterable = d[list_idx]
                except TypeError:
                    pass
        # when traversing a list, there is no key
        if not isinstance(d, dict):
            self._num_nodes += 1
            # treat iterables / add the list item
            self._node_hierarchy[self._num_nodes] = self._parse_object(obj=d, parent_id=parent_id, list_idx=_list_idx)
            # now if there is an inner nested type in a list, parse it as well
            if _inner_iterable is not None:
                logger.debug(f"[DictTree] INNER ITERABLE [{self._num_nodes}]")
                if isinstance(_inner_iterable, dict):
                    self._traverse_dict(_inner_iterable, parent_id=self._num_nodes, list_idx=None)
                else:
                    self._traverse_iterable(_inner_iterable, parent_id=self._num_nodes)
            return

        # traverse the dict
        for k, v in d.items():
            if parent_id is not None:
                self._num_nodes += 1
                logger.debug(f"[DictTree] Parsing KEY [{k}], IDX [{self._num_nodes}]")
                self._node_hierarchy[self._num_nodes] = self._parse_object(
                    obj=v, parent_id=parent_id, key=k, list_idx=_list_idx
                )
            else:
                _obj_id = 0

            # atomic types
            if isinstance(v, (str, bool, float, int)):
                continue
            elif isinstance(v, dict):  # For DICT
                self._traverse_dict(d=v, parent_id=self._num_nodes, list_idx=_list_idx)
            else:  # Assume we have an iterable
                self._traverse_iterable(d=v, parent_id=self._num_nodes)

    def _get_dict_path(self, node_id: int) -> list:
        """calculate the dict path from predecessors"""
        out = []
        _hierarchy = self._node_hierarchy.get(node_id)
        # _predecessors = _hierarchy[PREDECESSORS]
        _predecessors = _hierarchy.predecessors

        for _predecessor in _predecessors:
            if _predecessor == 0:
                continue
            _pred_hierarchy = self._node_hierarchy[_predecessor]
            _key = _pred_hierarchy.key
            _index = _pred_hierarchy.list_idx
            # we either get a dict key or an index of a list
            if _key is not None:
                out.append(_key)
            if _index is not None:
                out.append(_index)
        logger.debug(f"[DictTree] Key [{node_id}], Path {out}")
        return out

    def _get_key_maps(self):
        """creates map of keys"""
        # get the hierarchy
        for _node_id, _node_info in self._node_hierarchy.items():
            _predecessors = self._tree.get_predecessors(_node_id)
            # add the root elementa and add the current element
            if not _node_id == 0:
                _predecessors.append(0)
            _predecessors.reverse()
            _predecessors.append(_node_id)

            _node_info.predecessors = _predecessors
            _node_info.dict_path = self._get_dict_path(_node_id)
            _node_info.level = len(_predecessors) - 1
            if _node_info.level > self._max_level:
                self._max_level = _node_info.level
            # add as child item
            if _node_info.parent_id is not None:
                self._node_hierarchy[_node_info.parent_id].children.append(_node_id)
        # set the info whether it is a leaf or a node
        for _node_id, _node_info in self._node_hierarchy.items():
            if len(_node_info.children) == 0:
                _node_info.is_leaf = True
            else:
                _node_info.is_leaf = False

    def _create_index(self) -> None:
        """create index dict path to object id"""
        self._index = {}
        self._index = {tuple(node_info.dict_path): node_id for node_id, node_info in self._node_hierarchy.items()}
        pass

    # TODO PRIO4 Create a method to move subtrees to another node
    # requires adoption of the navigation path

    @property
    def tree(self) -> Tree:
        """tree object"""
        return self._tree

    @property
    def max_level(self) -> int:
        """gets the hierarchy depth"""
        return self._max_level

    def is_node_type(self, node_id: str, node_type: NodeType = "any") -> bool:
        """check if a filter is of certain node type"""
        if node_type == "any":
            return True
        _type = "leaf"
        if self._node_hierarchy[node_id].is_leaf is False:
            _type = "node"
        return node_type == _type

    @valid_node_id
    def get_node(self, node_id: int) -> DictTreeNodeModel:
        """returns the info for a tree node"""
        return self._node_hierarchy[node_id]

    def get_node_id_by_path(self, node_path: Union[dict | tuple]) -> int:
        """gets the node id from the index using a dict path"""
        _path = node_path
        out = None
        if not isinstance(_path, tuple):
            _path = tuple(_path)
        try:
            out = self._index[_path]
        except KeyError:
            logger.info(f"[DictTree] There is no key {node_path}")
        return out

    @valid_node_id
    def get_subtree_ids(self, node_id: int, node_type: NodeType = "any") -> list:
        """gets the subtree node elements"""
        _subtree_root = self.get_node(node_id)
        _all_children = []
        _nodes = _subtree_root.children
        while len(_nodes) > 0:
            _children = []
            for _node in _nodes:
                _all_children.append(_node)
                _children.extend(self.get_node(_node).children)
            _nodes = _children
        _all_children = [_n for _n in _all_children if self.is_node_type(_n, node_type)]
        return _all_children

    def get_leaf_ids(self) -> list:
        """returns all leaves of the tree"""
        return [_id for _id, _info in self._node_hierarchy.items() if _info.is_leaf]

    @valid_node_id
    def is_leaf(self, node_id: int) -> bool:
        """returns info whether a node is a leaf"""
        return self.get_node(node_id).is_leaf

    @valid_node_id
    def key_path(self, node_id: int) -> list:
        """returns the key path for a given node"""
        return self.get_node(node_id).dict_path

    @valid_node_id
    def value(self, node_id: int, node_type: NodeType = "any") -> object:
        """returns the value for a given node"""
        if not self.is_node_type(node_id):
            logger.info(f"[DictTree] Node [{node_id}] is not of type [{node_type}]")
            return
        return self.get_node(node_id).obj

    @valid_node_id
    def siblings(self, node_id: int, node_type: NodeType = "any", include_self: bool = True) -> list:
        """returns all siblings for a given node"""
        _node_info = self.get_node(node_id)
        _parent_id = _node_info.parent_id
        _children = self.get_node(_parent_id).children
        _siblings = [_c for _c in _children]
        if not include_self:
            _siblings = [_c for _c in _children if _c != node_id]
        # filter by node types
        _siblings = [_s for _s in _siblings if self.is_node_type(_s, node_type=node_type)]
        return _siblings

    def get_nodes_in_level(self, level_min: int = None, level_max: int = None, node_type: NodeType = "any") -> list:
        """gets all nodes in level min / max"""
        _level_max = None
        _level_min = None
        if level_max is None:
            _level_max = self._max_level
        else:
            _level_max = level_max
        if level_min is None:
            _level_min = 1
        else:
            _level_min = level_min
        _nodes_in_level = [
            _id
            for _id in range(1, self._num_nodes + 1)
            if self._node_hierarchy[_id].level >= _level_min and self._node_hierarchy[_id].level <= _level_max
        ]
        _nodes_in_level = [_n for _n in _nodes_in_level if self.is_node_type(_n, node_type=node_type)]
        return _nodes_in_level

    def hierarchy_dict(self, node_type: NodeType = "any", fields: List[str] = None) -> dict:
        """returns hierarchy dict of nodes"""
        out = {}

        _all_fields = list(DictTreeNodeModel.model_fields.keys())

        _fields = fields
        if fields is None:
            _fields = _all_fields

        for _node, _node_info in self._node_hierarchy.items():
            if not self.is_node_type(_node, node_type=node_type):
                continue
            _info_dict = {}
            for _field in _fields:
                if _field not in _all_fields:
                    continue
                _info_dict[_field] = getattr(_node_info, _field)
            out[_node] = _info_dict

        return out


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    test_struc = """
        { "k1":"value1",
          "test_key":500,
          "k2":{"k2.1":5,
                "k2.2":"v2.2",
                "k2.3":["l1","test value","l3",{"dict_inner":["a","b","c"]}]
                }
        }
    """
    # test_struc = '{"k1":{"k1":"v1","k2":[1,2,3]},"k_nested_list_dict":["a",{"b":"c"}]}'
    # test_struc = '{"k1":"value1","k_nested_list_list":["a",["b","c"]]}'
    test_dict = json.loads(test_struc)
    my_dict_tree = DictTree(test_dict)
    # here's the pulbic methods
    _max_level = my_dict_tree.max_level
    _node_info = my_dict_tree.get_node(2)
    _leaves = my_dict_tree.get_leaf_ids()
    _key_path = my_dict_tree.key_path(2)
    _value = my_dict_tree.value(2)
    _tree = my_dict_tree.tree
    _siblings = my_dict_tree.siblings(2)
    _dict_info = my_dict_tree.hierarchy_dict(node_type="leaf")
    _subtree = my_dict_tree.get_subtree_ids(6, node_type="node")
    _idx_invalid = my_dict_tree.get_node_id_by_path(["a"])
    _idx_valid = my_dict_tree.get_node_id_by_path(["k2", "k2.3", 1])
    pass
