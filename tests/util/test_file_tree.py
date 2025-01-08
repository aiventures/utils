"""testing the file tree"""

from util.file_tree import FileTree


def test_file_tree(fixture_params_find):
    """testing tree"""
    _file_tree = FileTree(fixture_params_find)
