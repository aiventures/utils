"""class to generically handle parent-child relationships"""

import json
import logging
import os
import sys

# import yaml
import util.constants as C
from model.model_tree import CHILDREN, LEVEL, NAME, PARENT, TreeNode
from typing import Dict


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class Tree:
    """Tree Object"""

    def __init__(self) -> None:
        logger.debug("[Tree] Tree Constructor")
        # self._nodes_dict: Dict[object, Dict] = None
        self._hierarchy_nodes_dict: Dict[object, Dict] = None
        self._num_nodes: int = 0
        self._root: object = None
        self._name_field: str = NAME
        self._parent_field: str = PARENT
        self._max_level: int = -1
        self._tree_level_stats = {}
        self._calc_tree_levels: bool = True
        # selecting only parts of tree can be used in subclasses
        self._tree_selector: object = None

    @property
    def hierarchy(self) -> Dict[object, TreeNode]:
        """tree hierarchy"""
        return self._hierarchy_nodes_dict

    @property
    def max_level(self):
        """max level of tree"""
        return self._max_level

    @property
    def root_id(self):
        """nodes"""
        return self._root

    def _create_node(self, node_info: dict, key: object) -> TreeNode:
        """creates a tree node from input dict"""
        if node_info is None:
            logger.warning(f"[Tree] Passed Input Dictionary has no key [{key}]")
            return
        _name = None
        _parent_id = None
        if isinstance(node_info, str) or isinstance(node_info, int):
            _name = str(node_info)
            _parent_id = node_info
        elif isinstance(node_info, dict):
            _name = node_info.get(self._name_field)
            _parent_id = node_info.get(self._parent_field)
        elif isinstance(node_info, object):
            try:
                _parent_id = getattr(node_info, self._parent_field)
            except AttributeError as e:
                logger.warning(f"[Tree] Passed Object has no parent field [{self._parent_field}],{e}")
                return
            if hasattr(node_info, self._name_field):
                _name = getattr(node_info, self._name_field)
        self._num_nodes += 1
        return TreeNode(id=key, parent_id=_parent_id, name=_name, obj=node_info)

    def create_tree(self, nodes_dict: dict, name_field: str = None, parent_field: str = None) -> None:
        """creates the tree hierarchy"""
        self._hierarchy_nodes_dict = {}
        logger.debug("[Tree] Create Tree")
        _root_nodes = []

        if name_field:
            self._name_field = name_field

        if parent_field:
            self._parent_field = parent_field

        for _node_id, _node_info in nodes_dict.items():
            # it was created before as parent node
            _node_obj = self._hierarchy_nodes_dict.get(_node_id)
            if not _node_obj:
                _node_obj = self._create_node(_node_info, _node_id)
                self._hierarchy_nodes_dict[_node_id] = _node_obj
            if not _node_obj:
                continue
            # get parent and add as child
            _parent_id = _node_obj.parent_id
            if _parent_id is None:
                _root_nodes.append(_node_id)
                continue
            _parent_node = self._hierarchy_nodes_dict.get(_parent_id)
            # create node if not already there
            if _parent_node is None:
                _parent_node = self._create_node(nodes_dict.get(_parent_id), _parent_id)
                if _parent_node:
                    self._hierarchy_nodes_dict[_parent_id] = _parent_node
                else:
                    continue
            _parent_node.children.append(_node_id)

        # verify that exactly one root is present in structure
        if len(_root_nodes) == 1:
            self._root = _root_nodes[0]
        else:
            logger.warning(f"[Tree] Create Tree, there are [{len(_root_nodes)}] root nodes {str(_root_nodes)[:30]}...")

        if self._calc_tree_levels:
            self.set_tree_levels()

        logger.debug(f"[Tree] Created [{self._num_nodes}] nodes in Tree")

    def set_tree_levels(self) -> None:
        """setting the tree levels. mus be a separate step since we do not assume the input dict as being in order"""
        _level = 0
        _current_node_ids = [self.root_id]
        while len(_current_node_ids) > 0:
            _next_node_ids = []
            self._tree_level_stats[_level] = 0
            for _node_id in _current_node_ids:
                _node = self.get_node(_node_id)
                if _node is None:
                    continue
                _node.level = _level
                self._tree_level_stats[_level] += 1
                _next_node_ids.extend(_node.children)
            _level += 1
            _current_node_ids = _next_node_ids
        self._max_level = _level - 1

    def _get_hierarchy_info(self, node_id) -> TreeNode:
        """gets the hierarchy information"""
        hierarchy_info = self.hierarchy.get(node_id, {})
        if self.is_node(node_id) is False:
            hierarchy_info = None
        return hierarchy_info

    def get_children(self, node_id, only_leaves=False) -> list:
        """returns ids of direct children"""
        children = None
        _node = self.get_node(node_id)
        if not _node:
            return children
        children = _node.children
        if only_leaves:
            children = [_c for _c in children if self.is_leaf(_c)]
        return children

    def get_all_children(self, node_id, only_leaves=False) -> list | bool:
        """gets all children nodes below node as list (option to select only leaves)
        also may check if children exist
        """
        logger.debug("[Tree] Get Children Nodes")
        children_nodes = []
        _parent_node = self.get_node(node_id)

        if not _parent_node:
            logger.warning(f"[Tree] Parent node with node id {node_id} was not found")
            return

        def _get_children_recursive(child_list):
            logger.debug(f"[Tree] get children recursive {child_list}")
            _new_children = []
            if len(child_list) > 0:
                for _child in child_list:
                    if (only_leaves and self.is_leaf(_child)) or (only_leaves is False):
                        children_nodes.append(_child)
                    _child_node = self.get_node(_child)
                    if _child_node is None:
                        continue
                    _new_children.extend(_child_node.children)
                _get_children_recursive(_new_children)
            else:
                return

        _parent_children = _parent_node.children
        _get_children_recursive(_parent_children)

        if only_leaves:
            children_nodes = [_c for _c in children_nodes if self.is_leaf(_c)]

        return children_nodes

    def has_children(self, node_id) -> bool:
        """checks if node has children"""
        out = None
        _node = self.get_node(node_id)
        if _node:
            out = True if len(_node.children) > 0 else False
        return out

    def get_predecessors(self, node_id) -> list:
        """gets the parent nodes in a list"""
        parents = []
        # _current_node = self.get_node(node_id)
        _current_node_id = node_id

        while _current_node_id is not None:
            _current_node = self.get_node(_current_node_id)
            if not _current_node:
                _current_node_id = None
                continue
            _parent_id = _current_node.parent_id
            if _parent_id:
                _current_node_id = _parent_id
                parents.append(_parent_id)
            else:
                _current_node_id = None

        return parents

    def get_node(self, node_id) -> TreeNode | None:
        """returns the tree node for given node id
        can also be overridden in subclass
        """
        return self._hierarchy_nodes_dict.get(node_id)

    def is_node(self, node_id) -> bool:
        """returns whether an id represents a node
        can also be used to be overridden in a subclass
        """
        return False if self.get_node(node_id) is None else True

    def is_leaf(self, node_id):
        """checks if node is leaf"""
        _node_info = self.get_node(node_id)
        if _node_info is None:
            return None
        _children = _node_info.children
        if isinstance(_children, list) and len(_children) == 0:
            return True
        else:
            return False

    def get_siblings(self, node_id, only_leaves=True) -> list:
        """gets the list of siblings and only leaves"""

        siblings = []
        _current_node = self.get_node(node_id)
        if _current_node is None:
            logger.info(f"[Tree] Node with ID {node_id} not found")
            return None

        # filtering already adressed if there is current node there is also a parent
        _parent_id = _current_node.parent_id
        if _parent_id is not None:
            _parent_node = self.get_node(_parent_id)
            siblings = _parent_node.children
            # either directly get siblings or check whether it is filtered
            siblings = [elem for elem in siblings if not elem == node_id]
            if self._tree_selector is not None:
                siblings = [elem for elem in siblings if self.is_node(elem)]

        if only_leaves:
            siblings = [elem for elem in siblings if self.is_leaf(elem)]

        return siblings

    # TODO PRIO Probably need to add key field to TreeNode
    # def get_key_path(self, node_id):
    #     """returns the keys list required to navigate to the element"""
    #     keys = []
    #     # get all predecessors
    #     _predecessor_ids = self.get_predecessors(node_id)
    #     _node_ids = [node_id, *_predecessor_ids]
    #     for _id in _node_ids:
    #         _tree_elem = self.get_node(_id)
    #         if not self._name_field:
    #             keys.append(_tree_elem["node"])
    #         else:
    #             keys.append(_tree_elem[self._name_field])
    #     keys.reverse()
    #     return keys

    def get_leaves(self) -> list:
        """returns the leaves of the tree"""
        leaves = []
        for _node_id in self._hierarchy_nodes_dict.keys():
            _node = self.get_node(_node_id)
            if not _node:
                continue
            if len(_node.children) == 0:
                leaves.append(_node_id)
        return leaves

    def get_leaf_siblings(self, only_leaves: bool = True) -> dict:
        """gets sibling leaves alongside with parent node path"""
        _leaves = self.get_leaves()
        leaf_siblings = []
        # processed list
        _processed = dict(zip(_leaves, len(_leaves) * [False]))
        for _leaf in _leaves:
            if _processed[_leaf]:
                continue
            _siblings = [_leaf]
            _siblings.extend(self.get_siblings(_leaf, only_leaves=only_leaves))
            for sibling in _siblings:
                _processed[sibling] = True
            _predecessors = self.get_predecessors(_leaf)
            leaf_siblings.append([_siblings, _predecessors])

        return leaf_siblings

    def get_nested_dict(self, add_leaf_values: bool = True) -> dict:
        """gets the keys of tree as nested dict without the value
        optionally add the leaf values / or just add empty dicts as
        leaf placeholders (might help in serializing structures)
        """
        logger.info("[Tree] Get nested Tree")
        _num_objects = 0
        _num_nodes = 0
        _node_hierarchy = self._hierarchy_nodes_dict
        # current_nodes = [self.root_id]
        nested_dict = {self.root_id: {}}

        def _get_next_nodes_recursive(_nested_dict: dict) -> dict:
            nonlocal _num_objects
            nonlocal _num_nodes
            if _nested_dict:
                for _node_id, _node_dict_info in _nested_dict.items():
                    _node: TreeNode = self.get_node(_node_id)
                    if not _node:
                        continue
                    _num_nodes += 1
                    _children_node_ids = _node.children
                    _children_dict = {}
                    _object = None
                    if len(_children_node_ids) > 0:
                        for _children_node_id in _children_node_ids:
                            _children_dict[_children_node_id] = {}
                    else:
                        _num_objects += 1
                        # add the leaf object to the dict
                        if add_leaf_values:
                            _children_dict = _node.obj
                    _node_dict_info.update(_children_dict)
                    _get_next_nodes_recursive(_children_dict)

        # recursively populate the dict
        _get_next_nodes_recursive(nested_dict)
        logger.info(f"[Tree] Nested Dict Creation, Parsed [{_num_nodes}] Nodes, [{_num_objects}] Objects")
        return nested_dict

    def get_reverse_tree_elements(self) -> dict:
        """gets the element paths dict of nested tree elements with empty dict as placeholder for value"""
        logger.info("[Tree] Get reverse nested Tree")
        _nested_tree = self.get_nested_dict(add_leaf_values=False)
        _root_key = list(_nested_tree.keys())[0]
        reverse_tree = {_root_key: _nested_tree[_root_key]}

        def _get_next_nodes_recursive(_nodes: dict) -> dict:
            if _nodes:
                _next_nodes = {}
                for _node, _node_info in _nodes.items():
                    reverse_tree[_node] = _node_info
                    _next_nodes.update(_node_info)
                _get_next_nodes_recursive(_next_nodes)
            else:
                pass

        _get_next_nodes_recursive(reverse_tree)
        return reverse_tree

    def json(self) -> str:
        """returns json string"""
        logger.debug("[Tree] json()")
        _nested_tree = self.get_nested_dict()
        return json.dumps(_nested_tree, indent=3)

    # def yaml(self) -> str:
    #     """returns yaml string"""
    #     logger.debug("[Tree] yaml()")
    #     nested_tree = self.get_nested_tree()
    #     return yaml.dump(nested_tree)

    def __str__(self) -> str:
        return self.json()


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # tree = {
    #     1: {"parent": None, "value": "value 1"},
    #     2: {"parent": 1},
    #     4: {"parent": 2},
    #     5: {"parent": 2},
    #     3: {"parent": 1},
    #     6: {"parent": 3},
    #     7: {"parent": 6},
    #     8: {"parent": 6},
    #     9: {"parent": 6},
    # }

    # 1
    # +---2
    # |   +---4
    # |   +---5
    # |
    # +---3
    #     +---6
    #         +---7
    #         +---8
    #             +---[10]
    #             +---[11]
    #         +---9

    tree = {
        1: {"parent": None, "value": "value 1", "object": "OBJ1"},
        2: {"parent": 1, "value": "value 2", "object": "OBJ2"},
        4: {"parent": 2, "value": "value 4", "object": "OBJ4"},
        5: {"parent": 2, "value": "value 5", "object": "OBJ5"},
        3: {"parent": 1, "value": "value 3", "object": "OBJ3"},
        6: {"parent": 3, "value": "value 6", "object": "OBJ6"},
        7: {"parent": 6, "value": "value 7", "object": "OBJ7"},
        8: {"parent": 6, "value": "value 8", "object": "OBJ8"},
        9: {"parent": 6, "value": "value 9", "object": "OBJ9"},
        10: {"parent": 8, "value": "value 10", "object": "OBJ10"},
        11: {"parent": 8, "value": "value 11", "object": "OBJ11"},
    }

    my_tree = Tree()
    # use name to get a different field
    # defining fields where parent and values (for display) are stored
    my_tree.create_tree(tree, name_field="value", parent_field="parent")
    my_root = my_tree.root_id
    my_hierarchy = my_tree.hierarchy
    my_levels = my_tree.max_level

    my_nested_tree = my_tree.get_nested_dict()
    children = my_tree.get_all_children(1, only_leaves=False)
    print(children)
    my_parents = my_tree.get_predecessors(8)
    my_siblings = my_tree.get_siblings(8)
    my_children = my_tree.get_children(3)
    my_all_children = my_tree.get_all_children(3)
    my_leaves = my_tree.get_leaves()
    my_leave_siblings = my_tree.get_leaf_siblings()
    my_reverse_tree = my_tree.get_reverse_tree_elements()
    my_element = my_tree.get_node(4)
    # my_key_path = my_tree.get_key_path(7)
    # display tree as json
    print("TREE AS JSON")
    print(json.dumps(my_nested_tree, indent=3))
    print("TREE AS YAML")
    # print(yaml.dump(my_nested_tree))
    print(str(my_tree))
    # print(my_tree.yaml())
