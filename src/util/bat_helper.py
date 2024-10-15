""" Utils in Conjunction with Bat Files """

import os
import sys
# import re
# import json
import logging
# from functools import wraps
# from pathlib import Path
# from rich import print_json
# from rich import print as rprint
# from datetime import datetime as DateTime
from util import constants as C
from util.config_env import Environment

logger = logging.getLogger(__name__)

class BatHelper():

    def __init__(self,f_environment:str=None) -> None:
        """ Constructor """
        self._f_environment = f_environment
        self._environment = None
        if f_environment:
            self._environment = Environment(f_environment)

    def create_vars_template(self,f_out:str=None)->str:
        """ creates the cvar template, returns the absolute file path of created bat file """
        return self._environment.create_set_vars_bat(f_out)
    
    # TODO CREATE COLOR CREATION TEMPLATE



if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
