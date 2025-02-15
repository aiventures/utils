"""bootstrapping the environemnt and configuration
this should be instanciated before anything else
"""

from pathlib import Path
import os
import shutil
from pprint import pprint
from logging import ERROR, WARNING

# list of bootstrap vars set in this file
OS_BOOTSTRAP_VARS = {}

# set log level from env variable CLI_LOG_LEVEL (or ERROR as default)
# this needs to be done before everything else, so that all logging modules
# will be provided a default logging level
ENV_CLI_LOG_LEVEL = os.environ.get("CLI_LOG_LEVEL")
OS_BOOTSTRAP_VARS["ENV_LOG_LEVEL"] = ENV_CLI_LOG_LEVEL
CLI_LOG_LEVEL = WARNING if ENV_CLI_LOG_LEVEL is None else int(ENV_CLI_LOG_LEVEL)
OS_BOOTSTRAP_VARS["ENV_CLI_LOG_LEVEL"] = ENV_CLI_LOG_LEVEL
OS_BOOTSTRAP_VARS["CLI_LOG_LEVEL"] = CLI_LOG_LEVEL

# setting default theme and current theme
ENV_DEFAULT_THEME = os.environ.get("CLI_DEFAULT_THEME")
OS_BOOTSTRAP_VARS["ENV_DEFAULT_THEME"] = ENV_DEFAULT_THEME
CLI_DEFAULT_THEME = "ubuntu" if ENV_DEFAULT_THEME is None else ENV_DEFAULT_THEME
OS_BOOTSTRAP_VARS["ENV_DEFAULT_THEME"] = ENV_DEFAULT_THEME
OS_BOOTSTRAP_VARS["CLI_DEFAULT_THEME"] = CLI_DEFAULT_THEME

ENV_THEME = os.environ.get("CLI_THEME")
OS_BOOTSTRAP_VARS["ENV_THEME"] = ENV_THEME
CLI_THEME = "ubuntu" if ENV_THEME is None else ENV_THEME
OS_BOOTSTRAP_VARS["ENV_THEME"] = ENV_THEME
OS_BOOTSTRAP_VARS["CLI_THEME"] = CLI_THEME

# Setting Default location for configuration items
PATH_ROOT = str(Path(__file__).parent.parent.parent.absolute())
OS_BOOTSTRAP_VARS["CLI_PATH_ROOT"] = PATH_ROOT

PATH_RESOURCES = os.path.join(PATH_ROOT, "resources")
OS_BOOTSTRAP_VARS["CLI_PATH_RESOURCES"] = PATH_RESOURCES
PATH_HOME_DEFAULT = os.path.join(str(Path.home()), ".cli_client")
OS_BOOTSTRAP_VARS["CLI_PATH_HOME_DEFAULT"] = PATH_HOME_DEFAULT
PATH_HOME = os.environ.get("CLI_PATH_HOME", PATH_HOME_DEFAULT)
OS_BOOTSTRAP_VARS["CLI_PATH_HOME"] = PATH_HOME

PATH_HOME_RESOURCES = os.path.join(PATH_HOME, "resources")
OS_BOOTSTRAP_VARS["CLI_PATH_HOME_RESOURCES"] = PATH_HOME_RESOURCES

PATH_TEST_OUTPUT = os.path.join(PATH_HOME, "test_output")
OS_BOOTSTRAP_VARS["CLI_PATH_TEST_OUTPUT"] = PATH_TEST_OUTPUT
FILE_CONFIGFILE_HOME = os.path.join(PATH_HOME, "cli_config.json")
OS_BOOTSTRAP_VARS["CLI_FILE_CONFIGFILE_HOME"] = FILE_CONFIGFILE_HOME

# configuration file from environment
FILE_CONFIGFILE_ENV = os.environ.get("CLI_CONFIG_ENV")
OS_BOOTSTRAP_VARS["CLI_FILE_CONFIGFILE_ENV"] = FILE_CONFIGFILE_ENV

