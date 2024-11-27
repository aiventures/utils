""" Unit Tests for the Config Sample """

import os
import logging
import pytest
# from unittest.mock import MagicMock
# from copy import deepcopy
# import shlex
from pathlib import Path
from util import constants as C
from util.config_env import ConfigEnv
from util.config_env import logger as util_logger
from util.utils import Utils

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

def test_config_setup(fixture_sample_config_json):
    """ test the reading of the configuration """
    config_env = ConfigEnv(fixture_sample_config_json)
    config = config_env._config
    # asser the valid environent variables containing CONFIGTEST
    # do have a valid reference
    for config_key, config_dict in config.items():
        if not "CONFIG" in config_key:
            continue
        assert config_dict.get(C.ConfigAttribute.REFERENCE.value) is not None, f"CONFIG KEY {config_key} is wrong"

def test_config_get_groups(fixture_sample_config_json):
    """ test the reading of the configuration """
    config_env = ConfigEnv(fixture_sample_config_json)
    _groups = config_env.get_config_by_groups("groupA")
    assert len(_groups) == 2


def test_validate_commands(fixture_sample_config_json):
    """ test the command pattern validations """

    config_env = ConfigEnv(fixture_sample_config_json)
    _config_keys = config_env._config_keys
    _valid_keys = []
    _initialized_keys = []
    _wrong_keys = []
    for _config_key in _config_keys:
        _config = config_env._config[_config_key]
        _status = C.ConfigStatus(_config.get(C.ConfigAttribute.STATUS.value))
        if _status is C.ConfigStatus.VALID:
            _valid_keys.append(_config_key)
        elif _status is C.ConfigStatus.INITIAL:
            _initialized_keys.append(_config_key)
        elif _status is C.ConfigStatus.INVALID:
            _wrong_keys.append(_config_key)
    # verify all keys either are wrong or roght but not initialized
    assert len(_initialized_keys) == 0
    assert len(_valid_keys) > 0
    assert len(_wrong_keys) >= 0


def verify_debug_messages(substr:str,messages:list)->bool:
    """ checks for a substring in the debug message lists from spy method
        returns true if message is found
    """
    for _message in messages:
        for _arg in _message.args:
            if substr in _arg:
                return True
    return False

# use cases to be tested, alos compare with settings in test config template
# A.01. cmd - minimal example
# A.02. cmd - path and file valid
# A.03. cmd - only path
# A.04. cmd - invalid command / valid command
# A.05  cmd - variants with or without file refs
# A.06  cmd -
# B.01  where - test where with executable in param name
# B.02  where - test where with executable in attribute
# ...
# TODO TEST THAT PLACEHOLDERS FOR KEYS ARE REPLACED BY ITS REFS
# TODO DO A NEGATIVE TEST FOR A PARAM THAT IS NEITHER A CONFIG KEY NOR A KEY IN COMMAND KEY

# https://docs.pytest.org/en/7.1.x/example/parametrize.html#paramexamples
@pytest.mark.parametrize(
    "cmd,cmd_params",
    [
        pytest.param("CMD_EXAMPLE1",{"file":"testfile.txt","line":5}, id="A.01 CMD Parsing a CMD simple"),
        pytest.param("CMD_EXAMPLE1",{"file":"[CMD_EXAMPLE1]","line":6}, id="A.02 CMD Parsing with a Config Reference"),
    ],
)
def test_parse_commands(fixture_sample_config_json,cmd,cmd_params,mocker):
    """ test the parsing of the command pattern options """
    # spying on debug methods
    spy_debug = mocker.spy(util_logger,"debug")
    config_env = ConfigEnv(fixture_sample_config_json)
    # parsing the commands as dict
    _cmd_from_dict = config_env.parse_cmd(cmd,**cmd_params)
    # note that shlex will strip quotes ...
    _cmd_dict_args = Utils.split(_cmd_from_dict)
    assert isinstance(_cmd_from_dict,str) and len(_cmd_dict_args) > 0
    # verify from spy that certain methods are called (as defined by their debug log messages )
    # get current test case id
    _current_test = os.environ.get("PYTEST_CURRENT_TEST")
    # verify special cases
    if "A.02" in _current_test:
        # message that a pointer was dereferenced
        _contains = verify_debug_messages("dereferenced to",spy_debug.call_args_list)
        assert _contains is True,"A.02 CMD Parsing with a Config Reference did fail"

