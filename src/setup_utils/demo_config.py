"""creates a demo config file with real paths"""

from pathlib import Path
import sys
import os
import logging
from rich.prompt import Confirm
from util import constants as C
from util.persistence import Persistence

from cli.bootstrap_env import CLI_LOG_LEVEL, TEST_PATH, FILE_CONFIGFILE_HOME


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


def create_demo_config(overwrite_if_exist: bool = False) -> str:
    """creates a demo config if not created yet and returns file path"""
    p_testpath = os.path.join(TEST_PATH, "test_data", "test_config")
    _sample_config_json = str(os.path.join(p_testpath, "config_env_sample.json"))
    if os.path.isfile(_sample_config_json) and overwrite_if_exist is False:
        print(f"    [DEMO_CONFIG] Sample already exists, return [{_sample_config_json}]")
        return _sample_config_json
    # create a sample file
    f_testconfig_template = str(Path(p_testpath).joinpath("config_env_template.json"))
    _sample_dict = Persistence.read_json(f_testconfig_template)
    print(f"    [DEMO_CONFIG] Reading [{f_testconfig_template}]")
    # populate path with real absolute paths
    _sample_dict["P_CONFIGTEST"]["p"] = str(p_testpath)
    # populate configfile 1 file with absolute path
    p_config_test1 = os.path.join(p_testpath, "file1_config.txt")
    _sample_dict["F_CONFIGTEST1"]["f"] = str(p_config_test1)
    # populate configfile3 with absolute path and file
    _sample_dict["F_CONFIGTEST3"]["p"] = str(p_testpath)
    print(f"    [DEMO_CONFIG] Saving updated sample config to [{_sample_config_json}]")
    Persistence.save_json(_sample_config_json, _sample_dict)
    return _sample_config_json


def create_config_home(overwrite_if_exist: bool = False) -> None:
    """creates a sample configuration in home, if not already there"""
    _p_home = str(Path(FILE_CONFIGFILE_HOME).parent)

    try:
        os.makedirs(str(_p_home))
    except FileExistsError:
        pass
    # get the demo file
    _f_demo = create_demo_config(overwrite_if_exist)
    _f_to = Persistence.copy_file(_f_demo, _p_home)
    print(f"### [DEMO_CONFIG] Created a sample file: [{_f_to}]")


if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name, C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _create_config = Confirm.ask(f"Do you want to create a sample config file [{FILE_CONFIGFILE_HOME}]?")
    if _create_config:
        create_config_home()
    else:
        print("Nothing created")
