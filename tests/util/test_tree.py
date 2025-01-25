"""Unit Tests for the Constants Class"""

import logging
import os
import util.constants as C
from util.tree import Tree

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_tree(fixture_tree: Tree):
    """test the tree object
    [1] ROOT (has no parents)
         +---[2]
              +---[4]
              +---[5]
         +---[3]
              +---[6]
                   +---[7]
                   +---[8]
                        +---[10]
                        +---[11]
                   +---[9]
    """

    _root = fixture_tree.root_id
    assert _root == 1
    _hierarchy = fixture_tree.hierarchy
    assert len(_hierarchy) == 11
    _max_level = fixture_tree.max_level
    assert _max_level == 5
    _all_children = fixture_tree.get_all_children(1, only_leaves=False)
    assert len(_all_children) == 10
    _children = fixture_tree.get_children(1)
    assert len(_children) == 2
    _parents = fixture_tree.get_predecessors(8)
    assert len(_parents) == 3
    _siblings = fixture_tree.get_siblings(8)
    assert len(_siblings) == 2
    _leaves = fixture_tree.get_leaves()
    assert len(_leaves) == 6
    # siblings alongside with parent paths
    _leave_siblings = fixture_tree.get_leaf_siblings()
    assert len(_leave_siblings) == 3
    _nested_dict = fixture_tree.get_nested_dict()
    assert isinstance(_nested_dict, dict)
    # [key] node id, then nested dict of subelements
    _reverse_tree = fixture_tree.get_reverse_tree_elements()
    assert isinstance(_reverse_tree, dict)
    _element = fixture_tree.get_element(4)
    assert isinstance(_element, dict)
    _key_path = fixture_tree.get_key_path(7)
    assert isinstance(_key_path, list)
    _element = fixture_tree.get_element(3)
    assert isinstance(_element, dict)
    _json = fixture_tree.json()
    assert isinstance(_json, str)
    assert fixture_tree.is_leaf(10)
    assert fixture_tree.is_node(9)
