""" command line client for share client """
import logging
import typer
# from typing_extensions import Annotated
import sys
from rich import print
import os 
from util import constants as C
# path to config json
# from util.const_local import F_CONFIG_ENV

# different config files
from util.const_local import F_CONFIG
from util.const_local import LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_share_parser_client", add_completion=False, help="Share Parser (Transforming share info to CSV)")

@app.command("test_scp")
@app.command("t_scp")
def xyz_function(xyz:str,test:str="Test"):
    """_summary_

    Args:
        xyz (str): _description_
        test (str, optional): _description_. Defaults to "Test".
    """
    print(f"Hello Share Parser CLI {test}")

# https://typer.tiangolo.com/tutorial/commands/callback/
@app.callback()
def main():
    """ main method """
    pass

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    app()
