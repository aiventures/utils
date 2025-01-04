"""Generic Filter Model"""

from pydantic import BaseModel, field_validator
from typing import List, Optional, Union, Dict, Literal, Any
from enum import Enum


class Filter(BaseModel):
    """Atomic Filter as Base Class for other filter types"""

    # key
    key: Optional[Any] = None
    # description
    description: Optional[str] = None
    # group assignment
    group: Optional[List] = []  # assignment to a filter group
    # AND/OR filter link: match for any or all within a filter group
    operator: Optional[Literal["any", "all"]] = "any"
    # include or exclude filter result (NOT logic)
    include: Optional[Literal["include", "exclude"]] = "include"
    # object type
    type: Optional[Any] = None


class NumericalFilter(Filter):
    """Filter for a numeric value"""

    value_min: Optional[float | int] = None
    value_max: Optional[float | int] = None
    # lower / lower equal operators
    operator_min: Optional[Literal["lt", "le", "eq"]] = None
    operator_max: Optional[Literal["gt", "ge", "eq"]] = None

    @field_validator("value_min", "value_max")
    @classmethod
    def validate(cls, value) -> float | int:
        """validation for numerical value"""
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError(f"[Filter] Got Value [{value}],expecting numerical type")
        return value


class RegexFilter(Filter):
    """Filter for a regex string"""

    regex: Optional[str] = None  # simply the regex string


class StringFilter(Filter):
    """Filtering a string"""

    filter_strings: Optional[str | List[str]] = None  # string or list of strings to be matched
    match: Optional[Literal["exact", "contains"]] = None  # str need to match excatly or only parts of it


class FilterResult(BaseModel):
    """result for given Base filters"""

    # total match
    match: Optional[bool] = None
    # filter group
    groups: Optional[List[str] | str] = None
    # filters that led to the result
    filters: Optional[List[str] | str] = None
    # optional filed that allows for explanation of matches
    origin: Optional[Dict[str, Any]]
