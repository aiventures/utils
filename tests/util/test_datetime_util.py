""" testing the datetime utils Runner """
from util.datetime_util import ( DateTimeUtil as DTU,
                                 Calendar, DayTypeEnum as DT )

from model.model_datetime import MonthAdapter,MonthModelType
from util.datetime_renderer import CalendarRenderer
from pydantic import ValidationError

def test_get_holiday_dates():
    """ getting all holiday date for a given year """
    _year = 2024
    _holidays = DTU.get_holiday_dates(_year)
    assert isinstance(_holidays,dict)

def test_get_month_info():
    """ getting all holiday date for a given year """
    _year = 2024
    _month_info = Calendar.get_month_info(_year,3)
    try:
        _validated = MonthAdapter.validate_python(_month_info)
        assert isinstance(_validated,dict),"Validation to Month Adpater is successful"
    except ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
        assert False,"Validation to Month Adapter failed"

def test_get_year_info():
    """ getting all holiday date for a given year """
    _year = 2024
    _year_info = DTU.create_calendar(_year)
    pass
    # try:
    #     _validated = MonthAdapter.validate_python(_month_info)
    #     assert isinstance(_validated,dict),"Validation to Month Adpater is successful"
    # except ValidationError as e:
    #     print(f"VALIDATION ERROR: {e}")
    #     assert False,"Validation to Month Adapter failed"

def test_calendar():
    """ testing creation of calendar """
    _year = 2024
    _calendar = Calendar(_year)
    # adding some additional daytypes
    _daytype_list = {DT.WORKDAY_HOME:["Mo Di Mi Fr"],
                     DT.FLEXTIME:["20240902"],
                     DT.VACATION:["20240919-20240923","20240927"]}
    _calendar = Calendar(_year,_daytype_list)

def test_calendar2():
    """ testing creation of calendar """
    # adding some additional daytypes
    _year = 2024
    _daytype_list = {DT.WORKDAY_HOME:[],
                     DT.FLEXTIME:[],
                     DT.VACATION:["20240919-20240923","20240927"]}
    _calendar = Calendar(_year,_daytype_list)
    _stats = _calendar.stats
    pass
    _calender_table = _calendar.get_calendar_table(4)
    CalendarRenderer.render_calendar(_calendar)

