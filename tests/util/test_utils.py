"""Testing the Utils class"""

import os
from datetime import datetime as DateTime

import pytest

from util import constants as C
from util.matrix_list import MatrixList
from util.utils import Utils


def test_date2xls_timestamp():
    """convert to XLS int"""
    assert Utils.date2xls_timestamp(DateTime(1970, 1, 1)) == C.DATE_INT_19700101


@pytest.mark.parametrize("_cmd", ["python", "git"])
def test_where(_cmd):
    """testing the location feature for git and python"""
    _cmd = Utils.where(_cmd)
    assert os.path.isfile(_cmd)


def test_get_python():
    """the get_python usually will select the Python associated with the VENV"""
    # to assert it we need to replace the quotes again ...
    _cmd = Utils.get_python()
    assert os.path.isfile(_cmd)


def test_helper_methods():
    """testing the helper methods"""
    _venv = Utils.get_venv()
    assert isinstance(_venv, str) or _venv is None
    _is_windows = Utils.is_windows()
    assert isinstance(_is_windows, bool)
    _branch = Utils.get_branch()
    assert isinstance(_branch, str) or _branch is None


def test_convert_methods():
    """testing the helper methods"""
    _venv = Utils.convert(C.Conversion.GIT_BRANCH.name)
    assert isinstance(_venv, str) or _venv is None
    _branch = Utils.convert(C.Conversion.VIRTUAL_ENV.name)
    assert isinstance(_branch, str) or _branch is None
    _python = Utils.convert(obj=C.Conversion.PYTHON.name, file_conversion=C.CygPathCmd.WIN2DOS.name)
    assert isinstance(_python, str)


def test_get_base_int():
    """testing the base number converter"""
    _num = 19
    _base = 2
    _base_num_list = Utils.get_base_int(_num, _base, inverse=False)
    _sum = 0
    for i in range(len(_base_num_list)):
        _sum += _base_num_list[i] * (_base**i)
    assert _num == _sum


def test_transpose_matrix():
    """test the transpose method"""  #
    m = [[1, 4], [2, 5], [3, 6]]
    t = MatrixList.transpose_matrix(m)
    assert t[0] == [1, 2, 3]
    assert t[1] == [4, 5, 6]


def test_reshape2rows():
    """test the reshape method
    (to be used for rich tables)
    a|b|c => [a,b,c]
    d|e|f    [d,e,f]
    """
    m = [["a", "d"], ["b", "e"], ["c", "f"]]
    t = MatrixList.reshape2rows(m)
    assert t[0] == ["a", "b", "c"]
    assert t[1] == ["d", "e", "f"]


def test_list2matrix():
    """test list2matrix"""
    m = ["a", "b", "c", "d", "e", "f", "g"]
    # reshape list into matrix
    t = MatrixList.list2matrix(m, 3)
    assert len(t) == 3
    assert len(t[0]) == 3
