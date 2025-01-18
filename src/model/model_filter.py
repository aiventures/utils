"""Generic Filter Model"""

from typing import List, Optional, Dict, Literal, Any
from datetime import datetime as DateTime

from pydantic import BaseModel, field_validator


class FilterModel(BaseModel):
    """Atomic Filter as Base Class for other filter types"""

    # key
    key: Optional[Any] = None
    # description
    description: Optional[str] = None
    # group assignment
    groups: Optional[List[Any] | str] = None  # assignment to a filter group
    # AND/OR filter link: match for any or all within a filter group
    operator: Optional[Literal["any", "all"]] = "any"
    # include or exclude filter result (NOT logic)
    include: Optional[Literal["include", "exclude"]] = "include"


class NumericalFilterModel(FilterModel):
    """Filter for a numeric value"""

    value_min: Optional[float | int | DateTime] = None
    operator_min: Optional[Literal["gt", "ge", "eq"]] = None

    value_max: Optional[float | int | DateTime] = None
    operator_max: Optional[Literal["lt", "le", "eq"]] = None

    # lower / lower equal operators

    @field_validator("value_min", "value_max")
    @classmethod
    def validate(cls, value) -> float | int | DateTime:
        """validation for numerical value"""
        if value is not None and not isinstance(value, (int, float, DateTime)):
            raise ValueError(f"[Filter] Got Value [{value}],expecting numerical type")
        return value


class RegexFilterModel(FilterModel):
    """Filter for a regex string"""

    regex: Optional[str] = None  # simply the regex string


class StringFilterModel(FilterModel):
    """Filtering a string"""

    filter_strings: Optional[str | List[str]] = None  # string or list of strings to be matched
    match: Optional[Literal["exact", "contains"]] = "contains"  # str need to match excatly or only parts of it
    string_operator: Optional[Literal["any", "all"]] = "any"  # same as oprator but on atomic filter level


class ObjectFilterModel(FilterModel):
    """Basically a Filter that can host Filters and Filter Sets by attribute"""

    # Model is a dict of [object_attribute_name][rulename][filter|filterset]
    field_filter_dict: Optional[Dict[str, Dict[str, object]]]
