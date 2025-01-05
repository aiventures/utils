"""Unit Tests for the Constants Class"""

import logging
import os
import util.constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_tree(fixture_tree):
    """test the tree object
    [1] ROOT (has no parents)
     +---[2]
          +---[4]
          +---[5]
     +---[3]
          +---[6]
               +---[7]
               +---[8]
               +---[9]
    """

    _root = fixture_tree.root_id
    assert _root == 1
    _hierarchy = fixture_tree.hierarchy
    assert len(_hierarchy) == 9
    _max_level = fixture_tree.max_level
    assert _max_level == 4
    _children = fixture_tree.get_children(1, only_leaves=False)
    assert len(_children) == 8
    _parents = fixture_tree.get_predecessors(8)
    assert len(_parents) == 3
    _siblings = fixture_tree.get_siblings(8)
    assert len(_siblings) == 2
    _leaves = fixture_tree.get_leaves()
    assert len(_leaves) == 5
    _leave_siblings = fixture_tree.get_leaf_siblings()
    assert len(_leave_siblings) == 2
    _nested_tree = fixture_tree.get_nested_tree()
    assert isinstance(_nested_tree, dict)
    _reverse_tree = fixture_tree.get_reverse_tree_elements()
    assert isinstance(_reverse_tree, dict)
    _element = fixture_tree.get_element(4)
    assert isinstance(_element, dict)
    _key_path = fixture_tree.get_key_path(7)
    assert isinstance(_key_path, list)
