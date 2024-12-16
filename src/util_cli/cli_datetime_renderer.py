""" Rendering some items from the datetime_util """

import logging
import os
import re
from enum import StrEnum

from pydantic import ValidationError
from rich.console import Console
from rich.emoji import Emoji
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.table import Table

from cli.bootstrap_config import console_maker
from cli.bootstrap_env import LOG_LEVEL
from model.model_datetime import CalendarDayType, CellRenderOptionType
from model.model_datetime import DayTypeEnum as DTE
from util import constants as C
from util.datetime_util import (MONTHS, MONTHS_SHORT, REGEX_DATE_RANGE,
                                REGEX_TIME_RANGE, REGEX_YYYYMMDD, WEEKDAY,
                                Calendar)
from util.utils import Utils

REGEX_ICON_STR = ":[a-zA-Z0-9_]+:" # alphanum chars embraced in colons
EMOJI_INFO = ":pencil:"

MONTH_EMOJIS = {1:":snowman:",2:":umbrella_with_rain_drops:",3:":seedling:",
               4:":leafy_green:",5:":man_biking:",6:":smiling_face_with_sunglasses:",
               7:":sun_with_face:",8:":beach_with_umbrella:",9:":sunflower:",
               10:":fallen_leaf:",11:":umbrella_with_rain_drops:",12:":zzz:",}

# OVERTIME THRESHOLD INDICATOR
OVERTIME_LEVELS = [-3.2,-2.8,-2,-1.,-0.4,0.,0.5,0.7,0.9,1.1,1.3,1.5,1.8,2.0,2.2]
OVERTIME_EMOJI_CODES = ["black_circle","zzz","blue_square","blue_circle",
                        "green_circle","green_square","yellow_circle",
                        "yellow_square","orange_circle",
                        "orange_square","red_circle","red_square","purple_circle",
                        "purple_square","skull"]
OVERTIME_EMOJIS = [Emoji.replace(f":{e}:") for e in OVERTIME_EMOJI_CODES]


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

    def __init__(self,calendar:Calendar,num_months_in_table:int=12,icon_render:CellRenderOptionType="all"):

        try:
            _ = CellRenderOptionType.model_validate(icon_render)
        except ValidationError as e:
            _error = e.errors()[0]
            _err = f"Couldn't parse as Pydantic Model, {_error['msg']}"
            logger.warning(_err)
            return

        self._calendar = calendar
        self._num_month = num_months_in_table
        self._console = console_maker.get_console()
        self._icon_render = icon_render

    @staticmethod
    def get_overtime_indicator(overtime:float)->str:
        """ calculates and renders overtime indicator """
        _idx = Utils.get_nearby_index(overtime,OVERTIME_LEVELS)
        return OVERTIME_EMOJIS[_idx]

    @staticmethod
    def show_overtime_indicator()->None:
        """ displays the overtime indicator """
        _finished = False
        _overtime = -3.
        while not _finished:
            _emoji = CalendarRenderer.get_overtime_indicator(_overtime)
            print(f"[OVERTIME INDICATOR] {_emoji} [{round(_overtime,1)}]")
            _overtime += 0.1
            if _overtime > 2.5:
                _finished = True

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
                    out = EMOJI_INFO
                elif icon_render == "first":
                    out = _icons[0]
                elif icon_render == "all":
                    out = "".join(_icons)
            else: # no icons in infos add default icon for info
                out = EMOJI_INFO

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
            self._console.print(_richtable)

    @staticmethod
    def render_info(info:str)->str:
        """ renders markdown information """
        # replace any icon shortcuts
        out_s = Emoji.replace(info)
        # drop durations
        out_s = re.sub(REGEX_TIME_RANGE, "", out_s)
        # drop date informations
        out_s = re.sub(REGEX_DATE_RANGE, "", out_s)
        out_s = re.sub(REGEX_YYYYMMDD, "", out_s)
        # replace datetime informations
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
        _s_i = None
        _d = day_info.duration
        # render duration and duration as emoji clock
        if isinstance(_d,float) and _d>0:
            _emoji_hours = int(round(_d)) % 12
            if _emoji_hours == 0:
                _emoji_hours = 12
            _emoji_clock = Emoji.replace(f":clock{str(_emoji_hours)}:")
            _hours_s = str(int(_d // 1)).zfill(2)
            _minutes_s = str(round(( _d % 1 ) * 60)).zfill(2)
            _time = f"{_hours_s}:{_minutes_s}"
            _ds = f"{_emoji_clock}{_time}"
        else:
            _ds = ""

        if _h is None:
            _h = ""
        else:
            _h = f"/{str(_h).upper()}"
        # @TODO RENDER DURATION WITH CLOCK EMOJI
        _markdown = Emoji.replace(f"* {_icon} {_dt} {_wd} KW{_w}/{_n} {_t}{_h} {_ds}")
        out.append(_markdown)

        if _i_list and add_info:
            for _i in _i_list:
                # render output string / drop items
                _i = CalendarRenderer.render_info(_i)

                out.append(f"  * {_i}  ")

        return out

    def get_markdown(self,month:int=None,add_info:bool=True,only_info:bool=False)->list:
        """ create markdown snippet for given month
            if month is None, the whole year will be
            returned
            add_info: if info is maintained add it to output
            only_info: only items with info are output
        """
        _stats = self.calendar.stats
        out = []
        if month is None:
            out.append(f"# **CALENDAR {self.calendar.year}**")
            _m_range = range(12, 0, -1)
        else:
            _m_range = range(month,month+1)
        for _month in _m_range:
            _has_info = len(_stats[_month]["days_with_info"]) > 0
            # only add month if there are infos in case only_info is selected
            if only_info is False or (only_info is True and _has_info):
                out.append("\n---")
                _month_emoji = Emoji.replace(MONTH_EMOJIS[_month])
                out.append(f"## {_month_emoji} **{self.calendar.year}-{str(_month).zfill(2)} {MONTHS[_month]}**")
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
    # console python -m rich.markdown test.md

    # sample creation of items. For real usafge this would be a plain txt file
    # allowing easy and quick entry of items
    _daytype_list = {DTE.WORKDAY_HOME:["Mo Di Mi Fr"],
                     DTE.FLEXTIME:["20240902"],
                     DTE.VACATION:["20240919-20240923","20240927"],
                     DTE.INFO:["20240929-20241004 :notebook: Test Info ",
                               "20240901 :red_circle: :green_square: MORE INFO 1230-1450 1615-1645",
                               "20241010 JUST INFO 0934-1134"]}
    _calendar = Calendar(2024,_daytype_list)
    # rendering the calendar and markdown list 
    # icon_render is "all","first","info","no_info"
    _renderer = CalendarRenderer(calendar=_calendar,num_months_in_table=12,icon_render="all")
    # render the calendar as table
    if False:
        _renderer.render_calendar()
    # render the calendar as markdown list (only_info=only items with INFO will be printed)
    _markdown_list = _renderer.get_markdown(only_info=False)
    console = _renderer.console
    if False:
        console.print(Markdown("\n".join(_markdown_list)))
    # overtime indicator
    if False:
        CalendarRenderer.show_overtime_indicator()
    # stats
    if True:
        _stats = _renderer.calendar.stats
        console.print(_stats)
        _stats_sum = _renderer.calendar.stats_sum
        console.print(_stats_sum)


