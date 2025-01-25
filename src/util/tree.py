"""class to generically handle parent-child relationships"""

import json
import logging
import os
import sys

# import yaml
import util.constants as C
from model.model_tree import CHILDREN, LEVEL, NAME, NODE, PARENT
from typing import Dict


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class Tree:
    """Tree Object"""

    def __init__(self) -> None:
        logger.debug("[Tree] Tree Constructor")
        self._nodes_dict: Dict[object, Dict] = None
        self._hierarchy_nodes_dict: Dict[object, Dict] = None
        self._root: object = None
        self._name_field: str = NAME
        self._parent_field: str = PARENT
        self._max_level = 0
        # selcting only parts of tree can be used in subclasses
        self._tree_selector = None

    @property
    def hierarchy(self):
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

    def create_tree(self, nodes_dict: dict, name_field: str = None, parent_field: str = None):
        """creates tree from passed dict root node is when there is a Non field
        returns tree structure
        """
        logger.debug("[Tree] Create Tree")
        self._nodes_dict = {}
        if name_field:
            self._name_field = name_field

        if parent_field:
            self._parent_field = parent_field

        for _node_id, _node_info in nodes_dict.items():
            _parent = None
            _name = None

            if isinstance(_node_info, str) or isinstance(_node_info, int):
                _name = str(_node_info)
                _parent = _node_info
            elif isinstance(_node_info, dict):
                _name = _node_info.get(self._name_field, str(_node_id))
                _parent = _node_info.get(self._parent_field)
            elif isinstance(_node_info, object):
                try:
                    _name = getattr(_node_info, self._name_field)
                    _parent = getattr(_node_info, self._parent_field)
                except AttributeError as e:
                    logger.warning(
                        f"[Tree] Passed Object has no attribute [{self._name_field}] of parent [{self._parent_field}],{e}"
                    )
                    continue

            if _parent is None:
                self._root = _node_id

            _node_dict = {NODE: _node_id, self._name_field: _name, self._parent_field: _parent}
            self._nodes_dict[_node_id] = _node_dict

        self._hierarchy_nodes_dict = self._get_hierarchy()

        return self._nodes_dict

    def _get_hierarchy_info(self, node_id) -> dict:
        """gets the hierarchy information"""
        hierarchy_info = self.hierarchy.get(node_id, {})
        if self.is_node(node_id) is False:
            hierarchy_info = {}
        return hierarchy_info

    def _get_hierarchy(self):
        """creates children hierarchy"""
        logger.debug("[Tree] Get Node Hierarchy")
        _all_nodes = []

        def _get_children_recursive(nodes):
            """build up hierarchy"""
            logger.debug(f"[Tree] get children for nodes {nodes}")
            _children = []
            if len(nodes) > 0:
                for _parent_node in nodes:
                    for _node_id, _parent_id in _parent_dict.items():
                        if _parent_id == _parent_node:
                            _children.append(_node_id)
                for _children_id in _children:
                    _parent_dict.pop(_children_id)
                if _children:
                    _all_nodes.append(_children)
                    _get_children_recursive(_children)
            else:
                return

        _parent_dict = {}
        # get a simple dictionary with node ids and parent
        _root_node = []
        hierarchy_nodes_dict = {}
        for _node_id, _node_dict in self._nodes_dict.items():
            if _node_dict.get(self._parent_field):
                _parent_dict[_node_id] = _node_dict.get(self._parent_field)
            else:
                _parent_dict[_node_id] = None
                _root_node.append(_node_id)
                _all_nodes.append(_root_node)
            _hier_node_dict = {}
            _hier_node_dict[self._parent_field] = _parent_dict[_node_id]
            _hier_node_dict[self._name_field] = _node_dict.get(self._name_field)
            _hier_node_dict[CHILDREN] = []
            hierarchy_nodes_dict[_node_id] = _hier_node_dict

        # create layered relations
        _get_children_recursive(_root_node)
        # determine level
        _level = 0
        for _nodes in _all_nodes:
            for _node in _nodes:
                hierarchy_nodes_dict[_node][LEVEL] = _level
            _level += 1
        self._max_level = _level

        # get children
        for _node, _hierarchy_node_dict in hierarchy_nodes_dict.items():
            _parent = _hierarchy_node_dict.get(self._parent_field)
            if _parent:
                hierarchy_nodes_dict[_parent][CHILDREN].append(_node)

        return hierarchy_nodes_dict

    def get_children(self, node_id, only_leaves=False) -> list:
        """returns ids of direct children"""
        _hier_info = self._get_hierarchy_info(node_id)
        children = _hier_info.get(CHILDREN, [])
        if only_leaves:
            children = [_c for _c in children if self.is_leaf(_c)]
        return children

    def get_all_children(self, node_id, only_leaves=False) -> list | bool:
        """gets all children nodes below node as list (option to select only leaves)
        also may check if children exist
        """
        logger.debug("[Tree] Get Children Nodes")
        children_nodes = []
        _parent_node = self._get_node_dict(node_id)

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
                    _child_node_dict = self._get_node_dict(_child)
                    if _child_node_dict is None:
                        continue
                    _new_children.extend(_child_node_dict[CHILDREN])
                _get_children_recursive(_new_children)
            else:
                return

        _parent_children = _parent_node[CHILDREN]
        _get_children_recursive(_parent_children)

        if only_leaves:
            children_nodes = [_c for _c in children_nodes if self.is_leaf(_c)]

        return children_nodes

    def has_children(self, node_id) -> bool:
        """checks if node has children"""
        _hier_info = self._get_hierarchy_info(node_id)
        return len(_hier_info.get(CHILDREN, [])) > 0

    def get_predecessors(self, node_id) -> list:
        """gets the parent nodes in a list"""
        parents = []
        _current_node = self._get_node_dict(node_id)
        while _current_node is not None:
            _parent_id = _current_node[self._parent_field]
            if _parent_id:
                _current_node = self._get_node_dict(_parent_id)
                parents.append(_parent_id)
            else:
                _current_node = None

        return parents

    def _get_node_dict(self, node_id) -> dict | None:
        """returns the node dict, using it in a method
        allows for overwrite in sublasses to introduce filtering
        """
        _node_dict = self._hierarchy_nodes_dict.get(node_id)
        return _node_dict

    def is_node(self, node_id) -> bool:
        """returns whether an id represents a node
        can also be used to be overridden in a subclass
        """
        _node_dict = self._get_node_dict(node_id)
        return True if isinstance(_node_dict, dict) else False

    def is_leaf(self, node_id):
        """checks if node is leaf"""
        _node_info = self._get_node_dict(node_id)
        if _node_info is None:
            return None

        if not _node_info.get(CHILDREN):
            return True
        else:
            return False

    def get_siblings(self, node_id, only_leaves=True) -> list:
        """gets the list of siblings and only leaves"""

        siblings = []
        _current_node = self._get_node_dict(node_id)
        if _current_node is None:
            logger.info(f"[Tree] Node with ID {node_id} not found")
            return None
        _parent_id = _current_node.get(self._parent_field)
        if _parent_id is not None:
            _parent_node = self._get_node_dict(_parent_id)
            siblings = _parent_node.get(CHILDREN)
            # either directly get siblings or check whether it is filtered
            siblings = [elem for elem in siblings if not elem == node_id]
            if self._tree_selector is not None:
                siblings = [elem for elem in siblings if self.is_node(elem)]

        if only_leaves:
            siblings = [elem for elem in siblings if self.is_leaf(elem)]

        return siblings

    def get_key_path(self, node_id):
        """returns the keys list required to navigate to the element"""
        keys = []
        # get all predecessors
        _predecessor_ids = self.get_predecessors(node_id)
        _node_ids = [node_id, *_predecessor_ids]
        for _id in _node_ids:
            _tree_elem = self.get_element(_id)
            if not self._name_field:
                keys.append(_tree_elem["node"])
            else:
                keys.append(_tree_elem[self._name_field])
        keys.reverse()
        return keys

    def get_leaves(self) -> list:
        """returns the leaves of the tree"""
        leaves = []
        for _node, _node_info in self._hierarchy_nodes_dict.items():
            if _node_info.get(CHILDREN):
                continue
            leaves.append(_node)
        return leaves

    def get_leaf_siblings(self) -> dict:
        """gets sibling leaves alongside with parent node path"""
        _leaves = self.get_leaves()
        leaf_siblings = []
        # processed list
        _processed = dict(zip(_leaves, len(_leaves) * [False]))
        for _leaf in _leaves:
            if _processed[_leaf]:
                continue
            _siblings = [_leaf]
            _siblings.extend(self.get_siblings(_leaf))
            for sibling in _siblings:
                _processed[sibling] = True
            _predecessors = self.get_predecessors(_leaf)
            leaf_siblings.append([_siblings, _predecessors])

        return leaf_siblings

    def get_nested_dict(self) -> dict:
        """gets the tree as nested dict"""
        logger.info("[Tree] Get nested Tree")
        _node_hierarchy = self._hierarchy_nodes_dict
        # current_nodes = [self.root_id]
        nested_tree = {self.root_id: {}}    

        def _get_next_nodes_recursive(_nodes: dict):
            if _nodes:
                for _node, _node_children in _nodes.items():
                    _children_nodes = _node_hierarchy[_node][CHILDREN]
                    _children_dict = {}
                    for _children_node in _children_nodes:
                        _children_dict[_children_node] = {}
                    _node_children.update(_children_dict)
                    _get_next_nodes_recursive(_node_children)
            else:
                pass

        _get_next_nodes_recursive(nested_tree)
        return nested_tree

    def get_reverse_tree_elements(self) -> dict:
        """gets the elements dict of nested tree elements"""
        logger.info("[Tree] Get reverse nested Tree")
        _nested_tree = self.get_nested_dict()
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

    def get_element(self, node_id)->dict:
        """returns the element for given node id"""
        element = self._nodes_dict.get(node_id)
        if not element:
            logger.warning(f"[Tree] Element with node id {node_id} not found in tree")
            return
        return element

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
    #         +---9

    tree = {
        1: {"parent": None, "value": "value 1", "object": "OBJECT1"},
        2: {"parent": 1, "value": "value 3", "object": "OBJECT2"},
        4: {"parent": 2, "value": "value 4", "object": "OBJECT4"},
        5: {"parent": 2, "value": "value 5", "object": "OBJECT5"},
        3: {"parent": 1, "value": "value 3", "object": "OBJECT3"},
        6: {"parent": 3, "value": "value 6", "object": "OBJECT6"},
        7: {"parent": 6, "value": "value 7", "object": "OBJECT7"},
        8: {"parent": 6, "value": "value 8", "object": "OBJECT8"},
        9: {"parent": 6, "value": "value 9", "object": "OBJECT9"},
    }

    my_tree = Tree()
    # use name to get a different field
    # defining fields where parent and values (for display) are stored
    my_tree.create_tree(tree, name_field="value", parent_field="parent")
    my_root = my_tree.root_id
    my_hierarchy = my_tree.hierarchy
    my_levels = my_tree.max_level

    children = my_tree.get_all_children(1, only_leaves=False)
    print(children)
    my_parents = my_tree.get_predecessors(8)
    my_siblings = my_tree.get_siblings(8)
    my_children = my_tree.get_children(3)
    my_all_children = my_tree.get_all_children(3)
    my_leaves = my_tree.get_leaves()
    my_leave_siblings = my_tree.get_leaf_siblings()
    my_nested_tree = my_tree.get_nested_dict()
    my_reverse_tree = my_tree.get_reverse_tree_elements()
    my_element = my_tree.get_element(4)
    my_key_path = my_tree.get_key_path(7)
    # display tree as json
    print("TREE AS JSON")
    print(json.dumps(my_nested_tree, indent=3))
    print("TREE AS YAML")
    # print(yaml.dump(my_nested_tree))
    print(str(my_tree))
    # print(my_tree.yaml())
