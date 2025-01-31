""" " model for file tree"""

from typing import List, Optional, Annotated, Literal
from pydantic import BaseModel


ID = "id"
PARENT_ID = "parent_id"
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
OUTPUT = "output"
DICT_TREE_NODE_MODEL = "DictTreeNodeModel"
DICT_PATH = "dict_path"

NodeType = Annotated[Literal["leaf", "node", "any"], "Node Type"]


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


class DictTreeInfoModel(BaseModel):
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


class TreeNodeModel(BaseModel):
    """generic Tree Node"""

    id: Optional[object] = None
    parent_id: Optional[object] = None
    children: Optional[List[object]] = []
    is_leaf: Optional[bool] = None
    name: Optional[str] = None
    obj: Optional[object] = None
    obj_type: Optional[str] = None
    level: Optional[int] = None
    predecessors: Optional[list] = None


class DictTreeNodeModel(TreeNodeModel):
    """TreeDict Node"""

    # keys for storing key name and list index
    key: Optional[str] = None
    list_idx: Optional[int] = None
    # dictionary key path
    dict_path: Optional[list] = None
    # output attribute to be filled with rendered node information
    output: Optional[str] = None
