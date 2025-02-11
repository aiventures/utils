"""Testing The Environment Class"""

import json
import logging
import os
import re

# import inspect
# from unittest.mock import MagicMock
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from unittest import mock

import pytest
from pydantic import Field, TypeAdapter, ValidationError

from model.model_config import (
    ConfigItemAdapter,
    ConfigItemProcessed,
    ConfigItemType,
    ConfigModelAdapter,
    ConfigModelType,
    ConfigRule,
    ConfigValidator,
    DataDefinition,
    SourceRef,
)

# import shlex
from util import constants as C
from util.config_env import ConfigEnv, Environment
from util.config_env import logger as util_logger
from util.utils import Utils
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


def test_environment(fixture_environment):
    """instanciate the Environment class"""
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
        pytest.param("D_DEPOTSTAMM", id="D_DEPOTSTAMM Non Env Config with ENV Attribute "),
    ],
)
def test_get_config_environments(fixture_environment, env_key):
    """testing parsing of some environments"""
    _environment = fixture_environment
    value = _environment.env_from_config(env_key)
    value_dict = _environment.env_from_config(env_key, info=True)

    # some basic checks
    if "WRONG" in env_key.upper():
        assert value is None
    elif "REF" in env_key.upper() or "WHERE" in env_key.upper():
        # assert any references are resolved
        bracket_expressions = re.findall(C.REGEX_BRACKET_CONTENT, value)
        assert len(bracket_expressions) == 0
        assert isinstance(value_dict, dict)
    elif env_key.startswith("D_"):
        assert isinstance(value, dict)
    else:
        assert isinstance(value_dict, dict)
        _env_key = value_dict.get(C.ConfigAttribute.KEY.value)
        _config_key = value_dict.get(C.ConfigAttribute.CONFIG_KEY.value)
        _config = _environment._config_env.get_config_by_key(_config_key)
        if _config_key is not None and _env_key != _config_key:
            assert _config.get(C.ConfigAttribute.KEY.value) == _env_key
    pass


@pytest.mark.parametrize("env_type", C.ENV_TYPES)
def test_get_envs_by_env_type(fixture_environment, env_type):
    """gets the env keys by type"""
    # getting a docstring
    # test = inspect.getdoc(Environment._resolve_env)

    _environment = fixture_environment
    _envs = _environment.get_envs_by_type(env_type)
    assert isinstance(_envs, list)
    _envs_dict = _environment.get_envs_by_type(env_type, True)
    assert isinstance(_envs_dict, dict)
    # get the corresponding env output by type
    _env_output = _environment.get_env_formatted(env_type)
    assert isinstance(_env_output, dict)
    pass


def test_set_environment(fixture_environment):
    """check setting of environment"""
    fixture_environment.set_environment(clear_env=True)
    # set environmment
    fixture_environment.set_environment()
    _env_dict = fixture_environment.get_envs_by_type(C.EnvType.OS_ENVIRON, info=True)
    for _env_key, _info in _env_dict.items():
        _value = _info.get(C.ConfigAttribute.VALUE.value)
        _env_value = os.environ.get(_env_key)
        assert _value == _env_value
    # clear environment
    fixture_environment.set_environment(clear_env=True)
    for _env_key, _ in _env_dict.items():
        _env_value = os.environ.get(_env_key)
        assert _env_value is None


def test_create_set_vars_bat(fixture_battest_path, fixture_environment):
    """check setting of environment"""
    # create a test env file
    _f_bat_set_vars = str(Path(fixture_battest_path).joinpath("test_bat_set_vars.bat"))
    # clean up previous test file
    if os.path.isfile(_f_bat_set_vars):
        os.remove(_f_bat_set_vars)

    f_ref = fixture_environment.create_env_vars_bat(_f_bat_set_vars)
    assert os.path.isfile(f_ref), "SET Vars file in HOME path could not be created"