def create_testcases_get_ref()->list:
    """ returns a list of pytest params as input for the test_get_ref unit test """
    out = []
    # get valid refs to real paths
    _p_testdata = Path(C.PATH_ROOT.joinpath("test_data","test_path"))
    _p_testdata_space = Path(C.PATH_ROOT.joinpath("test_data","test_path","path with space"))
    _f_testfile_without_space = str(_p_testdata.joinpath("lorem_doc_root.md"))
    _f_testfile_with_space = str(_p_testdata.joinpath("test with space.txt"))
    _f_testfile_with_spacepath = str(_p_testdata_space.joinpath("test.txt"))
    # get valid refs with a path
    _ref_file_valid = "F_CONFIGTEST2"
    _ref_path_valid = "P_CONFIGTEST"
    _ref_cmd_valid = "W_PYTHON"
    _ref_cmd_valid_anycase = "w_pYTHoN"
    # valid ref with invalid path info
    _ref_valid_invalid_fileinfo = "P_30_ENTWICKLUNG"
    # get invalid ref with valid parent paths
    _f_testfile_validroot_invalidfile = _p_testdata.joinpath("invalid_file")
    # get ref with a filename only
    _f_filename_only = "only_filename.txt"
    # return tuple with valid, ref_exists, and path/ref information
    out.append(pytest.param(True, True, str(_p_testdata) ,id="C.01 valid Path"))
    out.append(pytest.param(True, True, str(_p_testdata_space) ,id="C.02 valid Path with spaces"))
    out.append(pytest.param(True, True, str(_f_testfile_without_space) ,id="C.03 valid File"))
    out.append(pytest.param(True, True, str(_f_testfile_with_space) ,id="C.04 valid File with spaces"))
    out.append(pytest.param(True, True, str(_f_testfile_with_spacepath) ,id="C.05 valid FIle with spaced Path"))
    out.append(pytest.param(True, True, str(_ref_file_valid) ,id="C.06 valid File Ref [F_CONFIGTEST2]"))
    out.append(pytest.param(True, True, str(_ref_path_valid) ,id="C.07 valid Path Ref [P_CONFIGTEST]"))
    out.append(pytest.param(True, True, str(_ref_cmd_valid) ,id="C.08 valid Where Ref [W_PYTHON]"))
    out.append(pytest.param(True, True, str(_ref_cmd_valid_anycase) ,id="C.09 valid Where Ref case insensitive test [w_pYTHoN]"))
    out.append(pytest.param(False,False, str(_ref_valid_invalid_fileinfo) ,id="C.10 valid Ref with invalid Path Ref [P_30_ENTWICKLUNG]"))
    out.append(pytest.param(False,False, str(_f_testfile_validroot_invalidfile) ,id="C.11 valid root path with invalid filename"))
    out.append(pytest.param(False,False, str(_f_filename_only) ,id="C.12 filename only"))
    return out

@pytest.mark.parametrize("valid_config,ref_exists,file_ref",create_testcases_get_ref())
def test_get_ref(fixture_config_env,valid_config,ref_exists,file_ref):
    """ testing the get ref method """
    _config_env = fixture_config_env
    _ref = _config_env.get_file_ref(file_ref,exists=False)
    _ref_exists = _config_env.get_file_ref(file_ref,exists=True)
    if valid_config:
        assert _ref is not None,"Valid Configuration should not be None"
        # check the exists check
        if ref_exists is True:
            assert _ref_exists is not None,"There should be a valid reference to a real file object"
            assert os.path.isfile(_ref_exists) or os.path.isdir(_ref_exists),"There should be ao real OS Object"
        else:
            assert _ref_exists is None,"There should be NO reference to a real file object"
            assert not os.path.isfile(_ref) or not os.path.isdir(_ref),"There should be no real OS Object"
    else:
        assert _ref_exists is None,"Invalid Configuration should be None"
        if _ref is not None:
            assert not os.path.isfile(_ref) or not os.path.isdir(_ref),"There should be no real OS Object"

