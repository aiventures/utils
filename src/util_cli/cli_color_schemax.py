"""Mapper Class for Color Schema Maps"""

import logging
import os
import re
from typing import Dict, Optional, List
from rich.logging import RichHandler
from rich.table import Table
from util import constants as C
from cli.bootstrap_env import LOG_LEVEL
from util_cli.cli_color_schema_maps import COLOR_SCHEMAS
from util_cli.cli_color_mapper import ColorMapper
from model.model_visualizer import (
    ColorSchemaSetType,
    ColorSchemaType,
    ColorSchemaMetaData,
    MULTICOLOR_SCHEMA,
    ColorEncodingType,
)

# extract the colors from the bracket
REGEX_COLORS_META = re.compile("\((.+)\)")
NUMCOLORS = re.compile("(\d)color")
DESCRIPTION = "description"
INVERT_FONT = "invert_font"
TYPE = "type"
MAX_NUM_COLORS = "max_num_colors"

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class ColorSchema:
    """Class for mapping Color Schemas"""

    def __init__(self, schema: ColorSchemaType = "spectral", color_encoding: ColorEncodingType = "hex"):
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
    def num_colors(self):
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
        """wrapping reaf/write access to buffer"""
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
        out.append(_schema_info[str(_num_colors)])
        _invert_font_info = _schema_info[INVERT_FONT][str(_num_colors)]
        _invert_fonts = [True if str(_idx) in _invert_font_info else False for _idx in range(1, _num_colors + 1)]
        out.append(_invert_fonts)
        return out

    def color(self, index: int, num_colors: int = None, schema: ColorSchemaType = None) -> List:
        """returns the color code and the information on whether to invert the font color"""
        _num_colors = self.adjust_num_colors(num_colors)
        out = []
        _schema_info = self._get_schema(_num_colors, schema)
        if _schema_info is None:
            return
        _color_code = _schema_info[str(_num_colors)][index - 1]
        _invert_font_info = _schema_info[INVERT_FONT][str(_num_colors)]
        _invert_font = True if str(index) in _invert_font_info else False
        return [_color_code, _invert_font]


def main():
    """main program"""
    _color_schema = ColorSchema()
    _metadata = _color_schema.metadata
    _schema = _color_schema.get_schema_info(schema="accent")
    _colors, _invert_fonts = _color_schema.colors(num_colors=5)
    _color, _invert_font = _color_schema.color(5)

    pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    main()
