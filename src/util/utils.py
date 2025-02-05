"""collection of utils"""

import configparser
import hashlib
import logging
import os
import platform
import re
import shlex
import subprocess
import sys
from os import lstat
import stat
import ctypes

from configparser import Error as ConfigParserError
from datetime import datetime as DateTime
from math import floor, inf, log
from pathlib import Path
from util import constants as C
from model.model_filter import AnyOrAllType, StringMatch, IncludeType, SimpleStrFilterModel

# from util.cmd_runner import CmdRunner
from util.persistence import Persistence

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# get a global variable since this might be used for any file operations
is_win = True if platform.system() == "Windows" else False

# environemnt variables (either from DOS or bash)

# TODO replace by config

# params for params conversion
ENV_NAME = "env_name"
OBJ_NAME = "obj_name"
P_WORK = "p_work"
F_WORK = "f_work"
F_SAVE = "f_save"
P_SAVE = "p_save"

# lstat data
PARENT = "parent"
VALUE = "value"
ROOT = "root"
FILES = "files"
PATHS = "paths"
SIZE = "size"
CHDATE = "chdate"
PERMISSION = "permission"
PERMISSION_CHMOD = "chmod"
IS_FILE = "is_file"
TOTAL_SIZE = "total_size"


class Utils:
    """util collection"""

    @staticmethod
    def simple_str_filter(s: str, str_filter: SimpleStrFilterModel) -> bool:
        """simple filter a string to filter against a list of strings"""
        # turn filter into a list
        if str_filter is None:
            return None
        _s = s
        if str_filter.case_insensitive:
            _s = s.lower()
        _matches = []
        match = None
        _str_filters = str_filter.str_filter
        if _str_filters is None:
            logger.warning("[Utils] No Filter was passed, string [{s}]")
            return None
        if isinstance(_str_filters, str):
            _str_filters = _str_filters.split(sep=str_filter.sep)
        if str_filter.case_insensitive:
            _str_filters = [_f.lower() for _f in _str_filters]
        if str_filter.match == "contains":
            _matches = [_f in s for _f in _str_filters]
        else:
            _matches = [_f == _s for _f in _str_filters]
        if str_filter.any_or_all == "any":
            match = any(_matches)
        else:
            match = all(_matches)
        if str_filter.include == "exclude":
            match = not match
        logger.debug(f"[Utils] String [{s}], matches [{_str_filters}], [{match}]")
        return match

    @staticmethod
    def get_short_win_path(path: str):
        """Returns Windows 8.3 Short Path without spaces"""
        # create a buffer and get the short path from Windows
        _buffer_size = 256
        try:
            _buffer = ctypes.create_unicode_buffer(_buffer_size)
            _get_short_path_name = ctypes.windll.kernel32.GetShortPathNameW
            _length = _get_short_path_name(path, _buffer, _buffer_size)

            if _length == 0:
                raise ctypes.WinError()

            return _buffer[:_length]
        except OSError as e:
            logger.warning(f"[Utils] error occured trying to get Windows 8.3 Short Path [{path}], [{e.args}]")
            return None

    @staticmethod
    def get_unspaced_path(path: str, quotes: bool = False, is_link: bool = False) -> str:
        """OS dependent resolve issues with spaces in path
        optionally surround with quotes
        WIN: get 8.3 Short path
        Other/Linux: add quotes
        """
        _s_link = ""
        if is_link:
            _s_link = "file://"

        _path = path
        if path[0] in ["'", '"'] and path[-1] == path[0]:
            _path = f"{_s_link}{_path[1:-1]}"

        _path = f"{_s_link}{_path}"

        # do not convert for unix
        if not " " in _path:
            return f"'{_path}'" if quotes else f"{_path}"

        if is_win:
            _path = f"{_s_link}{Utils.get_short_win_path(path)}"
        else:
            quotes = True  # override path setting

        return f'"{_path}"' if quotes else _path

    @staticmethod
    def is_list_or_tuple(obj):
        """check if item is list or tuple"""
        return isinstance(obj, (list, tuple)) and not isinstance(obj, str)

    @staticmethod
    def get_hash(s: str):
        """calculates a hash string of transferred string"""
        hash_object = hashlib.md5(s.encode())
        return hash_object.hexdigest()

    @staticmethod
    def split_string(s: str, n: int, fill: str = None) -> list:
        """splits a string into same length strings
        optionally fills up the last string with fill chars
        to match the same string length
        """
        num_chars = len(s)
        if fill:
            mod_s = num_chars % n
            s += [fill] * (n - mod_s)
            num_chars = len(s)
        return [s[i : i + n] for i in range(0, num_chars, n)]

    @staticmethod
    def get_lstat_metadata(p: str) -> dict:
        """adds metadata to output dict from meta lstat data"""
        out = {}

        try:
            _lstat = lstat(p)
            _st_mode = _lstat.st_mode
            if stat.S_ISREG(_st_mode):
                out[IS_FILE] = True
            elif stat.S_ISDIR(_st_mode):
                out[IS_FILE] = False
            else:
                out[IS_FILE] = None
            out[SIZE] = _lstat.st_size
            _permission = Utils.parse_st_mode(_lstat.st_mode)
            out[PERMISSION_CHMOD] = _permission[0]
            out[PERMISSION] = _permission[1]
            out[CHDATE] = DateTime.fromtimestamp(_lstat.st_ctime)
        except OSError:
            logger.error(f"[FileTree] {p} is not a valid path")
            _meta = None
        return out

    @staticmethod
    def parse_st_mode(st_mode: int) -> tuple:
        """parses st_mode from the os lstat module
        User-Group-Others
        4: Read permission
        2: Write permission
        1: Execute permission
        0: No permission
        """
        permissions_rwx = ""
        permissions_chmod = ""
        for i in range(3):
            _chmod = 0
            # r
            permission = True if st_mode & (0o400 >> (i * 3)) else False
            if permission:
                _chmod += 4
                permissions_rwx += "r"
            else:
                permissions_rwx += "-"
            # w
            permission = True if st_mode & (0o200 >> (i * 3)) else False
            if permission:
                _chmod += 2
                permissions_rwx += "w"
            else:
                permissions_rwx += "-"
            # x
            permission = True if st_mode & (0o100 >> (i * 3)) else False
            if permission:
                _chmod += 1
                permissions_rwx += "x"
            else:
                permissions_rwx += "-"
            permissions_chmod += str(_chmod)
        return permissions_chmod, permissions_rwx

    @staticmethod
    def byte_info(x: int, short: bool = True, num_decimals: int = 1):
        """returns formatted size in bytes
        Parameters
        ----------
        x : int
            Byte size (integer)
        short: boolean, optional (default True)
            output as string or dictionary
        num_decimals: int, optional (default 1)
            number of decimals
        Returns
        -------
        str,dict
            depending on short flag, formatted string or dictionary with all conversion details
        """

        if x == 0:
            r = {}
            r["value_int"] = x
            r["power_int_1024"] = (-1) * inf
            r["power_frac_1024"] = 1
            r["value"] = 0
            r["units"] = ""
            r["text"] = "0 bytes"
            if short:
                return r["text"]
            else:
                return r

        ld_x = log(x, 2**10)  # exponent to base 1024
        exp_int = floor(ld_x)
        exp_frac = ld_x - exp_int
        # units = ("", "Kilo", "Mega", "Giga", "Tera", "Peta", "Exa", "Zetta", "Yotta")
        units = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
        value = (2**10) ** exp_frac
        text = str(round(value, num_decimals)) + " " + units[exp_int] + "B"
        if short:
            r = text
        else:
            r = {}
            r["value_int"] = x
            r["power_int_1024"] = exp_int
            r["power_frac_1024"] = exp_frac
            r["value"] = round(value, num_decimals)
            r["units"] = units[exp_int]
            r["text"] = text

        return r

    @staticmethod
    def trunc_string(s, start=19, end=19, s_length=40):
        """will format string and cut off in the middle parts if it exceeds length.
        will return a string of length s_length"""
        s_new = s
        fill_s = ".."
        len_fill = len(fill_s)
        len_s = len(s)
        # cut string
        if (len_s + len_fill) > s_length:
            s_start = s[:start]
            i_start_end = max([(len_s - end), start])
            s_end = s[i_start_end:]
            s_new = s_start + fill_s + s_end
            s_new = s_new[:s_length]

        return s_new.ljust(s_length)

    @staticmethod
    def get_nearby_index(value, sorted_list: list, debug=False) -> int:
        """returns index for closest value in a sorted list for a given input value,
        uses binary search
        """

        idx = -1
        idx_min = 0
        idx_max = len(sorted_list)
        idx_old = -2

        if (value is None) or (isinstance(sorted_list, list) and len(sorted_list) == 0):
            return None

        finished = False

        logger.debug(f"[Utils] Sorting List containing [{len(sorted_list)}] elements")

        # out of bounds will return a negative value
        if value > sorted_list[idx_max - 1]:
            finished = True
            idx = idx_max - 1

        elif value < sorted_list[0]:
            finished = True
            idx = 0

        while not finished:
            idx = idx_min + (idx_max - idx_min) // 2

            # converged / exact value not found
            if idx == idx_old:
                finished = True

            val_idx = sorted_list[idx]
            if val_idx < value:
                idx_min = idx
            elif val_idx > value:
                idx_max = idx
            else:
                finished = True

            idx_old = idx
            logger.debug(f"[Utils] Current Index [{idx}]")

        return idx

    @staticmethod
    def read_ini_config(f_config: str) -> dict:
        """reads configuration from a config file in INI format"""
        # https://docs.python.org/3/library/configparser.html
        # https://stackoverflow.com/questions/1773793/convert-configparser-items-to-dictionary
        if not os.path.isfile(f_config):
            logger.warning(f"[UTILS] File [{f_config}] is not a file to be used for INI Configuration")
            return
        _config = configparser.ConfigParser()
        try:
            _config.read(f_config)
        except ConfigParserError:
            logger.warning(f"[UTILS] File [{f_config}] can't be parsed as INI Configuration)")
            return

        return {_section_name: dict(_config[_section_name]) for _section_name in _config.sections()}

    @staticmethod
    def get_base_int(num: int, base: int = 16, inverse: bool = True, length: int = None) -> list:
        """creates the  number representation to a given base
        list will be sorted according to base (opposite to number representation)
        num = i*1 + j*base + k*base^2 + ... if inverse is set result will be reversd
        """
        out = []
        _num_left = num
        _finished = False
        while _finished is False:
            _mod = _num_left % base
            out.append(_mod)
            _num_left = _num_left // base
            if _num_left < base:
                out.append(_num_left)
                _finished = True
        # get number of zeros to be appended
        zeros = []
        if length and len(out) < length:
            zeros = [0] * (length - len(out))
            out.extend(zeros)
        if inverse:
            out.reverse()
        return out

    @staticmethod
    def split(args, platform: str = None):
        """shlex not really works on win so convert paths using a
        custom method, credit:
        https://stackoverflow.com/questions/69909487/taming-shlex-split-behaviour
        Like calling shlex.split, but sets `posix=` according to platform
        and unquotes previously quoted arguments on Windows
        :param args: a command line string consisting of a command with arguments,
                     e.g. r'dir "C:\Program Files"'
        :param platform: a value like os.name would return, e.g. 'nt'
        :return: a list of arguments like shlex.split(args) would have returned
        TODO maybe switch to asyncio in the future ...
        """
        if platform is None:
            if Utils.is_windows():
                platform = C.ENV_WINDOWS
            else:
                platform = C.ENV_UNIX_STYLE
        elif platform != C.ENV_WINDOWS:
            platform = C.ENV_UNIX_STYLE

        if platform == C.ENV_WINDOWS:
            _arg_list = shlex.split(args, posix=False)
        else:
            _arg_list = shlex.split(args)

        # there is a case to strip leading quotes
        # _split_args = [a[1:-1].replace('""', '"') if a[0] == a[-1] == '"' else a for a in _arg_list]
        return _arg_list

    @staticmethod
    def analyze_path(p: str) -> list:
        """checks, whether a path can be interpreted as certain path types
        (max 8 chars per path and no spaces in it)
        doesn't check the existence of path
        """
        _path_types = []
        _p_test = p
        # check for spaces
        if " " in p:
            _path_types.append(C.FileFormat.SPACE)

        # check for quotes
        if p.startswith('"') or p.startswith("'"):
            if p.endswith('"') or p.endswith("'"):
                _path_types.append(C.FileFormat.QUOTE)
                _p_test = _p_test.replace('"', "")
                _p_test = _p_test.replace("'", "")

        # check for slash indicating unc type
        if "/" in _p_test:
            _path_types.append(C.FileFormat.UNC)
        if "\\" in _p_test:
            _path_types.append(C.FileFormat.WIN)
        # if there is no slashes then it is a file in native format
        if not ("\\" in _p_test or "/" in _p_test):
            if Utils.is_windows():
                _path_types.append(C.FileFormat.WIN)
            else:
                _path_types.append(C.FileFormat.UNC)

        # check for backslash indicating win type
        _elems_win = _p_test.split("\\")
        if len(_elems_win) > 1:
            # test for any spaces or path elements
            if not " " in _p_test:
                _max_len = max([len(e) for e in _elems_win])
                if _max_len <= 8:
                    _path_types.append(C.FileFormat.DOS)
        return _path_types

    @staticmethod
    def resolve_path(
        p: str, check_exist: bool = True, transform_rule: str = None, info: bool = False, quotes: bool = True
    ) -> str | dict:
        """(ugly) Guess Path by parsing, transform on request.

        Args:

            p (str): path / file string
            check_exist (bool, optional): checks if file exists. Defaults to False.
            If true file needs to exist otherwise None will be returned
            transform_rule (C.FileFormat, optional): target format.
            Defaults to None (supported values are Keys of FileFormat: WIN, UNC, DOS, OS)
            Always tries to return absolute path or a dict containing file information
            NOTE: dos conversion wil only work for existing file objects
        """

        if transform_rule is None:
            logger.info(f"[Utils]No tranformation rule supplied for conversion of Path [{p}]")
            return None
        _transform_rule = transform_rule.upper()

        _test_path = p
        _real_path = None
        _path_types = []
        # get os specific params
        _sep_native = os.sep
        _os = ""

        if Utils.os_system() == C.ENV_WINDOWS:
            _os = "WIN"
            _native_file_convert = C.CygPathCmd.UNC2WIN.name
        else:
            _os = "UNC"
            _native_file_convert = C.CygPathCmd.WIN2UNC.name

        # try to guess type from path signatures
        # _path_types = Utils.analyze_path(_test_path)

        # 1. replace any quote occurrences
        if '"' in _test_path:
            _test_path = _test_path.replace('"', "")
        if "'" in _test_path:
            _test_path = _test_path.replace("'", "")

        # 2. Get the transformation rule
        try:
            _convert_rule = C.FORMAT_MAP[_os][transform_rule]
            if _transform_rule == "OS":
                _convert_rule = _native_file_convert
        except KeyError:
            logger.warning(
                f"[UTILS] No transform of path [{p}], transform rule [{transform_rule}] invalid (WIN, UNC, DOS, OS)"
            )
            return None

        # 3. Get absolute path in native OS
        _path_converter = PathConverter()
        kwargs = {C.CYGPATH_PATH: _test_path, C.CYGPATH_CONV: _native_file_convert}
        _native_path = _path_converter.convert(**kwargs)

        # 4. Get absolute path from transformation
        if _convert_rule == _native_file_convert:
            _converted_path = _native_path
        else:
            kwargs = {C.CYGPATH_PATH: _test_path, C.CYGPATH_CONV: _convert_rule}
            _converted_path = _path_converter.convert(**kwargs)

        # 5. If check for absolute path is done check for existing dir / file
        #    Using native file path
        if check_exist:
            if os.path.isfile(_native_path) or os.path.isdir(_native_path):
                _real_path = _native_path
            if _real_path is None:
                logger.warning(f"[Utils] path [{p}] doesn't exist, return None")

        _quoted = f'"{_converted_path}"'

        # 6. return transformed path or the dict
        if info:
            # TODO define variables
            out = {
                "OS": _os,
                "RULE": _transform_rule,
                "CONVERTED": _converted_path,
                "QUOTE": _quoted,
                "ORIGINAL": p,
                "REAL_PATH": _real_path,
            }
        else:
            if check_exist and _real_path is None:
                out = None
            else:
                if quotes:
                    out = _quoted
                else:
                    out = _converted_path

        return out

    @staticmethod
    def is_windows() -> bool:
        """flag whether running under windows"""
        return Utils.os_system() == "Windows"

    @staticmethod
    def os_system() -> str:
        """returns OS platform"""
        # https://docs.python.org/3/library/platform.html
        # platform.uname()._asdict
        return platform.system()  # Linux, Windows, JAva ...

    @staticmethod
    def date2xls_timestamp(d: DateTime) -> int:
        """returns int representaion of Date object"""
        days_passed = (d - DateTime(1970, 1, 1)).days
        return C.DATE_INT_19700101 + days_passed

    @staticmethod
    def get_venv(**kwargs) -> str:
        """gets the venv variable if a venv is activated"""
        logger.debug("[Utils] determine VENV from python Version")
        _python = Utils.get_python(**kwargs)
        if not _python:
            logger.debug("[Utils] No Python Version was found")
        if not "scripts" in _python.lower():
            logger.warning(f"[Utils] Seems like no VENV Python Version was found [{_python}]")
            return None
        return Path(_python).parent.parent.stem

    @staticmethod
    def get_branch(**kwargs) -> str:
        """gets the git branch if there is a git repo"""
        # try to get the head file in git subfolder
        _f_head = os.path.join(kwargs.get(P_WORK, os.getcwd()), ".git", "HEAD")
        if not os.path.isfile(_f_head):
            logger.warning(f"[Utils] Couldn't locate file [{_f_head}]")
            return None
        _branch_line = Persistence.read_txt_file(_f_head)[0]
        branch = _branch_line.split("/")[-1]
        logger.debug(f"[Utils] Path [{_f_head}], Branch [{branch}]")
        return branch

    @staticmethod
    def where(cmd: str, to_string: bool = True, re_prefered: str = None) -> str | list:
        """tries to find executables using where command (you need to ensure where command is on PATH
        optionally allows to searc1h for a preferred version of an executable
        """
        _cmd_list = CmdRunner().cmd(os_cmd=f"where {cmd}", as_string=False)
        # validate if it is a file
        _valid = False
        # find a prefered version
        _prefered = None
        if re_prefered is not None:
            _prefered_cmds = []
            for _cmd in _cmd_list:
                _prefered = re.findall(re_prefered, _cmd, re.IGNORECASE)
                if len(_prefered) > 0:
                    _prefered_cmds.extend(_prefered)
            if len(_prefered_cmds) > 0:
                _cmd_list = _prefered_cmds

        if len(_cmd_list) > 0:
            _valid = all([os.path.isfile(c) for c in _cmd_list])
        if not _valid:
            logger.warning(
                f"[Utils] Couldn't locate where command when trying to find [{cmd}].Ensure where is set on your PATH"
            )
            return C.INVALID

        if to_string:
            if len(_cmd_list) == 0:
                return None
            if len(_cmd_list) == 1:
                return _cmd_list[0]
            else:
                # TODO add crtieria configuration to pick a preferred version
                logger.warning(f"[Utils] More than 1 executables for [{cmd}] found {_cmd_list}, returning 1st entry")
                return _cmd_list[0]
        else:
            return _cmd_list

    @staticmethod
    def get_executable(
        cmd: str, conversion: str = C.CygPathCmd.NO_CONV.name, quotes: bool = False, re_prefered: str = None
    ) -> str:
        """gets an executable in correct file format
        Args:
            cmd (str): Command / Executable (Defined as in CMD)
            format (str): Output format (as defeind in C.CygPathCmd)
            quotes (bool): Enclose Command in quotes (might be relevant in Windows with PAths containing spaces)
        """
        executable = Utils.where(cmd, to_string=True, re_prefered=re_prefered)
        if executable is None:
            return None

        # format executable into a target format
        if conversion and conversion != C.CygPathCmd.NO_CONV.name:
            _params = {C.CYGPATH_PATH: executable, C.CYGPATH_CONV: conversion}
            # TODO convert to target format

        if quotes:
            executable = f'"{executable}"'

        return executable

    @staticmethod
    def get_git(**kwargs) -> str:
        """gets availabe git versions with a preference for the version in cmd"""
        # https://stackoverflow.com/questions/8947140/git-cmd-vs-git-exe-what-is-the-difference-and-which-one-should-be-used
        # TODO

    @staticmethod
    def get_python(**kwargs) -> str:
        """gets the most likely python version
        - python from an environment
        - installed python
        - any other first python version
        """
        # gets the python versions
        _python_list = Utils.where(C.Cmd.PYTHON.value, to_string=False)
        _python_executables = {}
        # prioritize python versions
        n = 2
        for _python in _python_list:
            if "Scripts" in _python:  # this is an activated venv
                _python_executables[1000] = _python
            elif "WindowsApps" in _python:  # Installed by MS has lowest prio
                _python_executables[1] = _python
            else:  # everything else
                _python_executables[n] = _python
                n += 1
        if len(_python_executables) == 0:
            logger.warning("[Utils] No Python Version was found")
            return None
        python_out = _python_executables.get(max(list(_python_executables.keys())))
        logger.debug(f"[Utils] Python version found [{python_out}]")
        return python_out

    @staticmethod
    def cygpath_convert(**kwargs) -> str:
        """Convert to any of cygpath supported output strings
        Returns:
            str: Converted Cyg Path
        """

        _conv_object = None
        _conv_path = kwargs.get(P_WORK)
        if _conv_path:
            _conv_object = _conv_path
        # file takes precedence over path
        _conv_file = kwargs.get(F_WORK)
        if _conv_file:
            _conv_object = _conv_file

        if not _conv_object:
            logger.info("[Utils] No Objects transferred to convert file objects using cygpath")
            return None

        _conv_args = {C.CYGPATH_PATH: _conv_object, C.CYGPATH_CONV: kwargs.get(C.CYGPATH_CONV)}
        converted_path = PathConverter().convert(**_conv_args)
        return converted_path

    @staticmethod
    def convert(
        obj: str,
        p_work: str = None,
        f_work: str = None,
        p_save: str = None,
        save: bool = True,
        file_conversion: str = C.CygPathCmd.NO_CONV.name,
    ) -> str:
        """Retrieves and Creates env vars

        Args:
            obj(str, optional): conversion object, will be checked against Enum to ensure proper validation method (C.Conversion)
            p_work (str, optional): work directory. If None, current directory will be used
            f_work (str, optional): work file. If None, it will be ignored
            p_save (str, optional): save directory. If None, current directory will be used
            conversion (CygPathCmd): covert any files to another path output format )
            save (bool, optional): save Flag. (info will be saved using env_name)

        Returns:
            str: _description_
        """

        conversion_key = C.Conversion.get_enum(obj)

        # File Name To Save
        f_save = conversion_key.value
        # initialize and validate all paths
        _f_save = os.path.join(os.getcwd(), f_save) if p_save is None else os.path.join(p_save, f_save)
        _p_work = os.getcwd() if p_work is None else p_work
        if not Path(_f_save).parent.is_dir():
            logger.warning(f"[Utils] save path [{p_save}] invalid")
            return None
        # Delete if it exists already
        if save and os.path.isfile(_f_save):
            os.remove(_f_save)

        # get the function using the other params and call it with all vars
        kwargs = {
            ENV_NAME: conversion_key,
            P_WORK: _p_work,
            F_WORK: f_work,
            F_SAVE: _f_save,
            P_SAVE: p_save,
            C.CYGPATH_CONV: file_conversion,
        }
        value = _ENV_MAP[conversion_key](**kwargs)
        if conversion_key in [C.Conversion.PYTHON, C.Conversion.CYGPATH]:
            if file_conversion is not None and file_conversion in C.CygPathCmd.get_names():
                _conv_args = {C.CYGPATH_CONV: file_conversion, C.CYGPATH_PATH: value}
                _path_transformed = PathConverter().convert(**_conv_args)
                value = _path_transformed

        if save:
            Persistence.save_txt_file(_f_save, value)
        return value


