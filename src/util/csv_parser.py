""" Parsing text files to CSV """

import os
import re
import logging
from datetime import datetime as DateTime
import json
from copy import deepcopy
from util import constants as C
from util.config_env import ConfigEnv
from util.persistence import Persistence

logger = logging.getLogger(__name__)

class CsvParser(Persistence):
    """ Parsing txt files into tablular data"""

    def __init__(self,f_read:str=None,f_save:str=None,f_config:str=None,**kwargs) -> None:
        """ Constructor """
        super().__init__(f_read,f_save,**kwargs)
        self._config = ConfigEnv(f_config)
        self._global_keys = {}
        self._config_key = "NO KEY"
        self._description = "NO_DESCRIPTION"
        self._regex = ""
        self._example = ""
        self._global_keys_config = {}
        self._import_columns = {}
        self._export_colums = []
        self._export_info = {}
        self._errors = []
        self._env = {}
        self._parsed_items = []
        self._warnings = []

    @staticmethod
    def _validate_export_items(config)->list:
        """ validate export against import items,returns error messages """
        _out = []
        _import_keys = list(config.get(C.CONFIG_DATA,{}).values())
        _export_list = config.get(C.CONFIG_EXPORT,[])
        _global_keys = list(config.get(C.CONFIG_KEY,{}).values())
        _allowed_keys = deepcopy(_import_keys)
        _allowed_keys.extend(deepcopy(_global_keys))

        for _export_item in _export_list:
            _import_key = None
            if isinstance(_export_item,dict):
                _import_key = _export_item.get(C.CONFIG_KEY)
                if _import_key is None:
                    _msg = f"[CsvParser] (E)xport Item [{_export_item}] has no (k)ey element in dict"
                    logger.warning(_msg)
                    _out.append(_msg)
            elif isinstance(_export_item,str):
                _import_key = _export_item
            else:
                _msg = f"[CsvParser] (E)xport Item [{_export_item}] is not a dict or string"
                logger.warning(_msg)
                _out.append(_msg)

            if _import_key.endswith(C.DATEXLS):
                _import_key = _export_item[:-len(C.DATEXLS)]

            if not _import_key in _allowed_keys:
                _msg = f"[CsvParser] (E)xport Item [{_export_item}] has no (k)ey in import list {_import_keys}"
                logger.warning(_msg)
                _out.append(_msg)

        return _out


    @staticmethod
    def validate_config(config:dict)->list:
        """ validates a config dict, returns string of errors in case errors are found """
        out = []
        # no expression at all
        _regex = config.get(C.CONFIG_REGEX)
        if _regex is None:
            _msg = "[CsvParser] Regex E(x)pression is empty"
            logger.warning(_msg)
            out.append(_msg)

        # cross check export fields to parse fields
        _column_data = config.get(C.CONFIG_DATA)

        if not _column_data and not isinstance(_column_data,dict):
            _msg = "[CsvParser] No valid Column Config Data (dd) could be found / is not a dict"
            logger.warning(_msg)
            out.append(_msg)

        # do a smoke test in case regex example is supplied
        _sample = config.get(C.CONFIG_SAMPLE)
        if _sample:
            _results = re.findall(_regex,_sample,re.IGNORECASE)
            if len(_results) == 0:
                _msg = f"[CsvParser] Regex [{_regex}] doesn't match sample expression [{_sample}]"
                out.append(_msg)

        # validate config data
        for index,col_info in _column_data.items():
            try:
                _idx_int = int(index)
            except ValueError:
                _msg = f"[CsvParser] Data Column [{index}] is non numerical, must be a numerical int string"
                logger.warning(_msg)
                out.append(_msg)
                break

            if isinstance(col_info,str):
                continue

            _msg = f"[CsvParser] Data Column [{index}] value is not a string, pls correct"
            out.append(_msg)


        # validate output data / if it is empty, all will be exported
        _export_items = config.get(C.CONFIG_EXPORT,{})
        if not isinstance(_export_items,list):
            _msg = "[CsvParser] Export Information (e) is not a list of dicts/strings"
            logger.warning(_msg)
            out.append(_msg)

        if len(_export_items) > 0 and isinstance(_column_data,dict):
            _msgs = CsvParser._validate_export_items(config)
            out.extend(_msgs)

        # validate environment items
        _env = config.get(C.CONFIG_ENV,{})
        if isinstance(_env,dict):
            _allowed_env_keys = list(_env.keys())
            for _env_key in list(_env.keys()):
                if not _env_key in _allowed_env_keys:
                    _msg = f"[CsvParser] Environment key [{_env_key}] invalid, allowed {_allowed_env_keys}"
                    out.extend(_msg)
        return out

    def _create_env(self,config:dict)->None:
        """ set up default environment """
        _env_config = config.get(C.CONFIG_ENV,{})
        self._env = {}
        self._env[C.ENV_DEC_SEPARATOR]=_env_config.get(C.ENV_DEC_SEPARATOR,C.ENV_DEC_SEPARATOR_DEFAULT)
        self._env[C.ENV_DATE_FORMAT]=_env_config.get(C.ENV_DATE_FORMAT,C.DATEFORMAT_DD_MM_JJJJ)
        self._env[C.ENV_CSV_WRAP_CHAR]=_env_config.get(C.ENV_CSV_WRAP_CHAR,C.ENV_CSV_WRAP_CHAR_DEFAULT)
        self._env[C.ENV_DATE_REF]=DateTime(1970,1,1)

    def _copy_config(self,config:dict)->None:
        """ copies config into object """
        self._description = config.get(C.CONFIG_DESCRIPTION,"NO_DESCRIPTION")
        self._regex = re.compile(config.get(C.CONFIG_REGEX,"NO_REGEX"),re.IGNORECASE)
        self._example = config.get(C.CONFIG_SAMPLE,"NO_SAMPLE")
        self._global_keys_config = config.get(C.CONFIG_KEY,{})
        self._import_columns = config.get(C.CONFIG_DATA,{})
        _export_columns = config.get(C.CONFIG_EXPORT,[])
        # no export columns were supplied, use the import columns instead
        if len(_export_columns) == 0:
            _export_columns = list(self._import_columns.values())
        self._export_colums = _export_columns
        self._export_info = self._get_export_info()
        self._create_env(config)

    def _reset_config(self)->None:
        """ resets parse specific filter """
        self._description = "NO_DESCRIPTION"
        self._regex = ""
        self._example = ""
        self._global_keys_config = {}
        self._import_columns = {}
        self._export_colums = []
        self._export_info = {}
        self._parsed_items = []

    @staticmethod
    def get_key_value(s:str,regex:str=C.REGEX_GLOBAL_KEY)->dict:
        """ identifies a key value pair based on regex """
        _results = re.findall(regex,s,re.IGNORECASE)
        if len(_results) == 0:
            return {}
        else:
            return {_results[0][0]:_results[0][1]}

    def _get_export_info(self)->dict:
        """ builds up info dict for export """
        _export_columns = self._export_colums
        _export_info = {}
        for _export_column in _export_columns:
            _column_info = _export_column
            if isinstance(_export_column,str):
                _column_info = {C.CONFIG_KEY:_export_column,C.CONFIG_TYPE:C.TYPE_STR}

            if not ( isinstance(_export_column,dict) or isinstance(_export_column,str)) :
                _msg = f"[CsvParser] Configuration [{self._config_key}], {_export_column} is not a dict or str"
                logger.warning(_msg)
                self._warnings.append(_msg)
                continue

            # convert unknown types to str
            if not _column_info.get(C.CONFIG_TYPE,"UNKNOWN") in C.TYPES:
                _msg = f"[CsvParser] Configuration [{self._config_key}], {_export_column} unknown data (t)ype, allowed {C.TYPES}"
                logger.warning(_msg)
                self._warnings.append(_msg)
                _column_info[C.CONFIG_TYPE] = C.TYPE_STR

            _key = _column_info[C.CONFIG_KEY]
            if _key.endswith(C.DATEXLS):
                _column_info[C.CONFIG_KEY] = _key
                _column_info[C.CONFIG_TYPE] = C.TYPE_DATEXLS
            _export_info[_key] = _column_info

        return _export_info

    def _to_str(self,value,dec_separator:str=".",dateformat:str=C.DATEFORMAT_DD_MM_JJJJ)->str:
        if isinstance(value,str):
            return value
        elif isinstance(value,int):
            return str(value)
        elif isinstance(value,float):
            value = str(value)
            if dec_separator == ",":
                value = value.replace(".",",")
        elif isinstance(value,DateTime):
            value = value.strftime(dateformat)
        return value

    def _as_string_dict(self)->list:
        """ convert result as stringified dict """
        out = []
        _dec_sep = self._env.get(C.ENV_DEC_SEPARATOR,C.ENV_DEC_SEPARATOR_DEFAULT)
        _dateformat = self._env.get(C.ENV_DATE_FORMAT,C.DATEFORMAT_DD_MM_JJJJ)
        for _list_item in self._parsed_items:
            _item_out = {}
            for _k,_v in _list_item.items():
                _item_out[_k] = self._to_str(_v,_dec_sep)
            out.append(_item_out)
        return out

    def _parse_float(self,value:str)->float:
        """ try to parse float. as we may have comma or dot, instead of
            trying to convert it with atof , set it up with a global env param
            set in the file
        """
        _sep = self._env.get(C.ENV_DEC_SEPARATOR,C.ENV_DEC_SEPARATOR_DEFAULT)
        if _sep == ",":
            value = value.replace(".","")
            value = value.replace(",",".")
        else:
            value = value.replace(",",".")

        try:
            return float(value)
        except ValueError:
            return None

    def _parse_date(self,value:str,format_str:str=None):
        """ parse to a date """
        _date_format = self._env.get(C.ENV_DATE_FORMAT,C.DATEFORMAT_DD_MM_JJJJ)
        if len(_date_format) == 0:
            _msg = "[CsvParser] Couldn't find Date Format String, check DATE_FORMAT in your  Configuration"
            logger.warning(_msg)
            self._warnings.append(_msg)

        try:
            _dt = DateTime.strptime(value,_date_format)
            # convert to XLS Format: get days since 1970
            if format_str == C.TYPE_DATEXLS:
                _dt = C.DATE_INT_19700101 + (_dt- self._env.get(C.ENV_DATE_REF)).days
            return _dt
        except ValueError:
            return None

    def _parse_value(self,value:str,export_info:dict):
        """ parse  value to a target format """
        try:
            _type = export_info.get(C.CONFIG_TYPE,"no_config")
            if _type == C.TYPE_FLOAT:
                value = self._parse_float(value)
            elif _type == C.TYPE_INT:
                value = int(value)
            elif _type in [C.TYPE_DATE,C.TYPE_DATEXLS]:
                value = self._parse_date(value,_type)
        except ValueError:
            value = None

        return value

    def _parse_match(self,match_dict:dict)->dict:
        """ parses and validates the match
            filter: filters to output values
        """
        # replace index numbers by column names
        _out_dict = {}
        _result_dict = {}
        for _key,_value in match_dict.items():
            _column_name = self._import_columns.get(_key)
            if _column_name is None:
                _msg = f"[CsvParser] Configuration [{self._config_key}], Couldn't find key [{_key}] in result {match_dict}"
                logger.warning(_msg)
                self._warnings.append(_msg)
                continue
            _result_dict[_column_name]=_value

        _export_info = self._export_info
        for export_key,export_info in _export_info.items():
            data_key = export_key
            if export_info.get(C.CONFIG_TYPE,"unknown") == C.TYPE_DATEXLS:
                data_key = export_key[:-len(C.DATEXLS)]
            _value = _result_dict.get(data_key)
            if not _value:
                _value = export_info.get(C.CONFIG_VALUE)
            if _value is None:
                _msg = f"[CsvParser] Configuration [{self._config_key}], column [{data_key}], no value found in {_result_dict}"
                logger.warning(_msg)
                self._warnings.append(_msg)
                _out_dict[export_key] = None
                continue

            _parsed_value = self._parse_value(_value,export_info)
            if _parsed_value is None:
                _msg = f"[CsvParser] Configuration [{self._config_key}], column [{data_key}], no value could be parsed from {_result_dict}"
                self._warnings.append(_msg)
                logger.warning(_msg)

            _out_dict[export_key] = _parsed_value

        return _out_dict

    def _parse_global_keys(self,global_keys:dict)->None:
        """ parses global_keys with configuration, export them to export configuration """
        _gk_configs = {}
        for k,v in self._global_keys_config.items():
            _gk_configs[k.lower()] = v
        for g_key, g_value in global_keys.items():
            _gk_export_key = _gk_configs.get(g_key.lower())
            if _gk_export_key is None:
                _msg = f"[CsvParser] Configuration [{self._config_key}],couldn't find found global key [{g_key}] in (k) configuration"
                logger.warning(_msg)
                self._warnings.append(_msg)
                continue
            _export_info = self._export_info.get(_gk_export_key)
            if _export_info is None:
                _msg = f"[CsvParser] Configuration [{self._config_key}], no export info for key [{_gk_export_key}] found"
                logger.warning(_msg)
                self._warnings.append(_msg)
            _export_info[C.CONFIG_VALUE] = g_value

    def content(self,export_format:str=C.EXPORT_DICT)->list|str:
        """ returns the content from the last read result """
        out = self._parsed_items

        if export_format == C.EXPORT_CSV:
            _wrap_char = self._env.get(C.ENV_CSV_WRAP_CHAR)
            _string_dict = self._as_string_dict()
            out = Persistence.dicts2csv(_string_dict,wrap_char=_wrap_char)
        elif export_format == C.EXPORT_JSON or export_format == C.EXPORT_JSON_DICT:
            _dateformat = self._env.get(C.ENV_DATE_FORMAT)
            _stringified = Persistence.dict_stringify({"dummykey":out},_dateformat)["dummykey"]
            if export_format == C.EXPORT_JSON_DICT:
                out = _stringified
            else:
                out = json.dumps(_stringified,indent=4)

        return out

    def parse(self,config_key:str=None,f:str=None,export_format:str=C.EXPORT_DICT)->list|str:
        """ parses file """
        self._warnings = []
        _out = []
        _f = self._f_read if f is None else f
        if _f is None or not os.path.isfile(_f):
            _msg = f"[CsvParser] files [{_f}] is not a valid file"
            logger.warning(_msg)
            self._warnings.append(_msg)
            return {}

        self._config_key = config_key
        self._reset_config()
        _config = self._config.get_config(config_key)

        if len(_config) == 0:
            return {}

        # check / validate
        _warnings = CsvParser.validate_config(_config)
        self._warnings.extend(_warnings)
        if len(_warnings) > 0:
            return {}

        # copy over valid configuration
        self._copy_config(_config)

        _lines = Persistence.read_txt_file(_f)
        _global_keys = {}
        _match_lines = []

        _result_list = []
        for _line in _lines:
            # collect any global key value settings
            _global_key = CsvParser.get_key_value(_line)
            if len(_global_key) > 0:
                _global_keys.update(_global_key)
                continue
            # check the current line with the regex
            _matches = self._regex.findall(_line)
            if len(_matches) > 0:
                _result_dict = {}
                _results = _matches[0]
                for n,_result in enumerate(_results):
                    _result_dict[str(n)] = _result
                _result_list.append(_result_dict)

        # parse the key value combinations found in the file
        # and copy values to export configuration dict
        self._parse_global_keys(_global_keys)

        for _result in _result_list:
            _parsed = self._parse_match(_result)
            if len(_parsed) > 0:
                _out.append(_parsed)

        self._parsed_items = _out

        # return the content
        return self.content(export_format)
