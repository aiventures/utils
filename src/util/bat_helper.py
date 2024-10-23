""" Utils in Conjunction with Bat Files """

import os
import sys
# import re
# import json
import logging
# from functools import wraps
# from pathlib import Path
# from rich import print_json
# from rich import print as rprint
# from datetime import datetime as DateTime
from util import constants as C
from util.config_env import Environment
from util_cli.cli_color_mapper import ThemeConsole
from util_cli.cli_color_mapper import ESC_MAP,RichStyle
from util.persistence import Persistence

logger = logging.getLogger(__name__)

class BatHelper():

    def __init__(self,f_environment:str=None) -> None:
        """ Constructor """
        self._f_environment = f_environment
        self._environment = None
        if f_environment:
            self._environment = Environment(f_environment)

    def create_vars_template(self,f_out:str=None)->str:
        """ creates the cvar template, returns the absolute file path of created bat file """
        return self._environment.create_env_vars_bat(f_out)
    
    # TODO CREATE COLOR CREATION TEMPLATE
    def create_colors_template(self,f_out:str=None,theme:str=None)->str:
        """ creates a default color env var template, optionally with a color theme """
        _bat_set_list = ["SET C_0=%ESC%[0m"]
        _bat_echo_list = []
        _theme_console = ThemeConsole(theme)
        _color_map = _theme_console.color_map
        
        # ADD DEFAULT COLORS FROM THEME
        _esc_color = ESC_MAP.get(RichStyle.COLOR)
        for col_key,_hexcol in _color_map.items():
            _colkey = "C_"+col_key.upper()
            _rgb = _theme_console.hex2rgb(_hexcol)
            _rgb = ";".join(map(str,_rgb))
            _esc_code = _esc_color.replace("R;G;B",_rgb)
            _esc_code = _esc_code.replace("ESC","%ESC%")
            _cmd = f"SET {_colkey}={_esc_code}"
            _show = f"ECHO %{_colkey}%ENV VAR [{_colkey}] THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG%C_0%"      
            _bat_set_list.append(_cmd)
            _bat_echo_list.append(_show)                  

        _style_dict = _theme_console.read_styles()
        _esc_code_dict = _theme_console.get_esc_codes()

        for _style,_style_info in _style_dict.items():
            _esc_code = _esc_code_dict.get(_style)
            _env_var = _style_info.get(C.EnvType.BAT.value)
            if _esc_code is None or _env_var is None:
                continue
            _cmd = f"SET {_env_var}={_esc_code}"
            _show = f"ECHO %{_env_var}%ENV VAR [{_env_var}] THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG%C_0%"
            # replace the ESC Placeholder
            _cmd = _cmd.replace("ESC","%ESC%")
            _show = _show.replace("ESC","%ESC%")
            _bat_set_list.append(_cmd)
            _bat_echo_list.append(_show)
            pass
        _f_out = self._environment.create_set_vars_bat(f_out=f_out,bat_set_list=_bat_set_list,
                                              bat_echo_list=_bat_echo_list)

        return _f_out
    
    def create_tmp_env_file(self,key:str,p:str=None,value:str=None)->str|None:
        """ creates small environment file containing setting of an environment variable to a given path
            returns path to created file
        """
        if value is None and self._environment is not None:
            value = self._environment.config_env.get_ref(key)
        if p is not None and not os.path.isdir(p):
            logger.warning(f"[BatHelper] Path [{p}] is not a valid path, check entry")
            return        
        if p is None:
            p = os.getcwd()
        p = os.path.abspath(p)
        f = os.path.join(p,"_tmp_"+key+".bat")
        s = f'SET "{key}={value}"'
        Persistence.save_txt_file(f,s)
        return f

    
if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
