"""Test Setup"""

import os
from copy import deepcopy
from datetime import datetime as DateTime
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, RootModel
import pytest

from setup_utils.demo_config import create_demo_config
from model.model_filter import NumericalFilterModel, RegexFilterModel, StringFilterModel, FilterSetModel
from model.model_persistence import ParamsFind
from cli.bootstrap_env import TEST_PATH
from util import constants as C
from util.abstract_enum import AbstractEnum
from util.bat_helper import BatHelper
from util.calendar_index import CalendarIndex
from util.config_env import ConfigEnv, Environment
from util.filter import CalendarFilterModel, CalendarFilterWrapper, NumericalFilter, RegexFilter, StringFilter
from util.filter_set import FilterSet
from util.persistence import Persistence
from util.tree import Tree
from util.utils import Utils

### [1] Fixtures for File Analyzer


@pytest.fixture(scope="module")
def fixture_testpath() -> Path:
    """Sample Path"""
    p_testpath = Path(os.path.join(TEST_PATH, "test_data", "test_path"))
    return p_testpath


@pytest.fixture(scope="module")
def fixture_path_testdata() -> str:
    """path to testdata"""
    return os.path.join(TEST_PATH, "test_data")


@pytest.fixture(scope="module")
def fixture_battest_path() -> str:
    """Sample Path"""
    p_testpath = os.path.join(TEST_PATH, "test_data", "bat")
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
    out.append(str(fixture_testpath))
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
    f_vars_template = Path(TEST_PATH).joinpath("resources", "set_vars_template.bat")
    return f_vars_template


@pytest.fixture(scope="module")
def fixture_set_vars() -> Path:
    """Sample Path to created path"""
    f_vars_template = Path(TEST_PATH).joinpath("resources", "set_vars.bat")
    return f_vars_template


@pytest.fixture(scope="module")
def fixture_bat_testpath() -> Path:
    """Sample Path"""
    p_bat_testpath = Path(TEST_PATH).joinpath("test_data", "bat")
    return p_bat_testpath


### [2] Fixtures for Config Env


@pytest.fixture
def fixture_config_env_testpath() -> Path:
    """Sample Path"""
    p_testpath = Path(os.path.join(TEST_PATH, "test_data", "test_config"))
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
    f_test_file = os.path.join(TEST_PATH, "test_data", "test_path", "testfile_for_table.txt")
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


