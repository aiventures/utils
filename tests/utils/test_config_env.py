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
