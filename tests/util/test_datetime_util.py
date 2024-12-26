"""testing the datetime utils Runner"""

from enum import EnumMeta


from util.datetime_util import DateTimeUtil as DTU

# from util_cli.cli_datetime_renderer import CalendarRenderer

def test_get_holiday_dates():
    """getting all holiday date for a given year"""
    _year = 2024
    _holidays = DTU.get_holiday_dates(_year)
    assert isinstance(_holidays, dict)

def test_year_index():
    """testing cereation of year index"""
    year_index = DTU.year_index()
    assert isinstance(year_index,dict)

def test_duration_from_str():
    """testing duration"""
    s_duration = "some info and durations 125-432 1230-1600 1800-1845"
    duration = DTU.duration_from_str(s_duration)
    assert duration == 4.25
    # assert isinstance(_year_info,Calendar)
    duration_s = DTU.duration_from_str(s_duration, True)
    assert duration_s == "04:15"

def test_add_shortcodes():
    """adding shortcodes """
    add_shortcodes = {"SHORTCODE":"SHORTCODE_VALUE"}
    _enum = DTU.add_shortcodes(add_shortcodes)
    assert isinstance(_enum,EnumMeta)
