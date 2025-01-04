"""Pydantic model for the persistence class"""

from pydantic import BaseModel
from typing import List, Optional, Union, Dict
from enum import Enum


class ParamsFind(BaseModel):
    """input structure that is used for the find method"""

    p_root_paths: Optional[Union[list | str]] = None
    include_abspaths: Optional[Union[list | str]] = None
    exclude_abspaths: Optional[Union[list | str]] = None
    include_files: Optional[Union[list | str]] = None
    exclude_files: Optional[Union[list | str]] = None
    include_paths: Optional[Union[list | str]] = None
    exclude_paths: Optional[Union[list | str]] = None
    paths: Optional[bool] = False
    files: Optional[bool] = True
    as_dict: Optional[bool] = False
    root_path_only: Optional[bool] = False
    match_all: Optional[bool] = False
    ignore_case: Optional[bool] = True
    show_progress: Optional[bool] = True
    max_path_depth: Optional[int] = None
    paths_only: Optional[bool] = False
    add_empty_paths: Optional[bool] = True
