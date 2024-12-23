""" Model Representation for worklog_txt """

from datetime import datetime as DateTime
from pydantic import BaseModel
from typing import List, Optional, Union, Dict
from enum import Enum, StrEnum
from model.model_datetime import (CalendarDayType,DayTypeEnum)

class ShortCodes(StrEnum):
    """shortcodes that can be used in worklog if prepended with @ """
    WEND = DayTypeEnum.WEEKEND.name
    WORK = DayTypeEnum.WORKDAY.name
    HOME = DayTypeEnum.WORKDAY_HOME.name
    VACA = DayTypeEnum.VACATION.name
    HOLI = DayTypeEnum.HOLIDAY.name
    FLEX = DayTypeEnum.FLEXTIME.name
    PART = DayTypeEnum.PARTTIME.name
    INFO = DayTypeEnum.INFO.name

class WorkLogModel(BaseModel):
    """ Model Representation for Text Based Work Log """
    line: Optional[int] = None
    original: Optional[str] = None
    tags: Optional[List] = []
    date: Optional[DateTime] = None
    daytype: Optional[str] = None
    duration: Optional[float] = 0.0
    todo_str: Optional[str] = None
    calendar_day: Optional[CalendarDayType] = None

