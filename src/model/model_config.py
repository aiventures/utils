""" model for the configuration environment """
from util.abstract_enum import AbstractEnum
from util.constants import ( EnvType,ConfigStatus,RuleFileAttribute, RuleFile, DataType
                            )
from pydantic import BaseModel
from typing import List,Optional,Union,Dict,Any,Literal
from enum import Enum,StrEnum

# TAXONOMY
# ALL:      d, k et
# P_ / F_ / W_ / E_ / CMD_ : f,p,ref,ff
# CMD_ : like above with C segment
# R_ : with additional rule segment => definition as in
# D_: with different

# mdoel config util.constats.py ConfigAtteribute Enum
# note there's even more fields after processing / validation
class ConfigItem(BaseModel):
    """ base class definition of a config item (P_,F_,W_,E_) """
    k   : Optional[str]                         # key (i dict is not used)
    v   : Optional[Any] = None                  # value
    t   : Optional[str] = None                  # type
    d   : Optional[str] = None                  # description
    g   : Optional[List[str]] = []              # assignment to configuration group
    p   : Optional[str] = None                  # path
    f   : Optional[str] = None                  # file
    ff  : Optional[Literal["dos","win","unc"]] = "win" # file format
    et  : Optional[List[EnvType]] = []          # assignment to an environment type

class ConfigItemProcessed(ConfigItem):
    """ Config Items that were processed """
    kk  : Optional[str] = None                  # This is the configuration json dictionary key.
                                                # if k is not supplied in values dictionary key will be used instead
    ref : Optional[str] = None                  # dereferenced path object
    dep : Optional[List[str]] = None            # List of dependencies to other keys in config
    st  : Optional[ConfigStatus] = None         # status whether an entry could be validated
    o   : Optional[str] = None                  # original value
    w   : Optional[str] = None                  # where field used to dereference commands

# Rule as defined in Util.constants RULEDICT
class RuleDict(BaseModel):
    """ RuleDict Model """
    name          : str                            # rule name
    ignorecase    : Optional[bool] = True          # ignore case
    is_regex      : Optional[bool] = True          # is a regex expression
    rule          : Optional[str]                  # rule matches string
    regex         : Optional[str]                  # regex rule
    rule_include  : Optional[bool] = True          # rule include or exclude search results
    apply         : Optional[Literal["any","all"]] # apply any or all rules

class RuleDictFile(RuleDict):
    """ RuleDict Model aplying to a file"""
    rule_file     : Optional[RuleFileAttribute]    # File Part top which the filter applies to
    find_by_lines : Optional[bool]                 # apply rule to line in file or to all in text

class ConfigRule(ConfigItemProcessed):
    """ base model for a Rule Definition Item (R_) """
    r  : Optional[List[Union[RuleDictFile,RuleDict]]] # List of Rules

class CommandDict(BaseModel):
    """ Command used in the command section """
    r : Optional[str]                              # rule string
    d : Optional[str]                              # description

class ConfigCommandLine(ConfigItemProcessed):
    """ base model for a COMMAND LINE definition (CMD_) """
    c  : Dict[str,Union[str,CommandDict]]       # Dict of Commands, eihter plain string or as dict

class DataExportType(BaseModel):
    """ exporting data either to CSV as plain str or as formatted string """
    k : str                    # Export key
    t : Optional[DataType]     # Data Type

class DataDefinition(BaseModel):
    """ Data Definitions to be used for parsing tablular data to from csv
        it's best to look ath the sample file in
        utils > test_data > test_config > config_env_termplate.json
        and the corresponding unit tests
        to comprehend what's going on
    """
    d   : Optional[str]                    # description
    x   : Optional[str]                    # regex to identify parts in text
    s   : Optional[str]                    # sample line to parse the regex
    k   : Optional[Dict[str,str]]          # extract markers, marked in text as key:ISIN=IEABSDEF12345
                                           # Command {"isin":"ISIN_NUMMER"} will map value to ISIN_NUMMER
    dd  : Dict[str,str]                    # data definition out column number - column title
    e   : List[Union[str,DataExportType]]  # Exporting Data Fields to CSV using format
    env : Optional[Dict[str,Any]]          # setting up default environment values (eg Date Format, separator, others ...)

# for model validation: use option union mode left to right
class SourceEnum(StrEnum):
    """ origin definitions of data as used by bootstrapping methods """
    PATH = "path"                 # directly from path
    FILE = "file"                 # directly from file path
    ENVIRONMENT = "environment"   # retrieved from os environment
    CONFIG_VALUE = "config_value" # retrieved from configuration value section
    CONFIG_REF = "config_ref"     # retrieved from ref section in configuration
    CWD = "cwd"                   # current work directory
    REF = "ref"                   # reference value to be used 


class SourceRef(BaseModel):
    """ Model of File Refs """
    key : str
    value : Optional[Any] = None
    ref_type : Optional[SourceEnum] = None
    is_file : Optional[bool] = None
    is_path : Optional[bool] = None
    cwd : Optional[str] = None
