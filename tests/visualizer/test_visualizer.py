"""Unit Tests Visualizers"""

import logging
import os
import util.constants as C
from util.tree import Tree
from util.dict_tree import DictTree
from model.model_tree import TreeNodeModel
from visualizer.tree_visualizer import TreeVisualizer
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

# test the tree object
# [1] ROOT (has no parents)
#      +---[2]
#           +---[4]
#           +---[5]
#      +---[3]
#           +---[6]
#                +---[7]
#                +---[8]
#                     +---[10]
#                     +---[11]
#                +---[9]
#


def test_create_tree_visualizer(fixture_tree_for_viz: Tree):
    """create the TreeVisualizer"""
    root_id = fixture_tree_for_viz.root_id
    hierarchy = fixture_tree_for_viz.hierarchy
    max_level = fixture_tree_for_viz.max_level
    visualizer = TreeVisualizer(root_node_id=root_id, tree_node_dict=hierarchy, num_levels=max_level)
    visualizer.render()
    pass


def test_create_dicttree_visualizer(fixture_test_dicttree: DictTree):
    """create the TreeVisualizer"""

    # { "k1":"value1",
    #   "test_key":500,
    #   "k2":
    #        {"k2.1":5,
    #         "k2.2":"v2.2",
    #         "k2.3":["l1",
    #                 "test value",
    #                 "l3",
    #                 {"dict_inner":[
    #                                "a",
    #                                "b",
    #                                "c"]}]
    #         }
    # }

    # get the dict tree and render the tree from there
    _tree = fixture_test_dicttree.tree
    root_id = _tree.root_id
    max_level = _tree.max_level
    hierarchy = _tree.hierarchy
    visualizer = TreeVisualizer(root_node_id=root_id, tree_node_dict=hierarchy, num_levels=max_level)
    visualizer.render()

    pass

    # _tree = fixture_test_dicttree.tree
    # root_id = _tree.root_id
    # hierarchy = _tree.hierarchy
    # visualizer = TreeVisualizer(root_node_id=root_id, tree_node_dict=hierarchy)
    # visualizer.render()
    pass
