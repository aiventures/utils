"""Mapper Class for Color Schema Maps"""

import logging
import os
import re
from typing import Dict, List, get_args
from rich.logging import RichHandler
from util import constants as C
from util_cli.cli_color_schema_maps import COLOR_SCHEMAS
from util_cli.cli_color_mapper import ColorMapper
from model.model_filter import AnyOrAllType
from model.model_visualizer import (
    ColorSchemaSetType,
    ColorSchemaKey,
    ColorSchemaType,
    ColorSchemaMetaData,
    SchemaColorType,
    MULTICOLOR_SCHEMA,
    ColorEncodingType,
    ColorSchemaData,
    ColorSchemaDataDict,
)

# extract the colors from the bracket
REGEX_COLORS_META = re.compile("\((.+)\)")
NUMCOLORS = re.compile("(\d)color")
DESCRIPTION = "description"
INVERT_FONT = "invert_font"
TYPE = "type"
MAX_NUM_COLORS = "max_num_colors"
ALL_COLORS = 999

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class ColorSchema:
    """Class for mapping Color Schemas"""

    def __init__(
        self,
        schema: ColorSchemaType = "spectral",
        color_encoding: ColorEncodingType = "hex",
        min_value: int | float = None,
        max_value: int | float = None,
        reverse_schema: bool = False,
    ):
        # upper and lower bounds
        self._min_value = min_value
        self._max_value = max_value
        # reverse the color schema
        self._reverse_schema = reverse_schema

        self._schemas = COLOR_SCHEMAS
        self._metadata: Dict[ColorSchemaType, ColorSchemaMetaData] = None
        # color encoding type to be used, should be rgb in most cases
        self._color_encoding: ColorEncodingType = color_encoding
        # create the color mapper
        self._color_mapper = ColorMapper()
        # store the last schema
        self._buffered_schema: ColorSchemaType = None
        self._buffered_schema_info: dict = self.get_schema_info(schema)
        self._buffered_num_colors = None

    @property
    def schemas(self):
        """raw schema"""
        return self._schemas

    @property
    def current_schema_metadata(self) -> ColorSchemaMetaData:
        """returns current color schema"""
        if self._buffered_schema is not None:
            return self._metadata[self._buffered_schema]
        else:
            return None

    def set_minmax_values(self, min_value: float | int = None, max_value: float | int = None):
        """set boundary numerical values for directly calculating  index number"""
        self._min_value = min_value if min_value is not None else 1
        self._max_value = max_value if max_value is not None else self._buffered_num_colors

    def get_minmax_values(self) -> list:
        """return limit values"""
        return [self._min_value, self._max_value]

    def _parse_schema_description(self, schema_description: str) -> ColorSchemaMetaData:
        """parses schema description"""
        out = ColorSchemaMetaData()
        _colors = REGEX_COLORS_META.findall(schema_description)[0].split(" ")

        try:
            _num_colors = int(NUMCOLORS.findall(schema_description)[0])
        except IndexError:
            _num_colors = MULTICOLOR_SCHEMA
        out.num_colorset = _num_colors
        out.color_list = _colors
        return out

    def _get_max_num_colors(self, _schema_info: dict) -> int:
        """returns the maximum number of colors in a schema palette"""
        _max_num_colors = 8
        for _idx in range(9, 13):
            if _schema_info.get(str(_idx)) is None:
                break
            else:
                _max_num_colors = _max_num_colors = _idx
        return _max_num_colors

    def _get_metadata(self) -> Dict[str, ColorSchemaMetaData]:
        """parses the color schema and extracts schema metadata"""
        out: Dict[str, ColorSchemaMetaData] = {}
        for _schema_name, _schema_info in COLOR_SCHEMAS.items():
            _description = _schema_info[DESCRIPTION]
            _metadata = self._parse_schema_description(_description)
            _metadata.name = _schema_name
            _metadata.schema_set = _schema_info[TYPE]
            _metadata.description = _description
            _metadata.num_max_colors = self._get_max_num_colors(_schema_info)
            out[_schema_name] = _metadata
        return out

    def get_schema_info(self, schema: ColorSchemaType = "spectral") -> dict:
        """parse the schema, buffer it locally and return it"""
        out = {}
        # schema is buffered already, nothing to do
        if self._buffered_schema == schema and self._buffered_schema_info is not None:
            return self._buffered_schema_info
        # schema not buffered
        _schema_info = self._schemas[schema]
        _schema_metadata = self.metadata[schema]
        out[DESCRIPTION] = _schema_info[DESCRIPTION]
        out[MAX_NUM_COLORS] = _schema_metadata.num_max_colors
        out[INVERT_FONT] = _schema_info[INVERT_FONT]

        # convert the rgb values
        for _idx in range(3, _schema_metadata.num_max_colors + 1):
            _colors = _schema_info[str(_idx)]
            _out_colors = []
            for _color in _colors:
                # convert the color codes into target format
                _col_tuple = tuple(_color)
                if self._color_encoding == "rgb":
                    _out_colors.append(_col_tuple)
                elif self._color_encoding == "hex":
                    _out_colors.append(self._color_mapper.rgb2hex(_col_tuple))
                elif self._color_mapper == "code":
                    _out_colors.append(self._color_mapper.rgb2code(_col_tuple))
            out[str(_idx)] = _out_colors
        self._buffered_schema = schema
        self._buffered_schema_info = out
        return out

    @property
    def metadata(self) -> Dict[str, ColorSchemaMetaData]:
        """schema metadata"""
        if self._metadata is None:
            self._metadata = self._get_metadata()
        return self._metadata

    @property
    def reverse_schema(self) -> bool:
        """reversed schema, only applies to colors and color methods"""
        return self._reverse_schema

    @reverse_schema.setter
    def reverse_schema(self, reverse_schema: bool) -> None:
        """set reverse schema, only applies to colors and color methods"""
        self._reverse_schema = reverse_schema

    @property
    def num_colors(self) -> int:
        """buffered num colors"""
        if self._buffered_num_colors is not None:
            return self._buffered_num_colors
        else:
            self.num_colors = 8

    @num_colors.setter
    def num_colors(self, num_colors: int) -> None:
        """set buffered filter key"""
        if num_colors is not None:
            self._buffered_num_colors = num_colors

    def adjust_num_colors(self, num_colors: int) -> int:
        """wrapping read/write access to buffer"""
        if num_colors is None:
            # read / set the buffer (8 color as standard)
            if self.num_colors is None:
                self.num_colors = 8
        else:
            self.num_colors = num_colors
        return self.num_colors

    def _get_schema(self, num_colors: int = 8, schema: ColorSchemaType = None) -> dict:
        """gets the schema for a given color palette"""
        _num_colors = self.adjust_num_colors(num_colors)
        self.num_colors = _num_colors

        _schema_info = None
        if schema is None:
            if self._buffered_schema is None:
                logging.warning("[ColorSchemaMapper] No Color Schema was buffered, instanciate before calling colors")
                return None
            _schema_info = self._buffered_schema_info
        else:
            _schema_info = self.get_schema_info(schema)
        if _schema_info[MAX_NUM_COLORS] < _num_colors:
            logging.warning(
                f"[ColorSchemaMapper] Requested [{_num_colors}] colors, but Schema [{self._buffered_schema}] only has [{_schema_info[MAX_NUM_COLORS]}] colors "
            )
            return None
        return _schema_info

    def colors(self, num_colors: int = None, schema: ColorSchemaType = None) -> List[List]:
        """returns the color list and the invert font info  for given number of colors in a set"""
        _num_colors = self.adjust_num_colors(num_colors)

        out = []
        _schema_info = self._get_schema(_num_colors, schema)
        if _schema_info is None:
            return
        # append the color table
        _color_list = _schema_info[str(_num_colors)]
        if self._reverse_schema:
            _color_list = list(reversed(_color_list))
        out.append(_color_list)
        _invert_font_info = _schema_info[INVERT_FONT][str(_num_colors)]
        _invert_fonts = [True if str(_idx) in _invert_font_info else False for _idx in range(1, _num_colors + 1)]
        if self._reverse_schema:
            _invert_fonts = list(reversed(_invert_fonts))
        out.append(_invert_fonts)
        return out

    def color(self, index: int, num_colors: int = None, schema: ColorSchemaType = None) -> list:
        """returns the color code and the information on whether to invert the font color"""
        _num_colors = self.adjust_num_colors(num_colors)
        _schema_info = self._get_schema(_num_colors, schema)
        if _schema_info is None:
            return
        _index = index - 1
        _index_invert_font = index
        if self._reverse_schema:
            _index = _num_colors - index
        _color_code = _schema_info[str(_num_colors)][_index]
        _invert_font_info = _schema_info[INVERT_FONT][str(_num_colors)]
        _invert_font = True if str(_index + 1) in _invert_font_info else False
        return [_color_code, _invert_font]

    def color_by_value(
        self,
        value: int | float,
        min_value: float | int = None,
        max_value: float | int = None,
        num_colors: int = None,
        schema: ColorSchemaType = None,
    ) -> list:
        """calculates colors based on value and"""
        # set min max values
        if min_value is not None and max_value is not None:
            self.set_minmax_values(min_value, max_value)
        _num_colors = num_colors if num_colors is not None else self._buffered_num_colors
        if _num_colors is None:
            logger.warning(f"[ColorSchema] was not able to set number of colors, ensure instanciation")
            return
        if value > self._max_value:
            value = self._max_value
        elif value < self._min_value:
            value = self._min_value
        _percentage = (value - self._min_value) / (self._max_value - self._min_value)
        _index = int(1 + round(_percentage * (_num_colors - 1), 0))
        return self.color(_index, num_colors, schema)

    def filter_schemas(
        self,
        color_filters: List[SchemaColorType] = None,
        num_colors: List[int] = None,
        color_schema_sets: List[ColorSchemaSetType] = None,
        filter_type: AnyOrAllType = "any",
    ) -> list:
        """filter metadata, return possible schemes"""
        _color_filters: List[SchemaColorType] = color_filters  # colors
        _num_colors: List[int] = num_colors  # number of colors in color set
        _color_schema_sets: List[ColorSchemaSetType] = color_schema_sets  # color schema
        if color_filters is None:
            _color_filters = ["all"]
        if _num_colors is None:
            _num_colors = [ALL_COLORS]
        if _color_schema_sets is None:
            _color_schema_sets = ["all"]
        out = []

        # Dict[ColorSchemaType, ColorSchemaMetaData] = None
        for _schema, _meta in self.metadata.items():
            _passed_colors = []
            _passed_schema = []
            _passed_num_colors = []
            _color_list = _meta.color_list
            # filter colors
            if "all" in _color_filters:
                _passed_colors.append(True)
            else:
                for _color in _color_filters:
                    if _color in _color_list:
                        _passed_colors.append(True)
                    else:
                        _passed_colors.append(False)
            if filter_type == "all":
                _passed_colors = all(_passed_colors)
            else:
                _passed_colors = any(_passed_colors)
            if not _passed_colors:
                logger.debug(
                    f"[ColorSchema] Schema [{_schema}], Colors {_color_list} not PASSED, filter colors {_color_filters}"
                )
                continue
            # filter schemas
            _passed_schema = False
            if _meta.schema_set in _color_schema_sets or "all" in _color_schema_sets:
                _passed_schema = True
            if not _passed_schema:
                logger.debug(
                    f"[ColorSchema] Schema [{_schema}], Schema Set [{_meta.schema_set}] not PASSED, filter schemas {_color_schema_sets}"
                )
                continue
            # filter numbers
            _passed_num_colors = False
            if _meta.num_colorset in _num_colors or ALL_COLORS in _num_colors:
                _passed_num_colors = True
            if not _passed_num_colors:
                logger.debug(
                    f"[ColorSchema] Schema [{_schema}], Num Colors [{_meta.num_colorset}] not PASSED, filter num colors {_num_colors}"
                )
                continue

            logger.debug(
                f"[ColorSchema] Schema [{_schema}], PASSED, colors {_color_filters}, schema {_color_schema_sets}, num colors {_num_colors}"
            )
            out.append(_schema)

        return out

    def get_color_schema(self, schema: ColorSchemaType) -> ColorSchemaData:
        """gets the color schema as Pydantic Model"""
        _metadata = self._metadata[schema]
        schema_data = ColorSchemaData(**_metadata.model_dump())
        schema_data.encoding = self._color_encoding
        _schema_info = self.get_schema_info(schema)
        _color_schema_map = {}
        for _idx in range(3, schema_data.num_max_colors + 1):
            _color_list = _schema_info[str(_idx)]
            _invert_font_info = _schema_info[INVERT_FONT][str(_idx)]
            _invert_fonts = [True if str(_idx) in _invert_font_info else False for _idx in range(1, _idx + 1)]
            _color_schema_map[str(_idx)] = dict(zip(_color_list, _invert_fonts))
        schema_data.color_schema_map = _color_schema_map
        return schema_data

    def get_color_schema_map(self, color_schemas: List[ColorSchemaType] = None) -> ColorSchemaDataDict:
        """returns an all in one schema model, that can easily be dumped as dict"""
        out = ColorSchemaDataDict()
        _color_schemas = color_schemas
        if _color_schemas is None:
            _color_schemas = get_args(ColorSchemaKey)
        for _schema in _color_schemas:
            out[_schema] = self.get_color_schema(_schema)
        return out


