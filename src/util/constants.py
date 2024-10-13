""" constants file """
from copy import deepcopy
from pathlib import Path
# from typing import Any
from util.abstract_enum import AbstractEnum
from logging import INFO as LOG_INFO

# TODO SWITCH TO PYDANTIC IN FUTURE
# Constants
FILE = "file"
PATH = "path"
HOME = "home"
OUTPUT = "output"
FORMATTED = "formatted"
LINE = "line"
RULES = "rules"
CMD = "cmd"
DESCRIPTION = "description"
NAME = "name"
VALUE = "value"
COLS = "cols" # columns
INDEX = "index"
EXPORT = "export"
EXAMPLE = "example"
# SUFFIX FOR CSV EXPORTS TO CREATE A DATE
DATEXLS = "_N"
INVALID = "INVALID"

# sdasving environment to files 
KEY_FILE_SUFFIX = "key"
ENV_FILE_SUFFIX = "env"

## PATHS and FILES

# default location of config file in home
FILE_CONFIGFILE_HOME=str(Path.home().joinpath(".cli_client","cli_config.json"))
# Project Paths
PATH_ROOT=Path(__file__).parent.parent.parent.absolute()

# bootstrap File Name
class ConfigBootstrap(AbstractEnum):
    """ bootstrap origins """
    CLI_CONFIG_ENV = "config_env"
    CLI_CONFIG_EXTERNAL = "config_external"
    CLI_CONFIG_HOME = "config_home"
    CLI_CONFIG_LOG_LEVEL = LOG_INFO
    CLI_CONFIG_DEMO = "DEMO"

# type definitions

class DataType(AbstractEnum):
    """ Enum for data types """
    INT = "int"
    FLOAT = "float"
    DATE = "date"
    DATEXLS = "datexls"
    STR = "str"
    CONFIG = "config" # config key
    PATH = "path" # path defined in a general way
    PATH_CMD = "path_cmd" # path var representing a path for a command, eg with quotes in win
    PATH_UNC = "path_unc" # path var as unc
    PATH_WIN = "path_win" # path var as win
    PATH_DOS = "path_dos" # path var as dos, eg without spaces and max 8 chars per path element


DATA_TYPES = DataType.get_values()

# REGEX FIELD NAME DEFINITIONS
class Rule(AbstractEnum):
    """Rule Types"""
    NAME="name"
    IGNORECASE="ignorecase"
    IS_REGEX="is_regex"
    RULE="rule"
    REGEX="regex"
    INCLUDE = "include"
    APPLY = "apply"
    # additional search attribute: rule for file object
    FILE = "rule_file"

RULE_NAME="name"
RULE_IGNORECASE="ignorecase"
RULE_IS_REGEX="is_regex"
RULE_RULE="rule"
RULE_REGEX="regex"
# Rule: Include or Exclude Result Entry (=Invert search result) / Default is True
RULE_INCLUDE = "rule_include"
# Rule for applying any or all rules
RULE_APPLY = "apply"

class RuleApply(AbstractEnum):
    """"Rule values for Rule Apply """
    ANY = "any"
    ALL = "all"

APPLY_ANY = "any"
APPLY_ALL = "all"
RULE_RESULTS = "results"
RULEDICT = {RULE_NAME:None,RULE_IGNORECASE:True,RULE_IS_REGEX:True,RULE_RULE:None,RULE_REGEX:None,RULE_APPLY:APPLY_ANY,RULE_INCLUDE:True}
# RULES FOR FILENAME SEARCH

# search in file name object
RULE_FILE = "rule_file"              # additional search attribute: rule for file object

class RuleFile(AbstractEnum):
    """"Rule values for Rule File """
    FILENAME = "filename"           # search in in filename only
    PATH = "path"                   # search in path
    ABSOLUTE_PATH = "absolute_path" # search in absolute path
    FILE_CONTENT = "file_content"

RULE_FILENAME = "filename"           # search in in filename only x
RULE_PATH = "path"                   # search in path x
RULE_ABSOLUTE_PATH = "absolute_path" # search in absolute path x
RULE_FILE_CONTENT = "file_content" # is a rule file

