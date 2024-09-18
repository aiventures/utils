""" Color Mapping.
"""

import logging
import os
from pathlib import Path
from typing import Any
from rich.table import Table
from rich.console import Console
from rich.logging import RichHandler

# TODO MOVE THIS TO A CONFIG FILE
from util.const_local import LOG_LEVEL
from util.persistence import Persistence
from cli.cli_color_maps import RGB_COLORS,HEX_COLORS,COLOR_NAMES

HEX = "hex"
ANSI = "ansi" # ansi ciodes not implemented yet
CODE = "code" # code 0-255
NAME = "name" # as in ANSI COLOR NAMES
RGB = "rgb"
BASE_HEX_COLORS = HEX_COLORS[:16]
BASE_RGB_COLORS = RGB_COLORS[:16]

logger = logging.getLogger(__name__)

# switch to 256 Colors as default
console = Console(color_system="256")

class ColorMapper():
    """ Class to handle Color Mappings """

    def _read_themes(self)->dict:
        """ reads themes for standard colors, returns theme dictionary """
        out = {}
        _f_themes = os.path.join(Path(__file__).parent,"themes.json")
        _themes = Persistence.read_json(_f_themes)
        for _theme in _themes:
            _name = _theme.get(NAME)
            if not _name:
                continue
            out[_name] = _theme
        return out

    def group_list(self,group_list,group_size):
        """ group a list into chunks """
        _num_elems = len(group_list)
        _num_iter = len(group_list) // group_size + 1
        out = []
        for i in range(_num_iter):
            _from = group_size *i
            _to = min(_num_elems,_from+group_size)
            out.append(group_list[_from:_to])
        return out

    def show_themes(self,num_columns:int=9)->None:
        """ displays all standard color themes grouped into tables """
        _standard_colors = COLOR_NAMES[:16]
        _themes = self._read_themes()
        _all_themes = list(_themes.keys())
        _all_themes = self.group_list(_all_themes,num_columns)

        for _themes_out in _all_themes:
            _table = Table(title=f"THEMES {_themes_out}")
            for _t in _themes_out:
                _table.add_column(_t,no_wrap=True,justify="left")

            for _c in _standard_colors:
                row = []
                for _t in _themes_out:
                    _theme = _themes.get(_t)
                    _hex = _theme[_c]
                    row.append(f"[{_hex}]{_c}")
                _table.add_row(*row)
            console.print(_table)

    def code2rgb(self,code:int)->str:
        """ convert code to rgb  """
        return self._rgb_colors[code]

    def code2name(self,code:int)->str:
        """ convert code to name """
        return COLOR_NAMES[code]

    def code2hex(self,code:int)->str:
        """ convert code to hex """
        return self._hexcolors[code]

    def rgb2name(self,rgb:tuple)->str:
        """ convert rgb to name """
        index = self.rgb2code(rgb)
        if index:
            return COLOR_NAMES[index]
        else:
            return None
        pass

    def rgb2hex(self,rgb:tuple)->str:
        """ convert rgb to hex """
        # https://forum.guvi.in/posts/7912/what-is-02x-and-how-it-works
        # "%02x" % 15
        # %: This indicates that we are using string formatting.
        # 0: This is the padding character, which, in this case, is a zero.
        # 2: This specifies the minimum width of the formatted string. In this case, it should be at least two characters wide.
        # x: This is the conversion type character, which means the integer will be formatted as a lowercase hexadecimal number.
        try: 
            return '#%02x%02x%02x' % rgb
        except TypeError:            
            logger.warning(f"[ColorMapper] Conversion failed for value [{rgb}] to HEX VALUE, no rgb tuple?")
            return None

    def rgb2code(self,rgb:tuple)->str:
        """ convert rgb to code """
        try:
            return self._rgb_colors.index(rgb)
        except ValueError:
            return None

    def name2rgb(self,name:str)->str:
        """ convert name to rgb  """
        index = self.name2code(name)
        if index:
            return self._rgb_colors[index]
        else:
            return None

    def name2hex(self,name:int)->str:
        """ convert name to hex """
        index = self.name2code(name)
        if index:
            return self._hexcolors[index]
        else:
            return None

    def name2code(self,name:int)->str:
        """ convert name to code """
        try:
            return COLOR_NAMES.index(name)
        except ValueError:
            return None

    def hex2rgb(self,chex:str)->str:
        """ convert hex to rgb  """
        # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        _chex = chex.lstrip('#')
        return tuple(int(_chex[i:i+2], 16) for i in (0, 2, 4))

    def hex2name(self,chex:str)->str:
        """ convert hex to name by getting its code in the lookkup table"""
        index = self.hex2code(chex)
        if index:
            return COLOR_NAMES[index]
        else:
            return None

    def hex2code(self,chex:str)->str:
        """ convert hex to code by finding its index"""
        try:
            return self._hexcolors.index(chex)
        except ValueError:
            return None

    def __init__(self,theme:str=None) -> None:
        self._code_map = {
            CODE:{RGB:self.code2rgb,NAME:self.code2name,HEX:self.code2hex},
            RGB:{NAME:self.rgb2name,HEX:self.rgb2hex,CODE:self.rgb2code},
            NAME:{RGB:self.name2rgb,HEX:self.name2hex,CODE:self.name2code},
            HEX:{RGB:self.hex2rgb,NAME:self.hex2name,CODE:self.hex2code},
            }
        self._name2code_dict = {}
        self._name2rgb_dict = {}
        self._name2hex_dict = {}
        self._code2hex_dict = {}
        self._hexcolors = HEX_COLORS
        self._rgb_colors = RGB_COLORS
        self._themes = {}
        self._theme = None
        if theme:
            self.theme = theme

    @property
    def theme(self):
        """ getter for theme """
        return self._theme

    @theme.setter
    def theme(self, theme:str):
        """ setter for theme """
        if not self._themes:
            self._themes = self._read_themes()

        if self._themes or theme is None:
            _theme_dict = self._themes.get(theme)
            if not _theme_dict:
                logger.info(f"[ColorMapper] Theme [{theme}] was not found, reset to base colors")
                self._theme = None
                _base_colors = BASE_HEX_COLORS
            else:
                self._theme = theme
                _base_colors = list(_theme_dict.values())[1:]

            for i in range(16):
                self._hexcolors[i] = _base_colors[i]
                self._rgb_colors[i] = self.hex2rgb(self._hexcolors[i])
        else:
            logger.warning(f"[ColorMapper] Configuration file was not found")

    @property
    def name2code_lut(self):
        """ get the lookup of names to code only instanciate if needed """
        if not self._name2code_dict:
            self._name2code_dict = dict(zip(COLOR_NAMES,range(256)))
        return self._name2code_dict

    @property
    def name2rgb_lut(self):
        """ get the lookup of names to rgb only instanciate if needed """
        if not self._name2rgb_dict:
            self._name2rgb_dict = dict(zip(COLOR_NAMES,RGB_COLORS))
        return self._name2rgb_dict

    @property
    def name2hex_lut(self):
        """ get the lookup of names to hex only instanciate if needed """
        if not self._name2hex_dict:
            self._name2hex_dict = dict(zip(COLOR_NAMES,HEX_COLORS))
        return self._name2hex_dict

    @property
    def code2hex_lut(self):
        """ get the lookup of names to code only instanciate if needed """
        if not self._code2hex_dict:
            self._code2hex_dict = dict(zip(range(256),HEX_COLORS))
        return self._code2hex_dict

    def convert(self,value:Any,to:str=HEX)->Any:
        """ Convert from one color code to the other, returns blank None if not available """
        _from = None
        if isinstance(value,int) and value < 256 and value >= 0:
            _from = CODE
        elif isinstance(value,str) and str(value).startswith("#"):
            _from =HEX
        elif isinstance(value,str):
            _from=NAME
        elif isinstance(value,tuple) or isinstance(value,list) and len(value) == 3:
            _from=RGB
        else:
            logger.warning(f"[ColorMapper] Invalid value [{value}] for color conversion, please check")
        try:
            return self._code_map[_from][to](value)
        except KeyError:
            if not to == _from:
                logger.warning(f"[ColorMapper] Conversion failed for value [{value}] from [{_from}] to [{to}], allowed {list(self._code_map.keys())}")
                return None
            return value

    def _rgb_colors_hex(self)->list:
        """ returns the rgb_colors as hex values """
        out = []
        for _rgb_col in RGB_COLORS:
            out.append(self.rgb2hex(_rgb_col))
            out.append(_rgb_col)
        return out

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    ColorMapper().show_themes()
    pass


