""" Managing Configuration for a given command line """

import os
import sys
import re
from pathlib import Path
# when doing tests add this to reference python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import logging
from util.persistence import Persistence
from util.colors import col
from util.const_local import F_CONFIG_ENV
from util import constants as C


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
        pass

    # todo get config groups
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
            _groups_env = _config_info.get(C.CONFIG_GROUPS,{})
            if len(_groups_env) == 0:
                continue
            if any([g_env in _groups for g_env in _groups_env]):
                logger.debug(f"Key [{_config_key}], found match in group {_groups_env}")
                out_config[_config_key] = _config_info
        logger.info(f"Get Config Env using groups {_groups}, returning [{len(out_config)}] entries")
        return out_config

    def _resolve_path(self,key):
        _config = self._config.get(key)
        _path_out = str(_config.get(C.CONFIG_PATH))
        if _path_out is None:
            logger.debug(f"No path was supplied in Config for key [{key}]")
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

        logger.debug(f"Config Key [{key}], replacing Path by reference from [{_path_key}]")
        if _path_key is None:
            logger.debug(f"Config Key [{key}], no path reference found")
            return None

        # get the path from path ref or from path as fallback
        _path_ref = _config.get(_path_key,{}).get(C.CONFIG_REFERENCE)
        if _path_ref is None:
            _path_ref = self._config.get(_path_key,{}).get(C.CONFIG_PATH)
        
        # resolve path from path refs in path variables
        if _path_ref is None or _replace_str is None:
            logger.info(f"Config [{key}], reference [{_path_key}], no information found")
            return None
        path_out = os.path.abspath(_path_out.replace(_replace_str,_path_ref))
        path_exists = os.path.isdir(path_out)
        s = f"Config Key [{key}], path [{_path_out}], calculated path [{path_out}], exists [{path_exists}]"
        if path_exists:
            logger.info(s)
            return path_out
        else:
            logger.warning(s)
            return None

    def _resolve_file(self,key:str)->str:
        """ validate a file reference in key"""
        _config = self._config.get(key)
        _fileref = _config.get(C.CONFIG_FILE,"")

        # check if it is a file
        if os.path.isfile(_fileref):
            _fileref = os.path.abspath(_fileref)
            logger.debug(f"Key [{key}]: absolute file path [{_fileref}]")
            return _fileref

        # validate pathref
        _pathref = self._resolve_path(key)

        # check if it is a valid path when using path_ref
        if _pathref:
            _fileref = os.path.abspath(os.path.join(_pathref,_fileref))
            if os.path.isfile(_fileref):
                logger.debug(f"Key [{key}]: combined path/file [{_fileref}]")
                return _fileref
            else:
                return None
    
    def validate_rules(self) -> dict:
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
            _rules = config.get(C.CONFIG_RULE)
            if _rules is None:
                logger.warning(f"Env Key [{key}] has no rule section")
                continue

            if not isinstance(_rules,list):
                logger.warning(f"Env Key [{key}] is not a list in rule section")
                continue

            _wrong_keys_per_key = []

            for _rule in _rules:
                _rule_keys = list(_rule.keys())
                _wrong_keys = [k for k in _rule_keys if not k in _ruledict_keys]
                if len(_wrong_keys) > 0:
                    logger.warning(f"Env Key [{key}], rules contain invalid keys {_wrong_keys}")                    
                    _wrong_keys_per_key.extend(_wrong_keys)
            _wrong_keys_per_key = list(set(_wrong_keys_per_key))
            if len(_wrong_keys_per_key) > 0:
                out_wrong_keys[key] = _wrong_keys_per_key
        return out_wrong_keys

    def _validate(self) -> None:
        """ validates the configuration and populates ref section """
        _config = self._config
        logger.debug(f"Configuration ({self._f_config}) contains [len({_config})] items")
        for key, config in _config.items():
            config[C.CONFIG_REFERENCE] = None
            key_prefix = key.split("_")[0]+"_"
            if not key_prefix in C.CONFIG_KEY_TYPES:
                logger.warning(f"Config Key [{key}] has invalid prefix, allowed {C.CONFIG_KEY_TYPES}")
                continue
            _file_ref = None
            # validate file file type
            if key_prefix == C.CONFIG_KEY_FILE or key_prefix == C.CONFIG_KEY_CMD:
                _file_ref = self._resolve_file(key)
            elif key_prefix == C.CONFIG_KEY_PATH:
                _file_ref = self._resolve_path(key)
            
            if _file_ref is not None:
                logger.debug(f"Resolved fileref for config key [{key}], value [{_file_ref}]")
                config[C.CONFIG_REFERENCE] = _file_ref
        
        # validate rules
        self._wrong_rule_keys = self.validate_rules()

    def get_ref(self,key:str)->str:
        """ returns the constructed reference from Configuration """
        _ref = self._config.get(key,{}).get(C.CONFIG_REFERENCE)
        if _ref is None:
            logger.warning(f"Key [{key}] is invalid")
        return _ref

    def show(self)->None:
        """ displays the config  """
        print(col(f"\n###### CONFIGURATION [{self._f_config}]\n","C_T"))
        _list = col("    *","C_TX")
        n = 1
        for key,config in self._config.items():
            _num = col(f"[{str(n).zfill(3)}] ","C_LN")
            _key = col(f"{key:<20} ","C_KY")
            _description = col(f"[{config.get(C.CONFIG_DESCRIPTION,'NO DESCRIPTION')}]","C_TX")
            _description = f"{_description:<60}"

            _ref = config.get(C.CONFIG_REFERENCE)
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

