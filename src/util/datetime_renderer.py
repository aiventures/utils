""" Rendering some items from the datetime_util """

import logging
import os
from rich.logging import RichHandler

from rich.table import Table
from rich.console import Console
from util.datetime_util import Calendar,MONTHS_SHORT
from util.const_local import LOG_LEVEL

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
                _tmp = [str(_elem) for _elem in _row]
                _richtable.add_row(*_tmp)
            _console.print(_richtable)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    _calendar = Calendar(2024)
    CalendarRenderer(_calendar,12).render_calendar()
