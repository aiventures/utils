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
# from util.config_env import ConfigEnv
from cli.bootstrap_config import config_env

logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_config_client", add_completion=True, help="Configuration and Environment Settings")

@app.command("show")
@app.command("s")
def show_config():
    """ shows the configuration environment"""
    config_env.show()

# @cli.callback("show_json")
@app.command("show_json")
@app.command("j")
def show_config_json():
    """ shows the configuration environment as json"""
    config_env.show_json()

# https://typer.tiangolo.com/tutorial/commands/callback/
@app.callback()
def main():
    """ main method """
    pass

if __name__ == "__main__":
    log_level = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=log_level, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    app()
