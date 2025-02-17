"""Helper class to analyze data types in dicts or objects
Can be useful to store types in dicts for analysis
"""

import sys
from copy import deepcopy
import logging
from typing import Dict, List
from pydantic import BaseModel, RootModel
from model.model_celltype import CellType, CellTypeMetaStats, CellTypeMetaDictType, CellTypeMeta
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class CellTypeAnalyzer:
    """Analyzing Data Columns"""

    def __init__(self, celltype_meta: List[CellTypeMeta] = None):
        """constructor"""
        self._object_type: CellType = None
        self._object: object = None
        self._field_stats: CellTypeMetaDictType = {}
        self._celltype_meta: Dict[str, CellTypeMeta] = {}
        self.set_celltype_meta(celltype_meta)
        self._is_active: bool = True

    # https://www.perplexity.ai/search/pydantic-root-model-get-fields-1mrSGwXASqG8new9aAmJhw

    @property
    def is_active(self) -> bool:
        """activate/deactivate analyzer"""
        return self._is_active

    @is_active.setter
    def is_active(self, is_active: bool) -> None:
        """activate/deactivate analyzer"""
        self._is_active = is_active

    def set_celltype_meta(self, celltype_meta_list: List[CellTypeMeta]) -> None:
        """sets metadata"""
        if celltype_meta_list is not None:
            for _cell_type_meta in celltype_meta_list:
                _cell_type_meta_copy = deepcopy(_cell_type_meta)
                if _cell_type_meta_copy.expected_cell_type in [CellType.FLOAT, CellType.INT]:
                    _cell_type_meta_copy.expected_cell_type = CellType.NUMERICAL
                if _cell_type_meta_copy.field_name is None:
                    _cell_type_meta_copy.field_name = CellType.PRIMITIVE
                self._celltype_meta[_cell_type_meta.field_name] = _cell_type_meta_copy

    def _calc_cell_meta_stats(
        self, obj: object, expected_cell_type: CellTypeMetaStats, field_meta_stats: CellTypeMetaStats
    ) -> bool:
        """validates object against basic expected cell type"""
        is_valid = True
        field_meta_stats.num = field_meta_stats.num + 1
        if expected_cell_type in [CellType.INT, CellType.FLOAT, CellType.NUMERICAL]:
            if not isinstance(obj, (float, int)):
                logger.info(f"[CellTypeAnalyzer] obj [{obj}] is not numerical")
                is_valid = False
            else:
                field_meta_stats.num_number = field_meta_stats.num_number + 1
                field_meta_stats.total = field_meta_stats.total + obj
                # initialize min max
                try:
                    if obj < field_meta_stats.min_value:
                        field_meta_stats.min_value = obj
                    if obj > field_meta_stats.max_value:
                        field_meta_stats.max_value = obj
                except TypeError:
                    field_meta_stats.min_value = obj
                    field_meta_stats.max_value = obj
        elif expected_cell_type == CellType.STRING:
            if not isinstance(obj, str):
                logger.info(f"[CellTypeAnalyzer] obj [{obj}] is not a string")
                is_valid = False
            else:
                field_meta_stats.num_str = field_meta_stats.num_str + 1
        elif expected_cell_type == CellType.BOOL:
            if not isinstance(obj, bool):
                logger.info(f"[CellTypeAnalyzer] obj [{obj}] is not a bool")
                is_valid = False
            else:
                field_meta_stats.num_bool = field_meta_stats.num_bool + 1
        elif obj is None:
            field_meta_stats.num_none = field_meta_stats.num_none + 1

        return is_valid

    def _update_field_meta(
        self, obj: object, field_meta_stats: CellTypeMetaStats, key: str = None
    ) -> CellTypeMetaStats:
        """update field metadata information with current object information"""
        # different logic if expected cell type is set in this case we do not
        # determine the type and only will try to update accordingly

        if field_meta_stats is None:
            logger.warning("[CellTypeAnalyzer] No MetaDataStats were initialized")
            return
        _last_seen_type = None
        if field_meta_stats.expected_cell_type is None:
            _last_seen_type = CellTypeAnalyzer.get_object_type(obj)
            _expected_cell_type = _last_seen_type
        else:
            _expected_cell_type = field_meta_stats.expected_cell_type
        _validated = self._calc_cell_meta_stats(obj, _expected_cell_type, field_meta_stats)
        if not _validated:
            logger.info(
                f"[CellTypeAnalyzer] obj [{obj}] has not expected type of [{field_meta_stats.expected_cell_type}] (key:{key})"
            )

        field_meta_stats.last_seen_cell_type = _last_seen_type

    def _init_field_meta(
        self,
        obj: object,
        field_name: str = None,
        description: str = None,
        key: object = None,
    ) -> CellTypeMetaStats:
        """init field information alow for potentially inconsistent usage of formats in data"""
        _obj_type = CellTypeAnalyzer.get_object_type(obj)

        _num_none = 0
        _num_str = 0
        _num_number = 0
        _num_bool = 0
        _total = 0
        _num = 1
        # get (external metadata)
        _description = description
        if _description is None:
            try:
                _description = self._celltype_meta.get(field_name).description
            except AttributeError:
                pass
        _celltype_field_meta = self._celltype_meta.get(field_name)
        _expected_cell_type = None
        if _celltype_field_meta:
            _expected_cell_type = _celltype_field_meta.expected_cell_type

        _cell_meta = CellTypeMetaStats(
            field_name=field_name,
            description=_description,
            expected_cell_type=_expected_cell_type,
            last_seen_cell_type=_obj_type,
        )
        if _obj_type == CellType.NONE:
            _num_none = 1
        elif _obj_type == CellType.STRING:
            _num_str = 1
        elif _obj_type in [CellType.INT, CellType.FLOAT]:
            _num_number = 1
            _cell_meta.total = obj
            _cell_meta.key_min = key
            _cell_meta.key_max = key
            _cell_meta.min_value = obj
            _cell_meta.max_value = obj
            _cell_meta.num_number = 1
        elif _obj_type == CellType.BOOL:
            _num_bool = 1
        _cell_meta.num = _num
        _cell_meta.num_none = _num_none
        _cell_meta.num_bool = _num_bool
        _cell_meta.num_number = _num_number
        _cell_meta.num_str = _num_str
        self._field_stats[field_name] = _cell_meta
        return _cell_meta

    def _analyze_primitive(self, obj: object, field_name: str = None, description: str = None, key: str = None) -> None:
        """Analyze primitive field"""
        # get the existiing meta data information
        _field_name = field_name
        # no field given assume it's a primitive field
        if _field_name is None:
            _field_name = CellType.PRIMITIVE
        _field_meta_stats = self._field_stats.get(_field_name)
        # initialize field meta data
        if _field_meta_stats is None:
            self._init_field_meta(obj, _field_name, description, key)
        else:
            self._update_field_meta(obj, _field_meta_stats, key)

    def _analyze_dict(self, obj: dict) -> None:
        """analyze dict"""
        for _key, _info in obj.items():
            self._analyze_primitive(_info, _key)

    def _analyze_base_model(self, obj: BaseModel) -> None:
        """analyze base model"""
        # _field_names = list(obj.model_fields)
        _obj_dict = obj.model_dump()
        self._analyze_dict(_obj_dict)

    def _analyze_root_model(self, obj: RootModel) -> None:
        """analyze root model"""
        _obj_dict = obj.model_dump()
        self._analyze_dict(_obj_dict)

    def analyze(self, obj: object = None, description: str = None) -> None:
        """analyze an object, only up to root level"""
        # skip if inactive
        if not self._is_active:
            return
        # initial analysis
        _obj_type = self._object_type
        if _obj_type is None:
            _obj_type = CellTypeAnalyzer.get_object_type(obj)
            self._object_type = _obj_type

        if _obj_type == CellType.DICT:
            self._analyze_dict(obj)
        elif _obj_type == CellType.ROOT_MODEL:
            self._analyze_root_model(obj)
        elif _obj_type == CellType.BASE_MODEL:
            self._analyze_base_model(obj)
        # primitive types
        elif _obj_type in [CellType.STRING, CellType.INT, CellType.FLOAT, CellType.NONE, CellType.BOOL]:
            # obj_type set to None triggers analysis of object type
            self._analyze_primitive(obj, CellType.PRIMITIVE, description)
        else:
            logger.warning(f"[CellTypeAnalyzer] object [{obj}] is of type [{type(obj)}] and not supported")
            return

    @staticmethod
    def get_object_type(obj: object) -> CellType:
        """analyzes an object returns the object type"""
        object_type = None
        if isinstance(obj, dict):
            object_type = CellType.DICT
        elif isinstance(obj, RootModel):
            object_type = CellType.ROOT_MODEL
        elif isinstance(obj, BaseModel):
            object_type = CellType.BASE_MODEL
        elif obj is None:
            object_type = CellType.NONE
        elif isinstance(obj, str):
            object_type = CellType.STRING
        elif isinstance(obj, float):
            object_type = CellType.FLOAT
        elif isinstance(obj, int):
            object_type = CellType.INT
        elif isinstance(obj, object):
            object_type = CellType.OBJECT
        return object_type

    @property
    def stats(self) -> CellTypeMetaDictType:
        """returns collected statistics"""
        return self._field_stats


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=CLI_LOG_LEVEL,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
