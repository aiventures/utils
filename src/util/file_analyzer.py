"""Analyzing Files and Paths"""

import logging
import os
import sys

# import re
from copy import deepcopy
from pathlib import Path

from util import constants as C
# from util.colors import col
from util.persistence import Persistence
from util.string_matcher import FileMatcher, StringMatcher

# from util.constants import APPLY_ALL
# from datetime import datetime as DateTime
# import json
# when doing tests add this to reference python path
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# from util.const_local import P_TOOLS


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class FileSysObjectInfo:
    """class to read os file and path info into a dictionary"""

    def __init__(self, root_paths: list | str = None) -> None:
        _root_paths = []
        self._root_paths = []
        self._filter_matcher = StringMatcher()
        if root_paths is None:
            _root_paths = [os.getcwd()]
            logger.debug(f"[FileInfo] No files addedAdding f{os.getcwd()} as root path")
        elif isinstance(root_paths, str):
            _root_paths = [root_paths]
        elif isinstance(root_paths, Path):
            _root_paths = [str(root_paths)]
        for _root_path in _root_paths:
            if not os.path.isdir(_root_path):
                logger.warning(f"[FileInfo] [{_root_path}] is not a valid path, skipping root path")
                continue
            self._root_paths.append(_root_path)
        self._files = {}
        self._paths = {}

        self._read_file_objects()

    def _read_file_objects(self) -> None:
        """get a list of all file system objects"""
        self._files = {}
        self._paths = {}
        for _root_path in self._root_paths:
            _paths = []
            logger.info(f"[FileInfo] Adding file system objects from [{_root_path}]")
            for subpath, _, files in os.walk(_root_path):
                _path = Path(subpath).absolute()
                _files_absolute = [_path.joinpath(f) for f in files]
                self._files[subpath] = {C.FILES_ABSOLUTE: _files_absolute, C.FILES: files}
                _paths.append(subpath)
            self._paths[_root_path] = _paths
        logger.debug(f"[FileInfo] Read [{self._files}] Files, [{self._paths }] Paths")

    @property
    def path_dict(self) -> dict:
        """returns paths by root in a dict"""
        return self._paths

    @property
    def paths(self) -> list:
        """get lsit of found paths / without root paths"""
        out_list = []
        _ = [out_list.extend(paths) for paths in list(self._paths.values())]
        return out_list

    @property
    def file_dict(self) -> dict:
        """returns dict of files"""
        logger.debug(f"[FileInfo] Returning files dict covering [{len(self._files)}] Directories")
        return self._files

    @property
    def files(self) -> list:
        """returns absolute Paths of all files found"""
        _file_list = []
        for p, p_info in self._files.items():
            _files = p_info.get(C.FILES_ABSOLUTE, [])
            _ = [_file_list.append(str(f)) for f in _files]
        logger.debug(f"[FileInfo] Returning [{len(_file_list)}] Files")
        return _file_list


