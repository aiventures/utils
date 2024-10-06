""" Testing The Environment Class """

import os
import logging
import pytest
# from unittest.mock import MagicMock
from copy import deepcopy
import re
# import shlex
from util import constants as C
from util.config_env import Environment
from util.config_env import logger as util_logger
from util.utils import Utils

logger = logging.getLogger(__name__)

def test_environment(fixture_environment):
    """ instanciate the Environment class """
    _environment = fixture_environment
    # do some basic tests that some parts are available from the sample configurations
    _env_dict = _environment._env_dict
    assert len(_env_dict[C.EnvType.INVALID]) > 0
    assert len(_env_dict[C.EnvType.ATTRIBUTE]) > 0
    assert len(_env_dict[C.EnvType.INTERNAL]) > 0
    assert len(_env_dict[C.EnvType.ENV_FILE]) > 0
    assert len(_env_dict[C.EnvType.KEY_FILE]) > 0
    pass

@pytest.mark.parametrize(
    "env_key",
    [
        pytest.param("E_SAMPLE", id="E_SAMPLE Typed environment key-value pair to be added"),
        pytest.param("E_SAMPLE_WRONG_TYPE", id="E_SAMPLE_WRONG_TYPE Typed environment with a wrong type"),
        pytest.param("E_SIMPLE", id="E_SIMPLE Minimal definition, key is the main key"),
        pytest.param("E_SAMPLE_WHERE", id="E_SAMPLE_WHERE Example for a value with a ref to a where key"),
        pytest.param("E_SAMPLE_REF2", id="E_SAMPLE_REF2 Example for a value with a ref to a REF"),
        pytest.param("E_SAMPLE_WRONGREF", id="E_SAMPLE_WRONGREF Value with a wrong ref"),
        pytest.param("E_SAMPLE_WITHKEY", id="E_SAMPLE_WITHKEY Value with a key"),
        pytest.param("E_SAMPLE_ALL_TYPES", id="E_SAMPLE_ALL_TYPES Environemnt for all env types"),
        pytest.param("E_SAMPLE_FILEREF", id="E_SAMPLE_FILEREF Env with a file reference"),
    ],
)
def test_get_config_environments(fixture_environment,env_key):
    """ testing parsing of some environments """
    _environment = fixture_environment
    value = _environment.env_from_config(env_key)
    value_dict = _environment.env_from_config(env_key,as_dict=True)

    # some basic checks 
    if "WRONG" in env_key.upper():
        assert value == None
    elif "REF" in env_key.upper() or "WHERE" in env_key.upper():
        # assert any references are resolved 
        bracket_expressions = re.findall(C.REGEX_BRACKET_CONTENT,value)        
        assert len(bracket_expressions) == 0    
        assert isinstance(value_dict,dict)
    else:
        assert isinstance(value_dict,dict)
        _env_key = value_dict.get(C.ConfigAttribute.KEY.value)
        _config_key = value_dict.get(C.ConfigAttribute.CONFIG_KEY.value)        
        _config = _environment._config_env.get_config_by_key(_config_key)        
        if _config_key is not None and _env_key != _config_key :
            assert _config.get(C.ConfigAttribute.KEY.value) == _env_key
    pass
