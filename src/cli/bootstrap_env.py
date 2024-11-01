""" bootstrapping the environemnt and configuration """

import os
from logging import ERROR

# set log level from env variable CLI_LOG_LEVEL (or ERROR as default)
# this needs to be done before everything else, so that all logging modules
# will be provided a default logging level

cli_log_level=str(os.environ.get("CLI_LOG_LEVEL",ERROR))
os.environ["CLI_LOG_LEVEL"]=cli_log_level