class FileAnalyzer:
    """search for file names and file contents"""

    def __init__(
        self,
        root_paths: list | str = None,
        apply: str = C.APPLY_ALL,
        by_line_default: bool = False,
        by_rule: bool = True,
    ) -> None:
        """File Info Object Constructor."""
        self._file_info = FileSysObjectInfo(root_paths)
        # separate matchers for each of the file types
        self._rule_dicts = {
            C.RULE_FILENAME: StringMatcher(apply_default=apply),
            C.RULE_PATH: StringMatcher(apply_default=apply),
            C.RULE_ABSOLUTE_PATH: StringMatcher(apply_default=apply),
            C.RULE_FILE_CONTENT: FileMatcher(apply=apply, by_line_default=by_line_default),
        }
        self._rule_dict = StringMatcher(apply_default=apply)
        self._by_rule = by_rule

    @property
    def rules(
        self,
    ) -> dict:
        """return as rules by rule matcher or as list"""
        _out = {}
        for _, _matcher in self._rule_dicts.items():
            _out.update(deepcopy(_matcher._rules))
        return _out

    def add_rule(self, rule: dict) -> None:
        """Adding Filename Rule"""
        _new_rule = deepcopy(C.RULEDICT_FILENAME)
        # copy over default values / use default values
        for k, default_value in _new_rule.items():
            _new_rule[k] = rule.get(k, default_value)
        # according to rule add rule to the appropriate matcher
        _rule_name = _new_rule.get(C.RULE_NAME)
        _rule_type = _new_rule.get(C.RULE_FILE)
        logger.debug(f"[FileAnalyzer] Adding rule [{_rule_name}], type [{_rule_type}]")
        try:
            _rule_matcher = self._rule_dicts[_rule_type]
            _rule_matcher.add_rule(_new_rule)
        except KeyError:
            logger.error(
                f"[FileAnalyzer] Can't Identify appropriate matcher, rule [{_rule_name}], got type [{_rule_type}]"
            )
        pass

    def _get_matcher(self, rule: str) -> StringMatcher | FileMatcher:
        """returns the matcher, preserves the object type"""
        return self._rule_dicts.get(rule)

    def add_rules(self, rules: list) -> None:
        """Adding Filename Rules (list of dicts of type RULEDICT_FILENAME )"""
        for _rule in rules:
            self.add_rule(_rule)

    def _match_files(self, find_dict: dict, matcher: str, filter_result_set: bool = True) -> dict:
        """Loop over all files and try to match objects
        filter_result_set ist a flag whether apply _all ffilters should be treated as one set
        """
        _file_object_matches = {}
        _rule_matcher = self._get_matcher(matcher)
        for _file_object_key, _file_object in find_dict.items():
            search_result = _rule_matcher.find_all(
                s=_file_object, by_rule=self._by_rule, filter_result_set=filter_result_set
            )
            # check if there are results ar all
            if len(search_result) > 0:
                _file_object_matches[_file_object_key] = search_result
        logger.info(f"[FileAnalyzer] Matcher [{matcher}], found [{len(_file_object_matches)}/{len(find_dict)}] objects")

        return _file_object_matches

    @staticmethod
    def _add_path_matches(file_objects: dict, path_objects: dict):
        """adding the path matches to search result"""

        for _path_object, _path_object_info in path_objects.items():
            for _file, _file_info in file_objects.items():
                if str(_path_object) in str(_file):
                    logger.debug(
                        f"[FileAnalyzer] Adding Path Matching Infos {list(_path_object_info.keys())} to [{_file}]"
                    )
                    _file_info.update(_path_object_info)

    @staticmethod
    def _filter_result_set(file_objects: dict, all_rules: list) -> None:
        """filters rule set: only items with all_rules will pass"""

        if len(all_rules) == 0:
            return file_objects

        _num_all_rules = len(all_rules)
        _num_file_objects = len(file_objects)

        _delete_keys = []
        for _fileobject_key, _file_object_info in file_objects.items():
            # _found_all_keys
            _object_keys = list(_file_object_info.keys())
            _found_keys = list(filter(lambda k: k in all_rules, _object_keys))
            if len(_found_keys) == _num_all_rules:
                continue
            _delete_keys.append(_fileobject_key)
        # now delete the all_key in the set
        # clean up
        for _delete_key in _delete_keys:
            _file_object_info = file_objects[_delete_key]
            for _rule in all_rules:
                _ = _file_object_info.pop(_rule, None)
            # length of 1 since there is the all_rules info
            if len(_file_object_info) <= 1:
                _ = file_objects.pop(_delete_key, None)

        logger.debug(
            f"[FileAnalyzer] File Objects after/before apply_all [{len(file_objects)}/{_num_file_objects}], deleted [{_delete_keys}] keys"
        )
        return file_objects

    def find_file_objects(self, filter_result_set: bool = True) -> dict:
        """get the file names
        filter_result_set is flag to treat apply_all as a joint rule set
        """
        _file_objects = {}
        _fi = self._file_info
        _all_rules = []

        # treat path objects separately
        _rule_matcher_path = self._get_matcher(C.RULE_PATH)
        _paths = _fi.paths
        _find_dict_path = dict(zip(_paths, _paths))
        _path_matches = self._match_files(_find_dict_path, C.RULE_PATH, filter_result_set=False)

        # iterate over all rule matchers
        for _rule in self._rule_dicts.keys():
            _rule_matcher = self._get_matcher(_rule)
            if not isinstance(_rule_matcher, StringMatcher):
                continue
            if _rule == C.RULE_FILE_CONTENT:
                continue
            _all_rules.extend(_rule_matcher._all_rules)
            if _rule == C.RULE_FILENAME:
                _filenames = [Path(f).name for f in _fi.files]
                _find_dict = dict(zip(_fi.files, _filenames))
            elif _rule == C.RULE_ABSOLUTE_PATH:
                _find_dict = dict(zip(_fi.files, _fi.files))
            elif _rule == C.RULE_PATH:
                continue
                # TODO CHANGE TO PATHS
            else:
                logger.warning(f"[FileAnalyzer] Invalid File Object Rule: [{_rule}]")
                continue
            _file_object_matches = self._match_files(_find_dict, _rule, filter_result_set=False)
            if len(_file_object_matches) > 0:
                FileAnalyzer._add_path_matches(_file_object_matches, _path_matches)
                _file_objects.update(_file_object_matches)
        # Apply All Filters
        if filter_result_set:
            FileAnalyzer._filter_result_set(_file_objects, _all_rules)
        return _file_objects

    def find(
        self,
        filter_result_set: bool = True,
        any_before: str = C.RESULT_ANY_PREFIX_BEFORE,
        any_after: str = C.RESULT_ANY_PREFIX_AFTER,
        all_before: str = C.RESULT_ALL_PREFIX_BEFORE,
        all_after: str = C.RESULT_ALL_PREFIX_AFTER,
        skip_prefix_handling: bool = False,
        as_dict: bool = False,
    ) -> list | dict:
        """returns the result occurence list as string, placeholders for
        search results (also for any|all search types ) can be adapted
        Can also be skipped using skip_prefix_handling
        as_dict determines whether a result dictionary will be returned
        """
        if as_dict is True:
            results = {}
        else:
            results = []

        _results = self.find_file_objects(filter_result_set=filter_result_set)
        logger.debug(f"[FileAnalyzer] Find/format items for [{len(_results)}] search results")
        for _out_result, _match_infos in _results.items():
            _rules = list(_match_infos.keys())
            if skip_prefix_handling:
                results.append(_out_result)
                continue
            s_out = str(_out_result)

            for _rule in _rules:
                _match_info = _match_infos[_rule]
                _apply_rule = _match_info.get(C.RULE_APPLY, C.APPLY_ANY)
                if _apply_rule == C.APPLY_ALL:
                    _s_before = all_before
                    _s_after = all_after
                else:
                    _s_before = any_before
                    _s_after = any_after

                for result in _match_info.get(C.RULE_RESULTS, []):
                    s_new = f"{_s_before}{result}{_s_after}"
                    s_out = s_out.replace(result, s_new)
            if as_dict:
                results[_out_result] = {C.PATH: _out_result, C.OUTPUT: _out_result, C.FORMATTED: s_out, C.RULES: _rules}
            else:
                results.append(s_out)

        return results


