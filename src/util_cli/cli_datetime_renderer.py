""" Rendering some items from the datetime_util """

import logging
from enum import StrEnum
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from util.datetime_util import Calendar,MONTHS_SHORT
from util.const_local import LOG_LEVEL
from model.model_datetime import DayTypeEnum as DTE

class DAYTYPE_ICONS(StrEnum):
    """ ICONS For Rich Table """
    WEEKEND = ":moai:"
    WORKDAY = ":purple_square:"
    WORKDAY_HOME = ":blue_square:"
    VACATION = ":red_circle:"
    HOLIDAY = ":rainbow:"
    FLEXTIME = ":orange_circle:" # Gleitzeit
    PARTTIME = ":red_circle:"

class CalendarRenderer():
    """ Rendering some datetime utils """

    def __init__(self,calendar:Calendar,num_months:int=4):
        self._calendar = calendar
        self._num_months = num_months
        pass

    def render_calendar(self):
        """ renders the calendar  """
        _console = Console()
        _tables = self._calendar.get_calendar_table(self._num_months)
        for _table in _tables:
            _month_min = _table[0][1][0]
            _month_max = _table[0][-1][0]+1
            _months = [MONTHS_SHORT[_m] for _m in range(_month_min,_month_max)]
            _months.insert(0,"DAY")
            _richtable = Table(title="CALENDAR",show_lines=True)
            for _m in _months:
                _richtable.add_column(_m,no_wrap=True,justify="left")
            for _row in _table:
                # _day_info = self._calendar.get_day_info()
                _rendered_row = []
                for _day_index in _row:
                    if not isinstance(_day_index,tuple):
                        _rendered_row.append(_day_index)
                        continue
                    _day_info = self._calendar.get_day_info(_day_index[0],_day_index[1])
                    _day_type = _day_info.day_type
                    _icon = DAYTYPE_ICONS[_day_type.name].value
                    _weekday = _day_info.weekday_s
                    _rendered_row.append(f"{_icon} {_weekday}")
                    # _rendered_row.append("xxx")
                    pass
                _richtable.add_row(*_rendered_row)



                # _tmp = [str(_elem) for _elem in _row]
                # _richtable.add_row(*_tmp)
            _console.print(_richtable)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])

    _daytype_list = {DTE.WORKDAY_HOME:["Mo Di Mi Fr"],
                     DTE.FLEXTIME:["20240902"],
                     DTE.VACATION:["20240919-20240923","20240927"]}

    _calendar = Calendar(2024,_daytype_list)
    CalendarRenderer(_calendar,12).render_calendar()
