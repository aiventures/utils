"""model for the configuration environment"""

import logging
import os
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Discriminator, RootModel, Tag, TypeAdapter, ValidationError
from util import constants as C
from util.constants import ConfigStatus, DataType, EnvType, RuleFileAttribute

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# TAXONOMY
# ALL:      d, k et
# P_ / F_ / W_ / E_ / CMD_ : f,p,ref,ff
# CMD_ : like above with C segment
# R_ : with additional rule segment => definition as in
# D_: with different


# model config util.constats.py ConfigAtteribute Enum
# note there's even more fields after processing / validation
class ConfigItem(BaseModel):
    """base class definition of a config item (P_,F_,W_,E_)"""

    # type Literal ['config_item']
    k: Optional[str] = None  # key (i dict is not used)
    v: Optional[Any] = None  # value
    t: Optional[Union[str | Dict]] = None  # type
    d: Optional[str] = None  # description
    g: Optional[List[str]] = []  # assignment to configuration group
    p: Optional[str] = None  # path
    f: Optional[str] = None  # file
    ff: Optional[Literal["dos", "win", "unc"]] = "win"  # file format
    et: Optional[List[EnvType]] = []  # assignment to an environment type


class ConfigItemProcessed(ConfigItem):
    """Config Items that were processed"""

    #    type Literal['config_item_processed']
    kk: Optional[str] = None  # This is the configuration json dictionary key.
    # if k is not supplied in values dictionary key will be used instead
    ref: Optional[str] = None  # dereferenced path object
    dep: Optional[List[str]] = None  # List of dependencies to other keys in config
    st: Optional[ConfigStatus] = None  # status whether an entry could be validated
    o: Optional[str] = None  # original value
    w: Optional[str] = None  # where field used to dereference commands


# Rule as defined in Util.constants RULEDICT
class RuleDict(BaseModel):
    """RuleDict Model"""

    name: str  # rule name
    ignorecase: Optional[bool] = True  # ignore case
    is_regex: Optional[bool] = True  # is a regex expression
    rule: Optional[str]  # rule matches string
    regex: Optional[str]  # regex rule
    rule_include: Optional[bool] = True  # rule include or exclude search results
    apply: Optional[Literal["any", "all"]]  # apply any or all rules


class RuleDictFile(RuleDict):
    """RuleDict Model aplying to a file"""

    rule_file: Optional[RuleFileAttribute]  # File Part top which the filter applies to
    find_by_lines: Optional[bool]  # apply rule to line in file or to all in text


class ConfigRule(ConfigItemProcessed):
    """base model for a Rule Definition Item (R_)"""

    # type Literal['config_rule']
    r: Optional[List[Union[RuleDictFile, RuleDict]]]  # List of Rules


class CommandDict(BaseModel):
    """Command used in the command section"""

    r: Optional[str]  # rule string
    d: Optional[str]  # description


class ConfigCommandLine(ConfigItemProcessed):
    """base model for a COMMAND LINE definition (CMD_)"""

    # type Literal['config_command_line']
    c: Dict[str, Union[str, CommandDict]]  # Dict of Commands, eihter plain string or as dict


class DataExportType(BaseModel):
    """exporting data either to CSV as plain str or as formatted string"""

    k: str  # Export key
    t: Optional[DataType]  # Data Type


class DataDefinition(BaseModel):
    """Data Definitions to be used for parsing tablular data to from csv
    it's best to look ath the sample file in
    utils > test_data > test_config > config_env_termplate.json
    and the corresponding unit tests
    to comprehend what's going on
    """

    #    type Literal['data_definition']
    k: Optional[str] = None  # Export key
    d: Optional[str] = None  # description
    x: Optional[str] = None  # regex to identify parts in text
    s: Optional[str] = None  # sample line to parse the regex
    k: Optional[Dict[str, str]] = None  # extract markers, marked in text as key:ISIN=IEABSDEF12345
    # Command {"isin":"ISIN_NUMMER"} will map value to ISIN_NUMMER
    dd: Dict[str, str] = None  # data definition out column number - column title
    e: List[Union[str, DataExportType]] = None  # Exporting Data Fields to CSV using format
    env: Optional[Dict[str, Any]] = (
        None  # setting up default environment values (eg Date Format, separator, others ...)
    )


def config_item_type_discriminator(v: Any) -> str:
    """depending on data signature, determine ConfigItemType for Union Type"""
    _fields = []
    if isinstance(v, dict):
        _fields = list(v.keys())

    if "dd" in _fields or "e" in _fields:
        return "data_definition"
    elif "r" in _fields:
        return "config_rule"
    elif "c" in _fields:
        return "config_command_line"
    elif "ref" in _fields or "dep" in _fields or "w" in _fields:
        return "config_item_processed"
    elif "k" in _fields or "v" in _fields or "p" in _fields or "f" in _fields:
        return "config_item"
    return "unknown"


class ConfigItemType(RootModel):
    """Config Item Model"""

    root: Annotated[
        Union[
            Annotated[ConfigItem, Tag("config_item")],
            Annotated[ConfigItemProcessed, Tag("config_item_processed")],
            Annotated[ConfigRule, Tag("config_rule")],
            Annotated[ConfigCommandLine, Tag("config_command_line")],
            Annotated[DataDefinition, Tag("data_definition")],
        ],
        Discriminator(config_item_type_discriminator),
    ]