def _bootstrap_examples() -> list:
    """testcase for test_bootstrap_ref"""
    out = []
    _tc = {"ref": "F_CONFIGTEST1"}
    out.append(pytest.param("suc dict", _tc, id="A.01 Successful retrieve of a file ref as dict"))
    _tc = {"ref": "F_CONFIGTEST1", "as_value": True}
    out.append(pytest.param("suc str", _tc, id="A.02 Successful retrieve of a file ref as string"))
    _tc = {"ref": "F_CONFIGTEST1", "as_sourceref": True}
    out.append(pytest.param("suc sourceref", _tc, id="A.03 Successful retrieve of a file ref as Source Ref"))
    _tc = {"ref": "ENV_VAR_TEST", "as_value": True}
    out.append(pytest.param("suc str", _tc, id="A.04 Successful retrieve of an environment value"))
    _tc = {"ref": "CMD_EXAMPLE3", "as_value": True}
    out.append(pytest.param("config str", _tc, id="A.05 Case returning config value"))
    _tc = {"ref": "CMD_EXAMPLE3"}
    out.append(pytest.param("config dict", _tc, id="A.06 Case returning config value"))
    _tc = {"ref": "HUGO4711", "strict": True, "as_value": True}
    out.append(pytest.param("err env value", _tc, id="B.01 Error case no valid environment,strict path checking"))
    _tc = {"ref": "HUGO4711", "strict": True, "as_sourceref": True}
    out.append(
        pytest.param(
            "err env SOURCEREF", _tc, id="B.01 Error case no valid environment, return sourceref, strict path checking"
        )
    )
    return out


@mock.patch.dict(os.environ, {"ENV_VAR_TEST": "ENVVARTEST_VALUE"}, clear=True)
@pytest.mark.parametrize("tc_signature,bootstrap_example", _bootstrap_examples())
def test_bootstrap_ref(fixture_environment, tc_signature, bootstrap_example):
    """testing the bootstrap ref method"""
    env_value = os.environ.get("ENV_VAR_TEST")
    _config_env = fixture_environment.config_env
    bootstrap_example["config_env"] = _config_env
    _bootstrap_value = fixture_environment.bootstrap_ref(**bootstrap_example)
    _type = None
    if _bootstrap_value:
        _type = type(_bootstrap_value)
    if "dict" in tc_signature:
        assert isinstance(_bootstrap_value, dict), f"Expected types don't match, got [{_type}], expected dict"
    elif "str" in tc_signature:
        assert isinstance(_bootstrap_value, str), f"Expected types don't match, got [{_type}], expected str"
    elif "sourceref" in tc_signature:
        assert isinstance(_bootstrap_value, SourceRef), f"Expected types don't match, got [{_type}], expected SourceRef"
    elif "err" in tc_signature:
        assert _bootstrap_value is None, f"Expected None but got {_bootstrap_value}"


def test_env_model(fixture_environment):
    """test the parsing of the env json into a pydantic model"""
    _config_env = fixture_environment.config_env
    _config = _config_env.config
    # Prefixes
    _config_item_types = ["F", "P", "E", "W", "J"]

    # try to parse each item with a fitting model
    for _key, _config_item in _config.items():
        _prefix = _key.split("_")[0]
        _model = None
        try:
            # parse dependening from path type
            if _prefix in _config_item_types:
                _model = ConfigItemProcessed(**_config_item)
                _model.k = _key
            elif _prefix == "R":
                _model = ConfigRule(**_config_item)
                _model.k = _key
            elif _prefix == "D":
                _model = DataDefinition(**_config_item)
                _model.k = _key
        except ValidationError as e:
            if "WRONG" in _key:
                continue
            _errors = e.errors()
            assert False, f"Key [{_key}], couldn't parse as Pydantic Model, {repr(_errors)}"

    _valid_config = {}
    for _key, _config_item in _config.items():
        try:
            _ = ConfigItemAdapter.validate_python(_config_item)
            _valid_config[_key] = _config_item
        except ValidationError as e:
            if "WRONG" in _key:
                continue
            _errors = e.errors()
            assert False, f"Key [{_key}], couldn't parse as Pydantic Model, {repr(_errors)}"

    # try to parse correct and incorrect configurations
    _validated = ConfigValidator.validate_config(_config)
    # if it is a dict, then some error occured
    # this is true for the original configuration
    _is_invalid_config = isinstance(_validated, dict) and _validated.get(C.ERROR) is not None
    assert _is_invalid_config, "Original Sample Config should contain validation errors"

    # try to parse the correct config (=the one with WRONG_... Keys dropped)
    _validated = ConfigValidator.validate_config(_valid_config)
    _is_valid_config = isinstance(_validated, dict) and _validated.get(C.ERROR) is None
    assert _is_valid_config, "Original Sample Config should be valid"
