""" Coloring Console """
from util_cli.cli_color_mapper import HEX,CODE,NAME,RGB, BASE_HEX_COLORS
from util_cli.cli_color_mapper import RGB_COLORS,HEX_COLORS,COLOR_NAMES

import pytest


# test some conversion variations
@pytest.mark.parametrize("value",[12,RGB_COLORS[10],HEX_COLORS[20],COLOR_NAMES[100]])
@pytest.mark.parametrize("to",[HEX,CODE,NAME,RGB])
def test_conversions_correct(fixture_color_mapper,value,to):
    """ Testing the various color conversions"""
    _code = fixture_color_mapper.convert(value,to)
    if to == HEX:
        assert str(_code).startswith("#")
    elif to == CODE:
        assert isinstance(_code,int)
    elif to == NAME:
        assert isinstance(_code,str) and not str(_code).startswith("#")
    elif to == RGB:
        assert isinstance(_code,tuple)

# test some conversion variations
@pytest.mark.parametrize("value",["magenta"])
@pytest.mark.parametrize("to",[HEX])
def test_theme_changed(fixture_color_mapper,value,to):
    """ Testing whether the value for themes are changing """
    # _color = fixture_color_mapper[value,NAME]

    # check the hex value is in base values
    theme = fixture_color_mapper.theme
    if theme is None:
        fixture_color_mapper.theme = None
    hex_value = fixture_color_mapper.convert(value,HEX)
    try:        
        index = BASE_HEX_COLORS.index(hex_value)
        if theme is None:
            assert True
        else:
            assert False
    except ValueError:
        if theme is not None:
            assert True
        else:
            assert False



# test some conversion variations
@pytest.mark.parametrize("value",["abcd",500.-3,(-100,23,54,23)])
@pytest.mark.parametrize("to",[HEX,CODE,NAME,RGB,"hugo"])
def test_conversions_invalid(fixture_color_mapper,value,to):
    """ Testing the various color conversions"""
    _code = fixture_color_mapper.convert(value,to)
    if not _code == value:
        assert _code is None



