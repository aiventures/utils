"""bootstrapping the environemnt and configuration
this should be instanciated before anything else
"""

from pathlib import Path
import os
from logging import ERROR, WARNING

# list of bootstrap vars set in this file
OS_BOOTSTRAP_VARS = {}

# set log level from env variable CLI_LOG_LEVEL (or ERROR as default)
# this needs to be done before everything else, so that all logging modules
# will be provided a default logging level

CLI_LOG_LEVEL = int(os.environ.get("CLI_LOG_LEVEL", WARNING))
os.environ["CLI_LOG_LEVEL"] = str(CLI_LOG_LEVEL)
OS_BOOTSTRAP_VARS["CLI_LOG_LEVEL"] = CLI_LOG_LEVEL

# set a default command line theme and theme if not set already in environment
# it's also defined in /util/conststants.py/ConfigBootStrap
cli_default_theme = str(os.environ.get("CLI_DEFAULT_THEME", "ubuntu"))
os.environ["CLI_DEFAULT_THEME"] = cli_default_theme
OS_BOOTSTRAP_VARS["CLI_DEFAULT_THEME"] = cli_default_theme

cli_theme = str(os.environ.get("CLI_THEME", cli_default_theme))
os.environ["CLI_THEME"] = cli_theme
OS_BOOTSTRAP_VARS["CLI_THEME"] = cli_theme

# Setting Default location for configuration items
PATH_ROOT = Path(__file__).parent.parent.parent.absolute()
PATH_RESOURCES = PATH_ROOT.joinpath("resources")
PATH_HOME_DEFAULT = str(Path.home().joinpath(".cli_client"))
PATH_HOME = os.environ.get("CLI_PATH_HOME", PATH_HOME_DEFAULT)
PATH_TEST_OUTPUT = Path(PATH_HOME).joinpath("test_output")
FILE_CONFIGFILE_HOME = os.path.join(PATH_HOME, "cli_config.json")

OS_BOOTSTRAP_VARS["CLI_PATH_ROOT"] = PATH_ROOT
OS_BOOTSTRAP_VARS["CLI_PATH_RESOURCES"] = PATH_RESOURCES
OS_BOOTSTRAP_VARS["CLI_PATH_HOME_DEFAULT"] = PATH_HOME_DEFAULT
OS_BOOTSTRAP_VARS["CLI_PATH_HOME"] = PATH_HOME
OS_BOOTSTRAP_VARS["CLI_PATH_TEST_OUTPUT"] = PATH_TEST_OUTPUT
OS_BOOTSTRAP_VARS["CLI_FILE_CONFIGFILE_HOME"] = FILE_CONFIGFILE_HOME
