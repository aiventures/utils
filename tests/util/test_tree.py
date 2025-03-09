"""Unit Tests for the Constants Class"""

import logging
from util.tree import Tree
from util.tree_filtered import TreeFiltered
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


def test_tree_stats_dict(fixture_test_tree):
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
    _tree = Tree()
    # use name to get a different field
    # my_tree.create_tree(tree,name_field="value")
    # _tree.create_tree(_tree_dict)
    _tree.create_tree(fixture_test_tree, analyze_fields=True, parent_field="parent")
    _stats = _tree.stats
    assert isinstance(_stats, dict) and len(_stats) > 0, "field stats of tree doesn't have entries"
    pass


def test_filtered_tree(fixture_test_tree):
    """testing filtering a tree"""
    _filtered_tree = TreeFiltered(filter_type="exclude")
    _filtered_tree.create_tree(fixture_test_tree, analyze_fields=True, parent_field="parent")
    # adding filter set
    _filtered_tree.add_filter(3)
    _node_filtered = _filtered_tree.get_node(8)
    assert _node_filtered is None, "Node should be filtered out"
    _node_filtered = _filtered_tree.get_node(3)
    assert _node_filtered is None, "Node mentioned in filter should be filtered out"
    _filtered_tree.is_active = False
    _node_filtered = _filtered_tree.get_node(8)
    assert _node_filtered is not None, "Node should be found as filter is switched off"
    _node_filtered = _filtered_tree.get_node(3)
    assert _node_filtered is not None, "Node should be found as filter is switched off"
