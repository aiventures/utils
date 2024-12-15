""" models for datetime_util methods """

from datetime import datetime as DateTime
from typing import Optional,Dict,Annotated,List,Literal
from enum import StrEnum
from pydantic import BaseModel,TypeAdapter,Field,RootModel


class DayTypeEnumEN(StrEnum):
    """ Type of Day """
    WEEKEND = "weekend"
    WORKDAY = "workday"
    WORKDAY_HOME = "workday_home"
    VACATION = "vacation"
    HOLIDAY  = "holiday"
    FLEXTIME = "flextime" # Gleitzeit
    PARTTIME = "parttime"
    INFO     = "info"  # information attribute

class DayTypeEnum(StrEnum):
    """ Type of Day """
    WEEKEND = "WOCHENENDE"
    WORKDAY = "ARBEITSTAG"
    WORKDAY_HOME = "HOMEOFFICE"
    VACATION = "URLAUB"
    HOLIDAY  = "FEIERTAG"
    FLEXTIME = "GLEITZEIT" # Gleitzeit
    PARTTIME = "TEILZEIT"
    INFO     = "INFO"  # information attribute

class CalendarDayType(BaseModel):
    """ Calendar Day Model """
    datetime_s    : str      # string representation YYYYMMDD
    datetime      : DateTime
    year          : int
    month         : int
    day           : int
    day_in_year   : int
    weekday_num   : int
    weekday_s     : str
    isoweeknum    : int
    holiday       : Optional[str]=None
    day_type      : DayTypeEnum
    duration      : Optional[float]=None # durations derived from info
    overtime      : Optional[float]=None # Overtime Calculation
    info          : Optional[str]=None # Additional Info

# derived models
MonthModel = Dict[str,CalendarDayType]
MonthAdapter = TypeAdapter(MonthModel)
MonthModelType = Annotated[MonthModel,MonthAdapter]
YearModel = Dict[int,Dict[int,CalendarDayType]]
YearAdapter = TypeAdapter(YearModel)
YearModelType = Annotated[YearModel,YearAdapter]

DayTypeListModel = Dict[DayTypeEnum,List[str]]
DayTypeListAdapter = TypeAdapter(DayTypeListModel)
DayTypeListType = Annotated[DayTypeListModel,DayTypeListAdapter]

# Custom type for rendering an additional icon in the calendar
# no_info = do not show an icon
# all = show all icons
# first = only first icon
# info = show default icon that info is there
CellRenderOptionField = Annotated[Literal["all","first","info","no_info"], Field(description="Calendar Rendering Option")]

class CellRenderOptionType(RootModel):
    """ Rendering OPtion for the calendar """
    root: CellRenderOptionField = "all"
