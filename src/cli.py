""" Command Line Client for all command tools """

# import sys
# import typer
# import logging
# from util_cli.cli_share_parser import cli as cli_sp
# from util_cli.cli_config import cli as cli_config
# from rich import print as rprint
# # different config files
# from util.const_local import F_CONFIG
# from util.const_local import LOG_LEVEL

# logger = logging.getLogger(__name__)

# cli = typer.Typer(name="cli_client", add_completion=False, help="Central Command Line Client")

# cli.add_typer(cli_sp, name="sp")
# cli.add_typer(cli_config, name="config")

# @cli.command("test")
# @cli.command("t")
# def test_function(xyz:str,test:str="Test"):
#     """_summary_

#     Args:
#         xyz (str): _description_
#         test (str, optional): _description_. Defaults to "Test".
#     """
#     print(f"Hello Main CLI {test}")

# if __name__ == "__main__":
#     logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
#                         level=LOG_LEVEL, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")    
#     cli()
