"""testing the file tree"""

from util.file_tree import FileTree


def test_file_tree(fixture_params_find):
    """testing tree"""
    _file_tree = FileTree(fixture_params_find)
    _tree = _file_tree.tree
    pass


def test_file_subtotals(fixture_params_find):
    """testing subtotal calculation"""
    _file_tree = FileTree(fixture_params_find, metadata=True)
    _file_tree._calc_total_size()
