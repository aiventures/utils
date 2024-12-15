""" Color Mapping.
    More on styles and theme manaager:
    Styles https://rich.readthedocs.io/en/stable/style.html
    Theme Manager https://pypi.org/project/rich-theme-manager/
"""

import logging
import os
from pathlib import Path
from enum import Enum
from typing import Any
from rich.table import Table
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich_theme_manager import Theme, ThemeManager
from copy import deepcopy

# TODO MOVE THIS TO A CONFIG FILE
from util import constants as C
from util.const_local import LOG_LEVEL
from util.persistence import Persistence
from util.utils import Utils
from util_cli.cli_color_maps import RGB_COLORS,HEX_COLORS,COLOR_NAMES, ANSI_VALUES
from util.matrix_list import MatrixList

HEX = "hex"
ANSI = "ansi" # ansi ciodes not implemented yet
CODE = "code" # code 0-255
NAME = "name" # as in ANSI COLOR NAMES
RGB = "rgb"
THEME = "theme"
THEMES = "themes"
DEFAULT = "default"
THEME_DEFAULT=C.ConfigBootstrap.CLI_DEFAULT_THEME.value
COLORS = "colors"
STYLES = "styles"
COLOR = "color"
TAGS = "tags"
STYLE_DESCRIPTION = "description"
P_RESOURCES = "resources"
P_RICH_THEMES = "rich_themes"
F_COLOR_THEMES = "color_themes.json"
F_STYLES = "styles.json"
BASE_HEX_COLORS = HEX_COLORS[:16]
BASE_RGB_COLORS = RGB_COLORS[:16]

class RichStyle(Enum):
    """ Rich Style Enum """
    COLOR = "color"
    BG_COLOR = "bgcolor"
    BOLD = "bold"
    UNDERLINE = "underline"
    ITALIC = "italic"
    REVERSE = "reverse"
    STRIKE = "strike"
    RESET = "reset"

    @staticmethod
    def values():
        """ returns list of values defined in Enum """
        return list(map(lambda c: c.value, RichStyle))

# MAP OF ESCAAPE CODES
# rgb colors are rgb codes in int
# https://en.wikipedia.org/wiki/ANSI_escape_code
ESC_MAP = {RichStyle.COLOR:"ESC[38;2;R;G;Bm",
           RichStyle.BG_COLOR:"ESC[48;2;R;G;Bm",
           RichStyle.BOLD:"ESC[22m",
           RichStyle.UNDERLINE:"ESC[24m",
           RichStyle.ITALIC:"ESC[23m",
           RichStyle.REVERSE:"ESC[27m",
           RichStyle.STRIKE:"ESC[29m",
           RichStyle.RESET:"ESC[0m",
           }

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

# switch to 256 Colors as default
# console = Console(color_system="256")

