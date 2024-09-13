""" Unit Tests for the Config Sample """

import pytest
from unittest.mock import MagicMock

from copy import deepcopy
import logging

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
        assert config_dict.get(C.CONFIG_REFERENCE) is not None

def test_config_get_groups(fixture_sample_config_json):
    """ test the reading of the configuration """
    config_env = ConfigEnv(fixture_sample_config_json)
    _groups = config_env.get_env_by_groups("groupA")
    assert len(_groups) == 2

def test_validate_commands(fixture_sample_config_json):
    """ test the command pattern valiudations """
    config_env = ConfigEnv(fixture_sample_config_json)
    wrong_commands = config_env._validate_commands()
    assert isinstance(wrong_commands,dict) and len(wrong_commands) > 0

def test_parse_commands(fixture_sample_config_json):
    """ test the parsing of the command pattern options """
    config_env = ConfigEnv(fixture_sample_config_json)
    # check the CMD_EXAMPLE1 definition of variables
    cmd = "CMD_EXAMPLE1"
    # parsing the commands as dict
    cmd_params = {"file":"testfile.txt","line":5}
    _cmd_dict = config_env.parse_cmd(cmd,**cmd_params)
    assert isinstance(_cmd_dict,str) and len(_cmd_dict) > 0
    # same but using kwargs
    _cmd_kwargs = config_env.parse_cmd(cmd,file="testfile.txt",line=5)
    assert _cmd_dict == _cmd_kwargs
