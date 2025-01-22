"""models for datetime_util methods"""

from datetime import datetime as DateTime
from datetime import timedelta
from typing import Optional, Dict, Annotated, List, Literal, Tuple
from enum import StrEnum
from pydantic import BaseModel, TypeAdapter, Field, RootModel


class DayTypeEnumEN(StrEnum):
    """Type of Day"""

    WEEKEND = "weekend"
    WORKDAY = "workday"
    WORKDAY_HOME = "workday_home"
    VACATION = "vacation"
    HOLIDAY = "holiday"
    FLEXTIME = "flextime"  # Gleitzeit
    PARTTIME = "parttime"
    ONDUTY = "onduty"  # Schicht
    INFO = "info"  # information attribute


class DayTypeEnum(StrEnum):
    """Type of Day"""

    WEEKEND = "WOCHENENDE"
    WORKDAY = "ARBEITSTAG"
    WORKDAY_HOME = "HOMEOFFICE"
    VACATION = "URLAUB"
    HOLIDAY = "FEIERTAG"
    FLEXTIME = "GLEITZEIT"  # Gleitzeit
    PARTTIME = "TEILZEIT"
    ONDUTY = "BEREITSCHAFT"
    INFO = "INFO"  # information attribute


class CalendarDayType(BaseModel):
    """Calendar Day Model"""

    datetime_s: Optional[str] = None  # string representation YYYYMMDD
    datetime: Optional[DateTime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    day_in_year: Optional[int] = None
    weekday_num: Optional[int] = None
    weekday_s: Optional[str] = None
    isoweeknum: Optional[int] = None
    holiday: Optional[str] = None
    workday: Optional[bool] = None
    day_type: Optional[DayTypeEnum] = None
    duration: Optional[float] = None  # durations derived from info
    work_hours: Optional[float] = None
    overtime: Optional[float] = None  # Overtime Calculation
    total_work: Optional[float] = None  # Cumulated overtime
    info: Optional[List] = None  # Additional Info
    info_raw: Optional[List] = None  # Original Info
    tags: Optional[List] = None  # all tags that were extracted from info
    todos_raw: Optional[List] = None  # all todo_txt strings from info


class IndexType(StrEnum):
    """CalendarIndex  Type"""

    INDEX_NUM = "num"
    INDEX_DAY_IN_YEAR = "day_in_year"
    INDEX_DATETIME = "datetime"
    INDEX_MONTH_DAY = "month_day"
    INDEX_ALL = "all"


class CalendarIndexType(BaseModel):
    """Summary Calendar Index"""

    datetime: Optional[DateTime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    day_in_year: Optional[int] = None
    calendar_week: Optional[int] = None
    month_day: Optional[List | Tuple] = None
    weekday: Optional[int] = None
    holiday: Optional[str] = None
    is_leap_year: Optional[bool] = None
    is_holiday: Optional[bool] = None
    is_weekend: Optional[bool] = None
    is_workday: Optional[bool] = None


class CalendarBuffer(BaseModel):
    """Calendar Buffer"""

    days_in_month: Optional[dict] = {}
    holidays: Optional[dict] = {}
    year: Optional[int] = None
    dt_dec31: Optional[DateTime] = None
    work_hours: Optional[float] = None


# derived models
MonthModel = Dict[str, CalendarDayType]
MonthAdapter = TypeAdapter(MonthModel)
MonthModelType = Annotated[MonthModel, MonthAdapter]
YearModel = Dict[int, Dict[int, CalendarDayType]]
YearAdapter = TypeAdapter(YearModel)
YearModelType = Annotated[YearModel, YearAdapter]

# lists of dayinfo
CalendarDayDictModel = Dict[str, CalendarDayType]
CalendarDayDictAdapter = TypeAdapter(CalendarDayDictModel)
CalendarDayDictType = Annotated[CalendarDayDictModel, CalendarDayDictAdapter]

DayTypeDictModel = Dict[DayTypeEnum, List[str]]
DayTypeDictAdapter = TypeAdapter(DayTypeDictModel)
DayTypeDictType = Annotated[DayTypeDictModel, DayTypeDictAdapter]

# Custom type for rendering an additional icon in the calendar
# no_info = do not show an icon
# all = show all icons
# first = only first icon
# info = show default icon that info is there
CellRenderOptionField = Annotated[
    Literal["all", "first", "info", "no_info"], Field(description="Calendar Rendering Option")
]


class CellRenderOptionType(RootModel):
    """Rendering Option for the calendar"""

    root: CellRenderOptionField = "all"


class CalendarColoringType(BaseModel):
    """Model containing params to render the Output Tree (allowing to alter it)
    also provides default values if used with defaults
    """

    # line styles are being used for lines in calendar trees
    # Note that the line styles will only show up for lines of child elements
    MONTH_LINE_STYLE: Optional[str] = "bold bright_green"
    WEEK_LINE_STYLE: Optional[str] = "blue"
    DAY_LINE_STYLE: Optional[str] = "magenta"
    # COLORS FOR THE DAYTYPES, KEYS CORRESPOND TO DAYTYPES
    WEEKEND: Optional[str] = "bright_black"
    WORKDAY: Optional[str] = "bright_green"
    WORKDAY_HOME: Optional[str] = "light_sky_blue1"
    VACATION: Optional[str] = "gold1"
    HOLIDAY: Optional[str] = "deep_pink3"
    FLEXTIME: Optional[str] = "bright_red"  # Gleitzeit
    PARTTIME: Optional[str] = "bright_black"
    ONDUTY: Optional[str] = "cyan1"  # Bereitschaft
    # INFO ITEM COLOR
    INFO: Optional[str] = "white"


class CalendarRegex(StrEnum):
    """class to parse date related strings as used by calendar filter"""

    # note that the definition of order here is important
    # as the regex parsing requires a certain order

    # capture characters before and after separator (-)
    REGEX_FROM_TO: Optional[str] = r"(.+)?-(.+)"

    # #1 NOW or now as marker for today so you can construct things like now-1d
    REGEX_NOW: Optional[str] = r"(now|NOW)"

    # #2 YYYYMMDD with some date validations
    # REGEX_YYYYMMDD: Optional[str] = r"[12]\d{3}[01][0-9][0-3]\d"
    REGEX_YYYYMMDD: Optional[str] = r"([^ouehira]|^)([12]\d{3}[01][0-9][0-3]\d)"

    # #3 MMDD, short form, year will be appended
    # REGEX_MMDD: Optional[str] = r"([^ouehira]|^)([01]\d{3})"

    # #4 regex to capture DATE with week days
    REGEX_YYYYMMDD_DAY: Optional[str] = r"((?:[MDFSTW][ouehira])+)([12]\d{3}[01][0-9][0-3]\d)"

    # #5 Parsing weeks, months, days,years offset +/-(NUMBER)(OFFSET UNIT)
    # But excluding second letters from week days so as to allow excusion
    # for week day Prefixes Mo Di Mi ... Mo Tu We ...
    # Lower case: relative to from date 1w = -7days
    # Upper Case: relative calendar 1W = Date of monday of this week
    REGEX_DWMY_OFFSET: Optional[str] = r"([^ouehira]|^)([+-]\d+)([dwmyDWMY])"

    # #6 One Capital Case and one lower capital case for week days
    # this allows to cpature regexes like MoMi-1d

    REGEX_DWMY_DAY_OFFSET: Optional[str] = r"((?:[MDFSTW][ouehira])+)([+-]\d+)([dwmyDWMY])"


class CalendarParseInfo(BaseModel):
    """Model to allow for processing of parsing strings to dates"""

    # original string
    filter_s: Optional[str] = None
    filter_matches: Optional[dict] = {}
    regex_result: Optional[dict] = {}
    date: Optional[DateTime] = None
    # for info: record all rules and their results
    dates: Optional[Dict[str, DateTime]] = {}
    timedeltas: Optional[Dict[str, timedelta]] = {}
    weekdays: Optional[List[int]] = None
    date_calculated: Optional[DateTime] = None
