""" Rendering the CLI.


"""
import logging
from typing import Any
from rich.color import ANSI_COLOR_NAMES
from rich.console import Console
from rich.logging import RichHandler

# TODO MOVE THIS TO A CONFIG FILE
from util.const_local import LOG_LEVEL

HEX = "hex"
ANSI = "ansi" # ansi ciodes not implemented yet
CODE = "code" # code 0-255
NAME = "name" # as in ANSI COLOR NAMES
RGB = "rgb"

logger = logging.getLogger(__name__)

# switch to 256 Colors as default
console = Console(color_system="256")

def convert(value:Any,to:str=HEX)->Any:
    """ Convert from one color code to the other """
    _from = None
    if isinstance(value,int):
        _from = CODE

def code2rgb(code:int)->str:
    """ convert code to rgb  """
    pass

def code2name(code:int)->str:
    """ convert code to name """
    pass

def code2hex(code:int)->str:
    """ convert code to hex value """
    pass

def code2code(code:int)->str:
    """ convert code to code value """
    pass




if __name__ == "__main__":  
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])

