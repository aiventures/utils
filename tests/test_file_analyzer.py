""" Testing the /util/file_analyzer module """

import pytest
from unittest.mock import MagicMock

import os
import sys

import logging

# from pathlib import Path
# from copy import deepcopy
from util import const_local
from util import constants as C
from util.file_analyzer import FileSysObjectInfo
from util.file_analyzer import FileAnalyzer
from util.file_analyzer import FileContentAnalyzer
from util.persistence import Persistence
from util.file_analyzer import FileSysObjectInfo

def test_setup(fixture_testfile,fixture_testpath,fixture_testfile_dict):
    """ Setup Method """
    assert fixture_testfile.is_file()
    assert fixture_testpath.is_dir()
    assert isinstance(fixture_testfile_dict,dict) and len(fixture_testfile_dict) > 0

def test_filesys_object_info(fixture_testpath):
    """ simple retrieval of all objects """
    _files_info = FileSysObjectInfo(fixture_testpath)
    _file_dict = _files_info.file_dict
    _files = _files_info.files
    _paths = _files_info.path_dict
    assert isinstance(_paths,dict) and len(_paths) > 0
    assert isinstance(_file_dict,dict) and len(_file_dict) > 0
    assert isinstance(_files,list) and len(_files) > 0

def test_file_anaylzer_simple(fixture_testpath,fixture_ruledict_filename):
    """ testing file analyzer with a simple rule """
    file_matcher = FileAnalyzer(fixture_testpath)    
    file_matcher.add_rule(fixture_ruledict_filename)
    # assert we have one rule
    rules = file_matcher._get_matcher(C.RULE_ABSOLUTE_PATH).rules
    assert len(rules) == 1
    # find objects
    file_objects = file_matcher.find_file_objects()
    assert isinstance(file_objects,dict) and len(file_objects) > 0

def test_file_anaylzer_filetext(fixture_testfile_md,fixture_ruledict_file_content):
    """ testing file analyzer with a simple rule """
    file_analyzer = FileContentAnalyzer()
    file_analyzer.add_rule(fixture_ruledict_file_content)
    rules = file_analyzer._get_matcher(C.RULE_FILE_CONTENT).rules
    # assert we have one rulej
    assert len(rules) == 1
    # find objects
    results = file_analyzer.find_file_content(fixture_testfile_md)
    # 3 hits in this file
    assert isinstance(results,dict) and len(results) == 3
    pass

def test_file_anaylzer_filetext_all_rules(fixture_testfile_md,fixture_ruledict_file_content_all_rules):
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






