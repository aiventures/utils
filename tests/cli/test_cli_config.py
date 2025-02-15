"""Unit Tests for command line features"""

import os
import pytest
from typer.testing import CliRunner
from cli.cli_customizing import app as cli_config
from cli.bootstrap_env import FILE_CONFIGFILE_HOME, FILE_TEST_CONFIG

runner = CliRunner()


def test_cli_config_show():
    """Testing the config show variant"""
    # mocking seems not to work, so change the variable itself
    if os.path.isfile(FILE_CONFIGFILE_HOME):
        pytest.skip(f"[TEST_CONFIG] config file {FILE_CONFIGFILE_HOME} exists in path, temporarily rename this file")
    if not os.path.isfile(FILE_TEST_CONFIG):
        pytest.skip(
            f"[TEST_CONFIG] test config file {FILE_TEST_CONFIG} doesn't exist in path, create a sample configuration"
        )

    result = runner.invoke(cli_config, ["show"], env={"HUGO": "HUGO"})
    assert result.exit_code == 0


# "config_external,config_env,config_home,demo"
# def test_cli_config_show_invalid_file(caplog):
#     """ Testing  the config show variant"""
#     # this is required to test command line commands
#     # https://github.com/pallets/click/issues/824
#     caplog.set_level(100000)
#     result = runner.invoke(cli,["--f","hugo"])
#     assert result.exit_code != 0
#     pass
