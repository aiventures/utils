""" Testing the /util/file_analyzer module """

import pytest
from unittest.mock import MagicMock

import os
import sys
from copy import deepcopy
import logging

# from pathlib import Path
# from copy import deepcopy
from util import const_local
from pathlib import Path
from util import constants as C
from util.file_analyzer import FileSysObjectInfo
from util.file_analyzer import FileAnalyzer
from util.file_analyzer import FileContentAnalyzer
from util.persistence import Persistence
from util.file_analyzer import FileSysObjectInfo
import logging
logger = logging.getLogger(__name__)

def test_setup(fixture_testfile,fixture_testpath,fixture_testfile_dict):
    """ Setup Method """
    assert Path(fixture_testfile).is_file()
    assert Path(fixture_testpath).is_dir()
    assert isinstance(fixture_testfile_dict,dict) and len(fixture_testfile_dict) > 0

def test_file_analyzer_simple(fixture_testpath,fixture_ruledict_filename):
    """ testing file analyzer with a simple rule """
    file_matcher = FileAnalyzer(fixture_testpath)
    file_matcher.add_rule(fixture_ruledict_filename)
    # assert we have one rule
    rules = file_matcher._get_matcher(C.RULE_ABSOLUTE_PATH).rules
    assert len(rules) == 1
    # find objects
    file_objects = file_matcher.find_file_objects()
    assert isinstance(file_objects,dict) and len(file_objects) > 0

def test_file_analyzer_all_rules(fixture_testpath,fixture_ruledict_filename_all_rules):
    """ testing file analyzer with an apply_all rules list """
    file_matcher = FileAnalyzer(fixture_testpath)
    # tmp check the all rules section
    file_matcher.add_rules(fixture_ruledict_filename_all_rules)
    # assert we have one rule
    rules = file_matcher._get_matcher(C.RULE_FILENAME).rules
    assert len(rules) == 2
    # find objects
    file_objects = file_matcher.find_file_objects()
    assert isinstance(file_objects,dict) and len(file_objects) == 1

def test_file_analyzer_all_diifferent_rule_types(fixture_testpath,fixture_ruledict_filename_path,fixture_ruledict_filename_lorem):
    """ testing file analyzer with different file objects """
    _rule_lorem = deepcopy(fixture_ruledict_filename_lorem)
    _rule_lorem[C.RULE_APPLY] = C.APPLY_ALL
    file_matcher = FileAnalyzer(fixture_testpath)
    # # tmp check the all rules section
    file_matcher.add_rules([_rule_lorem,fixture_ruledict_filename_path])
    # assert we have two rules
    _rules = file_matcher.rules
    assert len(_rules) == 2
    # find objects
    file_objects = file_matcher.find_file_objects()
    assert isinstance(file_objects,dict) and len(file_objects) == 1

def test_find_all_diifferent_rule_types(fixture_testpath,fixture_ruledict_filename_path,fixture_ruledict_filename_lorem):
    """ testing find with different file objects """
    _rule_lorem = deepcopy(fixture_ruledict_filename_lorem)
    _rule_lorem[C.RULE_APPLY] = C.APPLY_ALL
    file_matcher = FileAnalyzer(fixture_testpath)
    # # tmp check the all rules section
    file_matcher.add_rules([_rule_lorem,fixture_ruledict_filename_path])
    # assert we have two rules
    _rules = file_matcher.rules
    assert len(_rules) == 2
    # find objects
    file_objects = file_matcher.find()
    assert isinstance(file_objects,list) and len(file_objects) == 1
    # assert we have four occurences of the find markers
    assert file_objects[0].count("#ALL") == 4
    # find object but as dictionary return
    file_objects = file_matcher.find(as_dict=True)
    assert isinstance(file_objects,dict) and len(file_objects) == 1


def test_file_analyzer_filetext(fixture_testfile_md,fixture_ruledict_file_content):
    """ testing file analyzer with a simple rule """
    file_analyzer = FileContentAnalyzer()
    file_analyzer.add_rule(fixture_ruledict_file_content)
    rules = file_analyzer._get_matcher(C.RULE_FILE_CONTENT).rules
    # assert we have one rule
    assert len(rules) == 1
    # find objects
    results = file_analyzer.find_file_content(fixture_testfile_md)
    # 3 hits in this file
    assert isinstance(results,dict) and len(results) == 3
    pass

def test_file_analyzer_filetext_all_rules(fixture_testfile_md,fixture_ruledict_file_content_all_rules):
    """ testing file analyzer with two all rules """
    file_analyzer = FileContentAnalyzer()
    file_analyzer.add_rules(fixture_ruledict_file_content_all_rules)
    rules = file_analyzer._get_matcher(C.RULE_FILE_CONTENT).rules
    # assert we have one rulej
    assert len(rules) == 2
    # find objects
    results = file_analyzer.find_file_content(fixture_testfile_md)
    # 3 hits for sum but only 1 when using all
    assert isinstance(results,dict) and len(results) == 1
    # deactivate all apply_all logic
    results = file_analyzer.find_file_content(fixture_testfile_md,filter_result_set=False)
    assert isinstance(results,dict) and len(results) == 3
    pass

def test_find_filetext_all_rules(fixture_testfile_md,fixture_ruledict_file_content_all_rules):
    """ testing find text of file analyzer with two all rules """
    file_analyzer = FileContentAnalyzer()
    file_analyzer.add_rules(fixture_ruledict_file_content_all_rules)
    rules = file_analyzer._get_matcher(C.RULE_FILE_CONTENT).rules
    # assert we have one rulej
    assert len(rules) == 2
    # find objects
    results = file_analyzer.find(fixture_testfile_md)
    # 3 hits for sum but only 1 when using all
    assert isinstance(results,dict) and len(results) == 1
    # assert we have four occurences of the find markers
    _result_line = results[6][C.FORMATTED]
    assert _result_line.count("#ANY") == 4
    assert "sum"  in _result_line and "crescit" in _result_line

def test_filesys_object_info(fixture_testpath):
    """ simple retrieval of all objects """
    _files_info = FileSysObjectInfo(fixture_testpath)
    _file_dict = _files_info.file_dict
    _files = _files_info.files
    _paths = _files_info.path_dict
    assert isinstance(_paths,dict) and len(_paths) > 0
    assert isinstance(_file_dict,dict) and len(_file_dict) > 0
    assert isinstance(_files,list) and len(_files) > 0
