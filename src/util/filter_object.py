# probably can be replace by filter set

# """Filter for filtering structured objects like dicts or objects"""

# import logging
# import os
# from model.model_filter import ObjectFilterModel
# from typing import Dict

# from util import constants as C
# from util.filter import AbstractAtomicFilter
# from util.filter_set import FilterSet

# logger = logging.getLogger(__name__)

# # get log level from environment if given
# logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# NOT_FOUND = "xyz_not_found"


# class ObjectFilter(AbstractAtomicFilter):
#     """generic superclass for object type filters"""

#     def __init__(self, obj_filter: ObjectFilterModel = None):
#         """use object filter model to filter objects"""
#         super().__init__(obj_filter)
#         self._filter: ObjectFilterModel = obj_filter
#         self._attribute_atomic_filters: Dict[str, AbstractAtomicFilter] = {}
#         self._attribute_filter_sets: Dict[str, FilterSet] = {}
#         self._build_filters()

#         of = obj_filter
#         logger.debug(
#             f"[ObjectFilter] Key [{of.key}] ({of.description}), operator [{of.operator}], include [{of.include}], groups {of.groups} "
#         )

#     def _build_filters(self) -> None:
#         """build the filters from passed filters"""
#         for _filter in self._filter.field_filters:
#             pass

#     def _get_dict_attribute(self, obj: dict, attribute: str) -> object:
#         """get the attribute of a dict"""
#         out = obj.get(attribute, NOT_FOUND)
#         if out == NOT_FOUND:
#             logger.info(f"[ObjectFilter] Attribute [{attribute}] not found in dict [{obj}]")
#         return out

#     def _get_obj_attribute(self, obj: object, attribute: str) -> object:
#         """get the attribute of a dict"""
#         if not hasattr(obj, attribute):
#             logger.info(f"[ObjectFilter] Object has no attribute [{attribute}], [{obj}]")
#             return NOT_FOUND
#         return getattr(obj, attribute)

#     def _get_value(self, obj: dict | object, attribute: str):
#         """get the attribute of the structure"""
#         out = None
#         if isinstance(obj, dict):
#             out = self._get_dict_attribute(obj, attribute)
#         else:
#             out = self._get_obj_attribute(obj, attribute)
#         if out == NOT_FOUND:
#             raise ValueError(f"[ObjectFilter] Object/Dict has no attribute [{attribute}]")
#         return out

#     def _evaluate_filter_result(self, filter_sets_passed: dict) -> bool | None:
#         """evaluate the filter rules"""
#         _out_by_attribute = {}
#         # get the filter settings for the object filter
#         _k = self.obj_filter.key
#         _obj_op = self.obj_filter.operator
#         _obj_include = self.obj_filter.include
#         _key = self.obj_filter.key
#         _description = self.obj_filter.description

#         _filter_results_by_attribute = {}
#         for _attribute, _filter_results in filter_sets_passed.items():
#             logger.debug(f"[ObjectFilter] Filter [{_k}] [{_obj_op}/{_obj_include}], Object Attribute [{_attribute}]")
#             _filter_results_by_op = {"any": [], "all": []}
#             for _filter, _filter_info in _filter_results["filters_atomic"].items():
#                 logger.debug(
#                     f"[ObjectFilter] Atomic Filter ({_filter_info['operator']}) [{_filter}], passed [{_filter_info['passed']}]"
#                 )
#                 _filter_results_by_op[_filter_info["operator"]].append(_filter_info["passed"])

#             for _filter, _filter_info in _filter_results["filter_sets"].items():
#                 _matches = _filter_info["matches"]
#                 _passes_all = _matches["passes_all"]
#                 _passes_any = _matches["passes_any"]
#                 if isinstance(_passes_any, bool):
#                     _filter_results_by_op["any"].append(_passes_any)
#                 if isinstance(_passes_all, bool):
#                     _filter_results_by_op["all"].append(_passes_all)
#                 _filter_any = _matches["any"]
#                 _filter_all = _matches["all"]

#                 logger.debug(
#                     f"[ObjectFilter] Attribute [{_attribute}] Filter Set [{_filter}], passes_any [{_passes_any}], passes all [{_passes_all}]"
#                 )
#                 logger.debug(
#                     f"[ObjectFilter] Attribute [{_attribute}] Filter Set [{_filter}] ALL FILTERS {_filter_all}"
#                 )
#                 logger.debug(
#                     f"[ObjectFilter] Attribute [{_attribute}] Filter Set [{_filter}] ANY FILTERS {_filter_any}"
#                 )
#                 pass

