"""Unit Tests for the Filter Set Class"""

import logging
import os
from util import constants as C
from model.model_filter import FilterSetModel
from util.filter_set import FilterSet

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


def test_filter_set(fixture_filter_set):
    """testing filter operation"""
    test_object = 13
    _filter_result_verbose = fixture_filter_set.filter(test_object)

    # _filter_result_verbose = fixture_filter_set.filter(test_object, short=False)
    assert isinstance(_filter_result_verbose, dict)
    assert isinstance(_filter_result_verbose.get("group1"), dict)
    _filter_result_short = fixture_filter_set.filter(test_object, short=True)
    assert isinstance(_filter_result_short, dict)
    assert isinstance(_filter_result_short.get("group1"), bool)
    # only one group
    _filter_result_onegroup = fixture_filter_set.filter(test_object, groups="group1", short=True)
    assert isinstance(_filter_result_onegroup, bool)
    pass