class RuleFileAttribute(AbstractEnum):
    """"Rule Attributes  for Rule File """
    # Path Objects
    ABSOLUTE = "files_absolute"         # attribute in search result dict: absolute path
    FILES = "files"                     # attribute in search result dict: file names
    FILE_LINE = "line"                  # file line in file
    # in file: look in complete text or line by line
    FIND_BY_LINE = "find_by_line"

# TODO REPLACE ATTRIBUTES
# Path Objects
FILES_ABSOLUTE = "files_absolute"    # attribute in search result dict: absolute path
FILES = "files"                      # attribute in search result dict: file names
FILE_LINE = "line"                   # file line in file
# in file: look in complete text or line by line
RULE_FIND_BY_LINE = "find_by_line"

# TODO REPLACE ATTRIBUTES
# search in content
RULEDICT_FILENAME = deepcopy(RULEDICT)
RULEDICT_FILENAME[RULE_FILE] = RULE_ABSOLUTE_PATH
RULEDICT_FILENAME[RULE_FIND_BY_LINE] = True

# TODO REPLACE ATTRIBUTES
# prefix and postfixes for search results to be used for formatting
RESULT_ANY_PREFIX_BEFORE = "#ANY1#"
RESULT_ANY_PREFIX_AFTER = "#ANY0#"
RESULT_ALL_PREFIX_BEFORE = "#ALL1#"
RESULT_ALL_PREFIX_AFTER = "#ALL0#"

# data dict definition

# definition of a data column
# name, value, description
# index: column index: index column to export
# export: flag, whther to export this column

# TODO REPLACE ATTRIBUTES
DATACOL = {NAME:None,VALUE:None,DESCRIPTION:None,INDEX:None,EXPORT:True}
DATADICT = {NAME:None,DESCRIPTION:None,RULE_IGNORECASE:True,RULE_IS_REGEX:True,RULE_RULE:None,COLS:{},EXAMPLE:None}

# supported file types
class FileType(AbstractEnum):
    """ File Types """
    FILETYPE_XLS = "xlsx"
    FILETYPE_CSV = "csv"
    FILETYPE_MD = "md"
    FILETYPE_TXT = "txt"
    FILETYPE_BAK = "bak"
    FILETYPE_YAML = "yaml"

# Supported file types for search
FILETYPES_SUPPORTED = FileType.get_values()

# CONFIG CONSTANTS FOR config_env.py
# for specification refer to the json sample
# it is possible to define paths or files or regex to define groups of files / paths as well
# it is also possible to plug in the configuration into the file_analzer

# JSON keys
class ConfigAttribute(AbstractEnum):
    """ Attributes in the Config File """
    PATH = "p"           # a path object reference
    FILE = "f"           # a file object reference
    DESCRIPTION = "d"    # one line documentation
    GROUPS = "g"         # a list of group this item belongs to
    REFERENCE = "ref"    # the resolved path or file path of this attribute if it can be resolved
    REGEX = "x"          # config should be treated as regex
    RULE = "r"           # rule dictionary for file_anaylzer / check the json how to use it
    COMMAND = "c"        # rule dictionary for command options
    DATA = "dd"          # data definition / structure definition
    SAMPLE = "s"         # sample / example data
    NAME = "n"           # name
    KEY = "k"            # key
    VALUE = "v"          # value
    WHERE = "w"          # path of a where executable
    FILEFORMAT = "ff"    # file format type
    TYPE = "t"           # (data) type
    EXPORT = "e"         # export map
    ENV = "env"          # environment settings, only some values are allowed and defined below
    ENV_TYPES = "et"     # environment types, controls behaviour how the env should be handled 
    DEPENDENCY = "dep"   # dependencies from other Attributes if there are some
    STATUS = "st"        # status of the configuration item
    ORIGINAL = "o"       # original value
    CONFIG_KEY = "kk"    # key used for config


class ConfigStatus(AbstractEnum):
    """ Status on processing / validity of a Configuration item """
    INITIAL = "initial" # initialized, but not final (eg replacement of placeholders pending)
    VALID = "valid"     # was checked and can be used
    INVALID = "invalid" # During Checking Routines there was an error

