"""Test Setup"""

import os
from copy import deepcopy
from datetime import datetime as DateTime
from pathlib import Path
import pytest
from util import constants as C


@pytest.fixture
def fixture_sample_import():
    """variations of import commands"""
    snippet = """
import sys
from os import chdir
from pathlib import Path as MyPath
from a.b import z
from d import k,m
from .xyz import abc
"""

    return snippet
