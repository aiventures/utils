""" " model for file tree"""

from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional, Union, Dict, Literal, Any
from enum import Enum
from datetime import datetime as DateTime
from model.model_persistence import ParamsFind
from util.filter import AbstractAtomicFilter, DictFilter
from util.filter_set import FilterSet


class ParamsFileTree(BaseModel):
    """Input Params for File Tree Constructor"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_filter_params: Optional[ParamsFind] = None
    add_metadata: Optional[bool] = False
    add_filesize: Optional[bool] = False
    file_filter: Optional[FilterSet | DictFilter] = None
    path_filter: Optional[FilterSet | DictFilter] = None
