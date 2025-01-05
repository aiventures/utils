"""Test Setup"""

import os
from copy import deepcopy
from pathlib import Path

import pytest

from demo.demo_config import create_demo_config
from util import constants as C
from util.abstract_enum import AbstractEnum
from util.bat_helper import BatHelper
from util.calendar_index import CalendarIndex
from util.config_env import ConfigEnv, Environment
from util.persistence import Persistence
from util.utils import Utils
from util.calendar_filter import CalendarFilter
from util.tree import Tree
from model.model_filter import NumericalFilterModel, RegexFilterModel, StringFilterModel, DateTimeFilterModel

### [1] Fixtures for File Analyzer


@pytest.fixture(scope="module")
def fixture_testpath() -> Path:
    """Sample Path"""
    p_testpath = str(C.PATH_ROOT.joinpath("test_data", "test_path"))
    return p_testpath


@pytest.fixture(scope="module")
def fixture_path_testdata():
    """path to testdata"""
    return str(C.PATH_ROOT.joinpath("test_data"))


@pytest.fixture(scope="module")
def fixture_battest_path() -> str:
    """Sample Path"""
    p_testpath = str(C.PATH_ROOT.joinpath("test_data", "bat"))
    return p_testpath


@pytest.fixture(scope="module")
def fixture_testpath_withspace(fixture_testpath) -> Path:
    """Sample Path"""

    p_testpath = str(Path(fixture_testpath).joinpath("path with space"))
    return p_testpath


@pytest.fixture(scope="module")
def fixture_win_paths(fixture_testpath, fixture_testpath_withspace) -> list:
    """fixture contianing several path combinations for windows"""
    out = []
    out.append(fixture_testpath)
    out.append(os.path.join(fixture_testpath, "lorem_doc_root.md"))
    out.append(os.path.join(fixture_testpath, "file_doesnt_exist.txt"))
    out.append(fixture_testpath_withspace)
    out.append(os.path.join(fixture_testpath_withspace, "file doesnt exist.txt"))
    out.append(os.path.join(fixture_testpath_withspace, "test.txt"))
    out.append("..\\")
    return out


@pytest.fixture(scope="module")
def fixture_unc_paths(fixture_win_paths) -> list:
    """fixture contianing several path combinations for unc"""
    out = []
    for _win_path in fixture_win_paths:
        _unc = Utils.resolve_path(p=_win_path, check_exist=False, transform_rule="UNC")
        out.append(_unc)
    return out


@pytest.fixture(scope="module")
def fixture_paths(fixture_win_paths, fixture_unc_paths) -> list:
    """fixture contianing several path combinations for unc and win"""
    out = deepcopy(fixture_win_paths)
    out.extend(fixture_unc_paths)
    return out


@pytest.fixture
def fixture_test_paths(fixture_testpath, fixture_testpath_withspace):
    """returns testpaths"""
    _testpaths = [f'"{fixture_testpath_withspace}" -param1 xyz ', fixture_testpath]
    return _testpaths


@pytest.fixture
def fixture_test_invalid_paths():
    """returns testpaths"""
    _testpaths = ["C:\HUGO\ any_path -param1 xyz"]
    return _testpaths


@pytest.fixture
def fixture_testfile(fixture_testpath) -> Path:
    """sample tesfile"""
    f_testfile = Path(os.path.join(fixture_testpath, "subpath1", "file3.txt"))
    return f_testfile


@pytest.fixture
def fixture_testfile_md(fixture_testpath) -> Path:
    """sample markdown tesfile"""
    f_testfile = Path(os.path.join(fixture_testpath, "lorem_doc_root.md"))
    return f_testfile


@pytest.fixture
def fixture_testfile_dict(fixture_testpath):
    """getting a test file from the sample path"""
    f_sample = Path(fixture_testpath).joinpath("lorem_doc_root.md")
    text_lines_dict = Persistence.read_txt_file(f_sample, comment_marker=None, with_line_nums=True)
    return text_lines_dict


@pytest.fixture
def fixture_ruledict_path():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "path2"
    file_rule[C.RULE_NAME] = "testrule_path_path2"
    file_rule[C.RULE_FILE] = C.RULE_PATH
    return file_rule


@pytest.fixture
def fixture_ruledict_filename_lorem():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "lorem"
    file_rule[C.RULE_NAME] = "testrule_path_lorem"
    file_rule[C.RULE_FILE] = C.RULE_FILENAME
    return file_rule