# map var to calculation method
_ENV_MAP = {
    C.Conversion.VIRTUAL_ENV: Utils.get_venv,
    C.Conversion.GIT_BRANCH: Utils.get_branch,
    C.Conversion.PYTHON: Utils.get_python,
    C.Conversion.CYGPATH: Utils.cygpath_convert,
}


class PathConverter:
    """converting paths into different path formats using CYGPATH (delivered in cyg with GIT standard intallation)
    put into utils class due to circular import issue
    https://cygwin.com/cygwin-ug-net/cygpath.html
    """

    def __init__(self) -> None:
        self._cmd_cygpath = Utils.get_executable(C.Cmd.CYGPATH.value)

        # self.cmd_cygpath = config.get_ref(CMD_CYGPATH)
        if self._cmd_cygpath is None:
            logger.error("[PathConverter] Couldn't find cygpath executable, check your path settings")
            return

    def convert(self, **kwargs) -> str:
        """convert passed path"""
        if self._cmd_cygpath is None:
            return None

        _path = kwargs.get(C.CYGPATH_PATH)
        if _path is None:
            logger.warning(f"[PathConverter] you didn't supply a path parameter [{C.CYGPATH_PATH}]")
            return None

        if self._cmd_cygpath is None:
            logger.warning("[PathConverter] Couldn't find cygpath executable, returning original path")
            return _path

        _convert_key = str(kwargs.get(C.CYGPATH_CONV))
        if _convert_key is None:
            logger.warning(f"[PathConverter] you didn't supply a convert key parameter [{C.CYGPATH_CONV}]")
            return None

        if _convert_key == C.CygPathCmd.NO_CONV.name:
            logger.debug(f"[PathConverter] No conversion for Path [{_path}]")
            return _path

        _convert_keys = C.CygPathCmd.get_names()
        if not _convert_key in _convert_keys:
            logger.warning(f"[PathConverter] convert key [{_convert_key}] is not one of [{_convert_key}]")
            return None

        _params = C.CygPathCmd[_convert_key].value

        # cygpath works with paths enclosed in quotes
        _path_wrap = f"{_path[0]}{_path[-1]}"
        if not (_path_wrap == '""' and _path_wrap == "''"):
            _path = f"'{_path}'"

        _cmd = f'"{self._cmd_cygpath}" {_path} {_params}'

        path_converted = str(CmdRunner().cmd(_cmd))
        # do not enclose in anything leave this up to the consumer
        return path_converted


