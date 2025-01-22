"""Unit Tests for the Filter Set Class"""

import pytest
import logging
import os
from util import constants as C
from typing import Optional, Literal
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
    _str_filter_params["key"] = "ANY_str_filter_model_xyz_and_hugo_0"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_or_hugo = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_or_hugo)
    out["_str_filter_model_xyz_or_hugo_no_keys"] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_and_hugo_1"
    _str_filter_params["description"] = "string to match xyz and hugo"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str_2"
    _str_filter_params["description"] = "string to match xyz and hugo"
    _str_filter_params["groups"] = ["str", "int"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo_assigned_to_groups_int_str = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "ALL_str_filter_model_xyz_or_hugo_match_plain_without_field_3"
    _str_filter_params["description"] = "string to match xyz or hugo directly without field"
    _str_filter_params["groups"] = ["str"]
    _str_filter_params["attributes"] = None
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_or_hugo_match_plain_without_field = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_or_hugo_match_plain_without_field)
    out[_str_filter_params["key"]] = _string_filter

    _regex_filter_params = deepcopy(filter_model_fields)
    _regex_filter_params["key"] = "ANY_regex_filter_model_starts_with_abc_4"
    _regex_filter_params["description"] = "regex string starts with abc"
    _regex_filter_params["groups"] = ["str"]
    _regex_filter_params["attributes"] = ["str_field"]
    _regex_filter_params["operator"] = "any"
    _regex_filter_params["regex"] = "^abc"
    _regex_filter_model_starts_with_abc = RegexFilterModel(**_regex_filter_params)
    _regex_filter = RegexFilter(_regex_filter_model_starts_with_abc)
    out[_regex_filter_params["key"]] = _regex_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "INVALID_str_filter_model_xyz_and_hugo_invalid_group_5"
    _str_filter_params["description"] = "string to match xyz and hugo invalid group"
    _str_filter_params["groups"] = ["invalid group"]
    _str_filter_params["attributes"] = ["str_field"]
    _str_filter_params["operator"] = "all"
    _str_filter_params["filter_strings"] = ["xyz", "hugo"]
    _str_filter_model_xyz_and_hugo_invalid_group = StringFilterModel(**_str_filter_params)
    _string_filter = StringFilter(_str_filter_model_xyz_and_hugo_invalid_group)
    out[_str_filter_params["key"]] = _string_filter

    _str_filter_params = deepcopy(filter_model_fields)
    _str_filter_params["key"] = "INVALID_str_filter_model_xyz_and_hugo_invalid_field_6"
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
    _num_filter_model_params["key"] = "ALL_num_filter_model_int_10_to_20_7"
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
    _datenum_filter_model_params["key"] = "ANY_datenum_filter_model_date_20250115_20250120_8"
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
    _calendar_filter_model_params["key"] = "ALL_calendar_filter_model_date_202501_1017_2326_9"
    _calendar_filter_model_params["description"] = "calendar matching Jan 2025 10-17 and 23-26"
    _calendar_filter_model_params["groups"] = ["calendar"]
    _calendar_filter_model_params["operator"] = "all"
    _calendar_filter_model_params["attributes"] = ["date_field"]
    _calendar_filter_model_params["filter_str"] = "20250110-20250117;20250123-20250126"
    _calendar_filter_model_date_202501_1820_2326 = CalendarFilterModel(**_calendar_filter_model_params)
    _calendar_filter = CalendarFilterWrapper(_calendar_filter_model_date_202501_1820_2326)
    out[_calendar_filter_model_params["key"]] = _calendar_filter

    test_idx = {}
    for _i, _text in enumerate(out.keys()):
        test_idx[_i] = _text

    #  groups date,int,str,calendar

    return (test_idx, out)


class TestModel(BaseModel):
    """sample model"""

    description: str = "[str:xyz hugo|int 15|date 17.1.2025]"
    str_field: str = "xyz hugo"
    int_field: int = 15
    date_field: DateTime = DateTime(2025, 1, 17)


