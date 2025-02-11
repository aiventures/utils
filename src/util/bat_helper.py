"""Utils in Conjunction with Bat Files"""

# import json
import logging
import os
import re
import sys

# from functools import wraps
# from pathlib import Path
# from rich import print_json
# from rich import print as rprint
from datetime import datetime as DateTime

from util import constants as C
from util.config_env import Environment
from util.persistence import Persistence
from util_cli.cli_color_mapper import ThemeConsole
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class BatHelper:
    """Commands for handling Bat Files"""

    def __init__(self, f_environment: str = None) -> None:
        """Constructor"""
        self._f_environment = f_environment
        self._environment = None
        if f_environment:
            self._environment = Environment(f_environment)

    @staticmethod
    def _create_comment_line():
        _timestamp = DateTime.now().strftime(C.DATEFORMAT_DD_MM_JJJJ_HH_MM_SS)
        _comment = f"rem created using bat_helper.py on {_timestamp}"
        return _comment

    def create_vars_template(self, f_out: str = None) -> str:
        """creates the cvar template, returns the absolute file path of created bat file"""
        return self._environment.create_env_vars_bat(f_out)

    # TODO CREATE COLOR CREATION TEMPLATE
    def create_colors_template(self, f_out: str = None, theme: str = None) -> str:
        """creates a default color env var template, optionally with a color theme"""
        _bat_set_list = ["SET C_0=%ESC%[0m"]
        _bat_echo_list = []
        _theme_console = ThemeConsole(theme)

        # is a key value dict for colors
        _color_map = _theme_console.color_map

        # ADD DEFAULT COLORS FROM THEME
        for col_key, _value in _color_map.items():
            _colkey = "C_" + col_key.upper()
            _value = _value.replace("ESC", "%ESC%")
            _cmd = f"SET {_colkey}={_value}"
            _show = f"ECHO %{_colkey}%ENV VAR [{_colkey}] THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG%C_0%"
            _bat_set_list.append(_cmd)
            _bat_echo_list.append(_show)

        _style_dict = _theme_console.read_styles()
        _esc_code_dict = _theme_console.get_esc_codes()

        for _style, _style_info in _style_dict.items():
            _esc_code = _esc_code_dict.get(_style)
            _env_var = _style_info.get(C.EnvType.BAT.value)
            if _esc_code is None or _env_var is None:
                continue
            _cmd = f"SET {_env_var}={_esc_code}"
            _show = f"ECHO %{_env_var}%ENV VAR [{_env_var}] THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG%C_0%"
            # replace the ESC Placeholder
            _cmd = _cmd.replace("ESC", "%ESC%")
            _show = _show.replace("ESC", "%ESC%")
            _bat_set_list.append(_cmd)
            _bat_echo_list.append(_show)
            pass
        _f_out = self._environment.create_set_vars_bat(
            f_out=f_out, bat_set_list=_bat_set_list, bat_echo_list=_bat_echo_list
        )

        return _f_out

    def create_env_file(
        self, key: str, value: str = None, p: str = None, prefix: str = "_tmp", quotes: bool = True
    ) -> str | None:
        """creates small environment file containing setting of an environment variable to a given path
        returns path to created file
        """
        if value is None and self._environment is not None:
            # get resolved ref or default value from config file
            value = self._environment.config_env.get_ref(key, fallback_value=True)
        if p is not None and not os.path.isdir(p):
            logger.warning(f"[BatHelper] Path [{p}] is not a valid path, check entry")
            return
        if p is None:
            p = os.getcwd()
        p = os.path.abspath(p)
        f = os.path.join(p, prefix + "_" + key.lower() + ".bat")
        if quotes:
            s = f'SET "{key}={value}"'
        else:
            s = f"SET {key}={value}"
        _comment = BatHelper._create_comment_line()
        Persistence.save_txt_file(f, f"{_comment}\n{s}")
        return f

    def get_env_files(self, p: str = None, prefix: str = "_tmp"):
        """get the env file list"""
        _files = Persistence.find(p_root_paths=p, root_path_only=True, include_files=f"^{prefix}.*.bat")
        return _files

    def read_env_files(self, p: str, prefix: str = "_tmp", as_dict: bool = False) -> dict | list:
        """reads all the set ... commands and extracts key value pairs
        optionally as dictionary with found files as key
        """
        out = {}
        _files = self.get_env_files(p, prefix)
        # regex to capture key value pairs with or without quotes
        # set  hugo_34="C:\ddd_dsxx"
        # set  "hugo_21=D:\ddd_dsxx
        # [^"]* matches any characters not being a quote / "? is zero or one quotes
        _re = re.compile('set\s+"?(.+)="?([^"]+)', re.IGNORECASE)
        # get the set vars
        for _f in _files:
            _lines = Persistence.read_txt_file(filepath=_f, comment_marker="rem")
            _out = {}
            for _line in _lines:
                _matches = _re.findall(_line)
                if len(_matches) == 0:
                    continue
                _key = _matches[0][0]
                _value = _matches[0][1]
                _out[_key] = _value
            logger.debug(f"[BatHelper] Read file [{_f}], Vars found {_out}")
            if as_dict:
                out[_f] = _out
            else:
                out.update(_out)

        return out

    def save_env_file(
        self, p: str = None, filename: str = "_envs.bat", prefix: str = "_tmp", quotes: bool = True
    ) -> str | None:
        """reading all env files and saving them to a collective env file
        returns path to created env file
        """
        # todo add comment
        _comment = BatHelper._create_comment_line()
        _out = [_comment]
        if not os.path.isdir(p):
            logger.warning(f"[BatHelper] Pile [{p}] is invalid, check")
            return
        # get all env files
        _env_dict = self.read_env_files(p, prefix=prefix)
        for _key, _value in _env_dict.items():
            if quotes:
                s = f'SET "{_key}={_value}"'
            else:
                s = f"SET {_key}={_value}"
            _out.append(s)
        f = os.path.join(p, filename)
        Persistence.save_txt_file(f, "\n".join(_out))
        if os.path.isfile(f):
            return f
        else:
            return None


if __name__ == "__main__":
    loglevel = CLI_LOG_LEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
