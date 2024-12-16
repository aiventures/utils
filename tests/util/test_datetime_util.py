"""testing the datetime utils Runner"""

from pydantic import ValidationError

from model.model_datetime import MonthAdapter
from util.datetime_util import Calendar
from util.datetime_util import DateTimeUtil as DTU
from util.datetime_util import DayTypeEnum as DT
# from util_cli.cli_datetime_renderer import CalendarRenderer


def test_get_holiday_dates():
    """getting all holiday date for a given year"""
    _year = 2024
    _holidays = DTU.get_holiday_dates(_year)
    assert isinstance(_holidays, dict)


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


def test_get_year_info():
    """getting all holiday date for a given year"""
    _year = 2024
    _year_info = DTU.create_calendar(_year)
    assert isinstance(_year_info, Calendar)


def test_duration_from_str():
    """testing duration"""
    s_duration = "some info and durations 125-432 1230-1600 1800-1845"
    duration = DTU.duration_from_str(s_duration)
    assert duration == 4.25
    # assert isinstance(_year_info,Calendar)
    duration_s = DTU.duration_from_str(s_duration, True)
    assert duration_s == "04:15"


def test_calendar():
    """testing creation of calendar"""
    _year = 2024
    _calendar = Calendar(_year,8)
    # adding some additional daytypes
    _daytype_list = {
        DT.WORKDAY_HOME: ["Mo Di Mi Fr"],
        DT.FLEXTIME: ["20240902"],
        DT.VACATION: ["20240919-20240923", "20240927"],
    }
    _calendar = Calendar(_year, _daytype_list)


def test_calendar2():
    """testing creation of calendar"""
    # adding some additional daytypes
    _year = 2024
    _daytype_list = {
        DT.WORKDAY_HOME: ["20240520-20240608"],
        DT.FLEXTIME: [],
        DT.VACATION: ["20240919-20240923", "20240927"],
        DT.INFO: [
            "20240929-20241004 Test Info ",
            "20240901 MORE INFO",
            "20240501 :brain: :maple_leaf: Testing with icons",
        ],
    }
    _calendar = Calendar(_year, _daytype_list)
    _stats = _calendar.stats
    assert isinstance(_stats, dict)
    _stats_sum = _calendar.stats_sum
    assert isinstance(_stats, dict)
    # render calendar table
    _calender_table = _calendar.get_calendar_table(4)
    # get markdown
    # console python -m rich.markdown test.md
    # _markdown = _calendar.get_markdown()
    # CalendarRenderer.render_calendar(_calendar)
