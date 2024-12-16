"""Pydantic model for the persistence class"""

from pydantic import BaseModel
from typing import List, Optional, Union, Dict
from enum import Enum


class ParamsFind(BaseModel):
    """input structure that is used for the find method"""

    p_root_paths: Union[list | str] = None
    include_abspaths: Union[list | str] = None
    exclude_abspaths: Union[list | str] = None
    include_files: Union[list | str] = None
    exclude_files: Union[list | str] = None
    include_paths: Union[list | str] = None
    exclude_paths: Union[list | str] = None
    paths: bool = False
    files: bool = True
    as_dict: bool = False
    root_path_only: bool = False
    match_all: bool = False
    ignore_case: bool = True
    show_progress: bool = True
    max_path_depth: int = None
