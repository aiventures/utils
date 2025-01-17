"""Combined Atomic Filters to a filter set"""

import logging
import os
from typing import List, Dict, Optional
from util.filter import AbstractAtomicFilter
from util import constants as C
from util.utils import Utils
from datetime import datetime as DateTime
from util.filter import DictFilter
from pydantic import ConfigDict, BaseModel
from model.model_persistence import ParamsFind

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class FilterSet:
    """Combining sets of (atomic) filters"""

    def __init__(self, filter_list: List[AbstractAtomicFilter]):
        """constructor"""
        self._filter_list: List[AbstractAtomicFilter] = filter_list
        self._filter_group_dict: Dict[str, List[AbstractAtomicFilter]] = {}
        self._filter_key_dict: Dict[str, AbstractAtomicFilter] = {}
        self._parse_list()
        pass

    def _parse_list(self):
        """parse the filter list"""
        for _atomic_filter in self._filter_list:
            _filter_key = _atomic_filter.key
            # add hash when there is no key
            if _filter_key is None:
                _seed = str(DateTime.now())
                _filter_key = Utils.get_hash(_seed)
                _atomic_filter.key = _filter_key
            _filter_groups = _atomic_filter.groups
            if isinstance(_filter_groups, str):
                _filter_groups = [_filter_groups]

            if self._filter_key_dict.get(_filter_key) is not None:
                logger.warning(f"[FilterSet] Filter Key {_filter_key} is duplicate")
            self._filter_key_dict[_filter_key] = _atomic_filter

            if isinstance(_filter_groups, list):
                for _filter_group in _filter_groups:
                    _filters_in_group = self._filter_group_dict.get(_filter_group, [])
                    _filters_in_group.append(_atomic_filter)
                    self._filter_group_dict[_filter_group] = _filters_in_group

    def filter(
        self, obj: object, groups: List[str] | str = None, short: bool = False, check_any: bool = False
    ) -> dict | bool:
        """filter all sets returns a single boolean or detailed result dict"""
        out = {}
        if isinstance(groups, str):
            groups = [groups]
        _groups = self.group_list
        # restrict filter groups to any of the existing ones
        if isinstance(groups, list):
            _groups = [_g for _g in groups if _g in _groups]
        _passed_list = {}
        for _group, _filters in self._filter_group_dict.items():
            if not _group in _groups:
                continue
            _filter_results = {"all": {}, "any": {}, "passes_all": None, "passes_any": None, "passes": None}
            for _filter in _filters:
                try:
                    _passed = _filter.filter(obj)
                except ValueError:
                    continue
                _key = _filter.key
                _operator = _filter.operator
                _filter_results[_operator][_key] = _passed
            # evaluate result: only if items are passing within one group
            _passes_all = None
            _passes_any = None
            if len(_filter_results["any"]) > 0:
                _passes_any = any(_filter_results["any"].values())
                _filter_results["passes_any"] = _passes_any
            if len(_filter_results["all"]) > 0:
                _passes_all = all(_filter_results["all"].values())
                _filter_results["passes_all"] = _passes_all
            # all filter takes precedence over any filters
            if _passes_all is not None:
                # also check for any passes_any
                if _passes_all is True and check_any is True and _passes_any is not True:
                    _passes_all = False
                _filter_results["passes"] = _passes_all
            else:
                _filter_results["passes"] = _passes_any
            _passed_list[_group] = _filter_results
        out = _passed_list
        if short is True:
            # if there is only one group, return the boolean only
            out = {_group: _result["passes"] for _group, _result in out.items()}
            if len(out) == 1:
                out = list(out.values())[0]
        return out

    @property
    def group_list(self):
        """get the group list"""
        return list(self._filter_group_dict.keys())

    @property
    def filter_keys(self):
        """get the filter keys"""
        return list(self._filter_key_dict.keys())


# TODO CHECK
# class ObjectFilterModel(FilterModel):
#     """filters on attributes of dict fields or object attributes
#     filters can be filters or filter sets
#     """

#     # Model is a dict of [object_attribute_name][rulename][filter|filterset]
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     # Model is a dict of [object_attribute_name][rulename][filter|filterset]
#     object_filter_dict = Dict[str, Dict[str, AbstractAtomicFilter | FilterSet]]


# TODO FIX IMPORT
class ParamsFileTreeModel(BaseModel):
    """Input Params for File Tree Constructor"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    file_filter_params: Optional[ParamsFind] = None
    add_metadata: Optional[bool] = False
    add_filesize: Optional[bool] = False
    file_filter: Optional[FilterSet | DictFilter] = None
    path_filter: Optional[FilterSet | DictFilter] = None
