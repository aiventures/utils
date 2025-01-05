"""Unit Tests for the Constants Class"""

import logging
import os
from util import constants as C

from util.filter import NumericalFilter
from copy import deepcopy

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
