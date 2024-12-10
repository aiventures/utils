""" Rendering some items from the datetime_util """

import logging
from enum import StrEnum
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from util.datetime_util import Calendar,MONTHS_SHORT
from util.const_local import LOG_LEVEL
from model.model_datetime import DayTypeEnum as DTE
from cli.bootstrap_config import console_maker

class DAYTYPE_ICONS(StrEnum):
    """ ICONS For Rich Table """
    WEEKEND = ":moai:"
    WORKDAY = ":purple_square:"
    WORKDAY_HOME = ":blue_square:"
    VACATION = ":red_circle:"
    HOLIDAY = ":rainbow:"
    FLEXTIME = ":orange_circle:" # Gleitzeit
    PARTTIME = ":red_circle:"

class DAYTYPE_COLORS(StrEnum):
    """ COLORS For Rich Table """
    WEEKEND = ""
    WORKDAY = "[magenta]"
    WORKDAY_HOME = "[deep_sky_blue1]"
    VACATION = "[red1]"
    HOLIDAY = "[gold1]"
    FLEXTIME = "[orange1]" # Gleitzeit
    PARTTIME = ""

class CalendarRenderer():
    """ Rendering some datetime utils """

    def __init__(self,calendar:Calendar,num_months:int=4):
        self._calendar = calendar
        self._num_months = num_months
        self._console = console_maker.get_console()
        pass

    def _render_cell(self,month:int,day:int)->str:
        _day_info = self._calendar.get_day_info(month,day)
        _day_type = _day_info.day_type
        _icon = DAYTYPE_ICONS[_day_type.name].value
        _color = DAYTYPE_COLORS[_day_type.name].value
        _weekday = _day_info.weekday_s
        _info_icon = ""
        if _day_info.info is not None:
            _info_icon = ":dizzy:"
        return f"{_icon} {_color}{_weekday}{_info_icon}"

    def render_calendar(self):
        """ renders the calendar  """
        _year = self._calendar._year
        _tables = self._calendar.get_calendar_table(self._num_months)
        for _table in _tables:
            _month_min = _table[0][1][0]
            _month_max = _table[0][-1][0]+1
            _months = [f"[green] {MONTHS_SHORT[_m]}" for _m in range(_month_min,_month_max)]
            _months.insert(0,"[green]DAY")
            _richtable = Table(title=f"CALENDAR [{_year}]",show_lines=True)
            for _m in _months:
                _richtable.add_column(_m,no_wrap=True,justify="left")
            for _row in _table:
                # _day_info = self._calendar.get_day_info()
                _rendered_row = []
                for _day_index in _row:
                    if not isinstance(_day_index,tuple):
                        if _day_index is not None:
                            _rendered_row.append(f"[green]{_day_index}")
                        else:
                            _rendered_row.append("")
                        continue
                    _rendered_cell = self._render_cell(month=_day_index[0],day=_day_index[1])
                    _rendered_row.append(_rendered_cell)
                _richtable.add_row(*_rendered_row)

                # _tmp = [str(_elem) for _elem in _row]
                # _richtable.add_row(*_tmp)
            self._console.print(_richtable)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])

    _daytype_list = {DTE.WORKDAY_HOME:["Mo Di Mi Fr"],
                     DTE.FLEXTIME:["20240902"],
                     DTE.VACATION:["20240919-20240923","20240927"],
                     DTE.INFO:["20240929-20241004 Test Info ","20240901 MORE INFO"]}

    _calendar = Calendar(2024,_daytype_list)
    CalendarRenderer(_calendar,12).render_calendar()