class ColorMapper():
    """ Class to handle Color Mappings """

    def _read_themes(self)->dict:
        """ reads themes for standard colors, returns theme dictionary """
        out = {}
        # TODO ALLOW TO CHANGE PATH in Constructor
        # self._f_color_themes = None
        _f_themes = os.path.join(self._f_color_themes)
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

    @property
    def themes(self)->dict:
        """ returns themes with color codes """
        return self._read_themes()

    def show_colors(self,num_colums:int=8,colors:list=None,console:Console=None)->None:
        """ displays all colors, you also my use filter strings """
        _color_list = []
        if colors is None:
            colors = []

        if console:
            _console = console
        else:
            _console = Console(color_system="256")

        _table = Table(title=f"Color Codes matching colors {colors}")
        _color_list_config = self.config["colors"]
        _keys = []
        _color_sort = {}
        if len(colors)==0:
            _color_sort["ALL"]=[]
            _color_list = _color_sort["ALL"]
        else:
            for f in colors:
                _color_sort[f] = []
        for _color in _color_list_config:
            name = _color[NAME]
            passed = True
            if len(colors) > 0:
                passed = False
                for c in colors:
                    if c in name:
                        _color_list = _color_sort[c]
                        passed = True
            if passed is False:
                continue

            s = f"[black on {_color[HEX]}]{str(_color[CODE]).zfill(3)} {_color[NAME]: <15}"
            _color_list.append(s)
        # get a sorted list of items
        _keys = []
        for v in _color_sort.values():
            _keys.extend(v)

        rows = self.group_list(_keys,num_colums)
        for row in rows:
            _table.add_row(*row)
        _console.print(_table)

    def show_themes(self,num_columns:int=9,console:Console=None)->None:
        """ displays all standard color themes grouped into tables """
        _standard_colors = COLOR_NAMES[:16]
        _themes = self._read_themes()
        _all_themes = list(_themes.keys())
        _all_themes = self.group_list(_all_themes,num_columns)
        if console:
            _console = console
        else:
            _console = Console(color_system="256")


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
            _console.print(_table)

    @staticmethod
    def _create_ansi_map():
        """ creates ansi array for later display """
        # https://hexdocs.pm/color_palette/color_table.html
        tables = []
        for _min_idx in [16,88,160]:
            _table = []
            for i in range(12):
                _idx = _min_idx + i*6
                _table.append(list(range(_idx,_idx+6)))
            _table = MatrixList.transpose_matrix(_table)
            tables.extend(_table)
        # basic colors and grey values
        _table=[[*list(range(8)),0,0,0,0],
                [*list(range(8,16)),0,0,0,0],
                list(range(232,244)),
                list(range(244,256))]
        tables.extend(_table)
        return tables

    @staticmethod
    def get_ansi_table(with_names:bool=True)->Table:
        """ creates map with ANSI codes  """

        def _render_col(ansi_code):
            if with_names:
                _s = f"[black on {HEX_COLORS[ansi_code]}] \[{str(ansi_code).zfill(3)}] \n{HEX_COLORS[ansi_code]}\n{COLOR_NAMES[ansi_code]}"
            else:
                _s = f"[black on {HEX_COLORS[ansi_code]}] \[{str(ansi_code).zfill(3)}] \n{HEX_COLORS[ansi_code]}"

            # _s = str(ansi_code)
            return _s

        _ansi_map = ColorMapper._create_ansi_map()
        table = Table(title="ANSI CODES",box=None)
        for _col in range(12):
            table.add_column(f"({str(_col).zfill(2)})", no_wrap=True)
        for _line in _ansi_map:
            _rendered = [_render_col(_ansi_code) for _ansi_code in _line]
            table.add_row(*_rendered)

        return table

    def code2rgb(self,code:int)->str:
        """ convert code to rgb  """
        return self._rgb_colors[code]

    @staticmethod
    def _ansi2rgb(ansi_code:int)->tuple:
        """ calculate the rgb tuple from ansi code """
        # rgb value is according to a base value
        # return default values for standard colors or grey values
        if ansi_code < 16 or ansi_code > 231:
            return RGB_COLORS[ansi_code]
        # calculate the rgb value (based on 6 values on color cube)
        ansi_code -= 16
        _rgb=Utils.get_base_int(ansi_code,6,inverse=True,length=3)
        _rgb=tuple([ANSI_VALUES[code] for code in _rgb])
        return _rgb

    @staticmethod
    def ansi2rgb(ansi_code)->tuple:
        """ get the rgb tuple for ansi code """
        return RGB_COLORS[ansi_code]

    @staticmethod
    def rgb2ansi(rgb:tuple)->int:
        """ create an ANSI color code for console out put
            Credits:
            https://github.com/Qix-/color-convert/blob/427cbb70540bb9e5b3e94aa3bb9f97957ee5fbc0/conversions.js#L555-L580
            https://stackoverflow.com/questions/15682537/ansi-color-specific-rgb-sequence-bash
        """
        r,g,b=rgb
        ansi = 0
        # gray values
        if ( r == g and r == b ):
            if r < 8:
                ansi = 16
            elif r > 231:
                ansi = 231
            else:
                ansi = int(round((r-8)/247) * 24 ) + 232
        # color values
        else:
            # color cube
            ansi = 16
            ansi += 6 * 6 * round((r/255) * 5)
            ansi += 6 * round((g/255) * 5)
            ansi += round((b/255) * 5)
        return int(ansi)

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

    def __init__(self,theme:str=None,p_resources:str=None) -> None:
        """ constructor
            theme: theme to set (defined in color_themes.json)
            p_resources: Configuration Path (defaults to /resources)
        """
        self._code_map = {
            CODE:{RGB:self.code2rgb,NAME:self.code2name,HEX:self.code2hex},
            RGB:{NAME:self.rgb2name,HEX:self.rgb2hex,CODE:self.rgb2code},
            NAME:{RGB:self.name2rgb,HEX:self.name2hex,CODE:self.name2code},
            HEX:{RGB:self.hex2rgb,NAME:self.hex2name,CODE:self.hex2code},
            }

        # set the configuration
        self._p_resources = p_resources
        self._f_color_themes = None
        self._set_config_path()

        self._hexcolors = HEX_COLORS
        self._rgb_colors = RGB_COLORS
        self._themes = []
        self._theme = None
        if theme:
            self._theme = theme
        # TODO APPLY DEFAULT THEME

    def _set_config_path(self):
        """ sets config path  """

        # set a default path
        if self._p_resources is None or not os.path.isdir(self._p_resources):
            self._p_resources = os.path.join(str(C.PATH_ROOT),"resources")
            logger.info(f"[ColorMapper] Setting resource path [{self._p_resources}]")

        self._f_color_themes = os.path.join(self._p_resources,F_COLOR_THEMES)
        if not os.path.isfile(self._f_color_themes):
            logger.warning("[ColorMapper] Couldn't find color theme file [{self._f_color_themes}]")
            self._f_color_themes = None

    @property
    def config(self)->dict:
        """ returns the configuration """
        out = {}
        out[THEME] = self._theme
        _colors = []
        for i in range(256):
            _colors.append({CODE:i,NAME:COLOR_NAMES[i],
                            HEX:self._hexcolors[i],
                            RGB:self._rgb_colors[i]})
        out[COLORS]=_colors
        out[THEMES] =self._read_themes()
        return out

    @property
    def theme(self):
        """ getter for theme """
        return self._themes

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

    def convert(self,value:Any,to:str=HEX)->Any:
        """ Convert from one color code to the other, returns blank None if not available
            Wraps all other conversion methods
        """
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

