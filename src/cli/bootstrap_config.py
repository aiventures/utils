""" bootstrapping environemnt and configuration """
from cli.bootstrap_env import OS_BOOTSTRAP_VARS
from util.config_env import ConfigEnv
from util_cli.cli_color_mapper import ThemeConsole

# only used for bootstrapping the enviroment variables before usage (eg log level for all modules)
os_bootstrap_vars = OS_BOOTSTRAP_VARS

# the configuration instance, the config file will be bootstrapped
# either from environment var (Filename stored in CLI_CONFIG_ENV) or from HOME path
config_env = ConfigEnv()

# the console output to be used for coloring output
# Note the Theme will be set in ThemeConsole Constructor in
# the following order (theme is set in the bootstrap_env odule):
# (1) environment env CLI_THEME
# (2) environment env CLI_THEME_DEFAULT
# (3) Hard Coded Variable util/constants.py/ConfigBootstrap.CLI_DEFAULT_THEME (ubuntu)
console_maker = ThemeConsole(theme=OS_BOOTSTRAP_VARS["CLI_THEME"])
# getting a default console 
console = console_maker.get_console()

