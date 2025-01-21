"""Unit Tests for the Filter Set Class"""

import pytest
import logging
import os
from util import constants as C
from pydantic import BaseModel
from model.model_filter import (
    FilterSetModel,
    FilterSetResult,
    NumericalFilterModel,
    StringFilterModel,
    RegexFilterModel,
)
from copy import deepcopy
from util.filter_set import FilterSet
from util.filter import NumericalFilter, StringFilter, CalendarFilterModel, CalendarFilterWrapper, RegexFilter
from util.calendar_filter import CalendarFilter as CalendarFilterObject
from datetime import datetime as DateTime

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_filter_set_setup(
    fixture_numerical_filter,
    fixture_numerical_filter_date,
    fixture_regex_filter,
    fixture_string_filter,
    fixture_calendar_filter,
):
    """testing filter set setup"""
    _filter_list = [
        fixture_numerical_filter,
        fixture_numerical_filter_date,
        fixture_regex_filter,
        fixture_string_filter,
        fixture_calendar_filter,
    ]

    _filterset_model = FilterSetModel(filter_list=_filter_list)
    _filter_set = FilterSet(obj_filter=_filterset_model)
    _group_list = _filter_set.group_list
    assert isinstance(_group_list, list)
    # passing 2 groups
    assert len(_group_list) == 2
    _filter_keys = _filter_set.filter_keys
    assert isinstance(_filter_keys, list)
    # passed 5 filters
    assert len(_filter_keys) == 5


def test_filter_set_simple(fixture_filter_set):
    """testing filter operation without checking for consistency"""
    test_object = 13
    _filter_result_verbose = fixture_filter_set.filter(test_object, verbose=True)

    # _filter_result_verbose = fixture_filter_set.filter(test_object, short=False)
    assert isinstance(_filter_result_verbose, FilterSetResult)
    _filter_result_short = fixture_filter_set.filter(test_object)
    assert isinstance(_filter_result_short, bool | None)
    # only one group
    _filter_result_onegroup = fixture_filter_set.filter(test_object, groups="group1", verbose=True)
    assert isinstance(_filter_result_onegroup, FilterSetResult)
    pass


