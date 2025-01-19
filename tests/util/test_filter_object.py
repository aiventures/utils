# probably replace by using filter set

#  """testing the filter object"""

# from util.filter_object import ObjectFilter
# from model.model_filter import ObjectFilterModel


# def test_object_filter_dict(
#     fixture_str_filter_match_va_x,
#     fixture_regex_filter_match_v_begin,
#     fixture_filter_set_match_va_x_begin,
#     fixture_filter_set_match_va_z_begin,
# ):
#     """testing Object Filter Using Atomic Filter and Filter Set"""
#     _test_dict = {"p1": "value x ", "p2": "value y", "p3": "value z"}
#     # fixture_str_filter_match_va_x.obj_filter.attributes
#     # apply filter to field "p1"

#     # set the attributes for filtering
#     fixture_regex_filter_match_v_begin.set_filtered_attributes("p1")
#     fixture_str_filter_match_va_x.set_filtered_attributes("p1")

#     # create the filter to be applied for separate parts of the dictionary
#     _filters = [
#         fixture_regex_filter_match_v_begin,
#         fixture_str_filter_match_va_x,
#     ]
#     object_filter_model = ObjectFilterModel(
#         field_filters=_filters, operator="any", description="A Description For this Object Filter"
#     )
#     obj_filter_dict = ObjectFilter(object_filter_model)
#     is_passed_as_dict = obj_filter_dict.filter(_test_dict, as_dict=True)
#     assert isinstance(is_passed_as_dict, dict)

# _filter = {
#     "p1": {
#         "fixture_filter_set_match_va_x_begin": fixture_filter_set_match_va_x_begin,
#         "filter_match_va_x": fixture_str_filter_match_va_x,
#     }
# }
# object_filter_model = ObjectFilterModel(
#     field_filter_list=_filter,
#     operator="any",
#     description="testing filter set and filter",
#     key="filter_with_set_and_key",
# )
# obj_filter_dict = ObjectFilter(object_filter_model)
# is_passed_as_bool = obj_filter_dict.filter(_test_dict)
# assert isinstance(is_passed_as_bool, bool)

# pass