# TEST PATH is used for all unit tests
# artifact files for tests can also be copied
# using /cli/bootstrap_env.py setup()
# also be sure to create the sample config file
# using /demo/demo_config.py
TEST_PATH = PATH_HOME
# SAMPLE CONFIG PATH
FILE_TEST_CONFIG = os.path.join(TEST_PATH, "config_env_sample.json")
OS_BOOTSTRAP_VARS["CLI_FILE_TEST_CONFIG"] = FILE_TEST_CONFIG

# bootstrap order for configuration
ENV_BOOTSTRAP_ORDER = os.environ.get("CLI_BOOTSTRAP_ORDER")
OS_BOOTSTRAP_VARS["ENV_BOOTSTRAP_ORDER"] = ENV_BOOTSTRAP_ORDER
# default order to get the configuration file

# 1. direct file path
# 2. environment variable ("config_env")
# 3. file env CLI_PATH_HOME/cli_config.json or HOME/cli_config.json (see above)
# 4. test path, right now set to CLI_PATH_HOME/cli_config_env_sample.json
#    or HOME/cli_config_env_sample.json
#  ConfigBootstrap: CLI_CONFIG_EXTERNAL, CLI_CONFIG_ENV,CLI_CONFIG_HOME, CLI_CONFIG_DEMO
CLI_BOOTSTRAP_ORDER = (
    "config_external,config_env,config_home,demo" if ENV_BOOTSTRAP_ORDER is None else ENV_BOOTSTRAP_ORDER
)
OS_BOOTSTRAP_VARS["CLI_BOOTSTRAP_ORDER"] = CLI_BOOTSTRAP_ORDER

OS_BOOTSTRAP_VARS["ENV_THEME"] = ENV_THEME
OS_BOOTSTRAP_VARS["CLI_THEME"] = CLI_THEME


def show_bootstrap_config():
    """display the bootstrapping config"""
    print("\n### BOOTSTRAPPING VARS (/cli/bootstrap_env.py)")
    pprint(OS_BOOTSTRAP_VARS, indent=4)


def setup(exist_ok: bool = True, copy_resources: bool = True) -> None:
    """create paths and artifacts from bootstrap environment create over existing"""
    print("\n### [BOOTSTRAP_ENV] Creating Paths")
    for _key, _path in OS_BOOTSTRAP_VARS.items():
        if not _key in ["CLI_PATH_HOME", "CLI_PATH_TEST_OUTPUT", "CLI_PATH_HOME_RESOURCES"]:
            continue

        try:
            os.makedirs(_path, exist_ok=exist_ok)
            print(f"    [BOOTSTRAP_ENV] {_key}: Created [{_path}]")
        except FileExistsError:
            print(f"    [BOOTSTRAP_ENV] [{_path}] already exists")
    if not copy_resources:
        return

    try:
        _ = shutil.copytree(PATH_RESOURCES, PATH_HOME_RESOURCES, dirs_exist_ok=exist_ok)
        print(f"    [BOOTSTRAP_ENV] Created Resources [{PATH_HOME_RESOURCES}]")
    except FileExistsError:
        print(f"    [BOOTSTRAP_ENV] Not Copying, [{PATH_HOME_RESOURCES}] already exists")

    try:
        _p_test_data = os.path.join(PATH_ROOT, "test_data")
        _p_test_data_home = os.path.join(PATH_HOME, "test_data")
        _ = shutil.copytree(_p_test_data, _p_test_data_home, dirs_exist_ok=exist_ok)
        print(f"    [BOOTSTRAP_ENV] Created Test Data [{_p_test_data_home}]")
    except FileExistsError:
        print(f"    [BOOTSTRAP_ENV] Not Copying, [{_p_test_data_home}] already exists")


if __name__ == "__main__":
    show_bootstrap_config()
    setup(exist_ok=True)
