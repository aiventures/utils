"""Rendering some items from the datetime_util"""

import logging
import os
import re
from datetime import datetime as DateTime
from enum import StrEnum
from typing import List

from pydantic import ValidationError
from rich.console import Console
from rich.emoji import Emoji
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.table import Table
from rich.tree import Tree

from cli.bootstrap_config import console_maker
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_calendar import CalendarColoringType, CalendarDayType, CellRenderOptionType, IndexType
from util.calendar_util import REGEX_DATE_RANGE, REGEX_YYYYMMDD, Calendar
from util.calendar_index import CalendarIndex
from util.datetime_util import (
    MONTHS,
    MONTHS_SHORT,
    REGEX_TIME_RANGE,
    WEEKDAY,
)
from util.emoji_util import EmojiUtil
from util.utils import Utils
from util.calendar_filter import CalendarFilter


REGEX_ICON_STR = ":[a-zA-Z0-9_]+:"  # alphanum chars embraced in colons
EMOJI_INFO = ":pencil:"

MONTH_EMOJIS = {
    1: ":snowflake:",
    2: ":umbrella_with_rain_drops:",
    3: ":seedling:",
    4: ":leafy_green:",
    5: ":man_biking:",
    6: ":smiling_face_with_sunglasses:",
    7: ":sun_with_face:",
    8: ":sunflower:",
    9: ":sheaf_of_rice:",
    10: ":fallen_leaf:",
    11: ":umbrella_with_rain_drops:",
    12: ":evergreen_tree:",
}

# OVERTIME THRESHOLD INDICATOR
OVERTIME_LEVELS = [-3.2, -2.8, -2, -1.0, -0.4, 0.0, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.8, 2.0, 2.2]
OVERTIME_EMOJI_CODES = [
    "black_circle",
    "zzz",
    "blue_square",
    "blue_circle",
    "green_circle",
    "green_square",
    "yellow_circle",
    "yellow_square",
    "orange_circle",
    "orange_square",
    "red_circle",
    "red_square",
    "purple_circle",
    "purple_square",
    "skull",
]

OVERTIME_EMOJIS = [Emoji.replace(f":{e}:") for e in OVERTIME_EMOJI_CODES]

OVERTIME_COLORS = [
    "bright_black",
    "navy_blue",
    "blue",
    "bright_blue",
    "dark_green",
    "green",
    "bright_yellow",
    "yellow",
    "gold1",
    "dark_orange3",
    "red",
    "bright_red",
    "deep_pink1",
    "bright_magenta",
    "medium_orchid1",
]


class DAYTYPE_ICONS(StrEnum):
    """ICONS For Rich Table"""

    WEEKEND = ":moai:"
    WORKDAY = ":purple_square:"
    WORKDAY_HOME = ":blue_square:"
    VACATION = ":red_circle:"
    HOLIDAY = ":rainbow:"
    FLEXTIME = ":orange_circle:"  # Gleitzeit
    PARTTIME = ":red_circle:"


