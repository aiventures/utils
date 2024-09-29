""" Unit Tests for the Config Sample """

import pytest
from unittest.mock import MagicMock

from copy import deepcopy
import logging
import shlex

from util import constants as C
from util.config_env import ConfigEnv

import logging

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
    

def test_parse_commands(fixture_sample_config_json):
    """ test the parsing of the command pattern options """
    config_env = ConfigEnv(fixture_sample_config_json)
    # check the CMD_EXAMPLE1 definition of variables
    cmd = "CMD_EXAMPLE1"
    # parsing the commands as dict
    cmd_params = {"file":"testfile.txt","line":5}
    _cmd_dict = config_env.parse_cmd(cmd,**cmd_params)
    # note that shlex will strip quotes ... 
    _cmd_dict_args = shlex.split(_cmd_dict)
    assert isinstance(_cmd_dict,str) and len(_cmd_dict) > 0
    # same but using kwargs
    _cmd_kwargs = config_env.parse_cmd(cmd,file="testfile.txt",line=5)
    assert _cmd_dict == _cmd_kwargs


def test_validate_data_rules(fixture_sample_config_json, fixture_sample_stocks_data):
    """ test the parsing of txt files to parse them as dict files """
    config_env = ConfigEnv(fixture_sample_config_json)
    _invalid_rules = config_env._validate_data_rules()
    assert True
    pass


