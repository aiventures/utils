"""testing the file tree"""

from util.file_tree import FileTree
from model.model_file_tree import ParamsFileTreeModel


def test_file_tree(fixture_params_find):
    """testing tree"""
    _file_tree_params = ParamsFileTreeModel(
        file_filter_params=fixture_params_find, add_metadata=True, add_filesize=True
    )

    _file_tree = FileTree(_file_tree_params)
    _tree = _file_tree.tree
    pass


def test_file_subtotals(fixture_params_find):
    """testing subtotal calculation"""
    _file_tree_params = ParamsFileTreeModel(
        file_filter_params=fixture_params_find, add_metadata=True, add_filesize=True
    )
    _file_tree = FileTree(_file_tree_params)
    _file_tree._calc_total_sizes()