#             _out_by_attribute[_attribute] = _filter_results_by_op

#         _out = {}
#         # condense filter results. of course we coul do thos with reduce or sth.
#         # but explicitly done so fo rdebugging purposes
#         for _attribute, _attribute_info in _out_by_attribute.items():
#             _any = None
#             _all = None
#             _passes = None
#             if len(_attribute_info["any"]) > 0:
#                 _any = any(_attribute_info["any"])
#             if len(_attribute_info["all"]) > 0:
#                 _all = all(_attribute_info["all"])
#             if _obj_op == "any":
#                 if _any is True or _all is True:
#                     _passes = True
#                 elif _any is False and _all is False:
#                     _passes = False
#             # only items with all are considered for the test
#             # as it will be assumed the consumer is setting up filters
#             # correctly
#             elif _obj_op == "all":
#                 if _all is True:
#                     _passes = True
#                 elif _all is False:
#                     _passes = False

#             _out[_attribute] = _passes

#             logger.debug(
#                 f"[ObjectFilter] [{_key}] ({_description}), OP [{_obj_op}] {_obj_include},  Attribute [{_attribute}] {_attribute_info}, results to [{_passes}]"
#             )

#         _out_values = [_p for _p in list(_out.values()) if isinstance(_p, bool)]

#         out = None
#         if len(_out_values) > 0:
#             if _obj_op == "any":
#                 out = any(_out_values)
#             elif _obj_op == "all":
#                 out = all(_out_values)

#         if _obj_include == "exclude" and isinstance(out, bool):
#             out = not out

#         logger.debug(
#             f"[ObjectFilter] [{_key}] ({_description}), OP [{_obj_op}] {_obj_include},  overall result [{out}]"
#         )

#         return out

#     def _filter_obj(self, obj: dict | object, as_dict: bool = False) -> bool | dict:
#         """internal filtering of object attributes
#         returns filter results by fields
#         """
#         _filter_sets_passed = {}
#         _obj_type = type(obj).__name__
#         for _attribute, _filter_dict in self._filter.field_filters.items():
#             _filter_tests_by_attribute = {"filters_atomic": {}, "filter_sets": {}, "value": None}
#             _value = None
#             try:
#                 _value = self._get_value(obj, _attribute)
#                 _filter_tests_by_attribute["value"] = _value
#             except ValueError as e:
#                 logger.info(f"[ObjectFilter] Object/Dict has no attribute [{_attribute}], {e.args}")
#                 continue
#             logger.debug(
#                 f"[ObjectFilter] Parse filters for [{_obj_type}], object attribute [{_attribute}], value [{_value}]"
#             )

#             for _filter_rule, _filter in _filter_dict.items():
#                 logger.debug(
#                     f"[ObjectFilter], Filtering Attribute [{_attribute}], value [{_value}], rule [{_filter_rule}"
#                 )
#                 if isinstance(_filter, AbstractAtomicFilter):
#                     _filter_tests_by_attribute["filters_atomic"][_filter_rule] = {
#                         "passed": _filter.filter(_value),
#                         "operator": _filter.operator,
#                     }

#                 elif isinstance(_filter, FilterSet):
#                     _check_any = self._filter.operator
#                     _filter_tests_by_attribute["filter_sets"][_filter_rule] = _filter.filter(
#                         _value, check_any=_check_any
#                     )

#             _filter_sets_passed[_attribute] = _filter_tests_by_attribute
#             logger.debug(f"[ObjectFilter] Attribute [{_attribute}], filter results: {_filter_tests_by_attribute}")

#         passes = self._evaluate_filter_result(_filter_sets_passed)

#         # filter parsing can be output as dict for analysis
#         if as_dict:
#             _filter_sets_passed["object_filter"] = {
#                 "operator": self.obj_filter.operator,
#                 "include": self.obj_filter.include,
#                 "groups": self.obj_filter.groups,
#             }
#             _filter_sets_passed["passes"] = passes
#             return _filter_sets_passed

#         return passes

#     def filter(self, obj: object, as_dict: bool = False) -> bool | dict:
#         """filtering the complex structured object"""
#         return self._filter_obj(obj, as_dict)


# # TODO IMPLEMENT UNIT TESTS
