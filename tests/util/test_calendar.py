"""testing the datetime utils Runner"""


from pydantic import ValidationError

from model.model_datetime import MonthAdapter
from util.calendar import Calendar

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
    _calendar = Calendar(_year,8,fixture_day_info_list)
    pass