def _create_atomic_filters() -> tuple:
    """create numerical filters"""
    out = {}

    # empty
    filter_model_fields = {
        "key": None,
        "description": None,
        "groups": None,
        "operator": "any",
        "include": "include",
        "attributes": ["str_field"],
        "ignore_missing_attributes": True,
        "ignore_none_filter_results": True,
    }

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ANY_str_filter_model_xyz_and_hugo"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_or_hugo = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_or_hugo)
    out["_str_filter_model_xyz_or_hugo_no_keys"] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_and_hugo"
    _str_filter_params["description"] = "string to match xyz and hugo"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str"
    _str_filter_params["description"] = "string to match xyz and hugo"
    _str_filter_params["groups"] = ["str", "int"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo_assigned_to_groups_int_str = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_or_hugo_match_plain_without_field"
    _str_filter_params["description"] = "string to match xyz or hugo directly without field"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = None
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_or_hugo_match_plain_without_field = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_or_hugo_match_plain_without_field)
    out[_str_filter_params["key"]] = _string_filter

    _regex_filter_params = deepcopy(filter_model_fields)
    _regex_filter_params["key"] = "ANY_regex_filter_model_starts_with_abc"
    _regex_filter_params["description"] = "regex string starts with abc"
    _regex_filter_params["groups"] = ["str"]
    _regex_filter_params["attributes"] = ["str_field"]
    _regex_filter_params["operator"] = "any"
    _regex_filter_params["regex"] = "^abc"
    _regex_filter_model_starts_with_abc = RegexFilterModel(**_regex_filter_params)
    _regex_filter = RegexFilter(_regex_filter_model_starts_with_abc)
    out[_regex_filter_params["key"]] = _regex_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "INVALID_str_filter_model_xyz_and_hugo_invalid_group"
    _str_filter_params["description"] = "string to match xyz and hugo invalid group"
    _str_filter_params["groups"] = ["invalid group"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo_invalid_group = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo_invalid_group)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "INVALID_str_filter_model_xyz_and_hugo_invalid_field"
    _str_filter_params["description"] = "string to match xyz and hugo invalid group"
    _str_filter_params["groups"] = ["invalid group"]
    _str_filter_params["attributes"] = ["invalid_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo_invalid_field = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo_invalid_field)
    out[_str_filter_params["key"]] = _string_filter

    # numerical filter model between 10 and 20
    _num_filter_model_params = deepcopy(filter_model_fields)
    _num_filter_model_params["key"] = "ALL_num_filter_model_int_10_to_20"
    _num_filter_model_params["description"] = "num to match int between 10 and 20"
    _num_filter_model_params["groups"] = ["int"]
    _num_filter_model_params["attributes"] = ["int_field"]
    _num_filter_model_params["operator"] = "all"
    _num_filter_model_params["value_max"] = 20
    _num_filter_model_params["value_min"] = 10
    _num_filter_model_int_10_to_20 = NumericalFilterModel(**_num_filter_model_params)
    _num_filter = NumericalFilter(_num_filter_model_int_10_to_20)
    out[_num_filter_model_params["key"]] = _num_filter

    # date filter between 15 and 20 Jan 2025
    _datenum_filter_model_params = deepcopy(filter_model_fields)
    _datenum_filter_model_params["key"] = "ANY_datenum_filter_model_date_20250115_20250120"
    _datenum_filter_model_params["description"] = "date num between Jan 15 2025 and Jan 20 2025"
    _datenum_filter_model_params["groups"] = ["date"]
    _datenum_filter_model_params["attributes"] = ["date_field"]
    _datenum_filter_model_params["value_min"] = DateTime(2025, 1, 15)
    _datenum_filter_model_params["value_max"] = DateTime(2025, 1, 20)
    _datenum_filter_model_jan_15_20 = NumericalFilterModel(**_datenum_filter_model_params)
    _datenum_filter = NumericalFilter(_datenum_filter_model_jan_15_20)
    out[_datenum_filter_model_params["key"]] = _datenum_filter

    # calendar filter model to pass dates between Jan 18-20 and and Jan 23-26 2025
    _calendar_filter_model_params = deepcopy(filter_model_fields)
    _calendar_filter_model_params["key"] = "ALL_calendar_filter_model_date_202501_1820_2326"
    _calendar_filter_model_params["description"] = "calendar matching Jan 2025 18-20 and 23-26"
    _calendar_filter_model_params["groups"] = ["calendar"]
    _calendar_filter_model_params["operator"] = "all"
    _calendar_filter_model_params["attributes"] = ["date_field"]
    _calendar_filter_model_params["filter_str"] = "20250118-20250120;20250123-20250126"
    _calendar_filter_model_date_202501_1820_2326 = CalendarFilterModel(**_calendar_filter_model_params)
    _calendar_filter = CalendarFilterWrapper(_calendar_filter_model_date_202501_1820_2326)
    out[_calendar_filter_model_params["key"]] = _calendar_filter

    test_idx = {}
    for _i, _text in enumerate(out.keys()):
        test_idx[_i] = _text

    #  groups date,int,str,calendar

    return (test_idx, out)


def atomic_filter_test_sets() -> list:
    """create pytest parametrizations for single atomic tests"""
    out = []

    _filter_idx, _atomic_filter_dict = _create_atomic_filters()

    class TestModel(BaseModel):
        """sample model"""

        description: str = " OBJECT [str:xyz hugo|int 15|date 17.1.2025]"
        str_field: str = "xyz hugo"
        int_field: int = 15
        date_field: DateTime = DateTime(2025, 1, 17)

    _test_object = TestModel()
    _test_object_description = _test_object.description

    # groups
    # short key vs filter descriptio
    # {0: '_str_filter_model_xyz_or_hugo_no_keys',
    #  1: 'ALL_str_filter_model_xyz_and_hugo',
    #  2: 'ALL_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str',
    #  3: 'ALL_str_filter_model_xyz_or_hugo_match_plain_without_field',
    #  4: 'ANY_regex_filter_model_starts_with_abc',
    #  5: 'INVALID_str_filter_model_xyz_and_hugo_invalid_group',
    #  6: 'INVALID_str_filter_model_xyz_and_hugo_invalid_field',
    #  7: 'ALL_num_filter_model_int_10_to_20',
    #  8: 'ANY_datenum_filter_model_date_20250115_20250120',
    #  9: 'ALL_calendar_filter_model_date_202501_1820_2326'}

    # create test data, test case description, test group, and expected matches
    _groups = ["str"]
    _rule_idx_matches = [0, 1, 2, 7, 8]
    
    _obj_type = "[plain_object] "
    if isinstance(_test_object, dict):
        _obj_type = "[dict] "
    elif isinstance(_test_object, BaseModel):
        _obj_type = "[pydantic] "
    # list of rule indices that should match to true
    for _i in range(0, 10):
        _atomic_filter_key = _filter_idx[_i]
        _rule_matches = False
        if _i in _rule_idx_matches:
            _rule_matches = True
        # invalid test case
        if _atomic_filter_key.startswith("INVALID"):
            _rule_matches = None
        # test case for plain object (not a dict or pydantic)
        if "plain" in _atomic_filter_key and "plain" not in _obj_type:
            _rule_matches = None

        _atomic_filter = _atomic_filter_dict[_atomic_filter_key]
        _test_case_id = f"{_obj_type} FILTER [{_atomic_filter_key}]{_test_object_description} [EXPECT:{_rule_matches}]"
        pass
        # ["rule_matches","atomic_filter","groups","test_object","id"]
        out.append(pytest.param(_rule_matches, _atomic_filter, _groups, _test_object, id=_test_case_id))
    return out


@pytest.mark.parametrize("rule_matches,atomic_filter,groups,test_object", atomic_filter_test_sets())
def test_filter_sets_single(rule_matches, atomic_filter, groups, test_object):
    """testing filter sets"""

    # create a filter set and do the test
    _filter_set_model = FilterSetModel(
        key="filter_set_single_atomic_filter", description=atomic_filter.description, filter_list=[atomic_filter]
    )
    _filter_set = FilterSet(obj_filter=_filter_set_model)
    _result = _filter_set.filter(test_object, groups=groups, verbose=True)

    assert _result.passed == rule_matches
