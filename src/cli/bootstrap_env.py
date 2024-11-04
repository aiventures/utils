""" bootstrapping the environemnt and configuration """

import os
from logging import ERROR

# list of bootstrap vars set in this file
OS_BOOTSTRAP_VARS = {}

# set log level from env variable CLI_LOG_LEVEL (or ERROR as default)
# this needs to be done before everything else, so that all logging modules
# will be provided a default logging level
cli_log_level=str(os.environ.get("CLI_LOG_LEVEL",ERROR))
os.environ["CLI_LOG_LEVEL"]=cli_log_level
OS_BOOTSTRAP_VARS["CLI_LOG_LEVEL"]=cli_log_level

# set a default command line theme and theme if not set already in environment
# it's also defined in /util/conststants.py/ConfigBootStrap
cli_default_theme=str(os.environ.get("CLI_DEFAULT_THEME","ubuntu"))
os.environ["CLI_DEFAULT_THEME"]=cli_default_theme
OS_BOOTSTRAP_VARS["CLI_DEFAULT_THEME"]=cli_default_theme

cli_theme=str(os.environ.get("CLI_THEME",cli_default_theme))
os.environ["CLI_THEME"]=cli_theme
OS_BOOTSTRAP_VARS["CLI_THEME"]=cli_theme
