"""Calendar and Time Utils"""

import logging
import os
import re
from datetime import datetime as DateTime
from typing import Any, Dict, List

from model.model_calendar import (
    CalendarIndexType,
    IndexType,
)

# regex to extract todo_txt string matching signature @(...)
from util import constants as C
from util.datetime_util import DAYS_IN_MONTH, DateTimeUtil
from util.utils import Utils
from util.calendar_constants import (REGEX_YYYYMMDD)

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

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
