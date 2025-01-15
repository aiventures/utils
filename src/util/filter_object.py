"""Filter for filtering structured objects like dicts or objects"""

import logging
import os
from model.model_filter import ObjectFilterModel

from util import constants as C
from util.filter import AbstractAtomicFilter
from util.filter_set import FilterSet

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

NOT_FOUND = "xyz_not_found"


class ObjectFilter(AbstractAtomicFilter):
    """generic superclass for objet type filters"""

    def __init__(self, obj_filter: ObjectFilterModel = None):
        """use object filter moel to filter objects"""
        super().__init__(obj_filter)
        self._filter: ObjectFilterModel = obj_filter

    def _get_dict_attribute(self, obj: dict, attribute: str) -> object:
        """get the attribute of a dict"""
        out = obj.get(attribute, NOT_FOUND)
        if out == NOT_FOUND:
            logger.info(f"[ObjectFilter] Attribute [{attribute}] not found in dict [{obj}]")
        return out

    def _get_obj_attribute(self, obj: object, attribute: str) -> object:
        """get the attribute of a dict"""
        if not hasattr(obj, attribute):
            logger.info(f"[ObjectFilter] Object has no attribute [{attribute}], [{obj}]")
            return NOT_FOUND
        return getattr(obj, attribute)

    def _get_value(self, obj: dict | object, attribute: str):
        """get the attribute of the structure"""
        out = None
        if isinstance(obj, dict):
            out = self._get_dict_attribute(obj, attribute)
        else:
            out = self._get_obj_attribute(obj, attribute)
        if out == NOT_FOUND:
            raise ValueError(f"[ObjectFilter] Object/Dict has no attribute [{attribute}]")
        return out

    def _evaluate_filter_result(self, atomic_filter_results: dict, filter_sets_results: dict) -> bool | None:
        """evaluate the filter rules"""
        out = None
        # TODO PRIO1 implement evaluate the results
        return out

    def _filter_obj(self, obj: dict | object) -> bool:
        """internal filtering of object attributes
        returns filter results by fields
        """
        _atomic_filters_passed = {}
        _filter_sets_passed = {}
        for _attribute, _filter_dict in self._filter.object_filter_dict.items():
            _value = None
            try:
                _value = self._get_value(obj, _attribute)
            except ValueError as e:
                logger.info(f"[ObjectFilter] Object/Dict has no attribute [{_attribute}], {e.args}")
                continue

            for _filter_rule, _filter in _filter_dict.items():
                logger.debug(f"[ObjectFilter], Filtering Attribute [{_attribute}], rule [{_filter_rule}")
                if isinstance(_filter, AbstractAtomicFilter):
                    _atomic_filters_passed[_filter_rule] = _filter.filter(_value)
                elif isinstance(_filter, FilterSet):
                    _check_any = self._filter.operator
                    _filter_sets_passed[_filter_rule] = _filter.filter(_value, check_any=_check_any)

        return self._evaluate_filter_result(_atomic_filters_passed, _filter_sets_passed)

    def filter(self, obj: object) -> bool:
        """filtering the complex structured object"""
        return self._filter_obj(obj)


# TODO IMPLEMENT UNIT TESTS
