""" constants file """
from copy import deepcopy
from typing import Any
from util.abstract_enum import AbstractEnum

# TODO SWITCH TO PYDANTIC IN FUTURE
# Constants
FILE = "file"
PATH = "path"
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
# type definitions

TYPE_INT = "int"
TYPE_FLOAT = "float"
TYPE_DATE = "date"
TYPE_DATEXLS = "datexls"
TYPE_STR = "str"
TYPES = [TYPE_STR,TYPE_INT,TYPE_FLOAT,TYPE_STR,TYPE_DATE,TYPE_DATEXLS]

# REGEX FIELD NAME DEFINITIONS
RULE_NAME="name"
RULE_IGNORECASE="ignorecase"
RULE_IS_REGEX="is_regex"
RULE_RULE="rule"
RULE_REGEX="regex"
# Rule: Include or Exclude Result Entry (=Invert search result) / Default is True
RULE_INCLUDE = "rule_include"
# Rule for applying any or all rules
RULE_APPLY = "apply"
APPLY_ANY = "any"
APPLY_ALL = "all"
RULE_RESULTS = "results"
RULEDICT = {RULE_NAME:None,RULE_IGNORECASE:True,RULE_IS_REGEX:True,RULE_RULE:None,RULE_REGEX:None,RULE_APPLY:APPLY_ANY,RULE_INCLUDE:True}
# RULES FOR FILENAME SEARCH

# search in file name object
RULE_FILE = "rule_file"              # additional search attribute: rule for file object
RULE_FILENAME = "filename"           # search in in filename only
RULE_PATH = "path"                   # search in path
RULE_ABSOLUTE_PATH = "absolute_path" # search in absolute path
# Path Objects
FILES_ABSOLUTE = "files_absolute"    # attribute in search result dict: absolute path
FILES = "files"                      # attribute in search result dict: file names
FILE_LINE = "line"                   # file line in file

# in file: look in complete text or line by line
RULE_FIND_BY_LINE = "find_by_line"

# search in content
RULE_FILE_CONTENT = "file_content"
RULEDICT_FILENAME = deepcopy(RULEDICT)
RULEDICT_FILENAME[RULE_FILE] = RULE_ABSOLUTE_PATH
RULEDICT_FILENAME[RULE_FIND_BY_LINE] = True

# prefix and postfixes for search results
RESULT_ANY_PREFIX_BEFORE = "#ANY1#"
RESULT_ANY_PREFIX_AFTER = "#ANY0#"
RESULT_ALL_PREFIX_BEFORE = "#ALL1#"
RESULT_ALL_PREFIX_AFTER = "#ALL0#"

# data dict definition

# definition of a data column
# name, value, description
# index: column index: index column to export
# export: flag, whther to export this column

DATACOL = {NAME:None,VALUE:None,DESCRIPTION:None,INDEX:None,EXPORT:True}
DATADICT = {NAME:None,DESCRIPTION:None,RULE_IGNORECASE:True,RULE_IS_REGEX:True,RULE_RULE:None,COLS:{},EXAMPLE:None}

# supported file types
class FileType(AbstractEnum):    
    FILETYPE_XLS = "xlsx"
    FILETYPE_CSV = "csv"
    FILETYPE_MD = "md"
    FILETYPE_TXT = "txt"
    FILETYPE_BAK = "bak"
    FILETYPE_YAML = "yaml"    

# Supported file types for search
FILETYPES_SUPPORTED = FileType.get_names()

# CONFIG CONSTANTS FOR config_env.py
# for specification refer to the json sample
# it is possible to define paths or files or regex to define groups of files / paths as well
# it is also possible to plug in the configuration into the file_analzer

# JSON keys
class ConfigAttribute(AbstractEnum):
    PATH = "p"           # a path object reference
    FILE = "f"           # a file object reference
    DESCRIPTION = "d"    # one line documentation
    GROUPS = "g"         # a list of group this item belongs to
    REFERENCE = "ref"    # the resolved path or file path if it can be resolved
    REGEX = "x"          # config should be treated as regex
    RULE = "r"           # rule dictionary for file_anaylzer / check the json how to use it
    COMMAND = "c"        # rule dictionary for command options
    DATA = "dd"          # data definition / structure definition
    SAMPLE = "s"         # sample / example data
    NAME = "n"           # name
    KEY = "k"            # key
    VALUE = "v"          # value
    TYPE = "t"           # (data) type
    EXPORT = "e"         # export map
    ENV = "env"          # environment settings, only some values are allowed and defined below

# CONFIG_PATH = "p"           # a path object reference
# CONFIG_FILE = "f"           # a file object reference
# CONFIG_DESCRIPTION = "d"    # one line documentation
# CONFIG_GROUPS = "g"         # a list of group this item belongs to
# CONFIG_REFERENCE = "ref"    # the resolved path or file path if it can be resolved
# CONFIG_REGEX = "x"          # config should be treated as regex
# CONFIG_RULE = "r"           # rule dictionary for file_anaylzer / check the json how to use it
# CONFIG_COMMAND = "c"        # rule dictionary for command options
# CONFIG_DATA = "dd"          # data definition / structure definition
# CONFIG_SAMPLE = "s"         # sample / example data
# CONFIG_NAME = "n"           # name
# CONFIG_KEY = "k"            # key
# CONFIG_VALUE = "v"          # value
# CONFIG_TYPE = "t"           # (data) type
# CONFIG_EXPORT = "e"         # export map
# CONFIG_ENV = "env"          # environment settings, only some values are allowed and defined below    
CONFIG_KEYS = ConfigAttribute.get_names()
# if this is set in path, then the current path is used
CONFIG_PATH_CWD = "CWD"


class ConfigKey(AbstractEnum):
    # Key Markers / Prefix may determine which type of file object is there
    CONFIG_KEY_CMD = "CMD_"
    # (W)here OPtion, tries to automativally determine an executable using where command
    CONFIG_KEY_WHERE = "W_"
    CONFIG_KEY_FILE = "F_"
    CONFIG_KEY_PATH = "P_"
    CONFIG_KEY_RULE = "R_"
    CONFIG_KEY_DATA = "D_"    

# Key Markers / Prefix may determine which type of file object is there
CONFIG_KEY_CMD = "CMD_"
# (W)here OPtion, tries to automativally determine an executable using where command
CONFIG_KEY_WHERE = "W_"
CONFIG_KEY_FILE = "F_"
CONFIG_KEY_PATH = "P_"
CONFIG_KEY_RULE = "R_"
CONFIG_KEY_DATA = "D_"
CONFIG_KEY_TYPES = ConfigKey.get_names()

# EXPORT FORMAT
EXPORT_CSV = "export_csv" # table of csv strings
EXPORT_DICT = "export_dict" # dict including json non compatible objects
EXPORT_JSON = "export_json" # json string
EXPORT_JSON_DICT = "export_json_dict" # json compatible dioct

# XLS INT of 1.1.1970
DATE_INT_19700101 = 25569
ENV_DATE_REF = "DATE19700101"

# REGEX EXPRESSIONS USED
# regex to find all strings enclosed in brackets
REGEX_BRACKETS = r"\[.+?\]"
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

# list of CYGPATH Transformations

# param definitions
CYGPATH_PATH = "path"
CYGPATH_CONV = "file_conversion"

class CygPathCmd(AbstractEnum):
    """ CygPath Command Line params """
    WIN2UNC = "--unix --absolute"
    WIN2DOS = "--dos --absolute"
    DOS2UNC = "--unix --absolute"
    UNC2WIN = "--windows --absolute"
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