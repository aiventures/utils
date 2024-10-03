""" creates a demo config file with real paths """

from pathlib import Path
from shutil import copy2
import sys
import os
import logging
from rich.prompt import Confirm
from util import constants as C
from util.persistence import Persistence

logger = logging.getLogger(__name__)

def create_demo_config()->str:
    """ creates a demo config if not created yet and returns file path """
    p_testpath = C.PATH_ROOT.joinpath("test_data","test_config")
    f_testconfig_template = str(p_testpath.joinpath("config_env_template.json"))
    _sample_config_json = str(os.path.join(p_testpath,"config_env_sample.json"))
    if os.path.isfile(_sample_config_json):
        return _sample_config_json
    # create a sample file
    _sample_dict = Persistence.read_json(f_testconfig_template)
    # populate path with real absolute paths
    _sample_dict["P_CONFIGTEST"]["p"]=str(p_testpath)
    # populate configfile 1 file with absolute path
    p_config_test1 = os.path.join(p_testpath,"file1_config.txt")
    _sample_dict["F_CONFIGTEST1"]["f"]=str(p_config_test1)
    # populate configfile3 with absolute path and file
    _sample_dict["F_CONFIGTEST3"]["p"]=str(p_testpath)
    Persistence.save_json(_sample_config_json,_sample_dict)
    return _sample_config_json

def create_config_home()->None:
    """ creates a sample configuration in home, if not already there """
    _p_home = str(Path(C.FILE_CONFIGFILE_HOME).parent)
    if os.path.isfile(C.FILE_CONFIGFILE_HOME):
        print(f"Nothing to do, there is already a file here: [{C.FILE_CONFIGFILE_HOME}]")
        return
    try:
        os.makedirs(str(_p_home))
    except FileExistsError:
        pass
    # get the demo file
    _f_demo = create_demo_config()
    copy2(_f_demo,C.FILE_CONFIGFILE_HOME)
    print(f"Created a sample file: [{C.FILE_CONFIGFILE_HOME}]")

if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    _create_config = Confirm.ask(f"Do you want to create a sample config file [{C.FILE_CONFIGFILE_HOME}]?")
    if _create_config:
        create_config_home()
    else:
        print("Nothing created")
