""" Unit Tests for the Constants Class """

import pytest
from unittest.mock import MagicMock
import os

from copy import deepcopy
import logging
from enum import Enum
import re

from util import constants as C
from util.config_env import ConfigEnv
from util.utils import PathConverter
from util.utils import Utils

import logging

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("conv",C.CygPathCmd.get_names())
def test_path_converter_valid(conv,fixture_testpath,fixture_testpath_withspace):
    """ test the path converter using cygpath
        Only test if the cygpath executable is present
    """
    cmd_cygpath = Utils.get_executable(C.Cmd.CYGPATH.name)
    if not cmd_cygpath:
        pytest.skip("CygPath could not be found on machine, check your setup")

    testpaths = [fixture_testpath,fixture_testpath_withspace,
                 '/c/30_Entwicklung/WORK_JUPYTER/root/utils/test_path',]
    for testpath in testpaths:
        path_converter = PathConverter()
        kwargs = {C.CYGPATH_CONV:conv,C.CYGPATH_PATH:testpath}
        _conv_path = path_converter.convert(**kwargs)
        assert isinstance(_conv_path,str)
        _conv_path_dir = re.findall(C.REGEX_STRING_QUOTED_STR,_conv_path)
        # checking for dir with paths containing quotes will lead to false
        if len(_conv_path_dir)>0:
            _conv_path_dir = _conv_path_dir[0]
        else:
            _conv_path_dir = _conv_path
        is_dir = os.path.isdir(_conv_path_dir)
        # UNV paths are not recognized as path
        if conv == "NO_CONV":
            assert _conv_path == testpath
            continue
        if conv.endswith("UNC"):
            continue
        assert is_dir
