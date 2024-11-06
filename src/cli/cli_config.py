""" Configuration and Env Client """

import logging
from typing_extensions import Annotated
import os
#import sys
#import json
import typer
from rich import print as rprint
from rich.console import Console
# from rich.markup import escape as esc
from rich.logging import RichHandler
import json
from rich import print_json
#from pathlib import Path
#from util.persistence import Persistence
from util import constants as C
from util.constants import DEFAULT_COLORS as CMAP
# from util.config_env import ConfigEnv
from cli.bootstrap_config import config_env
from cli.bootstrap_env import OS_BOOTSTRAP_VARS
from util_cli.cli_color_mapper import ColorMapper
# from util_cli import 

logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_config_client", add_completion=True, help="Configuration and Environment Settings")

@app.command("bootstrap")
def show_bootstrap_config():
    rprint(f"[{CMAP['out_title']}]### ENV BOOTSTRAP CONFIGURATION (cli.bootstrap_env)")
    print_json(json.dumps(OS_BOOTSTRAP_VARS))

@app.command("show")
@app.command("s")
def show_config():
    """ shows the configuration environment"""
    config_env.show()

@app.command("show-json")
@app.command("j")
def show_config_json():
    """ shows the configuration environment as json"""
    config_env.show_json()
    # show the env bootsrapping config 
    show_bootstrap_config()

@app.command("color-themes")    
def show_color_themes():
    """ shows the available color themes """
    pass

@app.command("ansi-colors")
def show_ansi_colors(with_names:bool=False):
    """ Show Table of ANSI COlors  """  
    _console = Console()  
    _ansi_table = ColorMapper.get_ansi_table(with_names)
    _console.print(_ansi_table)
    
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

