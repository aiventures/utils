""" sample cli config """
import logging
import typer
import sys
import os
from rich import print
from util import constants as C

from util.const_local import LOG_LEVEL

logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_demo_client", add_completion=False, help="Demo Parser (show casing typer)")

sample_int = 10
sample_str = "HUGO"

@app.command("demo1")
def demo1(xyz:str,test:str="Test"):
    """_summary_

    Args:
        xyz (str): _description_
        test (str, optional): _description_. Defaults to "Test".
    """
    print(f"Hello Share Parser CLI {test} ssample_Str [{sample_str}]")

# https://typer.tiangolo.com/tutorial/commands/callback/
@app.callback()
def main(sample_int:int=5,sample_str:str="Hugo"):
    """ main method using callback to allow for providing params """
    print(f"Calling main with [{sample_int}] and [{sample_str}]") 

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    app()