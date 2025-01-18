"""Generic Filter"""

import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime as DateTime
from re import Pattern
from typing import Any, List, Optional

from pydantic import ConfigDict

from model.model_filter import FilterModel, NumericalFilterModel, RegexFilterModel, StringFilterModel
from util import constants as C
from util.calendar_filter import CalendarFilter as CalendarFilterObject

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class AbstractAtomicFilter(ABC):
    """generic definition of an atomic filter"""

    def __init__(self, obj_filter: FilterModel | None = None):
        """constructor"""
        self._filter = obj_filter

    @property
    def key(self) -> Any:
        """return filter key"""
        return self._filter.key

    @key.setter
    def key(self, key: object) -> Any:
        """return filter key"""
        self._filter.key = key

    @property
    def groups(self) -> List[Any]:
        """return filter groups"""
        return self._filter.groups

    @property
    def description(self) -> str | None:
        """return filter key"""
        return self._filter.groups

    @property
    def operator(self) -> str | None:
        """return all or any operator"""
        return self._filter.operator

    @property
    def obj_filter(self) -> FilterModel:
        """return the filter"""
        return self._filter

    @abstractmethod
    def filter(self, obj: Any) -> bool:
        """abstract filter method"""


class NumericalFilter(AbstractAtomicFilter):
    """Numerical Filter"""

    def __init__(self, obj_filter: NumericalFilterModel):
        """constructor"""
        super().__init__()
        self._filter: NumericalFilterModel = obj_filter
        self._filter_type = None
        if obj_filter.value_max is not None:
            self._filter_type = type(obj_filter.value_max)
        if self._filter_type is None:
            self._filter_type = type(obj_filter.value_min)

    def filter(self, obj) -> bool:
        """filter passed object"""
        if not isinstance(obj, (int, float, DateTime)):
            raise ValueError(
                f"[NumericalFilter] Passed {obj} of type [{type(obj).__name__}], expected [{self._filter_type.__name__}]"
            )

        # type checking
        if self._filter_type is not type(obj):
            raise ValueError(
                f"[NumericalFilter] Passed {obj} of type [{type(obj).__name__}], expected [{self._filter_type.__name__}]"
            )

        passed = True
        # if filter is not set then the result will be undefined
        if self._filter.value_max is None and self._filter.value_min is None:
            return None

        if self._filter.value_max is not None:
            _op = "le"
            if self._filter.operator_max is not None:
                _op = self._filter.operator_max
            if _op == "lt" and obj >= self._filter.value_max:
                passed = False
            elif _op == "le" and obj > self._filter.value_max:
                passed = False
            elif _op == "eq" and obj != self._filter.value_max:
                passed = False

        if self._filter.value_min is not None:
            _op = "ge"
            if self._filter.operator_min is not None:
                _op = self._filter.operator_min
            if _op == "gt" and obj <= self._filter.value_min:
                passed = False
            elif _op == "ge" and obj < self._filter.value_min:
                passed = False
            elif _op == "eq" and obj != self._filter.value_min:
                passed = False

        # revert result
        if self._filter.include == "exclude":
            passed = not passed

        return passed


class RegexFilter(AbstractAtomicFilter):
    """Parsing Regex"""

    def __init__(self, obj_filter: RegexFilterModel):
        """constructor"""
        super().__init__()
        self._filter: RegexFilterModel = obj_filter
        self._regex_s: str = obj_filter.regex
        self._regex: Pattern = re.compile(self._regex_s)
        self._last_match: list = None
        self._last_str: str = None

    def filter(self, obj) -> bool:
        """filter passed object"""
        if not isinstance(obj, str):
            raise ValueError(f"[RegexFilter] Passed {obj} of type [{type(obj).__name__}], expected str")
        passed = True
        self._last_str = obj

        self._last_match = self._regex.findall(obj)
        if len(self._last_match) == 0:
            self._last_match = None
            passed = False

        if self._filter.include == "exclude":
            passed = not passed

        return passed

    def find_all(self, obj):
        """returning the matches"""
        _ = self.filter(obj)
        return self._last_match


class StringFilter(AbstractAtomicFilter):
    """Parsing Regex"""

    def __init__(self, obj_filter: StringFilterModel):
        """constructor"""
        super().__init__()
        self._filter: StringFilterModel = obj_filter

    def filter(self, obj) -> bool:
        """filter passed object"""

        if not isinstance(obj, str):
            raise ValueError(f"[StringFilter] Passed {obj} of type [{type(obj).__name__}], expected str")
        passed = False

        _filter_strings = self._filter.filter_strings
        if _filter_strings is None:
            raise ValueError(
                f"[StringFilter] String Filter [{self._filter.key}] ({self._filter.description}) has no value"
            )

        if isinstance(_filter_strings, str):
            _filter_strings = [_filter_strings]
        _match = self._filter.match  # contains/exact

        _passed_list = []
        # check each item
        for _filter_s in _filter_strings:
            _passed = False
            if _match == "contains":
                if _filter_s in obj:
                    _passed = True
            else:
                if _filter_s == obj:
                    _passed = True
            _passed_list.append(_passed)
        if self._filter.string_operator == "all":
            passed = all(_passed_list)
        else:
            passed = any(_passed_list)

        if self._filter.include == "exclude":
            passed = not passed

        return passed


class CalendarFilterModel(FilterModel):
    """Filtering DateTime in a Calenfdar Object"""

    # allow to use non pydantic model and skip any validation
    model_config = ConfigDict(arbitrary_types_allowed=True)
    filter_str: Optional[str] = None  # Filter String to be used for Calendar
    date_list: Optional[List[List[DateTime] | DateTime]] = None
    calendar_filter: Optional[CalendarFilterObject] = None


class CalendarFilterWrapper(AbstractAtomicFilter):
    """Calendar Filter (basically a wrapper around the calendar filter object)"""

    def __init__(self, obj_filter: CalendarFilterModel):
        """constructor"""
        super().__init__()
        self._filter: CalendarFilterModel = obj_filter
        self._filter_str: str = obj_filter.filter_str
        self._date_list_in = obj_filter.date_list
        self._calendar_filter_obj: CalendarFilterObject = obj_filter.calendar_filter
        # invalidate the calendar filter
        if self._calendar_filter_obj and self._filter_str != self._calendar_filter_obj._filter_s_raw:
            self._calendar_filter_obj = None
        # init the calendar filter
        if self._calendar_filter_obj is None:
            self._calendar_filter_obj = CalendarFilterObject(self._filter_str, self._date_list_in)
        self._datelist = self._calendar_filter_obj.datelist

    def filter(self, obj: DateTime) -> bool:
        """filtering the calendar object"""
        if not isinstance(obj, DateTime):
            raise ValueError(
                f"[CalendarFilter] Passed {obj} of type [{type(obj).__name__}], expected datetime.datetime"
            )

        passed = True if obj in self._datelist else False

        if self._filter.include == "exclude":
            passed = not passed

        return passed

    @property
    def datelist(self) -> List[DateTime]:
        """returns the date list"""
        return self._datelist
