""" Configuration and Env Client """

import logging
from typing_extensions import Annotated
import os
#import sys
#import json
import typer
#from rich import print as rprint
#from rich.markup import escape as esc
from rich.logging import RichHandler
#from rich import print_json
#from pathlib import Path
#from util.persistence import Persistence

from util import constants as C
from util.config_env import ConfigEnv

logger = logging.getLogger(__name__)

# the configuration instance, the config file will be bootstrapped 
# either from environment vars or from HOME path
config_env = ConfigEnv()

cli = typer.Typer(name="cli_config_client", add_completion=True, help="Configuration and Environment Settings")

@cli.command("show")
@cli.command("s")
def show_config():
    """ shows the configuration environment"""
    config_env.show()

# @cli.callback("show_json")
@cli.command("show_json")
@cli.command("j")
def show_config_json():
    """ shows the configuration environment as json"""
    config_env.show_json()    

if __name__ == "__main__":
    log_level = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)    
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=log_level, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    cli()
    # typer.run(main)

