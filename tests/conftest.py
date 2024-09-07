""" Test Setup """

import pytest
import sys
import os
from copy import deepcopy
from pathlib import Path
import logging
from util import constants as C
from util.persistence import Persistence

@pytest.fixture
def fixture_testpath()->Path:
    """ Sample Path """
    p_testpath = Path(__file__).parent.parent.joinpath("test_path")
    return p_testpath

@pytest.fixture
def fixture_testfile(fixture_testpath)->Path:
    """ sample tesfile """
    f_testfile = Path(os.path.join(fixture_testpath,"subpath1","file1.txt"))
    return f_testfile

@pytest.fixture
def fixture_testfile_md(fixture_testpath)->Path:
    """ sample markdown tesfile """
    f_testfile = Path(os.path.join(fixture_testpath,"lorem_doc_root.md"))
    return f_testfile

@pytest.fixture
def fixture_testfile_dict(fixture_testpath):
    """  getting a test file from the sample path """
    f_sample = fixture_testpath.joinpath("lorem_doc_root.md")
    text_lines_dict = Persistence.read_txt_file(f_sample,comment_marker=None,with_line_nums=True)
    return text_lines_dict

@pytest.fixture
def fixture_ruledict_filename():
    """  getting a test file from the sample path """
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "test"
    file_rule[C.RULE_NAME] = "testrule_simple"
    return file_rule

@pytest.fixture
def fixture_ruledict_filename_absolute_path():
    """  getting a test file from the sample path """
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "lorem" # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_lorem" # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_ABSOLUTE_PATH
    return file_rule

@pytest.fixture
def fixture_ruledict_filename_filename():
    """  getting a test file from the sample path """
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "file1" # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_file1" # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_FILENAME
    return file_rule

@pytest.fixture
def fixture_ruledict_filename_path():
    """  getting a test file from the sample path """
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "subpath2" # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_subpath2" # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_PATH
    return file_rule

@pytest.fixture
def fixture_ruledict_file_content():
    """  getting a test file from the sample path """
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "sum" # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_file_content_sum" # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_FILE_CONTENT
    return file_rule

@pytest.fixture
def fixture_ruledict_file_content_all_rules(fixture_ruledict_file_content):
    """  getting two rules linked with an all  """
    file_rule = deepcopy(fixture_ruledict_file_content)
    file_rule[C.RULE_RULE] = "sum" # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule1_file_content_sum" # rule name
    file_rule[C.RULE_APPLY] = C.APPLY_ALL
    file_rule[C.RULE_FILE] = C.RULE_FILE_CONTENT
    file_rule2 = deepcopy(file_rule)
    file_rule2[C.RULE_RULE] = "crescit" # the search pattern, literal or regex
    file_rule2[C.RULE_NAME] = "testrule2_file_content_sum" # rule name
    return [file_rule,file_rule2]

