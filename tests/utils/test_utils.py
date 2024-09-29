""" Testing the Utils class """

import pytest
from datetime import datetime as DateTime
import os
from util import constants as C
from util.utils import Utils

def test_date2xls_timestamp():
    """ convert to XLS int """
    assert Utils.date2xls_timestamp(DateTime(1970,1,1)) == C.DATE_INT_19700101

@pytest.mark.parametrize("_cmd",["python","git"])
def test_where(_cmd):
    """ testing the location feature for git and python"""
    _cmd = Utils.where(_cmd)
    assert os.path.isfile(_cmd)

def test_get_python():
    """ the get_python usually will select the Python associated with the VENV """
    # to assert it we need to replace the quotes again ...
    _cmd = Utils.get_python()
    assert os.path.isfile(_cmd)

def test_helper_methods():
    """ testing the helper methods """
    _venv = Utils.get_venv()
    assert isinstance(_venv,str) or _venv is None
    _is_windows = Utils.is_windows()
    assert isinstance(_is_windows,bool)
    _branch = Utils.get_branch()
    assert isinstance(_branch,str) or _branch is None

def test_convert_methods():
    """ testing the helper methods """
    _venv = Utils.convert(C.Conversion.GIT_BRANCH.name)
    assert isinstance(_venv,str) or _venv is None
    _branch = Utils.convert(C.Conversion.VIRTUAL_ENV.name)
    assert isinstance(_branch,str) or _branch is None
    _python = Utils.convert(obj=C.Conversion.PYTHON.name,
                            file_conversion=C.CygPathCmd.WIN2DOS.name)
    assert isinstance(_python,str)














