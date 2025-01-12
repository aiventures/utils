"""Pydantic model for the persistence class"""

from typing import Optional, Union

from pydantic import BaseModel


class ParamsFind(BaseModel):
    """input structure that is used for the find method
    in the Persistence module
    """

    # root folder
    p_root_paths: Optional[Union[list | str]] = None
    # regex experession(s) to include / exclude in absolute path of file
    include_abspaths: Optional[Union[list | str]] = None
    exclude_abspaths: Optional[Union[list | str]] = None
    # regex experession(s) to include / exclude in file names
    include_files: Optional[Union[list | str]] = None
    exclude_files: Optional[Union[list | str]] = None
    # regex experession(s) to include / exclude in parent path
    include_paths: Optional[Union[list | str]] = None
    exclude_paths: Optional[Union[list | str]] = None
    # flags to export as path and pr file
    paths: Optional[bool] = False
    files: Optional[bool] = True
    # export as dict
    as_dict: Optional[bool] = False
    # search in root only
    root_path_only: Optional[bool] = False
    # match all or any
    match_all: Optional[bool] = False
    # regex case sensitive / insensitive
    ignore_case: Optional[bool] = True
    # show progress bar
    show_progress: Optional[bool] = True
    # check up to a maximum depth level
    max_path_depth: Optional[int] = None
    # process up to a max number
    max_num_files: Optional[int] = None
    max_num_dirs: Optional[int] = None
    # ???
    paths_only: Optional[bool] = False
    # add empty paths without folder to result list
    add_empty_paths: Optional[bool] = True
