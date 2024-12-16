"""testing the CMD Runner"""

import pytest
from util.utils import CmdRunner


# @pytest.mark.parametrize("conversions",_cmd_conversions)
def test_custom_win_split_valid(fixture_test_paths):
    """converting valid paths for windows"""
    for test_path in fixture_test_paths:
        converted = CmdRunner.custom_win_split(test_path)
        assert isinstance(converted, list) and len(converted) > 0


# @pytest.mark.parametrize("conversions",_cmd_conversions)
def test_custom_win_split_invalid(fixture_test_invalid_paths):
    """converting valid paths for windows"""
    for test_path in fixture_test_invalid_paths:
        converted = CmdRunner.custom_win_split(test_path)
        assert converted is None
