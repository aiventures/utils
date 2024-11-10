""" Unit Tests for command line features """

from typer.testing import CliRunner
from cli.cli_customizing import app as cli_config

runner = CliRunner()

def test_cli_config_show():
    """ Testing the config show variant"""
    result = runner.invoke(cli_config,["show"])
    assert result.exit_code == 0

# def test_cli_config_show_invalid_file(caplog):
#     """ Testing  the config show variant"""
#     # this is required to test command line commands     
#     # https://github.com/pallets/click/issues/824
#     caplog.set_level(100000)  
#     result = runner.invoke(cli,["--f","hugo"])
#     assert result.exit_code != 0
#     pass

