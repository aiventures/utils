"""setup to test visualizers"""

# import os
# from copy import deepcopy
# from datetime import datetime as DateTime
# from pathlib import Path
import pytest
import json

# from model.model_filter import NumericalFilterModel, RegexFilterModel, StringFilterModel, FilterSetModel
# from util import constants as C
from util.tree import Tree
from util.dict_tree import DictTree
# from util.utils import Utils


@pytest.fixture(scope="module")
def fixture_tree_for_viz() -> Tree:
    """tree model
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

    _tree_dict = {
        1: {"parent_id": None, "value": "value 1", "object": "OBJ1"},
        2: {"parent_id": 1, "value": "value 2", "object": "OBJ2"},
        4: {"parent_id": 2, "value": "value 4", "object": "OBJ4"},
        5: {"parent_id": 2, "value": "value 5", "object": "OBJ5"},
        3: {"parent_id": 1, "value": "value 3", "object": "OBJ3"},
        6: {"parent_id": 3, "value": "value 6", "object": "OBJ6"},
        7: {"parent_id": 6, "value": "value 7", "object": "OBJ7"},
        8: {"parent_id": 6, "value": "value 8", "object": "OBJ8"},
        9: {"parent_id": 6, "value": "value 9", "object": "OBJ9"},
        10: {"parent_id": 8, "value": "value 10", "object": "OBJ10"},
        11: {"parent_id": 8, "value": "value 11", "object": "OBJ11"},
    }

    _tree = Tree()
    # use name to get a different field
    _tree.create_tree(_tree_dict, name_field="value", parent_field="parent_id")
    return _tree


@pytest.fixture(scope="module")
def fixture_test_dicttree() -> DictTree:
    """fixture filter set"""
    test_struc = """
        { "k1":"value1",
          "test_key":500,
          "k2":{"k2.1":5,
                "k2.2":"v2.2",
                "k2.3":["l1","test value","l3",{"dict_inner":["a","b","c"]}]
                }
        }
    """
    test_dict = json.loads(test_struc)
    my_dict_tree = DictTree(test_dict)
    return my_dict_tree
