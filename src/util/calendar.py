"""Calendar and Time Utils"""

import logging
import os
import re
from copy import deepcopy
from datetime import datetime as DateTime
from datetime import timedelta
from enum import EnumMeta
from typing import Any, Dict, List

from model.model_calendar import (
    CalendarBuffer,
    CalendarDayDictType,
    CalendarDayType,
    CalendarIndexType,
    DayTypeDictType,
    DayTypeEnum,
    IndexType,
    MonthModelType,
    YearModelType,
)
from model.model_worklog import ShortCodes

# regex to extract todo_txt string matching signature @(...)
from util import constants as C
from util.datetime_util import DAYS_IN_MONTH, REGEX_TIME_RANGE, WEEKDAY, DateTimeUtil
from util.utils import Utils
from util.calendar_constants import (REGEX_DATE_RANGE,REGEX_YYYYMMDD,REGEX_WEEKDAY,REGEX_TOTAL_WORK,
                                     REGEX_TODO_TXT,REGEX_TODO_TXT_REPLACE,
                                     REGEX_TOTAL_WORK_REPLACE,REGEX_TAGS,WORKDAYS)

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

class Calendar:
    """Calendar Object"""

    # buffering calendar
    _cls_calendar_buffer: Dict[int, CalendarBuffer] = {}

    def __init__(
        self, year: int = None, work_hours: float = 8.0, dayinfo_list: List[str] = None,
        short_codes: EnumMeta = None
    ):
        """Constructor"""
        if year is None:
            year = DateTime.now().year
        self._year: int = year
        # regular working time, used for calculating overtime
        self._work_hours: float = work_hours
        # get first monday of isoweek
        self._isoweek_info: dict = DateTimeUtil.get_isoweekyear(year)
        self._year_info: YearModelType = None
        self._create_year_info()
        self._dayinfo_list: List[str] = []
        if isinstance(dayinfo_list, list):
            self._dayinfo_list = dayinfo_list
        self._daytype_dict: DayTypeDictType = {}
        self._short_codes: EnumMeta = ShortCodes
        if short_codes is not None:
            self._short_codes = short_codes
        self._short_code_list = [f"{_short_code.name}" for _short_code in self._short_codes]
        self._parse_shortcodes()
        # TODO REFACTOR THIS PART
        self._set_daytypes()
        # adds information from info file
        self._add_info()


    @classmethod
    def _set_calendar_buffer(cls, year: int, work_hours: float = None) -> None:
        """add year info to calendar buffer"""
        if year is None:
            cls._cls_calendar_buffer = {}
            return
        _holidays = DateTimeUtil.get_holiday_dates(year)
        _days_in_month = deepcopy(DAYS_IN_MONTH)
        _dt_dec31 = DateTime(year, 1, 1) - timedelta(days=1)
        if DateTimeUtil.is_leap_year(year):
            _days_in_month[2] = 29
        cls._cls_calendar_buffer[year] = CalendarBuffer(
            days_in_month=_days_in_month, holidays=_holidays, year=year, dt_dec31=_dt_dec31, work_hours=work_hours
        )

    @classmethod
    def set_work_hours(cls, work_hours: float = 8.0) -> None:
        """setting the work hours in all calendars of the calendar buffer"""
        for _, _calendar_buffer in cls._cls_calendar_buffer.items():
            _calendar_buffer.work_hours = work_hours

    @classmethod
    def _get_calendar_buffer(cls, year: int) -> CalendarBuffer:
        """gets calendar meta data from calendar buffer and sets working hours"""
        _calendar_buffer = cls._cls_calendar_buffer.get(year)
        if _calendar_buffer is None:
            cls._set_calendar_buffer(year)
            _calendar_buffer = cls._cls_calendar_buffer.get(year)
        return _calendar_buffer

    @property
    def year(self) -> int:
        """return year"""
        return self._year

    @property
    def year_info(self) -> YearModelType:
        """return year info"""
        return self._year_info

    @staticmethod
    def create_day_info(year: int, month: int, day: int, work_hours: float = None) -> CalendarDayType:
        """returning a dayinfo object from date information"""
        _calendar_buffer = Calendar._get_calendar_buffer(year)
        if _calendar_buffer.work_hours is None and work_hours is not None:
            Calendar.set_work_hours(work_hours)
            _calendar_buffer = Calendar._get_calendar_buffer(year)
        _holidays = _calendar_buffer.holidays
        _work_hours = _calendar_buffer.work_hours
        _dt_dec31 = _calendar_buffer.dt_dec31
        _dt = DateTime(year, month, day)
        _dt_s = _dt.strftime("%Y%m%d")
        _y = _dt.year
        _m = _dt.month
        _d = _dt.day
        _weekinfo = DateTimeUtil.isoweek(_dt)
        _day_in_year = (_dt - _dt_dec31).days
        _week_day_num = _weekinfo.get("weekday")
        _week_day_s = WEEKDAY[_week_day_num]
        _calendar_week = _weekinfo.get("calendar_week")
        _holiday = _holidays.get(_dt)
        if _holiday:
            _holiday = _holiday.get("name")
        # get default day type
        _day_type = DayTypeEnum.WORKDAY_HOME
        if _week_day_num > 5:
            _day_type = DayTypeEnum.WEEKEND
        elif _holiday is not None:
            _day_type = DayTypeEnum.HOLIDAY

        _day_info = {
            "datetime_s": _dt_s,
            "datetime": _dt,
            "year": _y,
            "month": _m,
            "day": _d,
            "day_in_year": _day_in_year,
            "weekday_num": _week_day_num,
            "weekday_s": _week_day_s,
            "isoweeknum": _calendar_week,
            "holiday": _holiday,
            "day_type": _day_type,
            "work_hours": _work_hours,
        }

        return CalendarDayType(**_day_info)

    @staticmethod
    def get_month_info(year: int, month: int, work_hours: float = None) -> MonthModelType:
        """gets date information as Pydantic Model"""
        # get this date for calculation of number of days
        out = {}
        _calendar_buffer = Calendar._get_calendar_buffer(year)
        if _calendar_buffer.work_hours is None and work_hours is not None:
            Calendar.set_work_hours(work_hours)
        # get holidays
        _days_in_month = _calendar_buffer.days_in_month
        # get days in month
        _days_in_month = _days_in_month.get(month)

        for _d in range(1, _days_in_month + 1):
            _dt = DateTime(year, month, _d)
            _dt_s = _dt.strftime("%Y%m%d")
            _ymdh = (_dt.year, _dt.month, _dt.day, work_hours)
            out[_dt_s] = Calendar.create_day_info(*_ymdh)
        return out

    @staticmethod
    def get_year_info(year: int, work_hours: float = None) -> YearModelType:
        """returns a year as matrix [month][day]
        also adds vacation list (either as date YYYYMMDD or as range
                                 YYYYMMDD-yyyymmdd)
        """
        out = {}
        for _month in range(1, 13):
            _month_info = Calendar.get_month_info(year, _month, work_hours)
            # transform it into a dict using day ints
            _month_info = dict([(_info.day, _info) for _info in _month_info.values()])
            out[_month] = _month_info
        return out

    def _create_year_info(self) -> None:
        """create a year calendar"""
        self._year_info = Calendar.get_year_info(year=self._year, work_hours=self._work_hours)

    def get_weekdays(self, weekdays: list = None) -> list:
        """get all weekdays ["Mo",...]from list"""
        out = []
        if isinstance(weekdays, str):
            weekdays = weekdays.split(" ")
        for _month in range(1, 13):
            _days_info = list(self._year_info[_month].values())
            for day_info in _days_info:
                if day_info.weekday_s in weekdays:
                    out.append(day_info.datetime)
        return out

    def _get_daytype_dates(self, daytype: DayTypeEnum = None, date_s: str = None) -> List[DateTime]:
        """get datetype_dates"""
        # get all dates in one string and apply regexes from there
        if date_s:
            _date_s = date_s
        else:
            _date_s = " ".join(self._daytype_dict.get(daytype, []))
        _date_ranges = REGEX_DATE_RANGE.findall(_date_s)
        dates = [DateTimeUtil.get_dates_from_range(_dr) for _dr in _date_ranges]
        dates = [_d for _daterange_list in dates for _d in _daterange_list]
        _dates_single = [DateTime.strptime(_d[1], "%Y%m%d") for _d in REGEX_YYYYMMDD.findall(_date_s)]
        dates.extend(_dates_single)
        _weekdays_s = REGEX_WEEKDAY.findall(_date_s)
        _week_dates = self.get_weekdays(_weekdays_s)
        dates.extend(_week_dates)
        dates = list(tuple(sorted(dates)))
        # remove all dates not in current calendar year 
        dates = [_d for _d in dates if _d.year == self._year]
        return dates

    def _parse_shortcodes(self) -> None:
        """parse shortcodes and set infodict"""
        self._daytype_dict = {}
        _regex_short_codes = [re.compile(f"@{_code}", re.IGNORECASE) for _code in self._short_code_list]

        for _dayinfo in self._dayinfo_list:
            _found = False
            for _regex in _regex_short_codes:
                # only use the first occurence
                _result = _regex.findall(_dayinfo)
                if len(_result) > 0:
                    _found = True
                    _shortcode = _regex.pattern.upper()[1:]
                    _daytype_name = ShortCodes[_shortcode].value
                    _daytype = DayTypeEnum[_daytype_name]
                    _info = self._daytype_dict.get(_daytype, [])
                    _info.append(_dayinfo)
                    self._daytype_dict[_daytype] = _info
                    break
            if _found is False:
                logger.warning(f"[Calendar] Found [{_dayinfo}] where no daytype could be found")

        return

    @staticmethod
    def parse_totalwork(total_workstring) -> float:
        """parses a totalwork string"""
        totalwork = None
        _totalwork_list = re.findall(REGEX_TOTAL_WORK, total_workstring, re.IGNORECASE)
        if len(_totalwork_list) > 0:
            totalwork = 0.0
            totalwork_list = [_tw.replace(",", ".") for _tw in _totalwork_list]
            for _tw in totalwork_list:
                try:
                    _twf = float(_tw)
                    totalwork += _twf
                except ValueError:
                    pass
        return totalwork

    def parse_dayinfo(self, dayinfo: str) -> CalendarDayDictType:
        """parses a dayinfo line"""
        out = {}
        # adapted string
        _s_adapted = dayinfo
        # get todo_txt part and drop it (since it might contain @tags)
        _todo_txts = []
        _todo_txts_replace = re.findall(REGEX_TODO_TXT_REPLACE, dayinfo)
        if len(_todo_txts_replace) > 0:
            for _todo_txt in _todo_txts_replace:
                _s_adapted = _s_adapted.replace(_todo_txt, "")
            # get the extracted todo
            _todo_txts = [re.findall(REGEX_TODO_TXT, _s)[0] for _s in _todo_txts_replace]

        # string parts that need to be dropped
        _string_matches = ["@"]

        _total_work = None

        # get total overtime
        _total_work_replace = re.findall(REGEX_TOTAL_WORK_REPLACE, dayinfo)
        if len(_total_work_replace) > 0:
            _total_work = 0.0
            for _total_work_s in _total_work_replace:
                _s_adapted = _s_adapted.replace(_total_work_s, "").strip()
                _total_work_single = Calendar.parse_totalwork(_total_work_s)
                if _total_work_single is not None:
                    _total_work += _total_work_single

        # get all dates
        _dates = self._get_daytype_dates(date_s=dayinfo)
        # get date parts
        _date_ranges_s = re.findall(REGEX_DATE_RANGE, dayinfo)
        _string_matches.extend(_date_ranges_s)
        # get single dates
        _dates_s = re.findall(REGEX_YYYYMMDD, dayinfo)
        _dates_s = [_d[1] for _d in _dates_s]
        _string_matches.extend(_dates_s)
        # get week parts
        _weekdays = re.findall(REGEX_WEEKDAY, dayinfo)
        _string_matches.extend(_weekdays)
        # get duration parts / calculate duration
        _durations = re.findall(REGEX_TIME_RANGE, dayinfo)
        _total_duration = DateTimeUtil.duration_from_str(_s_adapted)

        _string_matches.extend(_durations)
        # get all tags
        _tags = re.findall(REGEX_TAGS, dayinfo)
        # get DayTypeInfo / use only the first occurence
        _daytype_short = None
        _daytypes = [_tag for _tag in _tags if _tag.upper() in self._short_code_list]
        if len(_daytypes) > 1:
            logger.warning(f"[Calendar] found more than one daytypes in [{dayinfo}], using the 1st")
            _daytype_short = _daytypes[0]
        elif len(_daytypes) == 0:
            logger.warning(f"[Calendar] found no daytypes in [{dayinfo}], using HOME")
            _daytype_short = ShortCodes.HOME.name
        else:
            _daytype_short = _daytypes[0]
        _day_type = DayTypeEnum[ShortCodes[_daytype_short.upper()].value]

        # self._short_code_list
        _string_matches.extend(_tags)

        # info string
        for _s in _string_matches:
            _s_adapted = _s_adapted.replace(_s, "")

        _info = _s_adapted.strip()
        if len(_info) == 0:
            _info = None
        else:
            _info = [_info]
        _s_adapted = _s_adapted.strip()

        for _date in _dates:
            _ymdh = (_date.year, _date.month, _date.day, self._work_hours)
            # create_day_info type
            _day_info = Calendar.create_day_info(*_ymdh)
            # add parts from the string parsing above
            Calendar._merge_daytype(_day_info, [_day_type])
            _day_info.duration = _total_duration
            _day_info.work_hours = self._work_hours
            if isinstance(_total_duration, (float, int)) and isinstance(self._work_hours, (float, int)):
                _day_info.overtime = _total_duration - self._work_hours
            _day_info.total_work = _total_work
            # @TODO _day_info.overtime
            if len(_s_adapted) > 0:
                _day_info.info = [_s_adapted]
            _day_info.info_raw = [dayinfo]
            _day_info.tags = _tags
            _day_info.todos_raw = _todo_txts
            out[_day_info.datetime_s] = _day_info

        return out

    @staticmethod
    def _is_workday(daytype: DayTypeEnum) -> bool:
        """returns if an enum is of workday type"""
        if daytype.name.lower() in WORKDAYS:
            return True
        else:
            return False

    @staticmethod
    def _merge_daytype(dayinfo: CalendarDayType, daytypes: List[DayTypeEnum]):
        """prioritizes daytype from incoming list"""
        if dayinfo.holiday is not None:
            dayinfo.day_type = DayTypeEnum.HOLIDAY
        elif dayinfo.weekday_num > 5:
            dayinfo.day_type = DayTypeEnum.WEEKEND
        elif DayTypeEnum.VACATION in daytypes:
            dayinfo.day_type = DayTypeEnum.VACATION
        elif DayTypeEnum.FLEXTIME in daytypes:
            dayinfo.day_type = DayTypeEnum.FLEXTIME
        elif DayTypeEnum.PARTTIME in daytypes:
            dayinfo.day_type = DayTypeEnum.PARTTIME
        elif DayTypeEnum.WORKDAY in daytypes:
            dayinfo.day_type = DayTypeEnum.WORKDAY
        else:
            dayinfo.day_type = DayTypeEnum.WORKDAY_HOME

    @staticmethod
    def _merge_dayinfo(dayinfos: List[CalendarDayType]) -> CalendarDayType:
        """merge a list of day infos into one entry"""

        # info / info_raw / tags /  / duration / holiday / overtime / day_type / todo_raw
        _merged = {
            "holiday": [],
            "day_type": [],
            "duration": [],
            "work_hours": [],
            "info": [],
            "info_raw": [],
            "tags": [],
            "todos_raw": [],
            "total_overtime": [],
        }
        for _dayinfo in dayinfos:
            for _name, _value in _dayinfo:
                if _value is None:
                    continue
                _value_list = _merged.get(_name)
                if _value_list is None:
                    continue
                if isinstance(_value, list) and len(_value) == 0:
                    continue
                if isinstance(_value, list):
                    _value_list.extend(_value)
                else:
                    _value_list.append(_value)

        _day_info = deepcopy(dayinfos[0])
        Calendar._merge_daytype(_day_info, _merged["day_type"])
        _ = _merged.pop("day_type")

        for _merge_field, _values in _merged.items():
            if len(_values) == 0:
                continue
            # merge to unique values / sum for some others
            _values = list(set(_values))
            if _merge_field in ["work_hours", "total_overtime"]:
                _day_info.work_hours = max([float(_v) for _v in _values if isinstance(_v, (float, int))])
            elif _merge_field == "duration":
                _sum = sum([float(_v) for _v in _values if isinstance(_v, (float, int))])
                setattr(_day_info, _merge_field, _sum)
            elif _merge_field == "holiday":
                _day_info.holiday = _values[0]
            else:
                setattr(_day_info, _merge_field, _values)

        # calculate overrtime
        if isinstance(_day_info.duration, (int, float)) and isinstance(_day_info.work_hours, (int, float)):
            _day_info.overtime = _day_info.duration - _day_info.work_hours
        else:
            _day_info.overtime = None

        return _day_info

    def _add_info(self) -> None:
        """adds information to calendar and merges multiple information lines"""
        _out = {}
        _dayinfo_dicts = {}

        # get dayinfos for each additional info line, blend them together
        for _day_info_s in self._dayinfo_list:
            _dayinfo_dict = self.parse_dayinfo(_day_info_s)
            for _date, _dayinfo in _dayinfo_dict.items():
                _day_infos = _dayinfo_dicts.get(_date, [])
                _day_infos.append(_dayinfo)
                _dayinfo_dicts[_date] = _day_infos

        for _date, _day_info in _dayinfo_dicts.items():
            if len(_day_info) == 1:
                _out[_date] = _day_info[0]
            elif len(_day_info) > 1:
                _out[_date] = _day_info

        for _date, _dayinfos in _out.items():
            if isinstance(_dayinfos, list):
                _merged = Calendar._merge_dayinfo(_dayinfos)
                _out[_date] = _merged

            _dayinfo = _out[_date]
            _dt = _dayinfo.datetime
            _year, _month, _day = (_dt.year, _dt.month, _dt.day)
            if _year != self.year:
                logger.warning("[Calendar] Additional Information: Year not matching")
                continue

            # adjust working times
            if _dayinfo.holiday is not None:
                _dayinfo.duration = None
                _dayinfo.overtime = None
            elif _dayinfo.day_type == DayTypeEnum.FLEXTIME:
                _dayinfo.duration = 0.0
                _dayinfo.overtime = -1 * self._work_hours
            elif _dayinfo.day_type in [
                DayTypeEnum.VACATION,
                DayTypeEnum.HOLIDAY,
                DayTypeEnum.WEEKEND,
                DayTypeEnum.PARTTIME,
            ]:
                _dayinfo.duration = None
                _dayinfo.overtime = None

            self.year_info[_month][_day] = _dayinfo

    def _set_daytype(self, daytype: DayTypeEnum) -> None:
        """setting a specific daytype"""
        _days_list = self._get_daytype_dates(daytype)
        for _day in _days_list:
            _y = _day.year
            if self._year != _y:
                continue
            _d = _day.day
            _m = _day.month
            _day_info = self._year_info[_m][_d]
            # only change info if working day
            if _day_info.day_type in [DayTypeEnum.WORKDAY, DayTypeEnum.WORKDAY_HOME]:
                _day_info.day_type = daytype

    def _set_daytypes(self) -> None:
        """setting the daytypes in a specific order"""
        # some order needs to be maintained
        _all_daytypes = [
            DayTypeEnum.WORKDAY_HOME,
            DayTypeEnum.WORKDAY,
            DayTypeEnum.PARTTIME,
            DayTypeEnum.FLEXTIME,
            DayTypeEnum.VACATION,
        ]
        _daytypes = list(self._daytype_dict.keys())
        for _daytype in _all_daytypes:
            if _daytype not in _daytypes:
                continue
            self._set_daytype(_daytype)

    def _get_calendar365(self) -> Dict[int, CalendarDayType]:
        """gets the calendar as dict"""
        out = {}
        for _m in range(1, 13):
            _day_infos = list(self._year_info[_m].values())
            for _day_info in _day_infos:
                out[_day_info.day_in_year] = _day_info
        return out

    @property
    def stats(self) -> dict:
        """get number of days in stats"""
        out = {}
        _num_total = 0
        for _month, _month_info in self._year_info.items():
            _month_out = {"weekday_s": {}, "day_type": {}, "holiday": [], "days_with_info": [], "duration": {}}
            for _day, _day_info in _month_info.items():
                _day_type = _day_info.day_type.value
                _num_days = _month_out["day_type"].get(_day_type, 0) + 1
                _month_out["day_type"][_day_type] = _num_days
                _weekday_s = _day_info.weekday_s
                _num_days = _month_out["weekday_s"].get(_weekday_s, 0) + 1
                _month_out["weekday_s"][_weekday_s] = _num_days
                _holiday = _day_info.holiday
                if _holiday:
                    _d = f" ({_weekday_s}, {_day_info.datetime.strftime('%d.%m')})"
                    _month_out["holiday"].append(_holiday + _d)
                if isinstance(_day_info.info, list):
                    _month_out["days_with_info"].append(_day)
                _duration = _day_info.duration
                if isinstance(_duration, float) and _duration > 0:
                    _month_out["duration"][_day] = _duration
            out[_month] = _month_out
        return out

    @property
    def stats_sum(self) -> dict:
        """Cumulated stats per year"""
        out = {"weekday_s": {}, "day_type": {}, "holiday": [], "duration": 0, "year": self.year}
        _stats_month = self.stats
        _duration = 0
        for _, _month_info in _stats_month.items():
            _weekday_info = _month_info["weekday_s"]
            for _day, _num in _weekday_info.items():
                _num_total = out["weekday_s"].get(_day, 0)
                out["weekday_s"][_day] = _num_total + _num
            _day_type_info = _month_info["day_type"]

            for _daytype, _num in _day_type_info.items():
                _num_total = out["day_type"].get(_daytype, 0)
                out["day_type"][_daytype] = _num_total + _num

            out["holiday"].extend(_month_info["holiday"])
            _duration += sum(list(_month_info["duration"].values()))
        out["duration"] = _duration
        return out

    def get_day_info(self, month: int, day: int) -> CalendarDayType:
        """returns the calendar info"""
        return self._year_info[month][day]

    def get_calendar_table(self, num_months: int = 6) -> list:
        """creates tabular format"""
        num_tables = 12 // num_months
        out = []
        for _num_table in range(num_tables):
            _first_month = _num_table * num_months + 1
            _last_month = _first_month + num_months
            _table = []
            for _day in range(1, 32):
                _row = [str(_day).zfill(2)]
                for _month in range(_first_month, _last_month):
                    _info = self._year_info[_month].get(_day)
                    _value = None
                    if _info is not None:
                        _value = (_month, _day)
                    _row.append(_value)
                _table.append(_row)
            out.append(_table)

        return out

