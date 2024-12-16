"""Unit Tests for command line features"""

from typer.testing import CliRunner
from cli.cli_demo import app as cli_demo

runner = CliRunner()


def test_cli_demo1(caplog):
    """Testing  the demo1 method"""
    # NOTE THAT CALLING TYPER TREATS CLASSES WITH MORE THAN
    # ONE COMMAND DIFFERENTLY AS THE ONES WITH ONLY 1 COMMAND
    # params with underscores are transferred into params with hyphens
    # ... CRAZY STUFF
    # this is required to test command line commands
    # https://github.com/pallets/click/issues/824
    # caplog.set_level(100000)
    # required param_str needs to be called without param
    result = runner.invoke(cli_demo, ["demo1", "HUGO", "--param-out", "TEST2"])
    assert result.exit_code == 0, f"STDOUT {result.stdout}"
