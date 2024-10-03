""" Managing Configuration for a given command line """

import os
import sys
import re
import json
import logging
from pathlib import Path
from rich import print_json
from rich import print as rprint

# TODO REPLACE BY UNIT TESTS
# when doing tests add this to reference python path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from copy import deepcopy
from util.persistence import Persistence
from util.colors import col
from util import constants as C
from util.utils import Utils
from demo.demo_config import create_demo_config

logger = logging.getLogger(__name__)

class ConfigEnv():
    """ Configuration of Command Line Environment  """

    def __init__(self,f_config:str=None) -> None:
        """ constructor """
        self._f_config = None
        self._f_config_dict = None
        self._bootstrap_path(f_config)
        self._config = Persistence.read_json(self._f_config)
        self._config_keys = list(self._config.keys())
        self._wrong_rule_keys = {}
        self._env = {}
        if not self._config:
            self._config = {}
        self._validate()

    def get_config(self,key:str=None)->dict:
        """ returns a configuration """
        if not isinstance(key,str):
            _msg = "[CONFIG] No valid key was passed"
            logger.warning(_msg)
            return {}

        if not isinstance(self._config,dict):
            _msg = "[CONFIG] There is no valid configuration"
            logger.warning(_msg)
            return {}

        config = self._config.get(key)
        if config is None:
            _msg = f"[CONFIG] There is no configuration with key [{key}]"
            logger.warning(_msg)
            return {}

        return config

    # TODO GET CONFIG GROUPS
    def get_config_by_groups(self,groups:list|str=None):
        """ filter config entries by group. """
        if isinstance(groups,str):
            _groups = [groups]
        else:
            _groups = groups

        out_config = {}

        if len(_groups) == 0:
            return out_config

        for _config_key,_config_info in self._config.items():
            _groups_env = _config_info.get(C.ConfigAttribute.GROUPS.value,{})
            if len(_groups_env) == 0:
                continue
            if any([g_env in _groups for g_env in _groups_env]):
                logger.debug(f"[CONFIG] Key [{_config_key}], found match in group {_groups_env}")
                out_config[_config_key] = _config_info
        logger.info(f"[CONFIG] Get Config Env using groups {_groups}, returning [{len(out_config)}] entries")
        return out_config


    def config_is_valid(self,key):
        """ Checks whether the referenced configuration item is valid """
        _status = self._config.get(key,{}).get(C.ConfigAttribute.STATUS.value)
        return _status == C.ConfigStatus.VALID.value

    def _get_cmd(self,key,cmd_key:str=None,**kwargs)->str:
        """ based on params supplied, identify the correct command and create a command line command
            alternatively directly pass command name, returns the cmd key or None if an error occured
        """
        # get the params as upper list
        _params = [p.upper() for p in list(kwargs.keys())]
        _num_params = len(_params)
        # get a dict that lists whether params are contained in a command
        _params_dict_template = {k:{"param":True,"cmd":False} for k in _params}

        # get the dict config
        _config_cmd_dict = self._config.get(key,{}).get(C.ConfigAttribute.COMMAND.value,{})
        # if command is supplied, try to get it directly
        if cmd_key is not None:
            cmd_out = _config_cmd_dict.get(cmd_key)
            if cmd_out is not None:
                logger.debug(f"[CONFIG] Key [{key}], rule [{cmd_key}], return command [{cmd_out}]")
                return cmd_key

        _cmd_matches = {}
        _num_max_matches = 0
        _cmd_out = []

        for _cmd_key,_cmd_info in _config_cmd_dict.items():

            # get all params in the command string drop the cmd
            _cmd_template = None
            if isinstance(_cmd_info,str):
                _cmd_template = _cmd_info
            elif isinstance(_cmd_info,dict):
                _cmd_template = _cmd_info.get(C.ConfigAttribute.RULE.value)
            if _cmd_template is None:
                _msg = (f"[CONFIG] Key [{key}], rule [{cmd_key}], Invalid setting")
                logger.warning(_msg)
                return None

            _cmd_params = re.findall(C.REGEX_BRACKET_CONTENT,_cmd_template)
            _cmd_params.remove(C.CMD.upper())
            # TODO if thwere are envsa and other things in the command list, drop them as well
            _num_cmd_params = len(_cmd_params)

            # analyze matches: little bit over designed but maybe useful for the future
            _params_dict = deepcopy(_params_dict_template)
            for _cmd_param in _cmd_params:
                _params_item = _params_dict.get(_cmd_param,{"param":False,"cmd":True})
                _params_item["cmd"]=True
                _params_dict[_cmd_param] = _params_item

            _executable = True
            _params_missing = []
            _num_matches = 0
            for _param,_param_info in _params_dict.items():
                if _param_info["param"] is True and _param_info["cmd"] is True:
                    _param_info["match"]=True
                    _num_matches += 1
                else:
                    _param_info["match"]=False
                # check whether the command is executable (all parameters in command are there )
                if _param_info["param"] is False and _param_info["cmd"] is True:
                    _params_missing.append(_param)

            if len(_params_missing)==0:
                _cmd_matches[_cmd_key]=_num_matches
                if _num_matches == _num_max_matches:
                    _cmd_out.append(_cmd_key)
                elif _num_matches > _num_max_matches:
                    _num_max_matches = _num_matches
                    _cmd_out = [_cmd_key]

        # return the valid command with the highest number of param matches
        # if there is more than one, return None issue a warning
        if len(_cmd_out) == 1:
            return _cmd_out[0]
        elif len(_cmd_out) == 0:
            _msg = f"[CONFIG] Key [{key}], rule [{cmd_key}], no command found for {kwargs}"
            return None
        elif len(_cmd_out) > 1:
            _msg = f"[CONFIG] Key [{key}], rule [{cmd_key}], ambiguous rules {_cmd_out} found for {kwargs}"
            return None

    def _parse_date_as_cmd_string(self,value:any)->str:
        """ parse an incoming string as date /
            incoming date as string to be used in command line
            according to environment (tbd)
        """
        # TODO do a conversion
        return str(value)

    def _parse_path_as_cmd_string(self,p:any)->str:
        """ parse an incoming string as path for use in command line
        """
        # TODO allow different path conversions
        # for now convert to os specific path
        _transform_rule = C.FileFormat.OS.name
        # do not use quotes
        if Utils.is_windows():
            _quotes = True
        else:
            _quotes = False
        _check_exist = False
        _info = False
        p_out = Utils.resolve_path(p,_check_exist,_transform_rule,_info,_quotes)
        if p_out is None:
            _msg = f"[CONFIG] Couldn't convert path [{p}]"
            logger.warning(_msg)
            return None

        return p_out

    def _parse_cmd_param(self,param_name:str,value:any,param_type:str|None)->any:
        """ parsing a a single configuration value """
        # _file_config_types = C.ConfigKey.get_file_config_types()
        _parsed = None
        _param_name = param_name.upper()
        _is_file_type = False # for path like objects, enclose in quotes

        # if the value is enclosed in brackets, try to get a reference stored in configuration
        if isinstance(value,str):
            _ref_key = re.findall(C.REGEX_BRACKET_CONTENT,value)
            if len(_ref_key) > 0 and _ref_key[0] in self._config_keys:
                _ref_value = self.get_ref(_ref_key[0])
                _msg = f"[CONFIG] Got Param [{param_name}], value [{value}], dereferenced to [{_ref_value}]"
                logger.debug(_msg)
                value = _ref_value

        if param_type is None:
            if isinstance(value,str):
                # eastereggs: implicit conversion based on
                # filename/value signature not on type
                if "FILE" in _param_name or "PATH" in _param_name:
                    _parsed = value
                    _is_file_type = True
                if not _parsed:
                    # brackets used in value, parse for config key
                    _config_key = re.findall(C.REGEX_BRACKET_CONTENT,value)
                    if len(_config_key)==1:
                        _parsed = self.get_ref(_config_key[0])
                        # check if a filetype config is reference
                        _is_file_type = C.ConfigKey.is_file_config_type(_config_key)
            else:
                _parsed = value
        # parse according to type
        else:
            # convert string to paramtype
            _data_type = C.DataType.get_enum(param_type,search_name=False,search_value=True,exact=True)
            if _data_type is None:
                _msg = f"[CONFIG] param [{param_name}], invalid param_type [{param_type}], allowed {C.DataType.get_values()}"
                logger.warning(_msg)
                return None
            if _data_type == C.DataType.INT:
                _parsed = int(value)
            elif _data_type == C.DataType.FLOAT:
                _parsed = float(value)
            elif _data_type == C.DataType.STR:
                _parsed = str(value)
            elif _data_type == C.DataType.DATE:
                _parsed = self._parse_date_as_cmd_string(value)
            elif _data_type == C.DataType.DATEXLS:
                _parsed = int(value)
            elif _data_type == C.DataType.CONFIG:
                _parsed = self.get_config(value)
                _is_file_type = C.ConfigKey.is_file_config_type(value)
            # for now, only support to a os native path type
            # do the specialisation later on
            elif "path" in param_type:
                _is_file_type = True
                _parsed = str(value)
        if _is_file_type:
            _parsed = self._parse_path_as_cmd_string(_parsed)
        if _parsed is None:
            _msg = f"[CONFIG] param [{param_name}], couldn't convert value [{value}], type [{param_type}]"
            logger.warning(_msg)

        return _parsed

    def _parse_cmd(self,key:str,cmd_key:str,**kwargs)->str|None:
        """ parse the cmd command it was ensured before in _get_cmd
           that all commands could be parsed
        """
        # first check if the executable is there
        _cmd = self.get_ref(key)
        if _cmd is None:
            _msg = f"[CONFIG] Couldn't find executable for key [{key}], can't parse"
            return None
        if Utils.is_windows():
            _cmd = f'"{_cmd}"'
        # get the cmd string
        _cmd_info = self._config.get(key).get(C.ConfigAttribute.COMMAND.value).get(cmd_key)
        if isinstance(_cmd_info,str):
            cmd_out = _cmd_info
        elif isinstance(_cmd_info,dict):
            cmd_out = _cmd_info.get(C.ConfigAttribute.RULE.value)
        # get all params / convert all params to upper case
        _cmd_params = re.findall(C.REGEX_BRACKET_CONTENT,cmd_out)
        for _cmd_param in _cmd_params:
            cmd_out = cmd_out.replace(f"[{_cmd_param}]",f"[{_cmd_param.upper()}]")
        _param_dict = {}
        for k,v in kwargs.items():
            _param_dict[k.upper()] = v
        # get parameter types in uppercase if available
        _param_info = self._config.get(key).get(C.ConfigAttribute.TYPE.value,{})
        _types_dict = {}
        for _type,_info in _param_info.items():
            _types_dict[_type.upper()] = _info

        _parsed_dict = {}
        _parsing_error = False
        # parse params / consider any typing
        for _param,_value in _param_dict.items():
            _type = _types_dict.get(_param)
            _parsed = self._parse_cmd_param(_param,_value,_type)
            _parsed_dict[_param] = _parsed
            if _parsed is None:
                _msg = f"[CONFIG] parsing error for key [{key}], param [{_param}], valie [{_value}], type [{_type}]"
                logger.warning(_msg)
                _parsing_error = True

        if _parsing_error is True:
            return None

        # replace string parts
        cmd_out = cmd_out.replace(f"[{C.CMD.upper()}]",_cmd)
        for _param_key,_param_value in _parsed_dict.items():
            if not isinstance(_param_value,str):
                _param_value = str(_param_value)
            cmd_out = cmd_out.replace(f"[{_param_key}]",_param_value)

        return cmd_out

    def parse_cmd(self,key:str,**kwargs) -> str|None:
        """ parses the a command line cmd for a configuration
            using the transferred kwargs (that need to match to the params)
            returns None if none could be found
        """
        # todo validate the passed args

        out = ""

        if C.ConfigKey.get_configtype(key) != C.ConfigKey.CMD:
            logger.debug(f"[CONFIG] Key [{key}] is not matching to a command line command")
            return None

        _cmd_config = self._config.get(key)
        if _cmd_config is None:
            logger.warning(f"[CONFIG] Key [{key}] is not in configured in environment")
            return None

        _commands = _cmd_config.get(C.ConfigAttribute.COMMAND.value)
        if _commands is None:
            logger.warning(f"[CONFIG] Key [{key}], no (c)ommands section")
            return None

        # find the correct command line parsing rule
        _cmd = self._get_cmd(key,cmd_key=None,**kwargs)
        if _cmd is None:
            logger.warning(f"[CONFIG] Key [{key}], Couldn't Parse CMD Rules with args {kwargs} ")
            return None

        # do the parsing
        out = self._parse_cmd(key=key,cmd_key=_cmd,**kwargs)
        return out

    def _validate_data_rules(self) -> dict:
        """ validates data rules  """
        out_wrong_keys = {}
        _config = self._config
        _ruledict_keys = list(C.RULEDICT_FILENAME.keys())
        for key, _ in _config.items():
            # _config_type =
            if C.ConfigKey.get_configtype(key) != C.ConfigKey.RULE:
                continue
        return out_wrong_keys

    def _get_config_keys(self):
        """ get config keys in order to ensure processing in order """
        _values = C.ConfigKey.get_values()
        out_keys = {v:[] for v in _values}
        _config_keys = list(self._config.keys())
        for _key in _config_keys:
            _out_key = _key.split("_")[0]+"_"
            out_keys[_out_key].append(_key)
        return out_keys

    def _resolve_path_object(self,key:str)->bool|None:
        """ resolves the path and file attributes """
        _config = self._config.get(key)

        # get file and path as file objects
        _p = _config.get(C.ConfigAttribute.PATH.value)
        _f = _config.get(C.ConfigAttribute.FILE.value)
        if _p is None and _f is None:
            return None

        _pf = [o for o in [_p,_f] if o is not None]
        _resolved = True
        for _o in _pf:
            # resolve variabeles found
            _matches = re.findall(C.REGEX_BRACKET_CONTENT,_o)
            if len(_matches) > 0: # underscore indicates a variable
                for _m in _matches:
                    self._add_dependency(key,_m)
                    _resolved = False

        # No dependencies, try to resolve items in order
        # file > file + path > path
        if _resolved is True:
            if _f and os.path.isfile(_f):
                _config[C.ConfigAttribute.REFERENCE.value] = _f
            elif _f and _p:
                _f_join = os.path.join(_p,_f)
                if os.path.isfile(_f_join):
                    _config[C.ConfigAttribute.REFERENCE.value] = _f_join
            elif _p and os.path.isdir(_p):
                _config[C.ConfigAttribute.REFERENCE.value] = _p
            else:
                _resolved = None
            if _resolved is None:
                logger.warning(f"[ConfigEnv] [{key}] can't be resolved to a valid file [{_f}], path [{_p}]")

        return _resolved

    def _resolve_where_object(self,key:str)->bool:
        """ resolves the where variable and returns whether it was resolved  """
        _config = self._config.get(key)
        # get the where key either from the key attribute or from Config
        _cmd_name = _config.get(C.ConfigAttribute.KEY.value,key.split("_")[1])
        # TODO you might add a preferred string
        # python as special case / determine the VENV
        if _cmd_name.lower() == "python":
            _cmd = Utils.get_python()
        else:
            _cmd = Utils.where(_cmd_name)

        _config[C.ConfigAttribute.WHERE.value] = _cmd
        # check whether this is an executable
        if os.path.isfile(_cmd):
            _resolved = True
        else:
            logger.warning(f"[ConfigEnv] [{key}] can't be resolved to a command [{_cmd}]")
            _resolved = None

        return _resolved

    def _add_meta(self,key:str)->bool:
        """ adds dependency (= other key is referenced )
            and config type to config item to attribute
            returns true if a reference was resolved
            None if there is an error or it was already processed
        """

        _config = self._config.get(key)
        if _config is None:
            logger.warning(f"[ConfigEnv] There is no key [{key}] in Config ")
            return None

        _config_type = C.ConfigKey.get_configtype(key)
        if _config_type:
            _config_key = _config_type.name

        # add type to group
        self._add_group(key,_config_key)
        self._set_status(key,C.ConfigStatus.INITIAL)

        # do not process anything if there is already a reference
        if _config.get(C.ConfigAttribute.REFERENCE.value) is not None:
            self._set_status(key,C.ConfigStatus.VALID)
            return True

        # analyze file object types
        # only further anaylsis is required for types of path, file, cmd and where
        _types_to_analyze = [C.ConfigKey.FILE,C.ConfigKey.PATH,C.ConfigKey.CMD,C.ConfigKey.WHERE,C.ConfigKey.RULE]
        _resolved = True
        if _config_type in _types_to_analyze:
            _resolved = self._resolve_path_object(key)

        if _config_type == C.ConfigKey.WHERE:
            _resolved = self._resolve_where_object(key)
        elif _config_type == C.ConfigKey.CMD:
            _resolved = self._resolve_command(key)

        # set the Config Status
        self._set_status(key,_resolved)

        return _resolved

    def _add_dependency(self,key:str,dependency:str)->None:
        """ adds a group item to a config Key """
        _config = self._config.get(key)
        if _config is None:
            return
        _dependencies = list(_config.get(C.ConfigAttribute.DEPENDENCY.value,[]))
        if not dependency in _dependencies:
            _dependencies.append(dependency)
            _config[C.ConfigAttribute.DEPENDENCY.value] = _dependencies

    def _set_status(self,key:str,status:C.ConfigStatus|bool|None)->None:
        """ sets the status, also accepts bool
            True: valid
            False: initial
            None: Invalid
        """
        _status = status
        if status is None:
            _status = C.ConfigStatus.INVALID
        if isinstance(status,bool):
            if status is True:
                _status = C.ConfigStatus.VALID
            elif status is False:
                _status = C.ConfigStatus.INITIAL
            else:
                _status = C.ConfigStatus.INVALID
        _config = self._config.get(key)

        _config[C.ConfigAttribute.STATUS.name] = _status.value

    def _add_group(self,key:str,group:str)->None:
        """ adds a group item to a config Key """
        _config = self._config.get(key)
        if _config is None:
            return
        _groups = list(_config.get(C.ConfigAttribute.GROUPS.value,[]))
        if not group in _groups:
            _groups.append(group)
            _config[C.ConfigAttribute.GROUPS.value] = _groups

    def _validate_command(self,key:str)->bool:
        """ Syntactically Validates a command
            Returns True if all is set
            Returns False if some parts need to resolved
            Returns None if there is an error
        """
        _config = self._config.get(key)
        _commands = _config.get(C.ConfigAttribute.COMMAND.value,{})
        # do a syntactical check for the command lines
        # cmd "CMD_F_FILE_LINE": "'[CMD]' -f [F_FILE] -l [LINE]"
        valid = True
        _used_params = []
        _param_names = []
        for _command,_command_info in _commands.items():
            if isinstance(_command_info,str):
                _command_str = _command_info
            elif isinstance(_command_info,dict):
                _command_str = _command_info.get(C.ConfigAttribute.RULE.value)
            if _command_str is None:
                _msg = f"[CONFIG] Param [{key}], (C)md [{_command}], couldn't locate command string"
                logger.warning(_msg)
                return None
            # get the keys
            _params_in_command = re.findall(C.REGEX_BRACKET_CONTENT,_command_str)
            # get the joint command params from key and command, take into account underscores
            _params_remaining = _command
            _params_in_key_and_command = []
            _wrong_params_in_command = []
            for _param_in_command in _params_in_command:
                if _param_in_command in _params_remaining:
                    _params_in_key_and_command.append(_param_in_command)
                    _params_remaining = _params_remaining.replace(_param_in_command,"")
                # param in command is not part of the command key
                else:
                    _wrong_params_in_command.append(_param_in_command)
                    # if the found key is not in configuration, mark this as error
                    if _param_in_command not in self._get_config_keys():
                        valid = None                    
                        _msg = f"[CONFIG] Param [{key}], param [{_param_in_command}] in [{_command_str}] is neither in Command Key nor it is a config key"
                        logger.warning(_msg)
                    # param is valid
                    else:
                        _used_params.append(_param_in_command)
            _used_params.extend(_params_in_key_and_command)

            _params_remaining = _params_remaining.split("_")
            # check if there are parts from the key in the command
            _wrong_params_in_command_key = []
            for _param_remaining in _params_remaining:
                if len(_param_remaining) == 0:
                    continue
                if not _param_remaining.lower() in _command_str.lower():
                    valid = None
                    _wrong_params_in_command_key.append(_param_remaining)
                    _msg = f"[CONFIG] Config [{key}], substring [{_param_remaining}] in cmd [{_command}] not found in command  [{_command_str}]"
                    logger.warning(_msg)
                

        # do a check for the types, if supplied
        _params = _config.get(C.ConfigAttribute.TYPE.value,{})
        _allowed_types = C.DataType.get_values()
        for _param_name,_param_type in _params.items():
            if not _param_name in _used_params:
                _msg = f"[CONFIG] Key [{key}], Param [{_param_name}], is not used in any of the variables {_used_params}"
                logger.warning(_msg)
                valid = None
            if not _param_type in _allowed_types:
                _msg = f"[CONFIG] Key [{key}], Param [{_param_name}], invalid type [{_param_type}], allowed {_allowed_types}"
                logger.warning(_msg)
                valid = None

        # TODO check for unresolved path / file references
        valid = self._resolve_path_object(key)

        return valid


    def _resolve_command(self,key:str)->dict:
        """ validates the command line commands
            returns True if valid configuration
            False if it still needs to be resolved
            None if there are inherent errors
        """
        _config = self._config.get(key)

        if C.ConfigKey.get_configtype(key) != C.ConfigKey.CMD:
            return None

        _commands = _config.get(C.ConfigAttribute.COMMAND.value)
        if _commands is None:
            _msg = f"[CONFIG] Key [{key}] has no (c)ommand section"
            logger.warning(_msg)
            return None

        if not isinstance(_commands,dict):
            _msg = f"[CONFIG] Key [{key}], (c)ommand section is not a dict"
            logger.warning(_msg)
            return None

        # validate the command
        _validated = self._validate_command(key)

        return _validated

    def _validate(self):
        """ analyzes key relations for any relations
            * in the first round resolve any paths / files without references already
            * in the second round try to fill missing refs
        """
        _config_all = self._config
        num_items = len(_config_all)
        num_success = 0
        _keys_dependent = []
        # get keys in order
        _key_dict = self._get_config_keys()
        _config_types = C.ConfigKey.get_values()
        # first resolve the ites without any references
        for _config_type in _config_types:
            _keys = _key_dict.get(_config_type,[])
            for _key in _keys:
                _resolved = self._add_meta(_key)
                if _resolved is False:
                    _keys_dependent.append(_key)
                elif _resolved is True:
                    num_success += 1

        # in the next turn resolve all initialized config items
        for _key in _keys_dependent:
            _resolved = self._resolve_dependencies(_key)
            if _resolved is True:
                num_success += 1
        logger.info(f"[ConfigEnv] Processed [{num_items}] configurations, successful [{num_success}] items")

    def _resolve_dependencies(self,key:str)->bool:
        """ resolves dependent entries in configuration
            returns true if all items were resolved, false otherwise
        """
        _config = self._config.get(key)
        if _config is None:
            return None
        _dependencies = list(_config.get(C.ConfigAttribute.DEPENDENCY.value))
        resolved = True
        # get references only
        _dependency_refs = {}
        for _dep in _dependencies:
            # TODO resolve single dependency
            _value = None
            if _dep == C.CONFIG_PATH_CWD:
                _value = os.getcwd()
            else:
                _config_ref_value = self.get_ref(_dep)
                if _config_ref_value is None:
                    logger.warning(f"[ConfigEnv] Config Key [{key}], can't resolve [{_dep}] to a path object")
                    return False
                else:
                    _dependency_refs[_dep] = _config_ref_value
        # now subtitute all dependencies
        _resolved = self._subst_dependencies(key,_dependency_refs)
        # set the processing status accordingly
        if _resolved == True:
            self._set_status(key,C.ConfigStatus.VALID)
        else:
            # if these items are False or None, set the status to invalid
            self._set_status(key,C.ConfigStatus.INVALID)
        return resolved

    def _subst_dependencies(self,key:str,dependencies:dict)->bool:
        """ substitute reference placeholders by its values and
            perform a substitution for path and file objects
        """
        _config = self._config.get(key)
        if _config is None:
            return True
        dependencies[C.CONFIG_PATH_CWD]=os.getcwd()

        # get file and path as file objects
        _attributes = [C.ConfigAttribute.FILE,C.ConfigAttribute.PATH]
        _config_deref = {}
        for _att in _attributes:
            _config_value_original = _config.get(_att.value)
            _config_value = _config_value_original
            if not _config_value:
                continue
            # find all placeholders
            _deps = re.findall(C.REGEX_BRACKET_CONTENT,_config_value)
            for _dep in _deps:
                _ref = dependencies.get(_dep)
                if not _ref:
                    continue
                # replace the bracketed placeholder by its referenced value
                _s_repl = f"[{_dep}]"
                _config_value = _config_value.replace(_s_repl,_ref)
            # sanity check: final value shouldn't contain any brackets
            if "[" in _config_value:
                logger.warning(f"[ConfigEnv] Error in Key [{key}], [{_att.name}], original [{_config_value_original}], resolved to [{_config_value}] ")
                return False
            _config_deref[_att] = _config_value
        # no substitutions
        if len(_config_deref) == 0:
            return True
        # now try to construct a path reference
        _p = _config_deref.get(C.ConfigAttribute.PATH)
        _f = _config_deref.get(C.ConfigAttribute.FILE)
        if _f and os.path.isfile(_f):
            _config[C.ConfigAttribute.REFERENCE.value]=_f
        elif _f and _p:
            _f_join = os.path.join(_p,_f)
            if os.path.isfile(_f_join):
                _config[C.ConfigAttribute.REFERENCE.value]=_f_join
            else:
                logger.warning(f"[ConfigEnv] Error in Key [{key}], resolved joined path [{_f_join}] invalid")
                return False
        elif _p and os.path.isdir(_p):
            _config[C.ConfigAttribute.REFERENCE.value]=_p
        else:
            logger.warning(f"[ConfigEnv] Error in Key [{key}], couldn construct path [{_p}] or file path [{_f}]")
            return False
        logger.debug(f"[ConfigEnv] Key [{key}], set path ref to [{_config[C.ConfigAttribute.REFERENCE.value]}]")
        return True

    def get_ref(self,key:str)->str:
        """ returns the constructed reference from Configuration """

        # treat special case with where variables where the excutable is stored
        # in the where attribute
        if C.ConfigKey.get_configtype(key) == C.ConfigKey.WHERE:
            _ref = self._config.get(key,{}).get(C.ConfigAttribute.WHERE.value)
        else:
            _ref = self._config.get(key,{}).get(C.ConfigAttribute.REFERENCE.value)
        if _ref is None:
            logger.warning(f"[CONFIG] Key [{key}] is invalid")
        return _ref

    def show_json(self)->None:
        """ display the configuration json """
        rprint("### CONFIGURATION")
        print_json(json.dumps(self._config))
        rprint("### CONFIG FILES FOUND IN BOOTSTRAPPING")
        print_json(json.dumps(self._f_config_dict))
        rprint(f"### CONFIG FILE USED \[{self._f_config }]")

    def show(self)->None:
        """ displays the config  """
        print(col(f"\n###### CONFIGURATION [{self._f_config}]\n","C_T"))
        _list = col("    *","C_TX")
        n = 1
        for key,config in self._config.items():
            _num = col(f"[{str(n).zfill(3)}] ","C_LN")
            _key = col(f"{key:<20} ","C_KY")
            _description = col(f"[{config.get(C.ConfigAttribute.DESCRIPTION.value,'NO DESCRIPTION')}]","C_TX")
            _description = f"{_description:<60}"

            _ref = config.get(C.ConfigAttribute.REFERENCE.value)
            if _ref:
                _ref = col("("+_ref+")","C_F")
            else:
                _ref = col("INVALID","C_ERR")
            print(_num+_key+_description+_ref)
            n+=1

    def _bootstrap_path(self,f_ext:str):
        """" bootstraps path to config file  i the following order
            if ENV CLI_CONFIG_DEMO is set => use /test_data/test_config/config_env_sample.json/

        """
        # choose one of the following paths for config in order

        # 1. demo config will be used first if set in VENV
        _f_demo = None
        if os.environ.get(C.ConfigBootstrap.CLI_CONFIG_DEMO.name) is not None:
            # create a demo config if not already there
            _f_demo = create_demo_config()
        # 2. external set path is next
        _f_ext = str(f_ext)
        # 3. path from environment
        _f_env = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_ENV.name)
        # 4. home path HOME/cli_client/cli_config.json (set in Constants)

        # parse for valid paths
        _config_names = [C.ConfigBootstrap.CLI_CONFIG_DEMO.name,
                         C.ConfigBootstrap.CLI_CONFIG_EXTERNAL.name,
                         C.ConfigBootstrap.CLI_CONFIG_ENV.name,
                         C.ConfigBootstrap.CLI_CONFIG_HOME.name]
        _config_files = [f if f is not None and os.path.isfile(f) else None for f in [_f_demo,_f_ext,_f_env,C.FILE_CONFIGFILE_HOME]]
        # the first in line is the config file
        _config_dict = dict(zip(_config_names,_config_files))
        for _name in _config_names:
            _f_config = _config_dict[_name]
            if _f_config is not None:
                self._f_config = _f_config
                break
        self._f_config_dict = _config_dict

if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    f = C.PATH_ROOT.joinpath("test_data","test_config","config_env_sample.json")
    config = ConfigEnv(f)
    # config.show()
    config.show_json()