CONFIG_STATUS =  ConfigStatus.get_values()

# supported file types
class FileFormat(AbstractEnum):
    """ File Formats """
    DOS = "dos"
    WIN = "win"
    UNC = "unc"
    QUOTE = "quote" # contains quotes
    OS = "os" # same type as os
    SPACE = "space" # contains spaces

# FORMATTING MAP (used in resolve_path)
FORMAT_MAP = {"WIN":{"WIN":"UNC2WIN","DOS":"WIN2DOS","UNC":"WIN2UNC","OS":"OS"},
              "UNC":{"WIN":"UNC2WIN","DOS":"UNC2DOS","UNC":"WIN2UNC","OS":"OS"}}

FILE_FORMATS = FileFormat.get_values()

CONFIG_KEYS = ConfigAttribute.get_values()
# if this is set in path, then the current path is used
CONFIG_PATH_CWD = "CWD" # Underscore marker

class ConfigKey(AbstractEnum):
    """ Key Markers / Prefix may determine which type of file object is there
        ORDER in Enums is preserved so it can be used to introdice a sequence for processing
        of config items
    """
    ENV = "E_"   # ENV should mainly contain configuration stuff but also things like date and file format
    PATH = "P_"  # 1st resolve paths
    WHERE = "W_" # WHERE can be resolved next (maybe some paths from previous steps are required)
    FILE = "F_"  # FILES MIGHT COME NEXT
    CMD = "CMD_" # COMMANDS should be avle to be setup from all previous artefacts
    RULE = "R_"  # RULES only of declarative nature
    DATA = "D_"  # DATA are of declearative nature as well
    # (W)here OPtion, tries to automativally determine an executable using where command
    # list of file config types

    @classmethod
    def is_file_config_type(cls,key:str)->bool:
        """Checks if key is a file config type """
        file_config_types = [ConfigKey.PATH,ConfigKey.FILE,ConfigKey.WHERE,ConfigKey.CMD]
        _config_type = ConfigKey.get_configtype(key)
        if _config_type in file_config_types:
            return True
        else:
            return False

    @classmethod
    def get_configtype(cls,config_key:str)->AbstractEnum:
        """ return the corresponding enum for a given config key """
        # get the prefix and get the corresponding value
        _prefix = config_key.split("_")[0]+"_"
        try:
            return ConfigKey(_prefix)
        except ValueError:
            return None

CONFIG_KEY_TYPES = ConfigKey.get_values()

# TODO REPLACE ATTRIBUTES
# EXPORT FORMAT
EXPORT_CSV = "export_csv" # table of csv strings
EXPORT_DICT = "export_dict" # dict including json non compatible objects
EXPORT_JSON = "export_json" # json string
EXPORT_JSON_DICT = "export_json_dict" # json compatible dioct

# XLS INT of 1.1.1970
DATE_INT_19700101 = 25569
ENV_DATE_REF = "DATE19700101"

# TODO PUT INTO ENUM
# REGEX EXPRESSIONS USED
# regex to find all strings enclosed in brackets
REGEX_BRACKETS = r"\[.+?\]"
REGEX_BRACKET_CONTENT = r"\[(.+?)\]" # get the strings enclosed in brackets
REGEX_STRING_QUOTED_STR = "^\"(.+)?\"$"
# REGEX GLOBAL KEY: Find pattern in txt files to identify global keys
REGEX_GLOBAL_KEY = r"key:(.+)=(.+)"
# REGEX for absolute path with and without quoted including quotes
REGEX_WIN_ABS_PATH='[a-zA-Z]:\\\\.+'
REGEX_WIN_ABS_PATH_WITH_QUOTES=f'"{REGEX_WIN_ABS_PATH}"'
REGEX_WIN_ABS_PATH_WITH_QUOTES_AND_BLANKS=r'"[a-zA-Z]\:.+[ ]{1,}.*"'