class CalendarIndex():
    """ creating a calendar index """
    def __init__(self,year:int=None,index_type:IndexType=IndexType.INDEX_NUM):

        if year is None:
            year = DateTime.now().year
        self._year: int = year
        self._index_type: IndexType = index_type
        self._year_index: Dict[int,CalendarIndexType] = DateTimeUtil.year_index(year)
        self._indices: dict = {IndexType.INDEX_DATETIME:[],
                         IndexType.INDEX_NUM:[],
                         IndexType.INDEX_MONTH_DAY:[]}
        self._create_indices()
        _isoweek_year: dict = DateTimeUtil.get_isoweekyear(year)
        self._first_monday:DateTime = _isoweek_year["first_monday"]
        self._last_monday:DateTime = _isoweek_year["last_monday"]
        self._last_sunday:DateTime = _isoweek_year["last_day"]
        self._num_weeks:int = _isoweek_year["weeks"]
        self._is_leap_year:bool = self._year_index[1].is_leap_year
        self._days_in_year = 365
        if self._is_leap_year:
            self._days_in_year += 1
        self._idx_first_monday:int= None
        self._week_indices:list = None
        self._month_indices:list = None
        self._calc_indices()

    @property
    def index_type(self):
        """ index type getter """
        return self._index_type

    @index_type.setter
    def index_type(self, index_type:IndexType):
        """ setting the index type """
        self._index_type = index_type

    def _calc_indices(self):
        """ calculates some indices """

        # calculate weekly indices
        if self._first_monday.year == self._year:
            self._idx_first_monday = self._first_monday.day
        else:
            self._idx_first_monday = self._first_monday.day - 31

        _min_idx = self._idx_first_monday
        _max_idx = _min_idx + 7 * self._num_weeks
        _week_indices = list(range(_min_idx,_max_idx+1,7))
        self._week_indices = _week_indices

        # calculate annual indices
        _offset = 1
        _month_indices = [1]
        for _m in range(1,13):
            _offset += DAYS_IN_MONTH[_m]
            if self._is_leap_year and _m == 2:
                _offset += 1
            _month_indices.append(_offset)
        self._month_indices = _month_indices

    def _create_indices(self):
        """ create the indices """
        for _idx,_idx_info in self._year_index.items():
            self._indices[IndexType.INDEX_DATETIME].append(_idx_info.datetime)
            self._indices[IndexType.INDEX_NUM].append(_idx)
            self._indices[IndexType.INDEX_MONTH_DAY].append([_idx_info.month,_idx_info.day])

    @property
    def index(self):
        """ returns the generated index """
        return self._year_index

    def index_map(self,key_index:IndexType=None,value_index:IndexType=None)->dict:
        """ returns date index map  """
        if key_index is None:
            key_index = IndexType.INDEX_NUM
        if value_index is None:
            value_index = self._index_type

        return dict(zip(self._indices[key_index],self._indices[value_index]))

    def info(self,key:Any,index_type:IndexType=None)->CalendarIndexType:
        """ retrieves calendar info using key  """
        _info = None
        _index = None

        # convert string to date
        if isinstance(key,str):
            _date_str = re.findall(REGEX_YYYYMMDD,key)
            if len(_date_str) > 0:
                key = DateTime.strptime(_date_str[0][1],"%Y%m%d")

        try:
            if isinstance(key,int):
                _index = key - 1
            elif Utils.is_list_or_tuple(key):
                _index = self._indices[IndexType.INDEX_MONTH_DAY].index(list(key))
            elif isinstance(key,DateTime):
                _index = self._indices[IndexType.INDEX_DATETIME].index(key)

            _info = self._year_index[_index+1]

        except (ValueError,KeyError):
            _index = None
            logger.warning(f"[CalendarIndex] Couldn't find Calendar index for [{key}]")

        # transform output to a given index type
        if index_type is not None:
            _attribute = index_type.value
            try:
                _info = getattr(_info,_attribute)
            except AttributeError:
                logger.warning(f"[CalendarIndex] There is not attribute [{_attribute}] in CalendarIndexType")

        return _info

    def month_map(self,index_type:IndexType=None)->Dict[int,List[Any]]:
        """ returns index keys by month   """
        if index_type is None:
            index_type = self._index_type
        _map = self.index_map(value_index=index_type)
        _values = list(_map.values())
        _month_indices = self._month_indices
        out = {_m: [] for _m in range(1,13)}
        for _m in range(12):
            # adjust indices
            try:
                _idx_from = max(_month_indices[_m]-1,0)
                _idx_to = min(_month_indices[_m+1]-1,self._days_in_year)
                out[_m+1]=_values[_idx_from:_idx_to]
            except IndexError:
                pass

        return out

    def week_map(self,index_type:IndexType=None)->Dict[int,List[Any]]:
        """ returns index keys by week  """
        if index_type is None:
            index_type = self._index_type
        _map = self.index_map(value_index=index_type)
        _values = list(_map.values())
        _week_indices = self._week_indices
        _num_weeks = self._num_weeks
        # 0 and 99 are items reserved for previous year and follow up year
        out = {_w: [] for _w in range(0,_num_weeks+1)}
        out[99] = []
        for _w in range(_num_weeks):
            # adjust indices
            try:
                _idx_from = max(_week_indices[_w]-1,0)
                _idx_to = min(_week_indices[_w+1]-1,self._days_in_year)
                out[_w+1]=_values[_idx_from:_idx_to]
            except IndexError:
                pass
        # add edge case for lower end (=last week of previous calender year)
        if _week_indices[0] > 1:
            out[00] = _values[:_week_indices[0]-1]
        # add items to the last bucket, if the new calendar week 1 already begins in the old year
        if self._last_sunday.year == self._year:
            _num_remaining_days = -1 *( DateTime(self._year,12,31) - self._last_sunday ).days
            if _num_remaining_days < 0:
                out[99] = _values[_num_remaining_days:]

        return out

    def monthweek_map(self,index_type:IndexType=None)->Dict[int,Dict[int,Dict[int,Any]]]:
        """Returns a Month Week Map (Month,Calendar,Week,Day)
        """
        if index_type is None:
            index_type = self._index_type
        out = {_m: {} for _m in range(1,13)}
        # brute force assignment loop over all items
        _weekmap = self.week_map(IndexType.INDEX_MONTH_DAY)
        for _w,_md_list in _weekmap.items():
            for _md in _md_list:
                _m = _md[0]
                _d = _md[1]
                _m_dict = out[_m]
                _w_dict = _m_dict.get(_w)
                if _w_dict is None:
                    _w_dict = {}
                    _m_dict[_w] = _w_dict
                _value = self.info(_md,index_type)
                _w_dict[_d] = _value
        return out
