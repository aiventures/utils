"""Unit Tests for the Constants Class"""

import logging
import os
from copy import deepcopy
from enum import Enum
from unittest.mock import MagicMock

import pytest

import util.constants as C
from util import constants as C
from util.config_env import ConfigEnv

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_abstract_enum(fixture_sample_enum):
    """test the abstract enum methods"""
    _names = fixture_sample_enum.get_names()
    assert len(_names) == 3
    _values = fixture_sample_enum.get_values()
    assert len(_values) == 3
    _dict = fixture_sample_enum.as_dict()
    assert isinstance(_dict, dict) and len(_dict) == 3


def test_abstract_enum_get(fixture_sample_enum):
    """finding keys"""
    _result = fixture_sample_enum.get_enum("TESTNAME2")
    assert isinstance(_result, Enum)
    _result = fixture_sample_enum.get_enum("TEST", exact=False)
    assert isinstance(_result, list) and len(_result) == 3
