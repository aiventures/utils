""" models for datetime_util methods """

from datetime import datetime as DateTime
from typing import Optional,Dict,Annotated,List
from enum import StrEnum
from pydantic import BaseModel,TypeAdapter


class DayTypeEnum(StrEnum):
    """ Type of Day """
    WEEKEND = "weekend"
    WORKDAY = "workday"
    WORKDAY_HOME = "workday_home"
    VACATION = "vacation"
    HOLIDAY = "holiday"
    FLEXTIME = "flextime" # Gleitzeit
    PARTTIME = "parttime"

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
