""" bootstrapping the environemnt and configuration """

import os
from util.constants import CLI_LOG_LEVEL
from logging import ERROR

# set log level from env variable CLI_LOG_LEVEL (or ERROR as default)
cli_log_level=str(os.environ.get(CLI_LOG_LEVEL,ERROR))
os.environ[CLI_LOG_LEVEL]=cli_log_level
