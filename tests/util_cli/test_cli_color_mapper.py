"""Coloring Console"""

from util_cli.cli_color_mapper import HEX, CODE, NAME, RGB, BASE_HEX_COLORS
from util_cli.cli_color_mapper import RGB_COLORS, HEX_COLORS, COLOR_NAMES
from util_cli.cli_color_mapper import ColorMapper

import pytest


# test some conversion variations
@pytest.mark.parametrize("value", [12, RGB_COLORS[10], HEX_COLORS[20], COLOR_NAMES[100]])
@pytest.mark.parametrize("to", [HEX, CODE, NAME, RGB])
def test_conversions_correct(fixture_color_mapper, value, to):
    """Testing the various color conversions"""
    _code = fixture_color_mapper.convert(value, to)
    if to == HEX:
        assert str(_code).startswith("#")
    elif to == CODE:
        assert isinstance(_code, int)
    elif to == NAME:
        assert isinstance(_code, str) and not str(_code).startswith("#")
    elif to == RGB:
        assert isinstance(_code, tuple)


# test some conversion variations
@pytest.mark.parametrize("value", ["abcd", 500.0 - 3, (-100, 23, 54, 23)])
@pytest.mark.parametrize("to", [HEX, CODE, NAME, RGB, "hugo"])
def test_conversions_invalid(fixture_color_mapper, value, to):
    """Testing the various color conversions"""
    _code = fixture_color_mapper.convert(value, to)
    if not _code == value:
        assert _code is None


def test_ansi2rgb():
    """test the ansi code calculation"""
    for _code in range(256):
        assert ColorMapper._ansi2rgb(_code) == ColorMapper.ansi2rgb(_code)
