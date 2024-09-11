""" constants file """
from copy import deepcopy

# Constants
FILE = "file"
PATH = "path"
OUTPUT = "output"
FORMATTED = "formatted"
LINE = "line"
RULES = "rules"

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

# supported file types
FILETYPE_XLS = "xlsx"
FILETYPE_CSV = "csv"
FILETYPE_MD = "md"
FILETYPE_TXT = "txt"
FILETYPE_BAK = "bak"
FILETYPE_YAML = "yaml"

# Supported file types for search
FILETYPES_SUPPORTED = [FILETYPE_CSV,FILETYPE_MD,FILETYPE_TXT,FILETYPE_BAK]

# CONFIG CONSTANTS FOR config_env.py 
# for specification refer to the json sample
# it is possible to define paths or files or regex to define groups of files / paths as well 
# it is also possible to plug in the configuration into the file_analzer

# JSON keys
CONFIG_PATH = "p"    # a path object reference
CONFIG_FILE = "f"    # a file object reference
CONFIG_DESCRIPTION = "d" # just a one line documentation
CONFIG_GROUPS = "g"             # a list of group this item belongs to 
CONFIG_REFERENCE = "ref" # the resolved path or file path if it can be resolved
CONFIG_REGEX = "x" # config should be treated as regex
CONFIG_RULE = "r" # rule dictionary for file_anaylzer / check the json how to use it

CONFIG_KEYS = [CONFIG_PATH,CONFIG_FILE,CONFIG_DESCRIPTION,CONFIG_GROUPS,CONFIG_REFERENCE]
# if this is set in path, then the current path is used
CONFIG_PATH_CWD = "CWD"
# Key Markers / Prefix may determine which type of file object is there 
CONFIG_KEY_CMD = "CMD_"
CONFIG_KEY_FILE = "F_"
CONFIG_KEY_PATH = "P_"
CONFIG_KEY_RULE = "R_"
CONFIG_KEY_TYPES = [CONFIG_KEY_CMD,CONFIG_KEY_FILE,CONFIG_KEY_PATH,CONFIG_KEY_RULE]

# REGEX EXPRESSIONS USED
# regex to find all strings enclosed in brackets
REGEX_BRACKETS = r"\[.+?\]"
