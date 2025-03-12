"""Tree Iterator wrapping an iterator to iterate over tree elements"""

import logging
import sys
from typing import Dict

from util.tree import Tree
from model.model_tree import TreeNodeModel
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class TreeIterator:
    """tree iterator"""

    def __init__(self, tree: Tree):
        """constructor"""
        self._tree = tree
        self._hierarchy: Dict[object, TreeNodeModel] = self._tree.hierarchy
        self._returned_objects = []
        self._root_id = self._tree.root_id
        self._stack = [self._root_id]

    def __iter__(self):
        """define class as iterable"""
        return self

    def __next__(self) -> object:
        """get next tree id"""
        if not self._stack:
            raise StopIteration  # End iteration when stack is empty
        _node_id = self._stack.pop()  # pop the last element from the list
        self._stack.extend(reversed(self._hierarchy.get(_node_id).children))
        return _node_id

    @property
    def hierarchy(self) -> Dict[object, TreeNodeModel]:
        """returns the hierarchy"""
        return self._hierarchy

    @property
    def tree(self) -> Tree:
        """returns the tree"""
        return self._tree


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
    my_tree.create_tree(tree, name_field="value", parent_field="parent", analyze_fields=True)
    my_root = my_tree.root_id
    my_tree_iterator = TreeIterator(my_tree)
    # _id = next(my_tree_iterator)
    # for node_id in my_tree_iterator:
    #     print(node_id)
    while True:
        _id = next(my_tree_iterator, "end")
        if _id == "end":
            break
        print(f"Iterating node {_id}")