class TestObject(BaseModel):
    """model for a test object"""

    obj: Optional[TestModel] = None
    obj_type: Optional[Literal["dict", "object", "plain"]] = "object"
    description: Optional[str] = None
    groups: Optional[list] = None
    rule_idx_matches: Optional[dict[int, bool | None]] = None
    # field to extract plain object
    field: Optional[str] = None
    # which atomic filters to test (None Test all )
    rules_to_test: Optional[list] = None


def test_objects() -> dict:
    """provide sets of test objects"""
    out = {}
    _test_model = TestModel()
    # _test_object_description = _test_object.description
    _groups = ["str"]
    _rule_idx_matches = {0: True, 1: True, 2: True, 5: None, 7: None, 9: None, 8: None}
    _test_object = TestObject(
        obj=_test_model,
        obj_type="object",
        description=_test_model.description,
        groups=_groups,
        rule_idx_matches=_rule_idx_matches,
    )
    out["TEST_OBJECT_GROUP_STR"] = _test_object
    # create one with int group
    _obj = TestModel()
    obj_type = "object"
    _groups = ["int"]
    _rule_idx_matches = {3: None, 7: True, 8: None}
    _rules_to_test = [3, 7, 8]
    _test_object = TestObject(
        obj=_obj,
        obj_type=obj_type,
        description=_obj.description,
        groups=_groups,
        rule_idx_matches=_rule_idx_matches,
        rules_to_test=_rules_to_test,
    )
    out["TEST_OBJECT_GROUP_INT"] = _test_object

    # create one with date group
    _obj = TestModel()
    obj_type = "object"
    _groups = ["date"]
    _rule_idx_matches = {7: None, 8: True}
    _rules_to_test = [7, 8]
    _test_object = TestObject(
        obj=_obj,
        obj_type=obj_type,
        description=_obj.description,
        groups=_groups,
        rule_idx_matches=_rule_idx_matches,
        rules_to_test=_rules_to_test,
    )
    out["TEST_OBJECT_GROUP_DATE"] = _test_object

    # create a calendar test object
    _obj = TestModel()
    obj_type = "object"
    _groups = ["calendar"]
    _rule_idx_matches = {8: None, 9: True}
    _rules_to_test = [8, 9]
    _test_object = TestObject(
        obj=_obj,
        obj_type=obj_type,
        description=_obj.description,
        groups=_groups,
        rule_idx_matches=_rule_idx_matches,
        rules_to_test=_rules_to_test,
    )
    out["TEST_OBJECT_GROUP_CALENDAR"] = _test_object

    return out


