"""Unit Tests for the Constants Class"""

import logging
from util.tree import Tree
from model.model_tree import TreeNodeModel
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


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
    assert _max_level == 4
    _nested_dict = fixture_tree.get_nested_dict(add_leaf_values=False)
    assert isinstance(_nested_dict, dict)

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

    # [key] node id, then nested dict of subelements
    _reverse_tree = fixture_tree.get_reverse_tree_elements()
    assert isinstance(_reverse_tree, dict)
    _node = fixture_tree.get_node(4)
    assert isinstance(_node, TreeNodeModel)
    # TODO PRIO2 FIX by adding name fileds ?
    #     _key_path = fixture_tree.get_key_path(7)
    #     assert isinstance(_key_path, list)
    _node = fixture_tree.get_node(3)
    assert isinstance(_node, TreeNodeModel)
    _json = fixture_tree.json()
    assert isinstance(_json, str)
    assert fixture_tree.is_leaf(10)
    assert fixture_tree.is_node(9)


def test_tree_min_max_dict(fixture_tree: Tree):
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

    _tree = {
        1: {"parent": None, "value": 1, "object": "OBJ1"},
        2: {"parent": 1, "value": 2, "object": "OBJ2"},
        4: {"parent": 2, "value": 3, "object": "OBJ4"},
        5: {"parent": 2, "value": 5, "object": "OBJ5"},
        3: {"parent": 1, "value": 5, "object": "OBJ3"},
        6: {"parent": 3, "value": 6, "object": "OBJ6"},
        7: {"parent": 6, "value": 7, "object": "OBJ7"},
        8: {"parent": 6, "value": 8, "object": "OBJ8"},
        9: {"parent": 6, "value": 9, "object": "OBJ9"},
        10: {"parent": 8, "value": 10, "object": "OBJ10"},
        11: {"parent": 8, "value": 11, "object": "OBJ11"},
    }

    _tree = Tree()

    # use name to get a different field
    # my_tree.create_tree(tree,name_field="value")
    # _tree.create_tree(_tree_dict)
    _tree.create_tree(_tree)
