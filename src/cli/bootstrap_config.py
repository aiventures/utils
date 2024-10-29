""" bootstrapping environemnt and configuration """
from cli.bootstrap_env import cli_log_level
from util.config_env import ConfigEnv

# only used for bootstrapping the enviroment variablesa before usage (eg log level for all modules)
_ = cli_log_level
# the configuration instance, the config file will be bootstrapped
# either from environment var (Filename stored in CLI_CONFIG_ENV) or from HOME path
config_env = ConfigEnv()





