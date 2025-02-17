"""Cell Type model"""

from enum import StrEnum
from typing import Optional, Dict, List, Annotated, Literal, TypeAlias
from pydantic import BaseModel, Field, TypeAdapter


# color = Color.GREEN
# if color == "green":
#     print("The color is green")
class CellType(StrEnum):
    """Enum Type for analysing data type"""

    BASE_MODEL = "base_model"
    ROOT_MODEL = "root_model"
    DICT = "dict"
    NUMERICAL = "numerical"
    FLOAT = "float"
    INT = "int"
    STRING = "string"
    OBJECT = "object"
    BOOL = "bool"
    PRIMITIVE = "primitive"
    NONE = "none"


class CellTypeMeta(BaseModel):
    """Additional Metadata"""

    field_name: Optional[str] = None
    description: Optional[str] = None
    # field that is expected
    expected_cell_type: Optional[CellType] = None


class CellTypeMetaStats(CellTypeMeta):
    """CellType MetaModel"""

    last_seen_cell_type: Optional[CellType] = "object"
    total: Optional[float] = 0
    num: Optional[int] = 0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    key_min: Optional[str] = None
    key_max: Optional[str] = None
    num_none: Optional[int] = None
    num_number: Optional[int] = None
    num_str: Optional[int] = None
    num_bool: Optional[int] = None


# derived models
CellTypeMetaStatsDictModel = Dict[str, CellTypeMetaStats]
CellTypeMetaStatsDictAdapter = TypeAdapter(CellTypeMetaStatsDictModel)
CellTypeMetaDictType = Annotated[CellTypeMetaStatsDictModel, CellTypeMetaStatsDictAdapter]
