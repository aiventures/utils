""" Rendering some items from the datetime_util """

import logging
import os
import re
from enum import StrEnum

from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.text import Text
from rich.table import Table
from rich.emoji import Emoji
from util import constants as C
from cli.bootstrap_config import console_maker
from model.model_datetime import CalendarDayType
from model.model_datetime import DayTypeEnum as DTE,CellRenderOptionType
from util.const_local import LOG_LEVEL
from util.datetime_util import ( MONTHS_SHORT, Calendar,
                                 WEEKDAY, MONTHS )
from pydantic import ValidationError


REGEX_ICON_STR = ":[a-zA-Z0-9_]+:" # alphanum chars embraced in colons

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

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

class CalendarRenderer():
    """ Rendering some datetime utils """

    def __init__(self,calendar:Calendar,num_months_in_table:int=12,icon_render:CellRenderOptionType="all",
                 force_terminal:bool=None):

        try:
            _ = CellRenderOptionType.model_validate(icon_render)
        except ValidationError as e:
            _error = e.errors()[0]
            _err = f"Couldn't parse as Pydantic Model, {_error['msg']}"
            logger.warning(_err)
            return

        self._calendar = calendar
        self._num_month = num_months_in_table
        self._console = console_maker.get_console(force_terminal=force_terminal)
        self._icon_render = icon_render

    @property
    def console(self)->Console:
        """ returns rich console """
        return self._console

    @property
    def calendar(self)->Calendar:
        """ returns calendar """
        return self._calendar

    @staticmethod
    def _get_icons(day_info:dict,icon_render:str)->str:
        """ gets the icons from list """

        if icon_render == "no_info":
            return ""
        out = ""
        _icon = ""
        _s_info = ""
        if day_info.info is not None:
            _s_info = " ".join(day_info.info)
            _icons = re.findall(REGEX_ICON_STR,_s_info)
            if len(_icons) > 0:
                out = _icons
                if icon_render == "info":
                    out = ":dizzy:"
                elif icon_render == "first":
                    out = _icons[0]
                elif icon_render == "all":
                    out = "".join(_icons)
            else: # no icons in infos add default icon for info
                out = ":dizzy:"

        return out

    def _render_cell(self,month:int,day:int)->str:
        _day_info = self._calendar.get_day_info(month,day)
        _day_type = _day_info.day_type
        _icon = DAYTYPE_ICONS[_day_type.name].value
        _color = DAYTYPE_COLORS[_day_type.name].value
        _weekday = _day_info.weekday_s
        _info_icons = CalendarRenderer._get_icons(_day_info,self._icon_render)
        rendered = f"{_icon} {_color}{_weekday}{_info_icons}"
        return rendered

    def render_calendar(self):
        """ renders the calendar  """
        _year = self.calendar.year
        _tables = self._calendar.get_calendar_table(self._num_month)
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

    @staticmethod
    def markdown_info(info:str)->str:
        """ renders markdown information """
        # replace any icon shortcuts
        out_s = Emoji.replace(info)
        return out_s

    @staticmethod
    def create_markdown(day_info:CalendarDayType,add_info:bool=True)->list:
        """ convert a day info into mark down
            Markdown and Rich Inline Colors can't be used together
            https://github.com/Textualize/rich/issues/3587
        """

        out = []

        _day_type = day_info.day_type
        _icon = DAYTYPE_ICONS[_day_type.name].value

        _dt = day_info.datetime_s
        # split daytime
        _dt = f"{_dt[:4]}-{_dt[4:6]}-{_dt[6:8]}"
        _wd = WEEKDAY[day_info.weekday_num]
        _w = str(day_info.isoweeknum).zfill(2)
        _h = day_info.holiday
        _t = str(_day_type).upper()
        _n = str(day_info.day_in_year).zfill(3)
        _i_list = day_info.info
        if _h is None:
            _h = ""
        else:
            _h = f"/{str(_h).upper()}"
        _markdown = Emoji.replace(f"* {_icon} {_dt} {_wd} KW{_w}/{_n} {_t}{_h}")

        out.append(_markdown)

        if _i_list and add_info:
            for _i in _i_list:
                # render output string
                _i = CalendarRenderer.markdown_info(_i)
                out.append(f"  * {_i}  ")

        return out

    def get_markdown(self,month:int=None,add_info:bool=True,only_info:bool=False)->list:
        """ create markdown snippet for given month
            if month is None, the whole year will be
            returned
            add_info: if info is maintained add it to output
            only_info: only items with info are output
        """
        out = []
        if month is None:
            out.append(f"# **CALENDAR {self.calendar.year}**")
            _m_range = range(12, 0, -1)
        else:
            _m_range = range(month,month+1)
        for _month in _m_range:
            if only_info is False:
                out.append("\n---")
                out.append(f"## **{self.calendar.year}-{str(_month).zfill(2)} {MONTHS[_month]}**")
            _month_info = self.calendar.year_info[_month]
            _days = list(_month_info.keys())
            _days.sort(reverse=True)
            for _day in _days:
                _day_info = _month_info.get(_day)
                if only_info and _day_info.info is None:
                    continue
                _markdown = CalendarRenderer.create_markdown(_day_info,add_info)
                out.extend(_markdown)

        if month is None and only_info is False:
            out.append("--- ")
        return out

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])

    _daytype_list = {DTE.WORKDAY_HOME:["Mo Di Mi Fr"],
                     DTE.FLEXTIME:["20240902"],
                     DTE.VACATION:["20240919-20240923","20240927"],
                     DTE.INFO:["20240929-20241004 :rainbow: Test Info ","20240901 :red_circle: :green_square: MORE INFO"]}

    _calendar = Calendar(2024,_daytype_list)
    _renderer = CalendarRenderer(calendar=_calendar,num_months_in_table=12,icon_render="no_info",force_terminal=True)
    # _renderer.render_calendar()
    _markdown_list = _renderer.get_markdown(only_info=False)
    # _markdown = Text.from_markup(Markdown("\n".join(_renderer.get_markdown(only_info=False))))
    # _markdown = Markdown(Text.from_markup("\n".join(_renderer.get_markdown(only_info=False))))

    # console python -m rich.markdown test.md
    console = _renderer.console
    console.print(Markdown("\n".join(_markdown_list)))
