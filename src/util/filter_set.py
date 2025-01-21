"""Combined Atomic Filters to a filter set"""

import logging
import os
from datetime import datetime as DateTime
from typing import Dict, List


from model.model_filter import FilterSetModel, AtomicFilterResult, FilterSetResult
from util import constants as C
from util.filter import AbstractAtomicFilter
from util.utils import Utils

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

PLAIN_OBJECT = "[plain_object]"


class FilterSet(AbstractAtomicFilter):
    """Combining sets of (atomic) filters / can also be used to filter
    structured objects like dicts and objects"""

    def __init__(self, obj_filter: FilterSetModel):
        """constructor"""
        super().__init__(obj_filter)
        self._filter_list: List[AbstractAtomicFilter] = obj_filter.filter_list
        self._filter_group_dict: Dict[str, list] = {}
        self._filter_attribute_dict: Dict[str, list] = {}
        self._filter_key_dict: Dict[str, AbstractAtomicFilter] = {}
        self._verbose = None
        # get items
        self._parse_filter_list()
        pass

    def _get_atomic_filter(self, key: object) -> AbstractAtomicFilter | None:
        """gets the filter by its key"""
        return self._filter_key_dict.get(key)

    def _parse_filter_list(self):
        """parse the filter list
        - get a dict of filters by key
        - get lists sorted into filter groups, attributes

        """
        for _atomic_filter in self._filter_list:
            # there is always a key / either custom or generated
            _filter_key = _atomic_filter.key
            _filter_description = _atomic_filter.description
            if self._filter_key_dict.get(_filter_key) is not None:
                logger.warning(f"[FilterSet] Filter Key {_filter_key} is duplicate")
                continue
            self._filter_key_dict[_filter_key] = _atomic_filter

            _filter_groups = _atomic_filter.groups
            if isinstance(_filter_groups, str):
                _filter_groups = [_filter_groups]

            # add filter to filter dict
            # update filter groups
            for _group in _filter_groups:
                # get the group
                _filters_in_group = self._filter_group_dict.get(_group, [])
                _filters_in_group.append(_filter_key)
                self._filter_group_dict[_group] = _filters_in_group

            # update filter by attributes
            _filtered_attributes = _atomic_filter.attributes
            if isinstance(_filtered_attributes, str):
                _filtered_attributes = [_filtered_attributes]
            if isinstance(_filtered_attributes, list):
                for _attribute in _filtered_attributes:
                    _filters_by_attribute = self._filter_attribute_dict.get(_attribute, [])
                    _filters_by_attribute.append(_attribute)
                    self._filter_attribute_dict[_attribute] = _filters_by_attribute
                    
        pass

    @property
    def group_list(self):
        """get the group list"""
        return list(self._filter_group_dict.keys())

    @property
    def attribute_list(self):
        """gets the attributes that can be filtered"""
        return list(self._filter_attribute_dict.keys())

    @property
    def filter_keys(self):
        """get the filter keys"""
        return list(self._filter_key_dict.keys())

    def _get_value(self, obj: object, attribute: str) -> object | None:
        """tries to get value from a structure like object or a d dict"""
        out = None
        if isinstance(obj, dict):
            out = obj.get(attribute)
        elif hasattr(obj, attribute):
            out = getattr(obj, attribute)
        return out

    def _passes_atomic_filter(
        self, obj: object, filter_key: object, attribute: str, atomic_filter: AbstractAtomicFilter
    ) -> AtomicFilterResult:
        """does the filtering using the atomic filter"""
        out = []
        _operator = atomic_filter.operator
        _include = atomic_filter.include
        # _attributes = atomic_filter.attributes
        _groups = atomic_filter.groups
        _passed = atomic_filter.filter(obj)
        logger.debug(
            f"[FilterSet] Object [{obj}], Set [{self.key}] filter [{filter_key}], attribute [{attribute}], passes [{_passed}]"
        )

        if _passed is None:
            logger.info(
                f"[FilterSet] Filter is NONE, Object [{obj}], Set [{self.key}] filter [{filter_key}], attribute [{attribute}]"
            )
            return None

        return AtomicFilterResult(
            filter_key=filter_key,
            obj=obj,
            operator=_operator,
            include=_include,
            attribute=attribute,
            groups=_groups,
            passed=_passed,
        )

    def _add_message_to_result(self, message: str, key: str, filter_set_result: FilterSetResult) -> None:
        """adding a message to the result set"""
        if not self._verbose:
            return
        _messages = filter_set_result.messages.get(key, [])
        _messages.append(message)
        filter_set_result.messages[key] = _messages

    def filter(
        self, obj: object, groups: list = None, verbose: bool = False
    ) -> bool | None | Dict[str, AtomicFilterResult]:
        """filtering the Filter Set"""
        self._verbose = verbose

        _filter_set_result = FilterSetResult()

        if isinstance(groups, str):
            groups = [groups]
        _passed_list = []
        out = None
        _result = []
        if verbose:
            out = {}

        for _filter_key, _atomic_filter in self._filter_key_dict.items():
            _atomic_filter_groups = _atomic_filter.groups
            # only continue if filter is assigned to the filter group
            # or all filters applied
            # or there are groups anyway
            if groups is not None and _atomic_filter_groups is not None:
                _filtered = [filtered_group for filtered_group in groups if filtered_group in _atomic_filter_groups]
                if len(_filtered) == 0:
                    _s = f"[FilterSet] Filter [{_filter_key}] is not in passed groups {groups}"
                    logger.debug(_s)
                    self._add_message_to_result(_s, _filter_key, _filter_set_result)
                    continue

            _values = {}

            # get the values to be checked
            if isinstance(_atomic_filter.attributes, list) and len(_atomic_filter.attributes) > 0:
                # try to get value from objects
                for _attribute in _atomic_filter.attributes:
                    _value = self._get_value(obj, _attribute)
                    if _value is None and self._filter.ignore_missing_attributes:
                        _s = f"[FilterSet] Filter [{_filter_key}], no value found for attribute [{_attribute}], result will be ignored"
                        logger.debug(_s)
                        self._add_message_to_result(_s, _filter_key, _filter_set_result)
                        continue
                    _values[_attribute] = _value
            # no attributes given, treat values as direct filter value
            else:
                _values = {PLAIN_OBJECT: obj}

            _result = None
            for _value_key, _value in _values.items():
                try:
                    _result = self._passes_atomic_filter(
                        obj=_value, filter_key=_filter_key, attribute=_value_key, atomic_filter=_atomic_filter
                    )
                except ValueError as e:
                    _s = f"[FilterSet] Wrong Type for filter, Object [{obj}], FilterSet [{self.key}] value key [{_value_key}],  Filter Type [{_atomic_filter._filter_type}], {e} "
                    self._add_message_to_result(_s, _filter_key, _filter_set_result)
                    logger.debug(_s)
                    _result = None
                    continue

                if _result is None and self._filter.ignore_missing_attributes:
                    _s = f"[FilterSet] Filter returns None, Object [{obj}], FilterSet [{self.key}] value key [{_value_key}],  Filter Type [{_atomic_filter._filter_type}]"
                    self._add_message_to_result(_s, _filter_key, _filter_set_result)
                    logger.debug(_s)
                    continue

                _passed_list.append(_result.passed)
                if verbose:
                    out[_filter_key] = _result

        # calculate filter result
        _filter = self._filter
        _result = None
        if len(_passed_list) > 0:
            if _filter.operator == "all":
                _result = all(_passed_list)
            else:
                _result = any(_passed_list)
        if isinstance(_result, bool) and _filter.include == "exclude":
            _result = not _result

        if verbose:
            _filter_set_result.filter_set_result = AtomicFilterResult(
                filter_key=_filter.key,
                obj=obj,
                operator=_filter.operator,
                include=_filter.include,
                groups=_filter.groups,
                passed=_result,
            )
            _filter_set_result.passed = _result
            out = _filter_set_result
        else:
            out = _result

        return out
