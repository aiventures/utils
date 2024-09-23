""" Managing Configuration for a given command line """

import os
import sys
import re
import logging
from pathlib import Path
# TODO REPLACE BY UNIT TESTS
# when doing tests add this to reference python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from util.persistence import Persistence
from util.colors import col
from util import constants as C
from util.utils import Utils

logger = logging.getLogger(__name__)

class ConfigEnv():
    """ Configuration of Command Line Environment  """

    def __init__(self,f_config:str=None) -> None:
        """ constructor """
        self._f_config = f_config
        self._config = Persistence.read_json(self._f_config)
        self._config_keys = list(self._config.keys())
        self._wrong_rule_keys = {}
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
    def get_env_by_groups(self,groups:list|str=None):
        """ filter env entries by group. """
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

    def _resolve_path(self,key):
        _config = self._config.get(key)
        _path_out = str(_config.get(C.ConfigAttribute.PATH.value))
        if _path_out is None:
            logger.debug(f"[CONFIG] No path was supplied in Config for key [{key}]")
            return None

        # path is current directory
        if _path_out == C.CONFIG_PATH_CWD: # use current path as directory
            return os.path.abspath(os.getcwd())

        # path can be resolved to a real path
        if os.path.isdir(_path_out):
            return os.path.abspath(_path_out)

        _path_key = None
        _replace_str = None
        # check if there is a PATHVAR replacements
        # path = '[PATHVAR]/subpath/.../' => [PATHVAR] will be resolved
        regex_subpaths = re.findall(C.REGEX_BRACKETS,_path_out)
        if len(regex_subpaths) == 1:
            _path_key = regex_subpaths[0][1:-1]
            _replace_str = regex_subpaths[0]
        # check if there is a single key reference
        elif _path_out in self._config_keys:
            _path_key = _path_out
            _replace_str = _path_out

        logger.debug(f"[CONFIG]  Key [{key}], replacing Path by reference from [{_path_key}]")
        if _path_key is None:
            logger.debug(f"[CONFIG]  Key [{key}], no path reference found")
            return None

        # get the path from path ref or from path as fallback
        _path_ref = _config.get(_path_key,{}).get(C.ConfigAttribute.REFERENCE.value)
        if _path_ref is None:
            _path_ref = self._config.get(_path_key,{}).get(C.ConfigAttribute.PATH.value)

        # resolve path from path refs in path variables
        if _path_ref is None or _replace_str is None:
            logger.info(f"[CONFIG]  [{key}], reference [{_path_key}], no information found")
            return None
        path_out = _path_out.replace(_replace_str,_path_ref)
        path_out = os.path.abspath(path_out)
        path_exists = os.path.isdir(path_out)
        s = f"[CONFIG]  Key [{key}], path [{_path_out}], calculated path [{path_out}], exists [{path_exists}]"
        if path_exists:
            logger.info(s)
            return path_out
        else:
            logger.warning(s)
            return None

    def _resolve_file(self,key:str)->str:
        """ validate a file reference in key"""
        _config = self._config.get(key)
        _fileref = _config.get(C.ConfigAttribute.FILE.value,"")

        # check if it is a file
        if os.path.isfile(_fileref):
            _fileref = os.path.abspath(_fileref)
            logger.debug(f"[CONFIG] Key [{key}]: absolute file path [{_fileref}]")
            return _fileref

        # validate pathref
        _pathref = self._resolve_path(key)

        # check if it is a valid path when using path_ref
        if _pathref:
            _fileref = os.path.abspath(os.path.join(_pathref,_fileref))
            if os.path.isfile(_fileref):
                logger.debug(f"[CONFIG] Key [{key}]: combined path/file [{_fileref}]")
                return _fileref
            else:
                return None

    def _get_cmd(self,key,**kwargs)->str:
        """ passed on params supplied, identify the correct command """
        _config_cmds = self._config.get(key,{}).get(C.ConfigAttribute.COMMAND.value,{})
        _cmd_keys = [k.lower() for k in list(kwargs.keys())]
        logger.debug(f"[CONFIG] Find command rule for env key [{key}], params {_cmd_keys}")
        _matching_rules = {}
        for _cmd in _config_cmds.keys():
            # match the signature in the configuration with
            # the passed parameters
            _rule_keys = _cmd.lower().split("_")
            _rule_matches = {}
            _matches_all_rules = True
            for _rule_key in _rule_keys:
                # ignore cmd, will be replaced by cmd in configuration
                if _rule_key == "cmd":
                    continue
                _matches_rule = True if _rule_key in _cmd_keys else False
                _rule_matches[_rule_key] = _matches_rule
                if _matches_rule is False:
                    _matches_all_rules = False
            logger.debug(f"[CONFIG]  Key [{key}], rule [{_cmd}], keys {_cmd_keys}, overall match [{_matches_all_rules}]")
            if _matches_all_rules:
                _matching_rules[_cmd] = _rule_matches

        num_matching_rules = len(_matching_rules)
        # returns found rule
        if num_matching_rules == 0:
            logger.warning("[CONFIG] No valid cmd rules found for Env Key [{key}], using keys {_cmd_keys}")
            return None

        # in case there is only one rule, return this one
        if num_matching_rules == 1:
            logger.info("[CONFIG] Valid rule found for Env Key [{key}], using keys {_cmd_keys}")
            return list(_matching_rules.keys())[0]

        # try to match the one with the highest number of matching parameters
        # do not return anything in case there are ambiguities
        num_max_params = 0
        rule_out = None
        duplicate_rules = []
        for _rule,_rule_info in _matching_rules.items():
            num_params = len(_rule_info)
            if num_params > num_max_params:
                duplicate_rules = [_rule]
                num_max_params = num_params
                rule_out = _rule
            elif num_params == num_max_params:
                duplicate_rules.append(_rule)
                rule_out = None

        if rule_out is None:
            logger.warning(f"[CONFIG] Multiple rules {duplicate_rules} found for Env Key [{key}], using keys {_cmd_keys}, skipped")
        else:
            logger.info(f"[CONFIG] Multiple rules for Env Key [{key}], using keys {_cmd_keys}, using rule [{rule_out}] (max num of params)")

        return rule_out

    def _parse_cmd(self,key:str,cmd_key:str,**kwargs)->dict:
        """ parse the cmd command """

        env_vars = {}
        for k,v in kwargs.items():
            env_vars[k.lower()] = v
        # get the config items / should be checked before
        _env_config = self._config.get(key)
        _cmd_info = _env_config.get(C.ConfigAttribute.COMMAND.value,{}).get(cmd_key)

        # replace the cmd commands
        if _cmd_info is None:
            logger.warning(f"[CONFIG] Key [{key}], cmd key [{cmd_key}] not found, please check")
            return None

        if isinstance(_cmd_info,str):
            _cmd_info = {C.ConfigAttribute.RULE.value:_cmd_info,
                         C.ConfigAttribute.DESCRIPTION.value:"No description"}

        # parse the command line string
        cmd_out = _cmd_info.get(C.ConfigAttribute.RULE.value)
        if cmd_out is None:
            logger.warning(f"[CONFIG] Rule [{key}], no (r)ule found")
            return None

        # replace the cmd string
        cmd = _env_config.get(C.ConfigAttribute.REFERENCE.value)
        if cmd is None:
            logger.warning(f"[CONFIG] [{key}], no executable was found, check file and path")
            return None
        env_vars[C.CMD] = cmd

        # from the cmd template get all variables for replacement
        _vars = re.findall(C.REGEX_BRACKETS,cmd_out,re.IGNORECASE)
        for _var in _vars:
            cmd_out = cmd_out.replace(_var,_var.lower())
        _vars = [v.lower() for v in _vars]

        # replace all occurences
        for _var in _vars:
            _key = _var[1:-1]
            # TDOO apply special logic in case the constant needs to be replaced
            # like for instance python exe needs to be replaced by VENV executable
            _value = str(env_vars.get(_key))
            # TODO check if value contains space and can be interpreted as string or path
            # if so, enclose it into parentheses / or us single quotes as marker to replace them due to json formatting
            if _value is None:
                logger.warning(f"[CONFIG]  Rule [{key}], cmd_key [{cmd_key}], couldn't replace [{_var}], env_vars {env_vars}")
                cmd_out = None
                break
            cmd_out = cmd_out.replace(_var,_value)
        # replace single quotes by double quotes
        cmd_out = cmd_out.replace("'",'"')
        return cmd_out

    def parse_cmd(self,key:str,**kwargs) -> str|None:
        """ parses the a command line cmd for a configuration
            returns None if now could be found
        """
        out = ""
        key_prefix = key.split("_")[0]+"_"
        if not key_prefix == C.CONFIG_KEY_CMD:
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
        _cmd = self._get_cmd(key,**kwargs)
        if _cmd is None:
            logger.warning(f"[CONFIG] Key [{key}], Couldn't Parse CMD Rules with args {kwargs} ")
            return None

        # do the parsing
        out = self._parse_cmd(key=key,cmd_key=_cmd,**kwargs)
        return out

    def _validate_command(self,key:str,command:str)->list:
        """ validates the command for formal correctness,
            will return an error message
        """
        msg_out = []
        # get the vars from the command key
        _cmd_keys = command.split("_")
        _cmd_keys = [k.lower() for k in _cmd_keys]

        # get the variables from the command string
        _cmd_info = self._config.get(key,{}).get(C.ConfigAttribute.COMMAND.value,{}).get(command)
        # command can either be a string or dict
        if isinstance(_cmd_info,str):
            _cmd_info = {C.ConfigAttribute.RULE.value:_cmd_info,C.ConfigAttribute.DESCRIPTION.value:"No description"}
        _cmd_vars = re.findall(C.REGEX_BRACKETS,_cmd_info.get(C.ConfigAttribute.RULE.value,""),re.IGNORECASE) # from the cmd template get all variables for replacement
        _cmd_vars = [c.lower()[1:-1] for c in _cmd_vars]

        # now at least all vars from command string should be present
        for _cmd_var in _cmd_vars:
            if not _cmd_var in _cmd_keys:
                _msg = f"[CONFIG] Key [{key}], command [{_cmd_var}] missing in Command key [{command}]"
                logger.warning(_msg)
                msg_out.append(_msg)

        # if a param is present in command key but not in command string, this is worth an information
        for _cmd_key in _cmd_keys:
            if not _cmd_key in _cmd_vars:
                logger.info(f"[CONFIG] key [{key}], parameter [{_cmd_key}] missing in Command key [{command}]")

        return msg_out


    def _validate_commands(self)->dict:
        """ validates the command line commands
            returns dict of wrong commands
        """
        out_wrong_keys = {}
        _config = self._config

        for key, config in _config.items():
            key_prefix = key.split("_")[0]+"_"
            if not key_prefix == C.CONFIG_KEY_CMD:
                continue

            _commands = config.get(C.ConfigAttribute.COMMAND.value)
            if _commands is None:
                _msg = f"[CONFIG] Key [{key}] has no (c)ommand section"
                logger.warning(_msg)
                out_wrong_keys[key] = [_msg]
                continue

            if not isinstance(_commands,dict):
                _msg = f"[CONFIG] Key [{key}], (c)ommand section is not a dict"
                logger.warning(_msg)
                out_wrong_keys[key] = [_msg]
                continue
            _msg_list = []
            for _cmd in _commands.keys():
                _msgs = self._validate_command(key,_cmd)
                if len(_msgs) > 0:
                    _msg_list.append(_msgs)
            if len(_msg_list) > 0:
                out_wrong_keys[key] = _msg_list

        return out_wrong_keys

    def _validate_rules(self) -> dict:
        """ validate the env Vars that represent a rule
            returns dict of wrong rule keys
        """
        out_wrong_keys = {}
        _config = self._config
        _ruledict_keys = list(C.RULEDICT_FILENAME.keys())
        for key, config in _config.items():
            key_prefix = key.split("_")[0]+"_"
            if not key_prefix == C.CONFIG_KEY_RULE:
                continue
            _rules = config.get(C.ConfigAttribute.RULE.value)
            if _rules is None:
                logger.warning(f"[CONFIG] Key [{key}] has no (r)ule section")
                continue

            if not isinstance(_rules,list):
                logger.warning(f"[CONFIG] Key [{key}] is not a list in rule section")
                continue

            _wrong_keys_per_key = []

            for _rule in _rules:
                _rule_keys = list(_rule.keys())
                _wrong_keys = [k for k in _rule_keys if not k in _ruledict_keys]
                if len(_wrong_keys) > 0:
                    logger.warning(f"[CONFIG] Key [{key}], rules contain invalid keys {_wrong_keys}")
                    _wrong_keys_per_key.extend(_wrong_keys)
            _wrong_keys_per_key = list(set(_wrong_keys_per_key))
            if len(_wrong_keys_per_key) > 0:
                out_wrong_keys[key] = _wrong_keys_per_key
        return out_wrong_keys

    def _validate_data_rules(self) -> dict:
        """ validates data rules
        """
        out_wrong_keys = {}
        _config = self._config
        _ruledict_keys = list(C.RULEDICT_FILENAME.keys())
        for key, _ in _config.items():
            key_prefix = key.split("_")[0]+"_"
            if not key_prefix == C.CONFIG_KEY_RULE:
                continue
        return out_wrong_keys

    def _validate(self) -> None:
        """ validates the configuration and populates ref section """
        _config = self._config
        logger.debug(f"[CONFIG] ({self._f_config}) contains [len({_config})] items")
        for key, config in _config.items():
            config[C.ConfigAttribute.REFERENCE.value] = None
            key_prefix = key.split("_")[0]+"_"
            if not key_prefix in C.CONFIG_KEY_TYPES:
                logger.warning(f"[CONFIG] Key [{key}] has invalid prefix, allowed {C.CONFIG_KEY_TYPES}")
                continue
            # check for data definition type
            if key_prefix == C.CONFIG_KEY_DATA:
                continue
            _file_ref = None
            # validate file file type
            if key_prefix == C.CONFIG_KEY_FILE or key_prefix == C.CONFIG_KEY_CMD:
                _file_ref = self._resolve_file(key)
            elif key_prefix == C.CONFIG_KEY_PATH:
                _file_ref = self._resolve_path(key)
            elif key_prefix == C.CONFIG_KEY_WHERE:
                # TODO Resolve command using where logic
                cmd = key.replace(C.CONFIG_KEY_WHERE,"").upper()
                # treat special cases
                if cmd == C.Cmd.GIT.name:
                    
                    pass
                elif cmd == C.Cmd.PYTHON.name:
                    _file_ref = Utils.get_python()
                    pass
                elif cmd == C.Cmd.VENV.name:
                    pass
                elif cmd == C.Cmd.CYGPATH.name:
                    pass
                else:
                    pass
                pass

            if _file_ref is not None:
                logger.debug(f"[CONFIG] Resolved fileref for config key [{key}], value [{_file_ref}]")
                config[C.ConfigAttribute.REFERENCE.value] = _file_ref

        # validate rules
        self._wrong_rule_keys.update(self._validate_rules())
        # validate commands
        # rule name list of wrong config keys
        self._wrong_rule_keys.update(self._validate_commands())



    def get_ref(self,key:str)->str:
        """ returns the constructed reference from Configuration """
        _ref = self._config.get(key,{}).get(C.ConfigAttribute.REFERENCE.value)
        if _ref is None:
            logger.warning(f"[CONFIG] Key [{key}] is invalid")
        return _ref

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

if __name__ == "__main__":
    loglevel = logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    f = Path(__file__).parent.parent.parent.joinpath("test_config","config_env_sample.json")
    config = ConfigEnv(f)
    config.show()

