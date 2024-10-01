""" Configuration and Env Client """

import logging
from typing_extensions import Annotated
import os
import sys
import json
import typer
from rich import print as rprint
from rich.markup import escape as esc
from rich.logging import RichHandler
from rich import print_json
from pathlib import Path
from util.persistence import Persistence

# different config files - use an env file instead
from util.const_local import F_CONFIG
from util.const_local import LOG_LEVEL
from util import constants as C

logger = logging.getLogger(__name__)

cli = typer.Typer(name="cli_config_client", add_completion=False, help="Show Command Line Configuration and Environment")

def bootstrap_config():
    """ bootstraps configuration from environment variabe CLI_CONFIG that points to a configuration file
        if nothing is provided, an error wil be shown that only a demo configuration will be loaded ("demo_mode")        
        Use a wrapper program or something else to set the enviroment variable 
    """
    f_config = os.environ.get("CLI_CONFIG")

@cli.command("show")
def show():
    """ show configuration """
    print("show")

@cli.command()
def hello(name: str):
    """ default program """
    print(f"Hello Main {name}")

if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL",logging.INFO)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    f = os.environ.get("TESTx")
    print(f"ENV {f}")
    cli()


# def get_config_fileref(f:str=None,test:bool=False)->dict:
#     """ gets the config file """
#     f_config = f
#     if test:
#         p_testconfig = Path(__file__).parent.parent.parent.joinpath("test_data","test_config")
#         # you need to run the unit tests to create this file
#         f_config = os.path.join(p_testconfig,"config_env_sample.json")
#     else:
#         if f is None:
#             f_config = F_CONFIG
#     if f_config is None or  not (os.path.isfile(f_config)):
#         logger.error(f"Invalid Path to Config file [{f}] was supplied")
#         f_config = None
#     return f_config

# @cli.command("show")
# def show_config(f: Annotated[str, typer.Option("--f")]=None,
#                 test: Annotated[bool, typer.Option("--test")] = False):
#     """Display Configuration File.

#     Args:
#         f (str, optional): Path to configuration JSON. Defaults to None. If None a default path F_CONFIG from /util/const_local.py will be used (create this file beforehand).
#         test (bool, optional): Test Mode. if true, it will use the dummy config in test_config folder. Run Unit tests beforehand
#     """
#     f_config = get_config_fileref(f,test=test)
#     if f_config is None:
#         rprint(f"[bold red]Config File not found for \[{esc(f)}]")
#         sys.exit(1)
#     _config = Persistence.read_json(f_config)
#     # displaying the configuration as json
#     print_json(json.dumps(_config))