class DAYTYPE_COLORS(StrEnum):
    """COLORS For Rich Table"""

    WEEKEND = ""
    WORKDAY = "[magenta]"
    WORKDAY_HOME = "[deep_sky_blue1]"
    VACATION = "[red1]"
    HOLIDAY = "[gold1]"
    FLEXTIME = "[orange1]"  # Gleitzeit
    PARTTIME = ""


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class CalendarRenderer:
    """Rendering some datetime utils"""

    def __init__(
        self,
        calendar: Calendar,
        num_months_in_table: int = 12,
        icon_render: CellRenderOptionType = "all",
        render_duration: bool = False,
        calendar_colors: CalendarColoringType = None,
    ):
        try:
            _ = CellRenderOptionType.model_validate(icon_render)
        except ValidationError as e:
            _error = e.errors()[0]
            _err = f"Couldn't parse as Pydantic Model, {_error['msg']}"
            logger.warning(_err)
            return

        self._calendar: Calendar = calendar
        self._year: int = calendar.year
        self._num_month: int = num_months_in_table
        self._console: Console = console_maker.get_console()
        self._icon_render: CellRenderOptionType = icon_render
        self._render_duration: bool = render_duration
        self._calendar_colors = None
        if calendar_colors is None:
            self._calendar_colors = CalendarColoringType()
        else:
            self._calendar_colors = calendar_colors
        self._calendar_index = CalendarIndex(year=self._year, index_type=IndexType.INDEX_DATETIME)
        self._month_week_filter_map: dict = None
        self._filter_datelist: List[DateTime] = None

    @staticmethod
    def get_overtime_indicator(overtime: float) -> str:
        """calculates and renders overtime indicator"""
        _idx = Utils.get_nearby_index(overtime, OVERTIME_LEVELS)
        return OVERTIME_EMOJIS[_idx]

    @staticmethod
    def get_overtime_color(overtime: float) -> str:
        """calculates and returns an overtime color"""
        _idx = Utils.get_nearby_index(overtime, OVERTIME_LEVELS)
        return OVERTIME_COLORS[_idx]

    @staticmethod
    def show_overtime_indicator() -> None:
        """displays the overtime indicator"""
        _console = console_maker.get_console()
        _finished = False
        _overtime = -3.0
        while not _finished:
            _emoji = CalendarRenderer.get_overtime_indicator(_overtime)
            _color = CalendarRenderer.get_overtime_color(_overtime)
            _console.print(f"[{_color}]\[OVERTIME INDICATOR] {_emoji} {_color} \[{round(_overtime, 1)}]")
            _overtime += 0.1
            if _overtime > 2.5:
                _finished = True

    @property
    def console(self) -> Console:
        """returns rich console"""
        return self._console

    @property
    def calendar(self) -> Calendar:
        """returns calendar"""
        return self._calendar

    @staticmethod
    def _get_icons(day_info: dict, icon_render: str) -> str:
        """gets the icons from list"""

        if icon_render == "no_info":
            return ""
        out = ""
        _icon = ""
        _s_info = ""
        if day_info.info is not None:
            _s_info = " ".join(day_info.info)
            _icons = re.findall(REGEX_ICON_STR, _s_info)
            if len(_icons) > 0:
                out = _icons
                if icon_render == "info":
                    out = EMOJI_INFO
                elif icon_render == "first":
                    out = _icons[0]
                elif icon_render == "all":
                    out = "".join(_icons)
            else:  # no icons in infos add default icon for info
                out = EMOJI_INFO

        return out

    @staticmethod
    def render_info(info: str) -> str:
        """renders markdown information by removing any informations stored elsewhere
        (such as date information)
        """
        # replace any icon shortcuts
        out_s = Emoji.replace(info)
        # drop durations
        out_s = re.sub(REGEX_TIME_RANGE, "", out_s)
        # drop date informations
        out_s = re.sub(REGEX_DATE_RANGE, "", out_s)
        out_s = re.sub(REGEX_YYYYMMDD, "", out_s)
        # replace datetime informations
        return out_s

    @property
    def calendar_filter(self) -> CalendarFilter:
        """returns rhe calendar filter"""
        if self._calendar_index is not None:
            return self._calendar_index.calendar_filter
        else:
            return None

    @property
    def calendar_index(self) -> CalendarIndex:
        """getter for calendar index"""
        return self._calendar_index

    @property
    def months_to_display(self) -> List[int]:
        """returns months to be displayed"""
        months = None
        if self._month_week_filter_map is None:
            months = range(1, 13)
        else:
            months = self._month_week_filter_map.keys()
        return sorted(list(months))

    @property
    def weeks_to_display(self) -> List[int] | None:
        """returns weeks to be displayed"""
        weeks = None
        if self._month_week_filter_map is not None:
            weeks = []
            for _weekdict in list(self._month_week_filter_map.values()):
                weeks.extend(list(_weekdict.keys()))
            weeks = sorted(list(set(weeks)))
        return weeks

    @property
    def dates_to_display(self) -> List[DateTime] | None:
        """returns dates to be displayed"""
        return self._filter_datelist

    def set_calendar_filter(self, filter_s: str = None, date_list: List[List[DateTime] | DateTime] = None) -> None:
        """sets the calendar filter to only render a portion of the calendar"""
        self._calendar_index.set_filter(filter_s, date_list)
        self._month_week_filter_map = None
        self._filter_datelist = None
        if self._calendar_index.calendar_filter is not None:
            self._month_week_filter_map = self._calendar_index.month_week_filter_map()
            self._filter_datelist = self._calendar_index.calendar_filter.datelist

    def _render_day_info(self, day_info: CalendarDayType, colorize: bool = False) -> str:
        """renders day information as line"""
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
        _ds = ""

        # render duration
        if self._render_duration:
            _d = day_info.duration
            _indicator = ""
            _overtime = ""

            if isinstance(day_info.overtime, (float, int)):
                _overtime = day_info.overtime
                _indicator = CalendarRenderer.get_overtime_indicator(_overtime)
                _color = CalendarRenderer.get_overtime_color(_overtime)

                _sign = "+"
                if _overtime < 0:
                    _sign = ""
                _overtime = f"{_sign}{_overtime:.1f}"

            # render duration and duration as emoji clock
            if isinstance(_d, float) and _d > 0:
                _emoji_hours = int(round(_d)) % 12
                if _emoji_hours == 0:
                    _emoji_hours = 12
                _emoji_clock = Emoji.replace(f":clock{str(_emoji_hours)}:")
                _hours_s = str(int(_d // 1)).zfill(2)
                _minutes_s = str(round((_d % 1) * 60)).zfill(2)
                _time = f"{_hours_s}:{_minutes_s}"
                _ds = f"{_indicator} {_time}/{_overtime}{_emoji_clock}"
            else:
                _ds = ""

            if colorize is True and len(_ds) > 0:
                _ds = f"[{_color}]{_ds}[/]"

        if _h is None:
            _h = ""
        else:
            _h = f"/{str(_h).upper()}"

        if colorize is False:
            out_s = f"{_icon} {_dt} {_wd} KW{_w}/{_n} {_t}{_h} {_ds}"
        else:
            _day_type = day_info.day_type.name
            _color = getattr(self._calendar_colors, _day_type)
            out_s = f"{_icon} [{_color}]{_dt} {_wd} KW{_w}/{_n} {_t}{_h}[/] {_ds}"

        out_s = Emoji.replace(out_s)
        return out_s


class CalendarTableRenderer(CalendarRenderer):
    """subclass to render calendar as Markdown or Table"""

    # def __init__(self, calendar, num_months_in_table=12, icon_render="all"):
    #     super().__init__(calendar, num_months_in_table, icon_render)

    def _render_cell(self, month: int, day: int) -> str:
        _day_info = self._calendar.get_day_info(month, day)
        _day_type = _day_info.day_type
        _icon = DAYTYPE_ICONS[_day_type.name].value
        _color = DAYTYPE_COLORS[_day_type.name].value
        _weekday = _day_info.weekday_s
        _info_icons = CalendarRenderer._get_icons(_day_info, self._icon_render)
        rendered = f"{_icon} {_color}{_weekday}{_info_icons}"
        return rendered

    def render_calendar(self):
        """renders the calendar as rich table"""
        _year = self.calendar.year
        _tables = self._calendar.get_calendar_table(self._num_month)
        for _table in _tables:
            _month_min = _table[0][1][0]
            _month_max = _table[0][-1][0] + 1
            _months = [f"[green] {MONTHS_SHORT[_m]}" for _m in range(_month_min, _month_max)]
            _months.insert(0, "[green]DAY")
            _richtable = Table(title=f"CALENDAR [{_year}]", show_lines=True)
            for _m in _months:
                _richtable.add_column(_m, no_wrap=True, justify="left")
            for _row in _table:
                # _day_info = self._calendar.get_day_info()
                _rendered_row = []
                for _day_index in _row:
                    if not isinstance(_day_index, tuple):
                        if _day_index is not None:
                            _rendered_row.append(f"[green]{_day_index}")
                        else:
                            _rendered_row.append("")
                        continue
                    _rendered_cell = self._render_cell(month=_day_index[0], day=_day_index[1])
                    _rendered_row.append(_rendered_cell)
                _richtable.add_row(*_rendered_row)
            self._console.print(_richtable)

    def create_markdown(self, day_info: CalendarDayType, add_info: bool = True) -> list:
        """convert a day info into mark down
        Markdown and Rich Inline Colors can't be used together
        https://github.com/Textualize/rich/issues/3587
        """

        # TODO PRIO2 add logic to only display some parts
        out = []
        _markdown = f"* {self._render_day_info(day_info)}"
        out.append(_markdown)

        _i_list = day_info.info
        if _i_list and add_info:
            for _i in _i_list:
                # render output string / drop items
                _i = CalendarRenderer.render_info(_i)
                out.append(f"  * {_i}  ")

        return out

    def get_markdown(self, add_info: bool = True, only_info: bool = False) -> list:
        """create markdown snippet for given month
        if month is None, the whole year will be
        returned
        add_info: if info is maintained add it to output
        only_info: only items with info are output
        """
        out = []
        # get filter settings
        _date_list = self._filter_datelist
        _month_week_filter_map = self._month_week_filter_map
        # no filter is set display all
        _m_range = range(12, 0, -1)
        if _month_week_filter_map is None:
            out.append(f"# **CALENDAR {self.calendar.year}**")
        else:
            _m_range = list(_month_week_filter_map.keys())
            _m_range.sort(reverse=True)

        _stats = self.calendar.stats
        _month = None
        for _month in _m_range:
            _has_info = len(_stats[_month]["days_with_info"]) > 0
            # only add month if there are infos in case only_info is selected
            # TODO PRIO3 put rendering options into a model
            if only_info is False or (only_info is True and _has_info):
                out.append("\n---")
                _month_emoji = Emoji.replace(MONTH_EMOJIS[_month])
                out.append(f"## {_month_emoji} **{self.calendar.year}-{str(_month).zfill(2)} {MONTHS[_month]}**")
            _month_info = self.calendar.year_info[_month]
            _days = list(_month_info.keys())
            _days.sort(reverse=True)
            for _day in _days:
                _day_info = _month_info.get(_day)
                _datetime = _day_info.datetime
                if (_date_list is not None and _datetime not in _date_list) or (only_info and _day_info.info is None):
                    continue

                _markdown = self.create_markdown(_day_info, add_info)
                out.extend(_markdown)

        if _month is None and only_info is False:
            out.append("--- ")
        return out


class CalendarTreeRenderer(CalendarRenderer):
    """subclass to render calendar as Markdown or Table"""

    def __init__(
        self,
        calendar: Calendar,
        num_months_in_table=12,
        icon_render: CellRenderOptionType = "all",
        render_duration: bool = False,
        colorize: bool = True,
        calendar_colors: CalendarColoringType = None,
        tree: Tree = None,
    ):
        super().__init__(calendar, num_months_in_table, icon_render, render_duration, calendar_colors)
        self._calendar_index: CalendarIndex = CalendarIndex(year=self._year, index_type=IndexType.INDEX_MONTH_DAY)
        self._monthweek_map = self._calendar_index.monthweek_map()
        # colorize lines
        self._colorize = colorize
        self._tree = None
        # TODO PRIO4 in future versions: Add Elements for a year to a multiyear tree
        if tree is not None:
            self._tree = tree
        self._month_nodes = {}
        self._week_nodes = {}
        self._day_nodes = {}

    def _render_tree_root(self):
        """renders the tree root"""
        _m_style = self._calendar_colors.MONTH_LINE_STYLE
        _title = f":books:  [bold {_m_style}]CALENDAR {self._year}[/]"
        self._tree = Tree(label=_title, guide_style=_m_style)

    def _render_month_nodes(self):
        """renders the month node in the tree"""
        _m_style = self._calendar_colors.MONTH_LINE_STYLE
        _w_style = self._calendar_colors.WEEK_LINE_STYLE
        # add months to root node
        _months = self.months_to_display

        for _m in _months:
            _icon_num_months = EmojiUtil.int2emoji(_m, 2)
            _icon_month = Emoji.replace(MONTH_EMOJIS[_m])
            _node_month_txt = f"{_icon_num_months}  [bold {_m_style}]{MONTHS[_m]} {self._year}[/] {_icon_month}"
            _month_node = self._tree.add(_node_month_txt, guide_style=_w_style)
            self._month_nodes[_m] = _month_node

    def _render_week_nodes(self):
        """renders the calendar week nodes"""
        _w_style = self._calendar_colors.WEEK_LINE_STYLE
        _d_style = self._calendar_colors.DAY_LINE_STYLE
        _months = self.months_to_display
        _weeks = self.weeks_to_display
        for _m in _months:
            self._week_nodes[_m] = {}
            _week_info = self._monthweek_map[_m]
            _month = MONTHS_SHORT[_m]
            _month_node = self._month_nodes[_m]
            for _cw, _cw_info in _week_info.items():
                if _cw not in _weeks:
                    continue
                _days = list(_cw_info.keys())
                _d_min, _d_max = [str(min(_days)).zfill(2), str(max(_days)).zfill(2)]
                _week_node_txt = f"[{_w_style}]KW{str(_cw).zfill(2)}/{self._year} {_d_min}-{_d_max}.{_month}[/]"
                _week_node = _month_node.add(_week_node_txt, guide_style=_d_style, highlight=False)
                self._week_nodes[_m][_cw] = _week_node

    def _render_day_info_nodes(self, day_info: CalendarDayType, day_node: Tree) -> None:
        """renders daily information list and attaches it to the day node"""
        # TODO PRIO2 add filter to only add node info according to certain add criteria TBD

        _infos = day_info.info
        if _infos is None or not isinstance(_infos, list):
            return
        _color = self._calendar_colors.INFO
        for _info in _infos:
            _info_s = f"[{_color}]{_info}[/]"
            day_node.add(_info_s)

    def _get_line_style(self, day_info: CalendarDayType) -> str:
        """returns the line style for any notes below day info"""
        # self._calendar_colors
        _day_type = day_info.day_type.name
        _color = getattr(self._calendar_colors, _day_type)
        return _color

    def _render_day_nodes(self):
        """renders the single day nodes"""
        _month_day_index = [tuple(_l) for _l in list(self._calendar_index.index_map().values())]
        _weeknum_map = self._calendar_index.weeknum_map(IndexType.INDEX_MONTH_DAY)
        # initialize the weekday node map
        _months = self.months_to_display
        _weeks = self.weeks_to_display
        for _m in _months:
            self._day_nodes[_m] = {}
        for _monthweek, _weeknum in _weeknum_map.items():
            _m = _monthweek[0]
            if not _m in _months:
                continue
            if not _weeknum in _weeks:
                continue
            self._day_nodes[_m][_weeknum] = []

        # 🗿 2024-01-28 So KW04/028 WOCHENENDE
        # _title = f":books:  [bold {_m_style}]CALENDAR {self._year}[/]"
        # get all information and render it
        for _md in _month_day_index:
            _month = _md[0]
            if not _month in _months:
                continue
            _week_num = _weeknum_map[_md]
            if not _week_num in _weeks:
                continue
            _day = _md[1]
            _date = DateTime(year=self._year, month=_month, day=_day)
            if _date not in self.dates_to_display:
                continue
            # TODO PRIO2 allow rules to filter out single dates
            _day_info = self._calendar.year_info[_month][_day]
            _line_style = self._get_line_style(_day_info)
            _day_info_s = self._render_day_info(_day_info, self._colorize)
            _week_node = self._week_nodes[_month][_week_num]
            _day_node = _week_node.add(_day_info_s, guide_style=_line_style, highlight=False)
            self._day_nodes[_month][_week_num].append(_day_node)
            self._render_day_info_nodes(_day_info, _day_node)
        pass

    def render_calendar(self):
        """renders the calendar as tree"""
        self._render_tree_root()
        self._render_month_nodes()
        self._render_week_nodes()
        self._render_day_nodes()
        # _w_style = self._tree_render.week_line_style

        self._console.print(self._tree)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=CLI_LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    # console python -m rich.markdown test.md

    # sample creation of items. For real usage this would be a plain txt file
    # allowing easy and quick entry of items
    _daytype_list = [
        # "@HOME Mo Di Mi Fr 0800-1200 1300-1700",
        # "@WORK Do 1000-1200 1300-1600",
        "@VACA 20240902-20240910",
        "@PART 20240919-20240923",
        "@VACA 20240927",
        "@WORK 20241216 1000-1600 :notebook: 6H Test Info ",
        "@WORK 20241217 1000-1700 :notebook: 7H Test Info ",
        "@HOME 20241218 1000-1800 :notebook: 8H Test Info ",
        "@WORK 20241219 1000-1900 :notebook: 9H Test Info ",
        "@WORK 20241220 1000-2000 :notebook: 10H Test Info ",
        "@WORK 20241201 1000-1800 :notebook: Test Change of Daily Work Regular Time Info @REGULARWORKTIME7.5",
        "@WORK 20240929-20241004 :notebook: Test Info ",
        "@WORK 20240901 :red_circle: :green_square: MORE INFO 1230-1450 1615-1645",
        "@FLEX 20241010 JUST INFO 0934-1134",
    ]
    _calendar = Calendar(2024, 8, _daytype_list)
    if True:
        # rendering the calendar and markdown list
        # icon_render is "all","first","info","no_info"
        _table_renderer = CalendarTableRenderer(calendar=_calendar, num_months_in_table=12, icon_render="all")
        # set date filter for rendering last 3 months
        _table_renderer.set_calendar_filter("20241015-20241231")
        # render the calendar as table
        if False:
            _table_renderer.render_calendar()

        # render the calendar as markdown list (only_info=only items with INFO will be printed)
        _markdown_list = _table_renderer.get_markdown(only_info=False)
        console = _table_renderer.console
        console.print(Markdown("\n".join(_markdown_list)))
    # overtime indicator
    if False:
        CalendarRenderer.show_overtime_indicator()
    # stats
    if False:
        _stats = _table_renderer.calendar.stats
        console.print(_stats)
        _stats_sum = _table_renderer.calendar.stats_sum
        console.print(_stats_sum)

    if False:
        _tree_renderer = CalendarTreeRenderer(
            calendar=_calendar, num_months_in_table=12, icon_render="all", render_duration=True
        )
        _tree_renderer.set_calendar_filter("MoDiMiDoFr20241016:20241220")
        # _tree_renderer.set_calendar_filter("20241016:20241220")
        _tree_renderer.render_calendar()
