""" " model for file tree"""

from typing import List, Optional
from pydantic import BaseModel


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


class TreeInfo(BaseModel):
    """generic model for storing tree information"""

    id: Optional[object] = None
    name: Optional[str] = None
    node_type: Optional[str] = None
    value: Optional[object] = None
    parent_id: Optional[object] = None
    parent_ids: Optional[List[object]] = []
    child_ids: Optional[List[object]] = []
    is_leaf: Optional[bool] = None
