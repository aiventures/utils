""" Unit Tests for command line features """

# from typer.testing import CliRunner
# from cli.cli_config import cli

# runner = CliRunner()

# def test_cli_config_show():
#     """ Testing  the config show variant"""
#     result = runner.invoke(cli,["--test"])
#     assert result.exit_code == 0
#     # result.stdout
#     pass

# def test_cli_config_show_invalid_file(caplog):
#     """ Testing  the config show variant"""
#     # https://github.com/pallets/click/issues/824
#     caplog.set_level(100000)  
#     result = runner.invoke(cli,["--f","hugo"])
#     assert result.exit_code != 0
#     pass