# @pytest.fixture(scope="module")
# def fixture_calendar_filter() -> CalendarFilter:
#     """fixture calendar index 2015 has 53 Calendar Weeks at start of year"""
#     _cal_filter = CalendarFilter()
#     return _cal_filter


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
                    +---[10]
                    +---[11]
               +---[9]
    """

    _tree_dict = {
        1: {"parent_id": None, "value": "value 1", "object": "OBJ1"},
        2: {"parent_id": 1, "value": "value 2", "object": "OBJ2"},
        4: {"parent_id": 2, "value": "value 4", "object": "OBJ4"},
        5: {"parent_id": 2, "value": "value 5", "object": "OBJ5"},
        3: {"parent_id": 1, "value": "value 3", "object": "OBJ3"},
        6: {"parent_id": 3, "value": "value 6", "object": "OBJ6"},
        7: {"parent_id": 6, "value": "value 7", "object": "OBJ7"},
        8: {"parent_id": 6, "value": "value 8", "object": "OBJ8"},
        9: {"parent_id": 6, "value": "value 9", "object": "OBJ9"},
        10: {"parent_id": 8, "value": "value 10", "object": "OBJ10"},
        11: {"parent_id": 8, "value": "value 11", "object": "OBJ11"},
    }

    _tree = Tree()

    # use name to get a different field
    # my_tree.create_tree(tree,name_field="value")
    # _tree.create_tree(_tree_dict)
    _tree.create_tree(_tree_dict)
    return _tree


@pytest.fixture(scope="module")
def fixture_numerical_filter() -> NumericalFilterModel:
    """returning a numerical filter"""
    _fields = {
        "key": "num filter key",
        "description": "description",
        "groups": ["group1"],
        "operator": "any",
        "include": "include",
        "operator_min": "gt",
        "value_min": 5,
        "value_max": 10,
        "operator_max": "lt",
    }
    return NumericalFilterModel(**_fields)


@pytest.fixture(scope="function")
def fixture_numerical_filter_date() -> NumericalFilterModel:
    """returning a numerical filter"""
    _fields = {
        "key": "num filter date key",
        "description": "description",
        "groups": ["group1"],
        "operator": "any",
        "include": "include",
        "operator_min": "gt",
        "value_min": DateTime(2024, 12, 5),
        "value_max": DateTime(2024, 12, 10),
        "operator_max": "lt",
    }
    return NumericalFilterModel(**_fields)


@pytest.fixture(scope="function")
def fixture_regex_filter() -> RegexFilterModel:
    """returning a regex filter"""
    _fields = {
        "key": "num filter regex key",
        "description": "description",
        "groups": ["group1", "group2"],
        "operator": "any",
        "include": "include",
        "regex": "hu(.+)go",
    }
    return RegexFilterModel(**_fields)


@pytest.fixture(scope="function")
def fixture_string_filter() -> StringFilterModel:
    """returning a string filter"""
    _fields = {
        "key": "num filter string key",
        "description": "description",
        "groups": "group2",
        "operator": "any",
        "string_operator": "any",
        "filter_strings": ["test", "another"],
        "match": "contains",
    }
    return StringFilterModel(**_fields)


@pytest.fixture(scope="function")
def fixture_calendar_filter() -> CalendarFilterModel:
    """returning a calendar filter"""
    _fields = {
        "description": "description",
        "operator": "all",
        "groups": "group1",
        "include": "include",
        "filter_str": "20241210-20241220",
        "date_list": None,
        "calendar_filter": None,
    }
    return CalendarFilterModel(**_fields)


@pytest.fixture(scope="function")
def fixture_filter_set(
    fixture_numerical_filter,
    fixture_numerical_filter_date,
    fixture_regex_filter,
    fixture_string_filter,
    fixture_calendar_filter,
):
    """testing filter set"""
    _filter_list = [
        NumericalFilter(fixture_numerical_filter),
        NumericalFilter(fixture_numerical_filter_date),
        RegexFilter(fixture_regex_filter),
        StringFilter(fixture_string_filter),
        CalendarFilterWrapper(fixture_calendar_filter),
    ]
    # _filter_list = [
    #     NumericalFilter(fixture_numerical_filter_date),
    # ]

    _filterset_model = FilterSetModel(filter_list=_filter_list)
    _filter_set = FilterSet(obj_filter=_filterset_model)
    return _filter_set


@pytest.fixture(scope="module")
def fixture_params_find(fixture_testpath) -> ParamsFind:
    """findall params"""
    _params = {
        "p_root_paths": str(fixture_testpath),
        "include_abspaths": None,
        "exclude_abspaths": None,
        "include_files": None,
        "exclude_files": None,
        "include_paths": None,
        "exclude_paths": None,
        "paths": True,
        "files": True,
        "as_dict": True,
        "root_path_only": False,
        "match_all": False,
        "ignore_case": True,
        "show_progress": False,
        "max_path_depth": None,
        "max_num_files": None,
        "max_num_dirs": None,
        "paths_only": False,
        "add_empty_paths": True,
    }
    return ParamsFind(**_params)


@pytest.fixture(scope="module")
def fixture_str_filter_match_va_x() -> StringFilter:
    """fixture atomic string filter"""
    _s_model_matches = StringFilterModel(
        key="filter_str_matches_va_x",
        description="str matches va AND x",
        groups=["matches"],
        filter_strings=["va", "x"],
        match="contains",
        string_operator="all",
        include="include",
    )
    _str_filter_match_va_x = StringFilter(_s_model_matches)
    return _str_filter_match_va_x


@pytest.fixture(scope="module")
def fixture_regex_filter_match_v_begin() -> RegexFilter:
    """fixture atomic regex filter"""
    _regex_model_matches_v = RegexFilterModel(
        key="regex_str_matches_v",
        description="str matches v at start",
        groups=["matches"],
        include="include",
        regex="^v",
    )
    _regex_filter_match_v_begin = RegexFilter(_regex_model_matches_v)

    return _regex_filter_match_v_begin


@pytest.fixture(scope="module")
def fixture_regex_filter_match_z_begin() -> RegexFilter:
    """fixture atomic regex filter"""
    _regex_model_matches_z = RegexFilterModel(
        key="regex_str_matches_z",
        description="str matches z at start",
        groups=["matches"],
        include="include",
        operator="all",
        regex="^z",
    )
    _regex_filter_match_v_begin = RegexFilter(_regex_model_matches_z)

    return _regex_filter_match_v_begin


@pytest.fixture(scope="module")
def fixture_filter_set_match_va_x_begin(fixture_str_filter_match_va_x, fixture_regex_filter_match_v_begin) -> FilterSet:
    """fixture filter set"""
    _filter_list = [fixture_str_filter_match_va_x, fixture_regex_filter_match_v_begin]
    return FilterSet(FilterSetModel(filter_list=_filter_list))


@pytest.fixture(scope="module")
def fixture_filter_set_match_va_z_begin(fixture_str_filter_match_va_x, fixture_regex_filter_match_z_begin) -> FilterSet:
    """fixture filter set"""
    _filter_list = [fixture_str_filter_match_va_x, fixture_regex_filter_match_z_begin]
    return FilterSet(FilterSetModel(filter_list=_filter_list))


@pytest.fixture(scope="module")
def fixture_test_dict() -> dict:
    """fixture filter set"""
    test_struc = """
        { "k1":"value1",
          "test_key":500,
          "k2":{"k2.1":5,
                "k2.2":"v2.2",
                "k2.3":["l1","test value","l3",{"dict_inner":["a","b","c"]}]
                }
        }
    """
    return test_struc


@pytest.fixture(scope="module")
def fixture_celltype_dict() -> dict:
    """tree dict"""

    _celltype_dict = {
        1: {"parent_id": None, "value": 1.3, "object": "OBJ1"},
        2: {"parent_id": 1, "value": 2.7, "object": "OBJ2"},
        3: {"parent_id": 2, "value": None, "object": "OBJ4"},
    }
    return _celltype_dict


@pytest.fixture(scope="module")
def fixture_celltype_basemodel() -> Dict[int, BaseModel]:
    """tree dict"""
    out = {}

    class CellTypeBaseModelTest(BaseModel):
        """sample class"""

        parent_id: Optional[object] = None
        value: Optional[object] = None
        obj: Optional[object] = None

    out[1] = CellTypeBaseModelTest(parent_id=None, value=1.3, obj="OBJ1")
    out[2] = CellTypeBaseModelTest(parent_id=1, value=2.7, obj="OBJ2")
    out[3] = CellTypeBaseModelTest(parent_id=2, value=None, obj="OBJ4")

    return out


@pytest.fixture(scope="module")
def fixture_celltype_rootmodel() -> Dict[int, RootModel]:
    """tree dict"""
    out = {}

    class CellTypeRootModelTest(RootModel):
        """sample class"""

        root: Dict[str, object] = {}

    out[1] = CellTypeRootModelTest({"parent_id": None, "value": 1.3, "object": "OBJ1"})
    out[2] = CellTypeRootModelTest({"parent_id": 1, "value": 2.7, "object": "OBJ2"})
    out[3] = CellTypeRootModelTest({"parent_id": 2, "value": None, "object": "OBJ4"})

    return out


@pytest.fixture(scope="module")
def fixture_test_tree() -> Dict[int, dict]:
    """test tree
    [1] ROOT (has no parents)
         +---[2]
              +---[4]
              +---[5]
         +---[3]
              +---[6]
                   +---[7]
                   +---[8]
                        +---[10]
                        +---[11]
                   +---[9]
    """

    _tree_dict = {
        1: {"parent": None, "value": 1, "object": "OBJ1"},
        2: {"parent": 1, "value": 2, "object": "OBJ2"},
        4: {"parent": 2, "value": 3, "object": "OBJ4"},
        5: {"parent": 2, "value": 5, "object": "OBJ5"},
        3: {"parent": 1, "value": 5, "object": "OBJ3"},
        6: {"parent": 3, "value": 6, "object": "OBJ6"},
        7: {"parent": 6, "value": 7, "object": "OBJ7"},
        8: {"parent": 6, "value": 8, "object": "OBJ8"},
        9: {"parent": 6, "value": 9, "object": "OBJ9"},
        10: {"parent": 8, "value": 10, "object": "OBJ10"},
        11: {"parent": 8, "value": 11, "object": "OBJ11"},
    }
    return _tree_dict


# https://stackoverflow.com/questions/53148623/is-there-a-way-to-nest-fixture-parametization-in-pytest
# @pytest.fixture(params=generated_list())
# def fn1(request):
#     return request.param
# @pytest.fixture(params=generates_list_2(fn1))
# def fn2(request, fn1):
#     return request.param
# def test_fn(fn2):
#     assert fn2 == 0
