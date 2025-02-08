"""Unit Tests for the Constants Class"""

import logging
import os
import json
import util.constants as C
from util.tree import Tree
from util.dict_tree import DictTreeNodeModel, DictTree

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_dict_tree(fixture_test_dict: dict):
    #     """test the dict tree object
    #     { "k1":"value1",
    #       "test_key":500,
    #       "k2":{"k2.1":5,
    #             "k2.2":"v2.2",
    #             "k2.3":["l1","test value","l3",{"dict_inner":["a","b","c"]}]
    #             }
    #     }
    #     """

    test_dict = json.loads(fixture_test_dict)
    my_dict_tree = DictTree(test_dict)
    # the underlying tree object
    _tree = my_dict_tree.tree
    assert isinstance(_tree, Tree)
    # here's the public methods
    _max_level = my_dict_tree.max_level
    assert isinstance(_max_level, int)
    _node_info = my_dict_tree.get_node(2)
    assert isinstance(_node_info, DictTreeNodeModel)
    _is_node_type = my_dict_tree.is_node_type(2, "leaf")
    assert isinstance(_is_node_type, bool)
    _is_leaf = my_dict_tree.is_leaf(2)
    assert isinstance(_is_leaf, bool)
    _nodes_in_level = my_dict_tree.get_nodes_in_level(2)
    assert isinstance(_nodes_in_level, list)
    _leaves = my_dict_tree.get_leaf_ids()
    # this is the reverse index > dict path
    _key_path = my_dict_tree.key_path(2)
    assert isinstance(_key_path, list)
    _value = my_dict_tree.value(2)
    assert isinstance(_value, int)
    _siblings = my_dict_tree.siblings(2)
    assert isinstance(_siblings, list)
    _dict_info = my_dict_tree.hierarchy_dict(node_type="leaf")
    assert isinstance(_dict_info, dict)
    _subtree = my_dict_tree.get_subtree_ids(6, node_type="node")
    assert isinstance(_subtree, list)
    _idx_invalid = my_dict_tree.get_node_id_by_path(["a"])
    assert _idx_invalid is None
    _idx_valid = my_dict_tree.get_node_id_by_path(["k2", "k2.3", 1])
    assert isinstance(_idx_valid, int)
    pass
