"""Filtering Date Strings and Getting Time Intervals"""

import logging
import os
import re
from datetime import datetime as DateTime
from datetime import timedelta
from typing import List

from model.model_calendar import (
    CalendarRegex,
    CalendarParseInfo,
    #     CalendarIndexType,
    #     IndexType,
)

# regex to extract todo_txt string matching signature @(...)
from util import constants as C
from util.datetime_util import WEEKDAY_NUM, WEEKDAY, DateTimeUtil

# from util.datetime_util import DAYS_IN_MONTH, DateTimeUtil
# from util.utils import Utils
# from util.calendar_constants import (REGEX_YYYYMMDD)


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# list separator for a filter string
LIST_SEP = ";"


class CalendarFilter:
    """creating a calendar index"""

    def __init__(self, filter_s: str = None, date_list: List[List[DateTime] | DateTime] = None):
        """Constructor"""
        self._filter_s_raw = filter_s
        self._filter_list_raw = date_list
        self._d_now = DateTime.now()
        self._d_now = self._d_now.replace(hour=0, minute=0, second=0, microsecond=0)
        self._parse_func = {
            CalendarRegex.REGEX_NOW: self._parse_now,
            CalendarRegex.REGEX_YYYYMMDD: self._parse_yyyymmdd,
            CalendarRegex.REGEX_DWMY_OFFSET: self._parse_dwmy_offset,
            CalendarRegex.REGEX_DWMY_DAY_OFFSET: self._parse_dwmy_day_offset,
            CalendarRegex.REGEX_YYYYMMDD_DAY: self._parse_yyyymmdd_day,
        }
        # track the origin of found dateranges
        self._daterange_origin = {}
        self._daterange_list = []
        # parse raw date strings into date ranges
        self._parse_filter_str_list()
        # adding the datetime filter lists
        self._add_filter_list(date_list)

    @property
    def datelist(self) -> List[DateTime]:
        """returns the date list"""
        date_list = []
        for _date_from_to in self._daterange_list:
            _date = _date_from_to[0]
            _date_to = _date_from_to[1]
            while _date <= _date_to:
                date_list.append(_date)
                _date += timedelta(days=1)
        return sorted(list(set(date_list)))

    def _add_filter_list(self, date_list=List[List[DateTime] | DateTime]) -> None:
        """adding datefrom dateto lists to attribute"""
        if date_list is None:
            return
        if not isinstance(date_list, list):
            return

        for _date in date_list:
            _date_from_to = _date
            if isinstance(_date_from_to, DateTime):
                _date_from_to = [_date, _date]
            if len(_date_from_to) == 2:
                self._daterange_list.append(_date_from_to)
            else:
                logger.warning(
                    f"[CalendarFilter] FromTo DateList is expected as DateTime or 2 element list, got {_date_from_to} "
                )

    @staticmethod
    def calc_day_start(date: DateTime, unit: str) -> DateTime:
        """calculate the date start depending on Unit"""

        # lower case: is equal to current date
        if unit in ["d", "D", "m", "w", "y"]:
            return date

        date_out = None
        if unit == "W":  # Week, return the monday of that week
            _offset = 1 - date.isoweekday()
            date_out = date + timedelta(days=_offset)
        elif unit == "M":  # Month return the 1st Day of this month
            date_out = DateTime(date.year, date.month, 1)
        elif unit == "Y":  # Year return the 1st January of the year
            date_out = DateTime(date.year, 1, 1)
        return date_out

    @staticmethod
    def calc_day_offset(date: DateTime, offset: int, unit: str = None) -> DateTime:
        """calculates Date Offset with default of days"""
        date_out = date
        if unit is None:
            unit = "d"
        _unit = unit.lower()
        if _unit not in "dwmy":
            logger.warning(f"[CalendarFilter] wrong unit [{unit}], allowed [dwmy]")
            return
        if _unit == "d":
            date_out += timedelta(days=offset)
        elif _unit == "w":
            date_out += timedelta(days=7 * offset)
        elif _unit == "y":
            _y = date.year + offset
            date_out = DateTime(year=_y, month=date.month, day=date.day)
        elif _unit == "m":
            _year, _month = DateTimeUtil.months_offset(date, offset)
            _day = date.day
            # adjust month date
            if _month == 2 and _day >= 28:
                # get last day of february including leap year
                _day = (DateTime(_year, 3, 1) + timedelta(days=-1)).day
                logger.info(f"[CalendarFilter] Month offset day [{date}] adjusted to Feb {_day} {_year} ")
            elif _day == 31 and _month in [4, 6, 9, 11]:
                _day = 30
                logger.info(f"[CalendarFilter] Month offset day [{date}] adjusted to 30th of Month")
            date_out = DateTime(_year, _month, _day)
        return date_out

    def _get_regex_result(self, parse_info: CalendarParseInfo, rule: CalendarRegex, num_items: int = 1) -> list | None:
        """validates rule"""
        _regex_result = parse_info.filter_matches.get(rule.name)
        if _regex_result is None:
            logger.warning(f"[CalendarFilter] Parsed Result matches [{rule.name}], but no parsing result found")
            return None
        if isinstance(_regex_result, list) and len(_regex_result) != num_items:
            logger.warning(
                f"[CalendarFilter] Parsed [{len(_regex_result)}] Result matches [{rule.name}], but there should be [{num_items}] matches"
            )
            return None
        return _regex_result

    def _parse_weekdays(self, weekday_s: str) -> list:
        """Parsing the Weekdays in the string"""
        return [_wd_num for _wd_s, _wd_num in WEEKDAY_NUM.items() if _wd_s in weekday_s]

    def _parse_filter_str(self, parse_info: CalendarParseInfo) -> dict:
        """parse a single filter string"""
        _filter_matches = {}
        for _regex in CalendarRegex:
            _matches = re.findall(_regex.value, parse_info.filter_s)
            if len(_matches) == 0:
                continue
            _filter_matches[_regex.name] = _matches
        parse_info.filter_matches = _filter_matches
        return _filter_matches

    def _parse_dwmy_day_offset(self, parse_info: CalendarParseInfo) -> list:
        """calculate time delta for given regex signature"""
        _regex_result = parse_info.filter_matches.get(CalendarRegex.REGEX_DWMY_DAY_OFFSET.name)
        if _regex_result is None:
            return

        _date = parse_info.date
        _weekday_s = _regex_result[0][0]
        _weekdays_num = self._parse_weekdays(_weekday_s)
        _quantity = int(_regex_result[0][1])
        _unit = _regex_result[0][2]
        _weekdays = parse_info.weekdays
        if isinstance(_weekdays, list):
            _weekdays.extend(_weekdays_num)
            _weekdays = list(set(_weekdays))
        else:
            _weekdays = _weekdays_num
        parse_info.weekdays = _weekdays

        # get the start date of this calculation
        _date_start = CalendarFilter.calc_day_start(_date, _unit)
        # # calculate offset
        _date_end = CalendarFilter.calc_day_offset(_date_start, _quantity, _unit)
        _timedelta = _date_end - _date
        parse_info.timedeltas[CalendarRegex.REGEX_DWMY_DAY_OFFSET.name] = _timedelta
        return _timedelta

    def _parse_dwmy_offset(self, parse_info: CalendarParseInfo) -> timedelta:
        """calculate time delta for given regex signature"""

        _regex_result = self._get_regex_result(parse_info, CalendarRegex.REGEX_DWMY_OFFSET)
        if _regex_result is None:
            return
        _date = parse_info.date
        _quantity = int(_regex_result[0][1])
        _unit = _regex_result[0][2]
        # get the start date of this calculation
        _date_start = CalendarFilter.calc_day_start(_date, _unit)
        # calculate offset
        _date_end = CalendarFilter.calc_day_offset(_date_start, _quantity, _unit)
        _timedelta = _date_end - _date
        parse_info.timedeltas[CalendarRegex.REGEX_DWMY_OFFSET.name] = _timedelta
        return _timedelta

    def _parse_yyyymmdd_day(self, parse_info: CalendarParseInfo) -> DateTime:
        """parse date for given regex hit"""
        _regex_result = self._get_regex_result(parse_info, CalendarRegex.REGEX_YYYYMMDD_DAY)
        if _regex_result is None:
            return
        _weekday_s = _regex_result[0][0]
        _weekdays_num = self._parse_weekdays(_weekday_s)
        _date_s = _regex_result[0][1]
        _date = DateTime.strptime(_date_s, C.DATEFORMAT_JJJJMMDD)
        parse_info.dates[CalendarRegex.REGEX_YYYYMMDD_DAY.name] = _date
        parse_info.date = _date
        parse_info.weekdays = _weekdays_num
        return _date

    def _parse_yyyymmdd(self, parse_info: CalendarParseInfo) -> DateTime:
        """parse date for given regex hit"""
        _regex_result = self._get_regex_result(parse_info, CalendarRegex.REGEX_YYYYMMDD)
        if _regex_result is None:
            return
        _date_s = _regex_result[0][1]
        _date = DateTime.strptime(_date_s, C.DATEFORMAT_JJJJMMDD)
        parse_info.dates[CalendarRegex.REGEX_YYYYMMDD.name] = _date
        parse_info.date = _date
        return _date

    def _parse_now(self, parse_info: CalendarParseInfo) -> DateTime:
        """parsing the regex now rule, return the current date"""
        parse_info.dates[CalendarRegex.REGEX_NOW.name] = parse_info.date
        return parse_info.date

    def _parse_regex_rules(self, parse_info: CalendarParseInfo) -> CalendarParseInfo:
        """parsing found rules and try to convert them into a datetime"""

        # default
        _timedeltas = []
        # if no date is submitted use current date as default
        _date = self._d_now
        # process rules in given order. in the end there should be a date and
        # optionally an offset rule that needs to be applied to the date
        # if no date is found today's date will be used as default
        _regex_rule_dict = parse_info.filter_matches
        _regex_rules = list(_regex_rule_dict.keys())

        for _calendar_regex in CalendarRegex:
            if _calendar_regex.name not in _regex_rules:
                continue
            _out = self._parse_func[_calendar_regex](parse_info)
            parse_info.regex_result[_calendar_regex.name] = _out

        # do some sanity checks
        if len(parse_info.dates) != 1:
            logger.info(f"[CalendarFilter] other than 1 dates found for [{parse_info.filter_s}]: [parse_info.dates]")

        date_out = parse_info.date
        _timedeltas = list(parse_info.timedeltas.values())
        for _timedelta in _timedeltas:
            date_out += _timedelta
        parse_info.date_calculated = date_out

        return parse_info

    @staticmethod
    def get_weekday_dates(day_s: str, date_interval: List[List[DateTime]]) -> List[DateTime]:
        """gets weekday dates for given day_str"""
        _date_list = []
        _date = date_interval[0]
        _date_to = date_interval[1]
        _weekdays = [k for k, v in WEEKDAY.items() if v in day_s]
        while _date <= _date_to:
            if _date.isoweekday() in _weekdays:
                _date_list.append(_date)
            _date += timedelta(days=1)
        return _date_list

    def _add_date_ranges(self, parse_infos: List[CalendarParseInfo], origin: str) -> None:
        """adding the date ranges and its origins"""
        _info_from, _info_to = parse_infos
        _date = _info_from.date_calculated
        _date_to = _info_to.date_calculated
        _weekdays = None
        if isinstance(_info_from.weekdays, list):
            _weekdays = _info_from.weekdays
        if isinstance(_info_to.weekdays, list):
            if _weekdays is None:
                _weekdays = _info_to.weekdays
            else:
                _weekdays.extend(_info_to.weekdays)
        if isinstance(_weekdays, list):
            _weekdays = list(set(_weekdays))
        _date_list = None
        if _weekdays is None:
            _date_list = [_date, _date_to]
        else:
            _date_list = []
            while _date <= _date_to:
                _weekday = _date.isoweekday()
                if _weekday in _weekdays:
                    _date_list.append([_date, _date])
                _date += timedelta(days=1)
        if isinstance(_date_list, list):
            if len(_date_list) == 2 and isinstance(_date_list[0], DateTime):
                self._daterange_list.append(_date_list)
            else:
                self._daterange_list.extend(_date_list)
            self._daterange_origin[origin] = _date_list

    def _parse_filter_str_list(self) -> None:
        """parse the filter string"""
        _filter_list_s = [_s.strip() for _s in self._filter_s_raw.split(LIST_SEP)]
        _regex_from_to = re.compile(CalendarRegex.REGEX_FROM_TO.value)
        for _filter in _filter_list_s:
            # get the from and to fields if there is no separator
            _from_to = _regex_from_to.findall(_filter)
            if len(_from_to) == 0:
                _from_to = ["now", _filter]
            elif len(_from_to) == 1:
                _from_to = [_from_to[0][0], _from_to[0][1]]
            else:
                logger.warning(f"[CalendarFilter] More than 1 '-' separator found in filter [{_filter}]")
                continue

            _parse_infos = [CalendarParseInfo(filter_s=_f, date=self._d_now) for _f in _from_to]
            # get rule matches
            _ = [self._parse_filter_str(_pi) for _pi in _parse_infos]
            # get dates
            _parse_infos = [self._parse_regex_rules(_r) for _r in _parse_infos]
            # change order
            if _parse_infos[0].date_calculated > _parse_infos[1].date_calculated:
                _parse_infos = [_parse_infos[1], _parse_infos[0]]
            self._add_date_ranges(_parse_infos, _filter)