class ConfigError(BaseModel):
    """Configuration Error"""

    config_key: Optional[str] = None  # configuration key
    type: Optional[str] = None  # type that is validated
    err_type: Optional[str] = None  # type that is validated
    msg: Optional[str] = None  # message
    msg_long: Optional[str] = None  # long message
    field: Optional[str] = None  # last element of loc fields, points to field
    hint: Optional[str] = None  # pydantic link pointing to error
    config_input: Optional[dict] = None  # location of error
    config_item: Optional[dict] = None  # original config item from config json
    error: Optional[dict] = None  # original error format


# model representation of the configuration item
ConfigItemAdapter = TypeAdapter(ConfigItemType)
# type that can be used as output of functions
ConfigModel = Dict[str, ConfigItemType]
ConfigModelAdapter = TypeAdapter(ConfigModel)
ConfigModelType = Annotated[ConfigModel, ConfigModelAdapter]


# for model validation: use option union mode left to right
class SourceEnum(StrEnum):
    """origin definitions of data as used by bootstrapping methods"""

    PATH = "path"  # directly from path
    FILE = "file"  # directly from file path
    ENVIRONMENT = "environment"  # retrieved from os environment
    CONFIG_VALUE = "config_value"  # retrieved from configuration value section
    CONFIG_REF = "config_ref"  # retrieved from ref section in configuration
    CWD = "cwd"  # current work directory
    REF = "ref"  # reference value to be used


class SourceRef(BaseModel):
    """Model of File Refs"""

    key: str
    value: Optional[Any] = None
    ref_type: Optional[SourceEnum] = None
    is_file: Optional[bool] = None
    is_path: Optional[bool] = None
    cwd: Optional[str] = None


class ConfigValidator:
    """Configuration Model"""

    @staticmethod
    def validate_config_item(config_item_dict: dict) -> ConfigItemType | list:
        """validates a config item and returns Validated item or list of errors"""
        validated = None
        try:
            validated = ConfigItemAdapter.validate_python(config_item_dict)
        except ValidationError as e:
            _errors = e.errors()
            _err = f"Couldn't parse as Pydantic Model, {repr(_errors)}"
            logger.warning(_err)
        return validated

    @staticmethod
    def config_model_schema() -> dict:
        """returns the json schema for the Config"""
        return ConfigModelAdapter.json_schema()

    @staticmethod
    def get_config_error(config_dict: dict, error: dict, schema: dict) -> ConfigError:
        """Parses the config dict"""
        _error_dict = {}
        _types = schema.get("$defs")
        _type_keys = list(_types.keys())
        _input = error.get("input")
        _err_type = error.get("type")
        _locs = error.get("loc")
        _input = error.get("input")
        _hint = error.get("url")
        _msg = error.get("msg")
        _num_loc = len(_locs)
        _config_key = None
        _field = None
        if _num_loc > 0:
            _config_key = _locs[0]
            _field = _locs[-1]
        # try to identify erroneous type
        _type_info = None
        _type = None
        for _type in _locs:
            if _type in _type_keys:
                _type_info = _types[_type]
                break
        # try to identify item in config
        _config_item = None
        if isinstance(config_dict, dict):
            _config_item = config_dict.get(_config_key)
        _msg_long = f"Config [{_config_key}]: {_msg}, type [{_type}], field name [{_field}] ({_hint})"
        # combine alll into an error model
        _error_dict["config_key"] = _config_key  # configuration key
        _error_dict["type"] = _type  # type that is validated
        _error_dict["err_type"] = _err_type  # type that is validated
        _error_dict["msg"] = _msg  # message
        _error_dict["msg_long"] = _msg_long  # long message
        _error_dict["field"] = _field  # last element of loc fields, points to field
        _error_dict["hint"] = _hint  # pydantic link pointing to error
        _error_dict["config_input"] = _input  # location of error
        _error_dict["config_item"] = _config_item  # original config item from config json
        _error_dict["error"] = error  # original error format
        _error = ConfigError(**_error_dict)
        return _error

    @staticmethod
    def get_config_errors(config_dict: dict, errors: list) -> Dict[str, ConfigError]:
        """parses the config errors as model"""
        out = {}
        _schema = ConfigValidator.config_model_schema()
        # loop through all items in the loc section and try to get a model
        for _error in errors:
            _error = ConfigValidator.get_config_error(config_dict, _error, _schema)
            _key = _error.config_key
            # we can have multiple errors per key
            _out_error = out.get(_key, [])
            _out_error.append(_error)
            out[_key] = _out_error
        return out

    @staticmethod
    def validate_config(config_dict: dict) -> ConfigModel | Dict[str, ConfigError]:
        """validates a config item and returns Validated item or dict of errors"""
        validated = None
        try:
            validated = ConfigModelAdapter.validate_python(config_dict)
            pass
        except ValidationError as e:
            _errors = e.errors()
            _errors_verbose = ConfigValidator.get_config_errors(config_dict, _errors)
            _err = f"Couldn't parse as Pydantic Model, founf [{len(_errors)}] errors"
            logger.warning(_err)
            validated = {C.ERROR: _errors_verbose}

        return validated