class ThemeConsole(ColorMapper):
    """" Handle Themes and rich Styles and create a themed console.
        themes are names the color mapping schemas in the class above
        style_... are the objects used in rich in conjunction with the themes
        defined there (so we have two separate things here)
    """

    def __init__(self, theme: str = None,color_system:str="256",create_themes:bool=False,p_resources=None) -> None:
        """Constructor.

        Args:
            theme (str, optional): Instanciate Console using theme.
            color_system (str, optional): The Color System as defined by rich . Defaults to "256".
            create_themes (bool, optional): Create the Rich Themes definition files in /resources/rich_themes.
            Defaults to False (needs to be run at least once).
        """

        super().__init__(theme,p_resources)

        # create a fallback theme
        _theme_env_default = os.environ.get(C.ConfigBootstrap.CLI_DEFAULT_THEME.name,C.ConfigBootstrap.CLI_DEFAULT_THEME.value)
        self._default_theme = _theme_env_default

        if theme is None:
            # try to bootstrap theme from OS (defined in /cli/bootstrap_env.py )
            _theme_env = os.environ.get(C.ConfigBootstrap.CLI_THEME.name)
            if _theme_env is None:
                _theme_env = _theme_env_default
            theme = _theme_env
            logger.debug(f"[ThemeConsole] Setting Theme from ENV/ENV_DEFAULT [{_theme_env}/{_theme_env_default}] to [{theme}]")

        self._color_system = color_system
        self._p_rich_themes = None
        self._set_rich_themes_path()

        # todo handle themes / instanciate theme manager
        self._theme_manager = None
        if create_themes:

            self._theme_manager = self.create_rich_themes()
        if not self._theme_manager:
            self._theme_manager = ThemeManager(theme_dir=self._p_rich_themes)
            self._themes = list(self._theme_manager._themes.keys())
        # validate theme
        if theme in self._themes:
            self._theme = theme
        else:
            logger.warning(f"[ThemeConsole] Invalid Theme [{theme}], allowed {self._themes},using default [{self._default_theme}]")
            self._theme = self._default_theme

    def get_esc_codes(self)->dict:
        """ returns the ANSI escape codes for the current theme """
        out = {}
        out["reset"]="ESC[0m"
        # get the color map and the styles from current theme
        # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
        # We need to transform the RGB code into ANSI Code (otherwise it seems not to be working
        # for BAT FILES, even as it's running with Rich)
        _esc_color = "ESC[38;5;ANSIm"
        _esc_bgcolor = "ESC[48;5;ANSIm"

        _theme = self._theme_manager.get(self._theme)
        _style_names = _theme.style_names
        _styles = _theme.styles
        _color_map = self.config.get("themes",{}).get(self._theme,{})
        for _style_name in _style_names:
            _esc_out=[]
            _style = _styles.get(_style_name)

            # resolve color to RGB values (convert ANSI Codes)
            _col_codes = []
            for _col in [_style.color,_style.bgcolor]:
                _col_code = None
                if _col is not None:
                    if _col.number is not None:
                        _col_code = _col.number
                    elif _col.triplet is not None:
                        _col_code = _col.triplet
                _col_codes.append(_col_code)
            _col = _col_codes[0]
            _col_bg = _col_codes[1]

            # add formattings

            # add front and back colors
            _style_cols = []
            if _col:
                _style_cols.append([_esc_color,_col])
            if _col_bg:
                _style_cols.append([_esc_bgcolor,_col_bg])

            for _style_col in _style_cols:
                _esc = _style_col[0]
                _col = _style_col[1]
                if isinstance(_col,int):
                    _ansi = str(_col)
                else:
                    _rgb = (_col.red,_col.green,_col.blue)
                    _ansi = str(ColorMapper.rgb2ansi(_rgb))
                _col_esc = _esc.replace("ANSI",_ansi)
                _esc_out.append(_col_esc)

            _style_map = ((_style.bold,"ESC[22m"),
                          (_style.underline,"ESC[24m"),
                          (_style.italic,"ESC[23m"),
                          (_style.reverse,"ESC[27m"),
                          (_style.strike,"ESC[29m"))
            for _style_opt in _style_map:
                if _style_opt[0] is None:
                    continue
                _esc_out.append(_style_opt[1])
            # add the resulting string to an output map
            out[_style_name]="".join(_esc_out)

        return out

    def read_styles(self)->dict:
        """ reads the styles file is existent """
        styles_dict = {}
        # TODO CHANGE LOCATION
        _f_styles = os.path.join(self._p_resources,F_STYLES)
        if os.path.isfile(_f_styles):
            styles_dict = Persistence.read_json(_f_styles)
            if isinstance(styles_dict,dict):
                logger.debug(f"[ThemeConsole] Read [{len(styles_dict)}] styles from [{_f_styles}]")
            else:
                styles_dict = {}
                logger.warning(f"[ThemeConsole] invalid data in styles file [{_f_styles}]")
        else:
            logger.warning(f"[ThemeConsole] invalid path to styles file [{_f_styles}]")
        return styles_dict

    # def _set_style_theme(self,theme:str=None)->None:
    #     """ setting the style theme """
    #     if theme in self.themes:
    #         self._style_theme = theme
    #     else:
    #         logger.warning(f"[ThemeConsole] Invalid Theme [{theme}],using default [{self._default_theme}] (valid:{self.themes})")
    #         self._style_theme = self._default_theme

    def preview_theme(self,theme:str=THEME_DEFAULT)->None:
        """ displays a theme """
        _themes = list(self.themes)
        try:
            _theme = self._theme_manager.get(theme)
            self._theme_manager.preview_theme(_theme)
        except ValueError:
            print(f"[ThemeConsole] No Theme named [{theme}], available {_themes} ")
            return

    def preview_themes(self)->None:
        """ show all availabkle themes """
        for _theme in self.themes:
            self.preview_theme(_theme)

    @property
    def color_map(self):
        """ get current color map for selected theme """
        return self.get_esc_codes()

    @property
    def theme(self):
        """ get current theme """
        return self._theme

    @property
    def themes(self):
        """ returns list of available themes """
        return self._themes

    @property
    def style_names(self)->dict:
        """ returns styles for currently selected theme """
        _theme = self._theme_manager.get(self._theme)
        return _theme.style_names

    def list_themes(self):
        """ shows the list of themes """
        self._theme_manager.list_themes()

    def create_rich_themes(self)->ThemeManager:
        """ parses the original thems and transforms them to rich themes if not created before
            returns the Theme Manage
        """
        if not self._p_rich_themes:
            logger.warning("[ThemeConsole] No valid path for Rich Themes, check configuration")
            return

        _themes = self._read_themes()
        _base_colors = COLOR_NAMES[:16]
        _rich_themes = []
        # reading the styles from a config file
        _rich_styles = self.read_styles()
        _default_color = _rich_styles.get(DEFAULT,{}).get(COLOR,"white")
        _style_list = RichStyle.values()

        for _theme_name,_theme_info in _themes.items():
            _description = f"Theme {_theme_name} generated using ThemeConsole"
            _theme = {NAME:_theme_name,STYLE_DESCRIPTION:_description}
            _styles = {}
            # create the default styles for the basic colors
            for _col_name in _base_colors:
                _color = _themes[_theme_name].get(_col_name,_default_color)
                _style = {}
                _style[COLOR]=_color
                _styles[_col_name]=Style(**_style)

            # now add the custom styles and replace any default colors by
            for _custom_style,_custom_info in _rich_styles.items():
                _custom_style_info = {}
                for _style in _style_list:
                    _value  = _custom_info.get(_style)
                    if _value is None:
                        continue
                    # try to get theme color otherwise use the existing one
                    if "color" in _style:
                        _style_col = _styles.get(_value)
                        if _style_col:
                            _value = _style_col.color.name
                    _custom_style_info[_style]=_value
                if len(_custom_info) > 0:
                    _styles[_custom_style] = Style(**_custom_style_info)

            _theme[STYLES]=_styles
            _theme[TAGS]=["os_theme"]

            logger.debug(f"[ThemeConsole] Creating Theme [{_theme_name}]")
            _rich_themes.append(Theme(**_theme))
        print(f"CREATED RICH STYLE THEMES IN [{self._p_rich_themes}]")
        return ThemeManager(theme_dir=self._p_rich_themes, themes=_rich_themes,overwrite=True)

    def _set_rich_themes_path(self):
        """" setting the rich themes folder as a subfolder of the resources folder """
        if os.path.isdir(self._p_resources):
            _p_rich_themes = os.path.join(self._p_resources,P_RICH_THEMES)
            if not os.path.isdir(_p_rich_themes ):
                Path(self._p_rich_themes).mkdir(parents=True)
            self._p_rich_themes = _p_rich_themes
        else:
            logger.warning("f[ThemeConsole] No valid resources path [{self._p_resources}], check your configuration")

    def get_console(self,theme:str=None,force_terminal:bool=None)->Console:
        """ returns a console with created theme """
        _theme_name = theme
        if not _theme_name in self._themes:
            logging.debug(f"[ThemeConsole] No theme was transferred, using initital theme")
            _theme_name = self._theme
        _theme = self._theme_manager.get(_theme_name)
        if theme is not None:
            self._theme = theme
        return Console(theme=_theme,force_terminal=force_terminal)

    def show_styles(self,theme:str=None)->None:
        """ prints the styles """
        _console = self.get_console(theme)
        _style_names = self.style_names
        for _style in _style_names:
            _console.print(f"[{_style}]\[STYLE {_style:<20}] THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])

    # # show color themes
    if False:
        ColorMapper().show_themes()
    # show color maps
    if False:
        ColorMapper().show_colors(num_colums=4)
        ColorMapper().show_colors(colors=["red","pink","coral","salmon","orange","yellow","gold","green","cyan","turq","blue","violet","purple","gray"])
        ColorMapper().show_colors(colors=["dark","medium","light","pale"])
    # handling via console
    if False:
        theme_console = ThemeConsole(create_themes=True)
        # theme_console._theme_manager.get()
        theme_console.list_themes()
        theme_console.preview_theme("ubuntu")
        # theme_console.preview_themes()
    # testing the themed console
    if False:
        _console_manager = ThemeConsole()
        _esc_codes = _console_manager.get_esc_codes()
        _theme = _console_manager.theme
        _themes = _console_manager.themes
        # print("### STYLES #########")
        _style_names = _console_manager.style_names
        print("### UBUNTU THEME  #########")
        _console_manager.show_styles(theme="ubuntu")
        print("### NEUTRON THEME #########")
        _console_manager.show_styles(theme="neutron")
        pass


# def test_theme():
#     k = {"color":"#126608","bold":False}
#     THEMES = [
#         Theme(
#             name="dark",
#             description="Dark mode theme",
#             tags=["dark"],
#             styles={
#                 # "info": Style(color="#126608",bold=True,reverse=False,link="hugo"),
#                 # "info": Style(color="#126608",bold=True,reverse=False,frame=True),
#                 "info": Style(**k),
#                 "yellow":"yellow2",
#                 "warning": "bold magenta",
#                 "danger": "bold red",

#         ),
#         Theme(
#             name="mono",
#             description="Monochromatic theme",
#             tags=["mono", "colorblind"],
#             styles={
#                 "info": "italic",
#                 "warning": "bold",
#                 "danger": "reverse bold",
#             },
#         ),
#     ]

#     # test = os.path.expanduser(".")
#     # pass

#     console = Console(theme=_theme)
#     # console.print("[info] this is a hugo test [warning] WARNING")
#     console.print("this is a hugo test WARNING",style="info")
#     # print("\n")

#     # console.print("This is information", style="info")
#     # console.print("[warning]The pod bay doors are locked[/warning]")
#     # console.print("Something terrible happened!", style="danger")

#     # pass