class CmdRunner:
    """Cnd Runner: Runs OS Commands locally"""

    def __init__(self, cwd: str = None) -> None:
        """constructor"""
        self._output = None
        self._return_code = 0
        if not cwd:
            cwd = os.getcwd()
        if not os.path.isdir(cwd):
            logger.error(f"{cwd} is not a path, check input")
        self._cwd = os.path.abspath(cwd)

    @staticmethod
    def custom_win_split(s: str) -> str:
        """under windows, convert path objects"""
        # do not convert anytrhing on non Windows platforms
        if not Utils.is_windows():
            return shlex.split(s)

        _path_converter = PathConverter()

        # replace any quoted path objects with spaces in it by its short windows counterpart
        _new_command = s

        _paths = re.findall(C.REGEX_WIN_ABS_PATH_WITH_QUOTES_AND_BLANKS, s)
        if len(_paths) > 0:
            for _path in _paths:
                kwargs = {C.CYGPATH_PATH: _path, C.CYGPATH_CONV: C.CygPathCmd.WIN2DOS.name}
                _converted_path = _path_converter.convert(**kwargs)
                if _converted_path:
                    _new_command = _new_command.replace(_path, f'"{_converted_path}"')
                else:
                    logger.warning(
                        f"[CmdRunner] Couldn't resolve _path [{_path}] in [{s}], invalid or not created, pls check"
                    )
                    return None
        # now split into commands again and add quotes for each file object (shlex swallows backslashes for unquoted parts)
        _commands = _new_command.split()
        # for windows additionally add quotes to path objects
        out = []
        for _command in _commands:
            _command = _command.strip()
            # validate if it is a windows like absolute path / ugly quotes need to be replaced
            _is_os_object = any([os.path.isdir(_command.replace('"', "")), os.path.isfile(_command.replace('"', ""))])
            if _is_os_object:
                if not _command.startswith('"'):
                    _command = f'"{_command}"'
            else:
                _path_like = re.findall(C.REGEX_WIN_ABS_PATH, _command)
                # is path like but has no os representation
                if len(_path_like) > 0:
                    logger.warning(
                        f"[CmdRunner] Couldn't resolve _path [{_command}] in [{s}], is not a file object, pls check"
                    )
                    return None
            out.append(_command)
        return out

    def run_cmd(self, os_cmd: str, win_split: bool = False) -> int:
        """runs command line commandm
            since shlex will break windows os paths
            a custom routine can be activated using the win_split activation
            (has no effect on non Windows OS)

        Args:
            os_cmd (str): the command string to be parsewd
            win_split (bool, optional): use alwternative parsing routine for paths / files

        Raises:
            subprocess.CalledProcessError: When an error occurs

        Returns:
            int: return code (0 is ok)
        """

        logger.info(f"RUN COMMAND [{os_cmd}]")
        if not os_cmd:
            logger.warning("No command submitted, return")
            return
        if win_split:
            oscmd_shlex = CmdRunner.custom_win_split(os_cmd)
        else:
            oscmd_shlex = shlex.split(os_cmd)
        # special case: output contains keywords (in this case its displaying a logfile)
        self._output = []
        self._return_code = 0
        try:
            # encoding for german umlauts
            with subprocess.Popen(
                oscmd_shlex,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                errors="ignore",
                universal_newlines=True,
                encoding="utf8",
                cwd=self._cwd,
            ) as popen:
                for line in popen.stdout:
                    line = line.replace("\n", "")
                    self._output.append(line)
                    logger.info(line)

            # popen.stdout.close()
            if popen.stderr:
                logger.error(f"ERROR OCCURED: {popen.stderr}")

            self._return_code = popen.returncode
            if self._return_code:
                raise subprocess.CalledProcessError(self._return_code, os_cmd)
        except subprocess.CalledProcessError as e:
            self._return_code = 1
            logger.error(f"EXCEPTION OCCURED {e}, command {os_cmd}")
        return self._return_code

    def cmd(self, os_cmd: str, as_string=True, separator: str = "\n", win_split: bool = False) -> str | list:
        """shortcut to directly get results from a command routine
        Args:
            os_cmd (str):
            as_string (bool, optional): Return cd result as string. Defaults to True.
            separator (str, optional): Separator for concatenated result . Defaults to "\n".
            win_split (bool, optional): Alternative command splitting mode for Windows. Defaults to False.

        Returns:
            str|list: _cmd execution result
        """

        err_code = self.run_cmd(os_cmd, win_split)
        if err_code != 0:
            logger.error("[CmdRunner] There was an error running CmdRunner, check the logs")
            return None
        return self.get_output(as_string, separator)

    def get_output(self, as_string=True, separator: str = "\n"):
        """Returns output from last command
        Args:
            as_string (bool, optional): if True, output string list will be concatenated. Defaults to True.
        Returns:
            string/list: single output strings as list or concatenated string
        """
        out = self._output
        if as_string and isinstance(out, list):
            out = separator.join([l.strip() for l in out])
        return out


if __name__ == "__main__":
    loglevel = logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # get some environment variables from environment or from files
    out = Utils.convert(C.Conversion.VIRTUAL_ENV.name)
    out = Utils.convert(C.Conversion.GIT_BRANCH.name)
    out = Utils.convert(C.Conversion.PYTHON.name)
    if True:
        s = "test_string"
        hash = Utils.get_hash(s)
        pass
