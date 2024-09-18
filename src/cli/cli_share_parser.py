""" command line client for share client """
import logging
import typer
import sys
from rich import print
# path to config json
from util.const_local import F_CONFIG_ENV

# different config files
from util.const_local import F_CONFIG
from util.const_local import LOG_LEVEL

logger = logging.getLogger(__name__)

cli = typer.Typer(name="cli_share_parser_client", add_completion=False, help="Share Parser (Transforming share info to CSV)")

@cli.command("test_scp")
@cli.command("t_scp")
def xyz_function(xyz:str,test:str="Test"):
    """_summary_

    Args:
        xyz (str): _description_
        test (str, optional): _description_. Defaults to "Test".
    """
    print(f"Hello Share Parser CLI {test}")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    cli()