# You may also set global keys that are not treated as values, but
# will be stored as ENVIRONMENT
# REGEX ENV KEY: Find pattern in txt files to identify env keys
# REGEX_ENV_KEY = r"env:(.+)=(.+)"
# only allow defined variables as some programming logic relies upon it
# DATEFORMATS
# Default Dateformat for parsing DateTime from/to String
ENV_DATE_FORMAT = "DATE_FORMAT"
DATEFORMAT_DD_MM_JJJJ= "%d.%m.%Y"
DATEFORMAT_JJJJMMDD= "%Y%m%d"

# TODO REPLACE ATTRIBUTES
DATEFORMAT_DD_MM_JJJJ_HH_MM_SS= "%Y-%m-%d %H:%M:%S"
# Separator used for CSV export
ENV_DEC_SEPARATOR = "DEC_SEPARATOR"
ENV_DEC_SEPARATOR_DEFAULT = "."
# Wrap Character for CSV export
ENV_CSV_WRAP_CHAR = "CSV_WRAP_CHAR"
ENV_CSV_WRAP_CHAR_DEFAULT = '"'
# Allowed ENV VARS FOR CSV_PARSER
ENV_VARS = [ENV_DEC_SEPARATOR,ENV_DATE_FORMAT,ENV_DATE_REF,ENV_CSV_WRAP_CHAR]
CSV_PARSER_ENV_VARS = [ENV_DEC_SEPARATOR,ENV_DATE_FORMAT,ENV_DATE_REF,ENV_CSV_WRAP_CHAR]
ENV_WINDOWS = "Windows"
ENV_UNIX_STYLE = "Unix"

class Env(AbstractEnum):
    """" Some Default Env Variables (with default values that can be overwritten by configuration) """
    # default date formats
    DATEFORMAT_DD_MM_JJJJ_HH_MM_SS= "%Y-%m-%d %H:%M:%S"
    DATEFORMAT_JJJJMMDD= "%Y%m%d"
    # XLS INT VALUE of 1.1.1970
    DATE_INT_19700101 = 25569
    # Separator used for CSV export
    DEC_SEPARATOR = ","
    # Wrap Character for CSV export
    CSV_WRAP_CHAR = '"'

class EnvType(AbstractEnum):
    """" Environment types determine how these are handled
         (only used internally, as OS environment, as Cofig Valu to be
         saved on filesystem)
    """
    # as env attribute of a config key 
    ATTRIBUTE = "attribute"    
    # only to be used within the program
    INTERNAL = "internal"
    # published in the OS environment
    OS_ENVIRON = "os_environ"
    # value to be stored in an envfile (key value pairs separated by equal sign)
    ENV_FILE = "env_file"    
    # keyfile a file to be stored with value in a file and name of file = variable name
    KEY_FILE = "key_file"
    # environment to be stored in an bat file
    BAT = "bat"
    # invalid
    INVALID = "invalid"


ENV_TYPES = EnvType.get_values()

# list of CYGPATH Transformations

# TODO REPLACE ATTRIBUTES
# param definitions
CYGPATH_PATH = "path"
CYGPATH_CONV = "file_conversion"

class CygPathCmd(AbstractEnum):
    """ CygPath Command Line params """
    WIN2UNC = "--unix --absolute"
    WIN2DOS = "--dos --absolute"
    DOS2UNC = "--unix --absolute"
    UNC2WIN = "--windows --absolute" # like --windows, but with regular slashes (C:/WINNT)
    UNC2MIX = "--mixed --absolute"
    UNC2DOS = "--dos --absolute"
    NO_CONV = "no_conversion"

class Conversion(AbstractEnum):
    """ Enum containing available Conersions from environment, functions etc """
    VIRTUAL_ENV = "VENV.ENV"
    GIT_BRANCH  = "BRANCH.ENV"
    PYTHON      = "PYTHON.ENV"
    CYGPATH     = "CYGPATH.ENV"

class EnvName(AbstractEnum):
    """ environemnt variable names """
    VIRTUAL_ENV = "VIRTUAL_ENV"

class Cmd(AbstractEnum):
    """ Known Commmamnds variables """
    PYTHON = "python"
    CYGPATH = "cygpath"
    GIT = "git"
    VENV = "venv"