def main():
    """main program"""
    _color_schema = ColorSchema()
    _metadata = _color_schema.metadata
    _schema = _color_schema.get_schema_info(schema="accent")
    _colors, _invert_fonts = _color_schema.colors(num_colors=5)
    _color, _invert_font = _color_schema.color(5)
    # calculate rgb value based on percentage of min max
    _test_scale, _ = _color_schema.color_by_value(value=30, min_value=0, max_value=100)

    _color_schema.reverse_schema = True
    _colors_rev, _invert_fonts_rev = _color_schema.colors(num_colors=5)
    _color_rev, _invert_font_rev = _color_schema.color(5)
    # assembling a filter
    _colors: List[SchemaColorType] = ["green"]
    _num_colors: List[int] = [1]
    color_schema_sets: List[ColorSchemaSetType] = ["all"]
    _schemas = _color_schema.filter_schemas(
        color_filters=_colors, num_colors=_num_colors, color_schema_sets=color_schema_sets
    )
    # get a complete Color Schema in a pydantic model
    _color_schema_data: ColorSchemaData = _color_schema.get_color_schema(schema="blues")
    # get all schemas in a root model / color_schemas is validated ...
    _all_color_schemas = _color_schema.get_color_schema_map(color_schemas=["blues"])
    # get it as dict
    # _all_color_schemas_dict = _all_color_schemas.model_dump()

    pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    main()
