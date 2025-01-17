"""Unit Tests for the Filter Class"""

import logging
import os
from util import constants as C
from datetime import datetime as DateTime

from util.filter import NumericalFilter, RegexFilter, StringFilter, CalendarFilterWrapper
# from util.calendar_filter import CalendarFilter

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


def test_numerical_filter(fixture_numerical_filter):
    """testing atomic filter"""
    # fixture  5 (value_min) < x < 10 (value_max)
    _num_filter = NumericalFilter(fixture_numerical_filter)
    _passed = _num_filter.filter(3)
    assert _passed is False
    _passed = _num_filter.filter(5)
    assert _passed is False
    _passed = _num_filter.filter(6)
    assert _passed is True
    _passed = _num_filter.filter(10)
    assert _passed is False
    _passed = _num_filter.filter(13)
    assert _passed is False
    # now check the edge cases
    fixture_numerical_filter.operator_min = "ge"
    fixture_numerical_filter.operator_max = "le"
    _num_filter = NumericalFilter(fixture_numerical_filter)
    _passed = _num_filter.filter(5)
    assert _passed is True
    _passed = _num_filter.filter(10)
    assert _passed is True
    pass


def test_numerical_filter_date(fixture_numerical_filter_date):
    """testing atomic date filter"""
    # fixture  2024.12.5 (value_min) < x < 2024.12.10 (value_max)
    _num_filter = NumericalFilter(fixture_numerical_filter_date)
    _passed = _num_filter.filter(DateTime(2024, 12, 3))
    assert _passed is False
    _passed = _num_filter.filter(DateTime(2024, 12, 5))
    assert _passed is False
    _passed = _num_filter.filter(DateTime(2024, 12, 6))
    assert _passed is True
    _passed = _num_filter.filter(DateTime(2024, 12, 10))
    assert _passed is False
    _passed = _num_filter.filter(DateTime(2024, 12, 13))
    assert _passed is False
    # now check the edge cases
    fixture_numerical_filter_date.operator_min = "ge"
    fixture_numerical_filter_date.operator_max = "le"
    _num_filter = NumericalFilter(fixture_numerical_filter_date)
    _passed = _num_filter.filter(DateTime(2024, 12, 5))
    assert _passed is True
    _passed = _num_filter.filter(DateTime(2024, 12, 10))
    assert _passed is True
    pass


def test_regex_filter(fixture_regex_filter):
    """testing regex filter"""
    _regex_filter = RegexFilter(fixture_regex_filter)
    # regex "hu(.+)go"
    _passed = _regex_filter.filter("hufoundgo")
    assert _passed is True
    _found_str = _regex_filter.find_all("hufoundgo")
    assert isinstance(_found_str, list)
    _passed = _regex_filter.filter("foundgo")
    assert _passed is False


def test_string_filter(fixture_string_filter):
    """testing regex filter"""
    # ["test", "another"],
    _string_filter = StringFilter(fixture_string_filter)
    _passed = _string_filter.filter("this is a test")
    assert _passed is True
    _passed = _string_filter.filter("this is missing")
    assert _passed is False


def test_calendar_filter(fixture_calendar_filter):
    """testing calendar filter"""
    # 20241205-20241210
    _calendar_filter = CalendarFilterWrapper(fixture_calendar_filter)
    _date_list = _calendar_filter.datelist
    assert isinstance(_date_list, list)
    _passed = _calendar_filter.filter(DateTime(2024, 12, 3))
    assert _passed is False
    _passed = _calendar_filter.filter(DateTime(2024, 12, 11))
    assert _passed is True
    _passed = _calendar_filter.filter(DateTime(2024, 12, 21))
    assert _passed is False
