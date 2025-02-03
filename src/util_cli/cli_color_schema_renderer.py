"""Rendering the color schemas"""

import logging
import os
from typing import List, get_args

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table


from cli.bootstrap_config import console_maker
from cli.bootstrap_env import LOG_LEVEL
from util import constants as C
from model.model_visualizer import (
    ColorSchemaKey,
    ColorSchemaType,
    ColorSchemaData,
    ColorSchemaDataDict,
)
from util_cli.cli_color_schema import ColorSchema

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class ColorSchemaRenderer:
    """Rendering The Color Schemas in the Shell"""

    def __init__(
        self,
        schemas: List[ColorSchemaType],
        schema: ColorSchemaType = "spectral",
        show_hex: bool = False,
        min_value: int | float = None,
        max_value: int | float = None,
        reverse_schema: bool = False,
    ):
        """Constructor"""
        self._console: Console = console_maker.get_console()
        _schemas = get_args(ColorSchemaKey) if schemas is None else schemas
        self._schemas: List[ColorSchemaData] = _schemas
        self._color_schema = ColorSchema(schema, "hex", min_value, max_value, reverse_schema)
        self._show_hex = show_hex

    @property
    def console(self) -> Console:
        return self._console

    @property
    def color_schema(self) -> ColorSchema:
        """returns the color schema instance"""
        return self._color_schema

    def _render_color_bar(self, colors_dict) -> str:
        """render output string"""
        out = ""
        for _idx, (_color, _font_invert) in enumerate(colors_dict.items()):
            _fontcol = "black"
            if _font_invert:
                _fontcol = "white"
            if self._show_hex:
                _text = f" {str(_idx + 1).zfill(2)}({_color}) "
            else:
                _text = f" {str(_idx + 1).zfill(2)} "
            out += f"[{_fontcol} on {_color}]{_text}[/]"
        return out

    def _render_table(
        self, num_colors: int = 8, sort_by_num_colors: bool = False, sort_by_schema_set: bool = False
    ) -> Table:
        """render the colors in a table"""
        _table = Table(title=f"Color Schemas (Num Colors: {num_colors})", show_lines=True)
        # add column titles
        _table.add_column(header=f"Color Schema ({num_colors} colors)", style="white")
        _table.add_column(header="Schema", style="white", no_wrap=True)

        _color_schema_map: ColorSchemaDataDict = self._color_schema.get_color_schema_map(self._schemas)

        # sort dictionary by fields in any case
        _color_schema_map_sorted = dict(
            sorted(_color_schema_map.items(), key=lambda item: [getattr(item[1], "description")], reverse=False)
        )

        # sort by schema set
        if sort_by_schema_set:
            _color_schema_map_sorted = dict(
                sorted(
                    _color_schema_map_sorted.items(), key=lambda item: [getattr(item[1], "schema_set")], reverse=False
                )
            )

        # sort by number of colors in color set
        if sort_by_num_colors:
            _color_schema_map_sorted = dict(
                sorted(
                    _color_schema_map_sorted.items(), key=lambda item: [getattr(item[1], "num_colorset")], reverse=False
                )
            )

        for _schema, _schema_data in _color_schema_map_sorted.items():
            _num_colors = num_colors if num_colors <= _schema_data.num_max_colors else _schema_data.num_max_colors
            _color_dict = _schema_data.color_schema_map[str(_num_colors)]
            _description = _schema_data.description
            _encoding = _schema_data.encoding
            _description = f"{_description} [{_encoding}]"
            _colorbar = self._render_color_bar(_color_dict)
            _table.add_row(_description, _colorbar)
        return _table

    def render(
        self,
        num_colors: int = 8,
        sort_by_num_colors: bool = False,
        sort_by_schema_set: bool = False,
        show_hex: bool = None,
    ) -> None:
        """render the output table"""
        if isinstance(show_hex, bool):
            self._show_hex = show_hex
        _table = self._render_table(num_colors, sort_by_num_colors, sort_by_schema_set)
        self._console.print(_table)


# TODO PRIO4 add filter to only render certain color schemas


def main() -> None:
    """sample output when running directly"""
    _schemas: List[ColorSchemaType] = ["blues", "orrd"]
    _schema_renderer = ColorSchemaRenderer(schemas=None, show_hex=True, min_value=0, max_value=100, reverse_schema=True)
    _schema_renderer.render(num_colors=15, sort_by_num_colors=False, sort_by_schema_set=True, show_hex=False)
    _color_schema = _schema_renderer.color_schema
    _console = _schema_renderer.console
    _schema = "spectral"
    _console.print(f"SCHEMA {_schema}")
    for _value in range(0, 101, 5):
        _color, _invert = _color_schema.color_by_value(value=_value, num_colors=11, schema=_schema)
        _console.print(f"[{_color}]VALUE ({_value}/100), hex value {_color}")
    pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    # console python -m rich.markdown test.md
    main()
