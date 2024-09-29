""" Configuration and Env Client """

import logging
from typing_extensions import Annotated
import os
import sys
import typer
from rich import print as rprint
from rich.markup import escape as esc
from rich.logging import RichHandler
from pathlib import Path

# different config files
from util.const_local import F_CONFIG
from util.const_local import LOG_LEVEL

logger = logging.getLogger(__name__)

cli = typer.Typer(name="cli_config_client", add_completion=False, help="Show Command Line Configuration and Environment")

def get_config_fileref(f:str=None,test:bool=False)->dict:
    """ gets the config file """
    f_config = f
    if test:
        p_testconfig = Path(__file__).parent.parent.parent.joinpath("test_data","test_config")
        # you need to run the unit tests to create this file
        f_config = os.path.join(p_testconfig,"config_env_sample.json")
    else:
        if f is None:
            f_config = F_CONFIG
    if f_config is None or  not (os.path.isfile(f_config)):
        logger.error(f"Invalid Path to Config file [{f}] was supplied")
        f_config = None
    return f_config

@cli.command("show")
def show_config(f: Annotated[str, typer.Option("--f")]=None,
                test: Annotated[bool, typer.Option("--test")] = False):
    """Display Configuration File.

    Args:
        f (str, optional): Path to configuration JSON. Defaults to None. If None a default path F_CONFIG from /util/const_local.py will be used (create this file beforehand).
        test (bool, optional): Test Mode. if true, it will use the dummy config in test_config folder. Run Unit tests beforehand
    """
    f_config = get_config_fileref(f)
    if f_config is None:
        rprint(f"[bold red]Config File not found for \[{esc(f)}]")
        sys.exit(1)
    rprint(f"Hello CONFIG CLI {test}")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    cli()

