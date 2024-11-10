""" main cli entry """

import os
import logging
import typer
from typing_extensions import Annotated
from rich.logging import RichHandler
from util import constants as C
from cli import cli_customizing
from cli import cli_demo

logger = logging.getLogger(__name__)
logger.setLevel(int(os.environ.get("LOG_LEVEL",logging.INFO)))

app = typer.Typer(name="cli_client", add_completion=True, help="Command Line Client")
app.add_typer(cli_customizing.app,name="customizing")
app.add_typer(cli_demo.app,name="demo")

if __name__ == "__main__":
    log_level = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    # log_level = 99
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=log_level, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    app()

pass

# main as entry point
# @cli.command()
# def main(show: Annotated[bool, typer.Option("--show","-s",help="Show Configuration Environemnt")] = False,
#          show_json: Annotated[bool, typer.Option("--show_json","-j",help="Show Configuration as JSON")] = False):
#     """_summary_

#     Args:
#         show: Show Configuration Environemnt. Defaults to False.
#         show_json: Show COnfiguration Environment as json. Defaults to False.
#     """
#     if show:
#         show_config()
#     if show_json:
#         show_config_json()