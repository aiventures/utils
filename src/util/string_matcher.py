"""module to filter / match strings"""

import logging
import os
import re
import sys
import uuid
from copy import deepcopy
from pathlib import Path

from util import constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# when doing tests add this to reference python path
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# reusing constants
RULE_NAME = C.RULE_NAME
RULE_IGNORECASE = C.RULE_IGNORECASE
RULE_IS_REGEX = C.RULE_IS_REGEX
RULE_RULE = C.RULE_RULE
RULE_REGEX = C.RULE_REGEX
RULEDICT = C.RULEDICT

# Rule for applying any or all rules
APPLY_ANY = C.APPLY_ANY
APPLY_ALL = C.APPLY_ALL


class StringMatcher:
    """bundling sets of rules to perform rule matching on strings"""

    def __init__(self, rules: list = None, apply_default: str = APPLY_ALL) -> None:
        self._rules = {}
        # 'all' rules that need match
        self._all_rules = []
        # apply all or any rules
        self._apply_default = apply_default
        self.add_rules(rules)

    def add_rules(self, rules: list) -> None:
        """add list of rules"""
        _rules = rules
        if not isinstance(_rules, list):
            logger.debug("[StringMatcher] No list of rules was supplied, skip")
            return
        for _rule in rules:
            self.add_rule(_rule)

    @property
    def rules(self):
        """getter method for rules"""
        return self._rules

    def clear(self) -> None:
        """reset list of rules"""
        self._rules = {}

    def _add_all_rules(self):
        """updates the all rules list"""
        self._all_rules = []
        for _rule, _rule_info in self._rules.items():
            if _rule_info.get(C.RULE_APPLY, self._apply_default) == C.APPLY_ALL:
                self._all_rules.append(_rule)
        logger.debug(f"[StringMatcher] ALL_RULES: {self._all_rules}")

    def add_rule(self, rule: dict) -> None:
        """validates and adds rule"""
        _rule = rule
        if not isinstance(_rule, dict):
            logger.warning(f"[StringMatcher] Trying to add rule [{rule}], which is not a rule")
            return

        try:
            _name = rule[RULE_NAME]
        except KeyError:
            rule[RULE_NAME] = None

        if rule[RULE_NAME] is None:
            _name = str(uuid.uuid4())[-8:]
            rule[RULE_NAME] = _name
            logger.info(f"[StringMatcher] No name was given, using {rule[RULE_NAME]} a s rule name")

        # step 1 copy default values
        _rule = deepcopy(RULEDICT)
        # 2step 2 copy all other values from original dict
        _rule = {key: value for (key, value) in rule.items()}

        # add regex
        try:
            if _rule[RULE_IS_REGEX]:
                if _rule[RULE_IGNORECASE] is True:
                    _rule[RULE_REGEX] = re.compile(rule[RULE_RULE], re.IGNORECASE)
                else:
                    _rule[RULE_REGEX] = re.compile(rule[RULE_RULE])
            logger.debug(f"[StringMatcher] Adding Rule [{_name}]: {_rule}")
            self._rules[_name] = _rule
        except (TypeError, KeyError) as e:
            logger.warning(
                f"[StringMatcher] Rule [{rule[RULE_NAME]}], no regex expression [{rule[RULE_RULE]}] was supplied, {e}"
            )

        self._add_all_rules()

    def find(self, s: str, rule: str) -> list:
        """looks for string using rule, returns found string as list"""
        _result = []
        _rule_dict = self._rules.get(rule)
        if _rule_dict is None:
            logger.warning(f"[StringMatcher] There is no matching rule named [{rule}]")
            return False

        _regex = _rule_dict[RULE_REGEX]
        _include_results = _rule_dict.get(C.RULE_INCLUDE, True)
        # either match using regex or simple rule
        if _regex is None:
            _rule = _rule_dict[RULE_RULE]
            if _rule_dict[RULE_IGNORECASE]:
                _s = s.lower()
            else:
                _s = s
            # include or excclude results
            # include results / regular approach
            if _include_results is True:
                if _rule in _s:
                    _result = [_rule]
                else:
                    _result = []
            # exclude results: Invert results
            else:
                # it was found but excluded / return empty list
                if _rule in _s:
                    _result = []
                # excluded, not found => _rule applies
                else:
                    _result = [_rule]
            logger.debug(
                f"[StringMatcher] Non Regex Find using rule [{rule}] (include: [{_include_results}]), string [{s}], result {_result}"
            )
            # todo add apply_alll logic
            return _result
        else:
            _regex = _rule_dict[RULE_REGEX]
            _matches = _regex.findall(s)
            if _include_results is True:
                _result = _matches
            # excluding results
            else:
                # if result is empty, then excluding negates it, return original string
                if len(_matches) == 0:
                    _result = [s]
                # there were matching results, exclude this
                else:
                    _result = []
            logger.debug(
                f"[StringMatcher] Regex Find using rule [{rule}] (include: [{_include_results}]), string [{s}], result {_result}"
            )
            # todo add apply_alll logic
            return _result

    def _filter_result_set(self, result_set: dict) -> dict:
        """check the result rules combinations"""

        # create the list of rule that must apply
        if len(self._all_rules) == 0:
            return result_set

        _num_results = len(result_set)
        _num_all_rules = len(self._all_rules)

        # if there is a single all rule that is not contained in
        # result set, then drop the whole aply_all result set
        drop_all_rule_set = False
        for all_rule in self._all_rules:
            if result_set.get(all_rule) is None:
                drop_all_rule_set = True
                break

        if drop_all_rule_set is True:
            for _all_rule in self._all_rules:
                _ = result_set.pop(_all_rule, None)

        _num_filtered = len(result_set)
        logger.debug(
            f"[StringMatcher] Got [{_num_all_rules}] apply_all rules, original/filtered num matches [{_num_filtered}/{_num_results}]"
        )

        return result_set

    def find_all(self, s: str, by_rule: bool = True, filter_result_set: bool = True) -> dict | list:
        """returns matches.
        returns found results as dict by rule
        or as list
        by_rule: control parameter whether results are grouped by rule
        filter_result_set: Check the all rules
        """
        _found_results = {}
        _rules = []
        _rule_names = self._rules.keys()
        logger.debug(f"[StringMatcher] Find in [{s}] using rules {_rule_names}")

        for _rule_name in _rule_names:
            # get the apply mode from rules or from default
            _apply = self._rules.get(_rule_name, {}).get(C.RULE_APPLY, self._apply_default)
            _results = self.find(s, _rule_name)
            _rules.append(_rule_name)
            if len(_results) > 0:
                _found_results[_rule_name] = {C.RULE_RESULTS: _results, C.RULE_APPLY: _apply}

        if filter_result_set:
            self._filter_result_set(_found_results)

        if by_rule is False:
            _results = list(_found_results.values())
            _found_results = []
            _ = [_found_results.extend(_result) for _result in _results]
            _found_results = list(set(_found_results))

        logger.debug(f"[StringMatcher] Applied rules {_rules} on [{s}], found [{len(_found_results)}] matches")
        return _found_results

    def matches_rule(self, s: str, rule: str) -> bool:
        """check for matching rule"""
        return len(self.find(s, rule)) > 0

    def is_match(self, s: str) -> bool:
        """checks against the list of rules"""
        # get all matches
        _rule_matches = {key: self.matches_rule(s, key) for key in self._rules.keys()}
        logger.debug(f"[StringMatcher] [{s}] rule matches [{_rule_matches}]")
        # depending on matching mode, set the resulting overall match
        if len(_rule_matches) == 0:
            return False
        _matches = list(_rule_matches.values())
        # TODO only match the ones that are in the apply_all category
        if self._apply_default == APPLY_ALL:
            return all(_matches)
        else:
            return any(_matches)


class FileMatcher(StringMatcher):
    """Applies search to file contents"""

    def __init__(self, rules: list = None, apply: str = APPLY_ALL, by_line_default: bool = True) -> None:
        """constructor, same as String Matcher additional params
        by_line_default: search in line only (True) or in complete texte (False)
        """
        super().__init__(rules, apply)
        self._by_line_default = by_line_default
        self._content = {}


def main():
    """ main method """
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
