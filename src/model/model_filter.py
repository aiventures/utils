"""Generic Filter Model"""

from pydantic import BaseModel, field_validator
from typing import List, Optional, Union, Dict, Literal, Any
from enum import Enum
from datetime import datetime as DateTime


class FilterModel(BaseModel):
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


class NumericalFilterModel(FilterModel):
    """Filter for a numeric value"""

    value_min: Optional[float | int] = None
    operator_min: Optional[Literal["gt", "ge", "eq"]] = None

    value_max: Optional[float | int] = None
    operator_max: Optional[Literal["lt", "le", "eq"]] = None

    # lower / lower equal operators

    @field_validator("value_min", "value_max")
    @classmethod
    def validate(cls, value) -> float | int:
        """validation for numerical value"""
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError(f"[Filter] Got Value [{value}],expecting numerical type")
        return value


class RegexFilterModel(FilterModel):
    """Filter for a regex string"""

    regex: Optional[str] = None  # simply the regex string


class StringFilterModel(FilterModel):
    """Filtering a string"""

    filter_strings: Optional[str | List[str]] = None  # string or list of strings to be matched
    match: Optional[Literal["exact", "contains"]] = None  # str need to match excatly or only parts of it


class DateTimeFilterModel(FilterModel):
    """Filtering DateTime"""

    filter_str: Optional[str] = None  # Filter String to be used for Calendar
    date_from: Optional[DateTime] = None
    date_to: Optional[DateTime] = None


class FilterResultModel(BaseModel):
    """result for given Base filters"""

    # total match
    match: Optional[bool] = None
    # filter group
    groups: Optional[List[str] | str] = None
    # filters that led to the result
    filters: Optional[List[str] | str] = None
    # optional filed that allows for explanation of matches
    origin: Optional[Dict[str, Any]]
