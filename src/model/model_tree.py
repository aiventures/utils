""" " model for file tree"""

from typing import List, Optional
from pydantic import BaseModel


ID = "id"
PARENT = "parent"
CHILDREN = "children"
IS_LEAF = "is_leaf"
PREDECESSORS = "predecessors"
DICT_PATH = "path"
KEY = "key"
ROOT = "root"
LIST_IDX = "list_idx"
LEVEL = "level"
OBJ_TYPE = "obj_type"
OBJECT = "obj"
NAME = "name"
NODE = "node"
VALUE = "value"


class FileTreeNodeRenderModel(BaseModel):
    """rendering"""

    extension: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    size_str: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_file: Optional[bool] = None
    is_path: Optional[bool] = None
    is_empty: Optional[bool] = None


class DictTreeInfo(BaseModel):
    """generic model for storing tree information"""

    id: Optional[int] = None
    parent: Optional[int] = None
    predecessors: Optional[List[int]] = None
    children: Optional[List[int]] = None
    is_leaf: Optional[bool] = None
    path: Optional[List[str | int]] = None
    key: Optional[str] = None
    list_idx: Optional[int] = None
    level: Optional[int] = None
    obj_type: Optional[str] = None
    obj: Optional[object] = None
