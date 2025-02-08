"""testing the datetime utils Runner"""

from datetime import datetime as DateTime

import pytest
from pydantic import ValidationError

from model.model_calendar import IndexType, MonthAdapter
from util.calendar_util import Calendar
from util.calendar_index import CalendarIndex

# from util_cli.cli_datetime_renderer import CalendarRenderer


def test_get_month_info():
    """getting all holiday date for a given year"""
    _year = 2024
    _month_info = Calendar.get_month_info(_year, 3)
    try:
        _validated = MonthAdapter.validate_python(_month_info)
        assert isinstance(_validated, dict), "Validation to Month Adpater is successful"
    except ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
        assert False, "Validation to Month Adapter failed"


def test_calendar(fixture_day_info_list):
    """testing creation of calendar"""
    _year = 2024
    _calendar = Calendar(_year, 8, fixture_day_info_list)


def test_calendar_index():
    """testing the calendar index"""
    _year = 2024
    _cal_index = CalendarIndex(_year)
    _index = _cal_index.index
    assert len(_index) == 366
    # checking the index map
    _index_map = _cal_index.index_map()
    assert isinstance(_index_map, dict)
    # checking the reverse calendar index
    _weekday_map = _cal_index.weeknum_map(IndexType.INDEX_MONTH_DAY)
    assert isinstance(_weekday_map, dict)
    _weekday_map2 = _cal_index.weeknum_map(IndexType.INDEX_DATETIME)
    assert isinstance(_weekday_map, dict)

def _calender_index_examples() -> list:
    """several variants for calendar index"""
    out = []
    out.append(pytest.param(True, DateTime(2024, 10, 3), id="A.01 Successful DateTime Object"))
    out.append(pytest.param(True, 110, id="A.02 Successful int Object"))
    out.append(pytest.param(True, (3, 10), id="A.03 Successful tuple Object"))
    out.append(pytest.param(True, "20240310", id="A.03 Successful YYYYMMDD str"))
    out.append(pytest.param(False, 600, id="B.01 Wrong int Object"))
    out.append(pytest.param(False, DateTime(2026, 10, 3), id="B.02 Wrong DateTime Object"))
    out.append(pytest.param(False, (99, 10), id="B.03 Wrong tuple Object"))
    out.append(pytest.param(False, "20260310", id="B.04 Wrong YYYYMMDD str"))
    return out


@pytest.mark.parametrize("is_valid,idx_param", _calender_index_examples())
def test_calendar2024_index_info(fixture_calendar2024_index, is_valid, idx_param):
    """testing calendar info method"""
    # 2024 is a leap year, 2010 has CW53 from previous year
    _info = fixture_calendar2024_index.info(idx_param)
    if is_valid:
        assert _info is not None, f"[{idx_param}] should be valid"
    else:
        assert _info is None, f"[{idx_param}] should be invalid"


def test_calendar2015_index_info(fixture_calendar2015_index):
    """testing calendar 2015 which has 53 calendar week from2019"""
    _info = fixture_calendar2015_index.info("20150810")
    assert _info is not None
    _month_map = fixture_calendar2015_index.month_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_month_map, dict)
    _week_map = fixture_calendar2015_index.week_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_week_map, dict)
    _monthweek_map = fixture_calendar2015_index.monthweek_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_monthweek_map, dict)


def test_calendar2024_index_maps(fixture_calendar2024_index):
    """testing calendar info method"""
    # 2024 is a leap year, 2010 has CW53 from previous year
    _month_map = fixture_calendar2024_index.month_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_month_map, dict)
    _week_map = fixture_calendar2024_index.week_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_week_map, dict)
    _monthweek_map = fixture_calendar2024_index.monthweek_map(index_type=IndexType.INDEX_MONTH_DAY)
    assert isinstance(_monthweek_map, dict)
