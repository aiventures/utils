"""Generic Filter"""

from typing import Any
from abc import ABC, abstractmethod


from model.model_filter import (
    FilterModel,
    RegexFilterModel,
    FilterResultModel,
    DateTimeFilterModel,
    StringFilterModel,
    NumericalFilterModel,
)


class AbstractAtomicFilter(ABC):
    """generic definition of an atomic filter"""

    @abstractmethod
    def filter(self, obj: Any) -> bool:
        """abstract filter method"""


class NumericalFilter(AbstractAtomicFilter):
    """Numerical Filter"""

    def __init__(self, obj_filter: NumericalFilterModel):
        self._filter: NumericalFilterModel = obj_filter

    def filter(self, obj) -> bool:
        """filter passed object"""
        if not isinstance(obj, (int, float)):
            raise ValueError(f"[NumericalFilter] Passed {obj} of type [{type(obj)}], expected number")
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

        return passed
