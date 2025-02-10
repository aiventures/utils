"""Unit Tests for the Constants Class"""

import logging
import os
import re
from copy import deepcopy
from enum import Enum
from unittest.mock import MagicMock

import pytest

from util import constants as C
from util.config_env import ConfigEnv
from util.utils import PathConverter, Utils
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


@pytest.mark.parametrize("transform_rule", ["UNC", "WIN", "DOS", "OS", None, "WRONG_TYPE"])
def test_resolve_paths(transform_rule, fixture_paths):
    """testing resolve path for win paths (implicitly using PathConverter)"""
    for _path in fixture_paths:
        _resolved_path = Utils.resolve_path(_path, transform_rule=transform_rule, check_exist=False, info=True)
        # do some sanity checks
        if transform_rule == "DOS" and not Utils.is_windows():
            continue

        if transform_rule is None:
            assert _resolved_path is None, "no transform rule was passed"
            continue
        if _resolved_path is None:
            assert transform_rule == "WRONG_TYPE", "assert that wrong type lead to an error"
            continue
        _os = _resolved_path["OS"]
        _rule = _resolved_path["RULE"]
        _converted = _resolved_path["CONVERTED"]
        _quote = _resolved_path["QUOTE"]
        _original = _resolved_path["ORIGINAL"]
        _real_path = _resolved_path["REAL_PATH"]
        if _real_path is None:
            continue

        assert _rule == transform_rule, "assert transfer rule is copied"
        assert '"' in _quote, "assert quote has quotes"
        assert not "'" in _quote, "assert single quotes not in string"

        # check semantics
        if _rule == "UNC":
            assert "/" in _converted
            assert not "\\" in _converted
        elif _rule in ["DOS", "WIN"]:
            assert "\\" in _converted
            assert not "/" in _converted

        # same os and valid file
        if _rule == "OS" and _real_path:
            assert _real_path == _converted, "Conversion within conversion"

        if _os == "WIN":
            if _real_path:
                assert os.path.isdir(_original) or os.path.isfile(_original)
            # check that win paths are file objects as well
            if _rule == "DOS" or _rule == "WIN" and _real_path:
                assert os.path.isdir(_converted) or os.path.isfile(_converted)
        else:
            # not implemented
            continue
        pass
