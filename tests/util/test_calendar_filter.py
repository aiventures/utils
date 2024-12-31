"""testing the CalendarFilter Object """

from datetime import datetime as DateTime

import pytest
from util.calendar_filter import CalendarFilter
from util.calendar_index import IndexType, CalendarIndex

# from util_cli.cli_datetime_renderer import CalendarRenderer

def _calender_filter_examples() -> list:
    """several variants for calendar index"""
    out = []
    out.append(pytest.param(True, "-1W", id="A.01 no start date 1 week offset from now implicit"))
    out.append(pytest.param(True, "now+1w", id="A.02 no start date 1 week offset from now explicit"))
    out.append(pytest.param(True, "now-1w:now+1w", id="A.03 Time range including separator"))
    out.append(pytest.param(True, "20241231:+1w", id="A.03 Fixed Date YYYYMMDD and offset including separator"))
    out.append(pytest.param(True, "now-2w:MoDi+2w", id="A.04 Date Offset and offset including Calendar Days"))

    return out

@pytest.mark.parametrize("is_valid,calendar_filter", _calender_filter_examples())
def test_filter(is_valid, calendar_filter):
    """testing calendar info method"""
    _filter = None
    _datelist = None
    if isinstance(calendar_filter,str):
        _filter = CalendarFilter(calendar_filter)
    elif isinstance(calendar_filter,list):
        _filter = CalendarFilter(date_list=calendar_filter)

    if is_valid:
        _datelist = _filter.datelist
        assert isinstance(_datelist,list)
    else:
        pass

    assert True

@pytest.mark.parametrize("is_valid,calendar_filter", _calender_filter_examples())
def test_calendar_index_filter(fixture_calendar2024_index:CalendarIndex,is_valid, calendar_filter):
    """ testing the calendar index with calendar filter """

    fixture_calendar2024_index.set_filter(filter_s=calendar_filter)
    _filtered_index_mask = fixture_calendar2024_index.index_map_filtered(IndexType.INDEX_DATETIME,IndexType.INDEX_DAY_IN_YEAR)
    _filtered_index = fixture_calendar2024_index.index_map_filtered(IndexType.INDEX_DATETIME,
                                                                         IndexType.INDEX_DAY_IN_YEAR,
                                                                         False)

    if is_valid:
        assert isinstance(_filtered_index_mask,dict)
        assert len(_filtered_index_mask) == 366
        assert len(_filtered_index) < 200
    