@pytest.fixture
def fixture_ruledict_filename():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "test"
    file_rule[C.RULE_NAME] = "testrule_simple"
    return file_rule


@pytest.fixture
def fixture_ruledict_filename_all_rules():
    """check the apply rule for filename"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "file"
    file_rule[C.RULE_NAME] = "testrule_file"
    file_rule[C.RULE_FILE] = C.RULE_FILENAME
    file_rule[C.RULE_APPLY] = C.APPLY_ALL
    file_rule2 = deepcopy(file_rule)
    file_rule[C.RULE_RULE] = "_2"
    file_rule[C.RULE_NAME] = "testrule_2"
    return [file_rule, file_rule2]


@pytest.fixture
def fixture_ruledict_filename_absolute_path():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "lorem"  # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_lorem"  # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_ABSOLUTE_PATH
    return file_rule


@pytest.fixture
def fixture_ruledict_filename_filename():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "file1"  # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_file1"  # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_FILENAME
    return file_rule


@pytest.fixture
def fixture_ruledict_filename_path():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "subpath2"  # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_subpath2"  # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_PATH
    file_rule[C.RULE_APPLY] = C.APPLY_ALL
    return file_rule


@pytest.fixture
def fixture_ruledict_file_content():
    """getting a test file from the sample path"""
    file_rule = deepcopy(C.RULEDICT_FILENAME)
    file_rule[C.RULE_RULE] = "sum"  # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule_file_content_sum"  # rule name
    # the file rule type file_rule["RULE_FILE"] = RULE_[FILENAME|PATH|ABSOLUTE_PATH|FILE_CONTENT]
    file_rule[C.RULE_FILE] = C.RULE_FILE_CONTENT
    return file_rule


@pytest.fixture
def fixture_ruledict_file_content_all_rules(fixture_ruledict_file_content):
    """getting two rules linked with an apply all rule"""
    file_rule = deepcopy(fixture_ruledict_file_content)
    file_rule[C.RULE_RULE] = "sum"  # the search pattern, literal or regex
    file_rule[C.RULE_NAME] = "testrule1_file_content_sum"  # rule name
    file_rule[C.RULE_APPLY] = C.APPLY_ALL
    file_rule[C.RULE_FILE] = C.RULE_FILE_CONTENT
    file_rule2 = deepcopy(file_rule)
    file_rule2[C.RULE_RULE] = "crescit"  # the search pattern, literal or regex
    file_rule2[C.RULE_NAME] = "testrule2_file_content_sum"  # rule name
    return [file_rule, file_rule2]


@pytest.fixture(scope="module")
def fixture_set_vars_template() -> Path:
    """Sample Path to bat template"""
    f_vars_template = C.PATH_ROOT.joinpath("resources", "set_vars_template.bat")
    return f_vars_template


@pytest.fixture(scope="module")
def fixture_set_vars() -> Path:
    """Sample Path to created path"""
    f_vars_template = C.PATH_ROOT.joinpath("resources", "set_vars.bat")
    return f_vars_template


@pytest.fixture(scope="module")
def fixture_bat_testpath() -> Path:
    """Sample Path"""
    p_bat_testpath = str(C.PATH_ROOT.joinpath("test_data", "bat"))
    return p_bat_testpath


### [2] Fixtures for Config Env


@pytest.fixture
def fixture_config_env_testpath() -> Path:
    """Sample Path"""
    p_testpath = C.PATH_ROOT.joinpath("test_data", "test_config")
    return p_testpath


@pytest.fixture
def fixture_config_env_testconfig_template(fixture_config_env_testpath) -> Path:
    """Sample Path to configuration file"""
    return str(fixture_config_env_testpath.joinpath("config_env_template.json"))


@pytest.fixture
def fixture_sample_stocks_data(fixture_config_env_testpath) -> Path:
    """Sample Path to configuration file"""
    return str(fixture_config_env_testpath.joinpath("sample_stocks_data.txt"))


@pytest.fixture
def fixture_sample_config_json():
    """creates a sample json config file from existing one in test folder
    replacing absolute test paths, returns path to sample config json
    """

    return create_demo_config()


@pytest.fixture
def fixture_sample_enum() -> AbstractEnum:
    """getting a sample enum class"""

    class sample_enum(AbstractEnum):
        """sample enum"""

        TESTNAME1 = "testvalue1"
        TESTNAME2 = "testvalue2"
        TESTNAME3 = "testvalue3"

    return sample_enum


@pytest.fixture(scope="module")
def fixture_environment() -> Environment:
    """instanciate the Environment class"""
    _f_sample_config = create_demo_config()
    _environment = Environment(_f_sample_config)
    return _environment


@pytest.fixture(scope="module")
def fixture_bat_helper(fixture_environment) -> BatHelper:
    """instanciate the Bat Helper class"""
    _f_config = fixture_environment.config_env._f_config
    _bat_helper = BatHelper(_f_config)
    return _bat_helper


@pytest.fixture(scope="module")
def fixture_config_env() -> ConfigEnv:
    """instanciate the Environment Config class"""
    _f_config = create_demo_config()
    _config_env = ConfigEnv(_f_config)
    return _config_env


@pytest.fixture(scope="module")
def fixture_testfile_tablizer() -> str:
    """Sample Path to tablizer file"""
    f_test_file = str(C.PATH_ROOT.joinpath("test_data", "test_path", "testfile_for_table.txt"))
    return f_test_file


@pytest.fixture(scope="module")
def fixture_day_info_list() -> list:
    """Fixture for worklog list"""
    out = [
        "20240929-20241004 Test Info @part",  # testing upper lower case sensitive
        "20240901 MORE INFO",  # no additional metatag check for default value assignment
        "20240901 EVEN MORE INFO 1000-1800",  # testing two lines
        "20240919-20240923 20240927 @VACA ",  # Testing raw info without additional info only
        "20240501 :brain: :maple_leaf: Testing with icons @flex",  # testing icons and additional comments
        "20241001 @flex 1024-1235 1300-1730 1800-1830",  # testing flextime
        "20240213 @TOTALWORK40.45",  # testing totalwork
        "20241001 1024-1235 1300-1730 1800-1830",  # testing datetime calculation
        "20241001 1024-9999 1300-1730 1800-1830",  # testing invalid datetimes
        "20251001 1024-1100 1300-1730 1800-1830",  # testing date outside of range
        "20231211-20240103 TESTING CALENDAR 2023",
        "@HOME Mo Di Mi Fr",
        "@WORK Do 1000-1800",  # testing default duration on each work day
    ]
    return out


@pytest.fixture(scope="module")
def fixture_calendar2024_index() -> CalendarIndex:
    """fixture calendar index"""
    _year = 2024
    _cal_index = CalendarIndex(_year)
    return _cal_index


@pytest.fixture(scope="module")
def fixture_calendar2015_index() -> CalendarIndex:
    """fixtrue calendar index 2015 has 53 Calendar Weeks at start of year"""
    _year = 2015
    _cal_index = CalendarIndex(_year)
    return _cal_index


@pytest.fixture(scope="module")
def fixture_calendar_filter() -> CalendarFilter:
    """fixture calendar index 2015 has 53 Calendar Weeks at start of year"""
    _cal_filter = CalendarFilter()
    return _cal_filter


@pytest.fixture(scope="module")
def fixture_tree() -> Tree:
    """tree model
    [1] ROOT (has no parents)
     +---[2]
          +---[4]
          +---[5]
     +---[3]
          +---[6]
               +---[7]
               +---[8]
               +---[9]
    """

    _tree_dict = {
        1: {"parent": None, "value": "value 1"},
        2: {"parent": 1, "value": "value 3"},
        4: {"parent": 2, "value": "value 4"},
        5: {"parent": 2, "value": "value 5"},
        3: {"parent": 1, "value": "value 3"},
        6: {"parent": 3, "value": "value 6"},
        7: {"parent": 6, "value": "value 7"},
        8: {"parent": 6, "value": "value 8"},
        9: {"parent": 6, "value": "value 9"},
    }

    _tree = Tree()

    # use name to get a different field
    # my_tree.create_tree(tree,name_field="value")
    _tree.create_tree(_tree_dict)
    return _tree


@pytest.fixture(scope="module")
def fixture_numerical_filter() -> NumericalFilterModel:
    """returning a numerical filter"""
    _fields = {
        "key": "",
        "description": "",
        "group": ["group1"],
        "operator": "any",
        "include": "include",
        "operator_min": "gt",
        "value_min": 5,
        "value_max": 10,
        "operator_max": "lt",
    }
    return NumericalFilterModel(**_fields)
