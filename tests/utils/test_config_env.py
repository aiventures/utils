""" Unit Tests for the Config Sample """

import os
import logging
import pytest
# from unittest.mock import MagicMock
from copy import deepcopy
# import shlex
from util import constants as C
from util.config_env import ConfigEnv
from util.config_env import logger as util_logger
from util.utils import Utils

logger = logging.getLogger(__name__)

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
    """ test the command pattern valiudations """

    config_env = ConfigEnv(fixture_sample_config_json)
    _config_keys = config_env._config_keys
    _valid_keys = []
    _initialized_keys = []
    _wrong_keys = []
    for _config_key in _config_keys:
        _config = config_env._config[_config_key]
        _status = C.ConfigStatus(_config.get(C.ConfigAttribute.STATUS.name))
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

def test_validate_data_rules(fixture_sample_config_json, fixture_sample_stocks_data):
    """ test the parsing of txt files to parse them as dict files """
    config_env = ConfigEnv(fixture_sample_config_json)
    _invalid_rules = config_env._validate_data_rules()
    assert True
    pass


