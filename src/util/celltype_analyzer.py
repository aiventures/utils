"""Helper class to analyze data types in dicts or objects
Can be useful to store types in dicts for analysis
"""

from util.constants import CellType
from pydantic import BaseModel, RootModel


class CellTypeAnalyzer:
    """Analyzing Data Columns"""

    def __init__(self):
        """constructor"""
        self._object_type = None
        self._object = None
        self._field_info = {}

    @staticmethod
    def analyze(obj: object) -> CellType:
        """anaylzes an object returns the object type"""
        object_type = None
        if isinstance(obj, dict):
            object_type = CellType.DICT
        elif isinstance(obj, BaseModel):
            object_type = CellType.BASE_MODEL
        elif isinstance(obj, str):
            object_type = CellType.STRING
        elif isinstance(obj, float):
            object_type = CellType.FLOAT
        elif isinstance(obj, int):
            object_type = CellType.INT
        elif isinstance(obj, RootModel):
            object_type = CellType.ROOT_MODEL
        elif isinstance(obj, object):
            object_type = CellType.OBJECT
        return object_type
    
