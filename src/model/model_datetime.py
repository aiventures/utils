"""models for datetime_util methods"""

from datetime import datetime as DateTime
from typing import Optional, Dict, Annotated, List, Literal
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
    day_type: Optional[DayTypeEnum] = None
    duration: Optional[float] = None  # durations derived from info
    overtime: Optional[float] = None  # Overtime Calculation
    info: Optional[List] = None  # Additional Info

# derived models
MonthModel = Dict[str, CalendarDayType]
MonthAdapter = TypeAdapter(MonthModel)
MonthModelType = Annotated[MonthModel, MonthAdapter]
YearModel = Dict[int, Dict[int, CalendarDayType]]
YearAdapter = TypeAdapter(YearModel)
YearModelType = Annotated[YearModel, YearAdapter]

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