def atomic_filter_test_sets(test_object_key: str = "TEST_OBJECT_GROUP_STR") -> list:
    """create pytest parametrizations for single atomic tests"""
    out = []

    # create a set of atomic filters
    _filter_idx, _atomic_filter_dict = _create_atomic_filters()
    # get the test object and integrate it into the test

    # create test data, test case description, test group, and expected matches
    # we have filters assigned to a filter group str,int,date, calendar (can be arbitrary value)
    _test_object_key = test_object_key
    _test_object_meta: TestObject = test_objects().get(_test_object_key)
    _test_object = _test_object_meta.obj
    _groups = _test_object_meta.groups
    _rule_idx_matches = _test_object_meta.rule_idx_matches
    _test_object_description = _test_object_meta.description
    _obj_type = _test_object_meta.obj_type
    _rules_to_test = _test_object_meta.rules_to_test
    if not isinstance(_rules_to_test, list):
        _rules_to_test = list(range(10))

    # groups / suffix is the index used in the rule_idx
    # short key vs filter descriptio
    # {0: '_str_filter_model_xyz_or_hugo_no_keys_0',
    #  1: 'ALL_str_filter_model_xyz_and_hugo_1',
    #  2: 'ALL_str_filter_model_xyz_and_hugo_assigned_to_groups_int_str_2',
    #  3: 'ALL_str_filter_model_xyz_or_hugo_match_plain_without_field_3',
    #  4: 'ANY_regex_filter_model_starts_with_abc_4',
    #  5: 'INVALID_str_filter_model_xyz_and_hugo_invalid_group_5',
    #  6: 'INVALID_str_filter_model_xyz_and_hugo_invalid_field_6',
    #  7: 'ALL_num_filter_model_int_10_to_20_7',
    #  8: 'ANY_datenum_filter_model_date_20250115_20250120_8',
    #  9: 'ALL_calendar_filter_model_date_202501_1820_2326_9'}

    # list of rule indices that should match to true
    for _i in _rules_to_test:
        _atomic_filter_key = _filter_idx[_i]
        # dict either contains True or None, False is default
        _rule_matches = _rule_idx_matches.get(_i, False)
        # invalid test case
        if _atomic_filter_key.startswith("INVALID"):
            _rule_matches = None
        # test case for plain object (not a dict or pydantic)
        if "plain" in _atomic_filter_key and "plain" not in _obj_type:
            _rule_matches = None

        _atomic_filter = _atomic_filter_dict[_atomic_filter_key]
        _test_case_id = f"[{_obj_type}] FILTER [{_atomic_filter_key}]OBJECT [{_test_object_description}] ATTRIBUTE {_atomic_filter.attributes} GROUPS {_groups} [EXPECT:{_rule_matches}]"
        pass
        # ["rule_matches","atomic_filter","groups","test_object","id"]
        out.append(pytest.param(_rule_matches, _atomic_filter, _groups, _test_object, id=_test_case_id))
    return out


def _filter_set_single_atomic_filter(atomic_filter, groups, test_object) -> FilterSetResult:
    """do the filtering"""
    # create a filter set and do the test
    _filter_set_model = FilterSetModel(
        key="filter_set_single_atomic_filter", description=atomic_filter.description, filter_list=[atomic_filter]
    )
    _filter_set = FilterSet(obj_filter=_filter_set_model)
    _result = _filter_set.filter(test_object, groups=groups, verbose=True)
    return _result


# there is a better way to paramtrize it via fixtures but we'll leave it for now
@pytest.mark.parametrize(
    "rule_matches,atomic_filter,groups,test_object", atomic_filter_test_sets("TEST_OBJECT_GROUP_STR")
)
def test_filter_sets_single_str_group(rule_matches, atomic_filter, groups, test_object):
    """testing filter sets"""
    _result = _filter_set_single_atomic_filter(atomic_filter, groups, test_object)
    assert _result.passed == rule_matches


@pytest.mark.parametrize(
    "rule_matches,atomic_filter,groups,test_object", atomic_filter_test_sets("TEST_OBJECT_GROUP_INT")
)
def test_filter_sets_single_int_group(rule_matches, atomic_filter, groups, test_object):
    """testing filter sets"""
    _result = _filter_set_single_atomic_filter(atomic_filter, groups, test_object)
    assert _result.passed == rule_matches


@pytest.mark.parametrize(
    "rule_matches,atomic_filter,groups,test_object", atomic_filter_test_sets("TEST_OBJECT_GROUP_DATE")
)
def test_filter_sets_single_date_group(rule_matches, atomic_filter, groups, test_object):
    """testing filter sets"""
    _result = _filter_set_single_atomic_filter(atomic_filter, groups, test_object)
    assert _result.passed == rule_matches


@pytest.mark.parametrize(
    "rule_matches,atomic_filter,groups,test_object", atomic_filter_test_sets("TEST_OBJECT_GROUP_CALENDAR")
)
def test_filter_sets_single_calendar_group(rule_matches, atomic_filter, groups, test_object):
    """testing filter sets"""
    _result = _filter_set_single_atomic_filter(atomic_filter, groups, test_object)
    assert _result.passed == rule_matches