# todo also check for content with transformed yaml, json and csv
class FileContentAnalyzer(FileAnalyzer):
    """Adding Features to read / filter file contents"""

    def __init__(
        self,
        root_paths: list | str = None,
        apply: str = C.APPLY_ALL,
        by_line_default: bool = False,
        by_rule: bool = True,
    ) -> None:
        """Constructor"""
        super().__init__(root_paths, apply, by_line_default, by_rule)
        # params to read out a text file
        self._encoding = "utf-8"
        self._comment_marker = None
        self._skip_blank_lines = False
        self._strip_lines = True
        self._with_line_nums = False
        self._content_lines = {}

    def _postprocess_file_content(self, content_dict: dict) -> dict | list:
        """reformat found file content according to settings"""
        return []

    def _find_file_content_txt(self, f: str, filter_result_set: bool = True) -> dict:
        """read a text type file line by line
        filter_result_set: Check the all rules
        """
        _results = {}
        _rules_matcher = self._get_matcher(C.RULE_FILE_CONTENT)
        _rules = _rules_matcher.rules
        _all_rules = _rules_matcher._all_rules
        # content lines
        _content_lines = Persistence.read_txt_file(
            f,
            encoding=self._encoding,
            comment_marker=None,
            skip_blank_lines=False,
            strip_lines=False,
            with_line_nums=True,
        )
        self._content_lines = _content_lines
        # content all in one for searching content in file instead of lines
        _content_file = "\n".join(list(_content_lines.values()))

        # get all file rules
        _all_rules_set = True
        for _rule, _rule_dict in _rules.items():
            _find_by_line = _rule_dict.get(C.RULE_FIND_BY_LINE, True)
            if _find_by_line is False:
                _content_dict = {0: _content_file}
            else:
                _content_dict = _content_lines
            for _line_num, _content in _content_dict.items():
                _result_matches = []
                # try to find matches using rule
                _matches = _rules_matcher.find(_content, _rule)
                if len(_matches) > 0:
                    # get previous matching results
                    _results_by_line = _results.get(_line_num, {})
                    # add existing result
                    _results_by_line[_rule] = _matches
                    _results[_line_num] = _results_by_line
                # no matches, check whether an all_rules set needs to be applied
                else:
                    if _rule in _all_rules:
                        _all_rules_set = False

        # do process the all rules set
        if filter_result_set is True and _all_rules_set is False:
            _drop_lines = []
            for line, _results_by_line in _results.items():
                # check if all keys are present
                _result_keys = list(_results_by_line.keys())
                all_keys_present = [all_rule_key in _result_keys for all_rule_key in _all_rules]
                if all(all_keys_present):
                    continue
                # at least one all rule is not matching, skip results
                for _all_rule in _all_rules:
                    _ = _results_by_line.pop(_all_rule, None)
                # if the dict is empty, clean itup later
                if len(_results_by_line) == 0:
                    _drop_lines.append(line)
            # clean up empty lines
            for _drop_line in _drop_lines:
                _results.pop(_drop_line)
                pass

        return _results

    def find_file_content(self, f: str, filter_result_set: bool = True) -> dict:
        """find occurences in file
        filter_result_set: Check the all rules
        """
        # use the file content rule
        _results = self._find_file_content_txt(f, filter_result_set)
        logger.info(f"[FileContentAnalyzer] File [{f}], found [{len(_results)}] hits")
        return _results

    def find(
        self,
        f: str = None,
        filter_result_set: bool = True,
        any_before: str = C.RESULT_ANY_PREFIX_BEFORE,
        any_after: str = C.RESULT_ANY_PREFIX_AFTER,
        all_before: str = C.RESULT_ALL_PREFIX_BEFORE,
        all_after: str = C.RESULT_ALL_PREFIX_AFTER,
        skip_prefix_handling: bool = False,
    ) -> dict:
        """returns the result occurence list as string, placeholders for
        search results (also for any|all search types ) can be adapted
        Can also be skipped using skip_prefix_handling
        as_dict determines whether a result dictionary will be returned
        """

        results = {}
        _results = self.find_file_content(f=f, filter_result_set=filter_result_set)
        for _line_num, _match_infos in _results.items():
            _result = {}
            _rules = list(_match_infos.keys())

            _result[C.LINE] = _line_num
            s_out = self._content_lines.get(_line_num, "")
            if skip_prefix_handling:
                results[_line_num] = s_out
                continue

            # for _rule in rules:, _match_infos in _match_infos.items():
            for _rule in _rules:
                # , _match_infos in _match_infos.items():
                _match_list = _match_infos[_rule]

                # right now we do not have this in the text file search
                _apply_rule = C.APPLY_ANY
                if _apply_rule == C.APPLY_ALL:
                    _s_before = all_before
                    _s_after = all_after
                else:
                    _s_before = any_before
                    _s_after = any_after

                for _match in _match_list:
                    s_new = f"{_s_before}{_match}{_s_after}"
                    s_out = s_out.replace(_match, s_new)

            _result[C.PATH] = str(f)
            _result[C.OUTPUT] = s_out
            _result[C.FORMATTED] = s_out
            _result[C.RULES] = _rules
            _result[C.LINE] = _line_num
            results[_line_num] = _result

        return results


def main():
    """run local in test mode"""
    # text_lines_dict = get_test_file_dict()
    # files_info =  get_file_objects()
    # test_file_matcher()
    pass


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
