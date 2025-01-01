"""Filtering Date Strings and Getting Time Intervals"""

import itertools
import logging
import os
import re
from datetime import datetime as DateTime
from datetime import timedelta
from typing import List

from model.model_calendar import (
    CalendarRegex,
    #     CalendarIndexType,
    #     IndexType,
)

# regex to extract todo_txt string matching signature @(...)
from util import constants as C
from util.datetime_util import WEEKDAY, DateTimeUtil

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
            CalendarRegex.REGEX_YYYYMMDD: self.parse_yyyymmdd,
            CalendarRegex.REGEX_MMDD: self.parse_mmdd,
            CalendarRegex.REGEX_DWMY_OFFSET: self._parse_dwmy_offset,
            CalendarRegex.REGEX_DWMY_DAY_OFFSET: self._parse_dwmy_day_offset,
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
            self._daterange_list.append(_date_from_to)

    def _parse_filter_str(self, filter_s: str) -> None:
        """parse a single filter string"""
        _filter_matches = {}
        for _regex in CalendarRegex:
            _matches = re.findall(_regex.value, filter_s)
            if len(_matches) == 0:
                continue
            _filter_matches[_regex.name] = _matches
        return _filter_matches

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

    def _parse_dwmy_day_offset(self, *args) -> list:
        """calculate time delta for given regex signature"""
        if not isinstance(args, tuple):
            logger.warning(f"[CalendarFilter] [{args}] is not a list (REGEX_DWMY_DAY_OFFSET)")
            return None
        if len(args) != 2:
            logger.warning(f"[CalendarFilter] [{args}] should be a two element list (REGEX_DWMY_DAY_OFFSET)")
            return None
        _date = args[1]
        _quantity = int(args[0][0][1])
        _unit = args[0][0][2]

        return self._parse_dwmy_offset([("", _quantity, _unit)], _date)

    def _parse_dwmy_offset(self, *args) -> timedelta:
        """calculate time delta for given regex signature"""
        if not isinstance(args, tuple):
            logger.warning(f"[CalendarFilter] [{args}] is not a list (REGEX_DWMY_OFFSET)")
            return None
        if len(args) != 2:
            logger.warning(f"[CalendarFilter] [{args}] should be a two element list (REGEX_DWMY_OFFSET)")
            return None
        _regex, _date = args
        quantity = int(_regex[0][1])
        unit = _regex[0][2]
        # get the start date of this calculation
        _date_start = CalendarFilter.calc_day_start(_date, unit)
        # calculate offset
        _date_end = CalendarFilter.calc_day_offset(_date_start, quantity, unit)

        return _date_end - _date

    def parse_yyyymmdd(self, *args) -> DateTime:
        """parse date for given regex hit"""
        date_out = None
        if not isinstance(args, tuple):
            logger.warning(f"[CalendarFilter] [{args}] is not a list (REGEX_YYYYMMDD)")
            return None
        if len(args) != 2:
            logger.warning(f"[CalendarFilter] [{args}] should be a two element list (REGEX_YYYYMMDD)")
            return None
        _dates, _date = args
        if len(_dates) != 1:
            logger.warning(
                f"[CalendarFilter] [{args}] Regex Hit {_dates} should only contain one date (REGEX_YYYYMMDD)"
            )
            return None
        try:
            date_out = DateTime.strptime(_dates[0], C.DATEFORMAT_JJJJMMDD)
        except ValueError as e:
            logger.warning(f"[CalendarFilter] Couldn't parse date {_dates}, check format (REGEX_YYYYMMDD), {e}")

        return date_out

    def parse_mmdd(self, *args) -> DateTime:
        """parse date for given regex hit"""
        return None

    def _parse_now(self, *args) -> DateTime:
        """parsing the regex now rule, return the current date"""
        return self._d_now

    def _parse_regex_rules(self, regex_rule: dict) -> DateTime | timedelta:
        """parsing found rules and try to convert them into a datetime"""
        # default
        date_out = None
        _dates = []
        _timedeltas = []
        # if no date is submitted use current date as default
        _date = self._d_now
        # process rules in given order. in the end there should be a date and
        # optionally an offset rule that needs to be applied to the date
        # if no date is found today's date will be used as default
        _regex_rules = list(regex_rule.keys())
        for _calendar_regex in CalendarRegex:
            if _calendar_regex.name not in _regex_rules:
                continue
            _regex_result = regex_rule[_calendar_regex.name]
            _out = self._parse_func[_calendar_regex](_regex_result, _date)

            if isinstance(_out, DateTime):
                _date = _out
                _dates.append(_out)
            elif isinstance(_out, timedelta):
                _timedeltas.append(_out)
        # now calculate the date based on timedeltas
        if len(_dates) == 0:
            _dates.append(self._d_now)
        if len(_dates) != 1:
            logger.warning(f"[CalendarFilter] Regex [{regex_rule}] has more than one date")
            return None

        date_out = _dates[0]
        for _timedelta in _timedeltas:
            date_out += _timedelta

        return date_out

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

    def _parse_filter_str_list(self) -> None:
        """parse the filter string"""
        _filter_list_s = [_s.strip() for _s in self._filter_s_raw.split(LIST_SEP)]
        _regex_from_to = re.compile(CalendarRegex.REGEX_FROM_TO.value)
        for _filter in _filter_list_s:
            # get the from and to fields if there is no dash,
            # from will be now as as default
            _from_to = _regex_from_to.findall(_filter)
            if len(_from_to) == 0:
                _from_to = ["now", _filter]
            elif len(_from_to) == 1:
                _from_to = [_from_to[0][0], _from_to[0][1]]
            else:
                logger.warning(f"[CalendarFilter] More than 1 '-' separator found in filter [{_filter}]")
                continue
            # get rule matches
            _from_to_regex = [self._parse_filter_str(_f) for _f in _from_to]
            # get all rules rules
            _regex_rules = [list(_r.keys()) for _r in _from_to_regex]
            _regex_rules = list(set(itertools.chain(*_regex_rules)))
            # get dates
            _date_from_to = [self._parse_regex_rules(_r) for _r in _from_to_regex]
            # check the dates
            _invalid = [1 for _d in _date_from_to if not isinstance(_d, DateTime)]
            if len(_invalid) > 0:
                logger.warning(f"[CalendarFilter] Invalid Date Range for filter [{_filter}]")
                continue
            # change order
            if _date_from_to[0] > _date_from_to[1]:
                _date_from_to = [_date_from_to[1], _date_from_to[0]]
            # special case: REGEX with Day Specific Offsets
            _regex_day_offset_name = CalendarRegex.REGEX_DWMY_DAY_OFFSET.name
            if _regex_day_offset_name in _regex_rules:
                _days = []
                for _regexes in _from_to_regex:
                    _days.extend(_regexes.get(_regex_day_offset_name, []))
                _days = "".join([_d[0] for _d in _days])
                _date_list = CalendarFilter.get_weekday_dates(_days, _date_from_to)
                _date_list = [[_d, _d] for _d in _date_list]
                self._daterange_list.extend(_date_list)
                self._daterange_origin[_filter] = _date_list
            else:
                self._daterange_list.append(_date_from_to)
                self._daterange_origin[_filter] = _date_from_to
