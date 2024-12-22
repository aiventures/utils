"""Class to represent a work log / journal allowing for
time tracking / work log keeping and more
Serves as input function for the datetime_util allowing
yout to create calendars and more
"""

from util.persistence import Persistence
from util.datetime_util import (REGEX_YYYYMMDD,REGEX_DATE_RANGE,REGEX_TIME_RANGE,REGEX_WEEKDAY)
from enum import Enum, StrEnum
from model.model_worklog import (ShortCodes,WorkLogModel)

# regex to extract todo_txt string matching signature @(...)
REGEX_TODO_TXT = r"\s@\((.+)?\)"

# default short tags that can be used in worklog 

class WorkLogTxt():
    """ Abstraction of a worklog_txt file """    

    def __init__(self,f_worklog_txt:str):
        self._calendars = {}
        pass
    

# def test_calendar2():
#     """testing creation of calendar"""
#     # adding some additional daytypes

#     _daytype_list = {
#         DT.WORKDAY_HOME: ["20240520-20240608"],
#         DT.FLEXTIME: [],
#         DT.VACATION: ["20240919-20240923", "20240927"],
#         DT.INFO: [
#             "20240929-20241004 Test Info ",
#             "20240901 MORE INFO",
#             "20240501 :brain: :maple_leaf: Testing with icons",
#         ],
#     }
#     _calendar = Calendar(_year, _daytype_list)
#     _stats = _calendar.stats
#     assert isinstance(_stats, dict)
#     _stats_sum = _calendar.stats_sum
#     assert isinstance(_stats, dict)
#     # render calendar table
#     _calender_table = _calendar.get_calendar_table(4)
    # get markdown
    # console python -m rich.markdown test.md
    # _markdown = _calendar.get_markdown()
    # CalendarRenderer.render_calendar(_calendar)

