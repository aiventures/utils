"""Testing the bat_helper module"""

import os
import uuid
from pathlib import Path


def test_create_colors_template(fixture_battest_path, fixture_bat_helper):
    """creating a colors template"""
    _f_bat_set_colors = Path(fixture_battest_path).joinpath("test_bat_set_colors.bat")
    # clean up previous test file
    if os.path.isfile(_f_bat_set_colors):
        os.remove(_f_bat_set_colors)
    _theme = "ubuntu"
    _f_out = fixture_bat_helper.create_colors_template(_f_bat_set_colors, _theme)
    assert os.path.isfile(_f_bat_set_colors)


def test_tmp_env_files(fixture_battest_path, fixture_bat_helper):
    """Creating and reading temporary file"""
    # write bat files
    # _f_bat_set_colors=Path(fixture_battest_path).joinpath("test_bat_set_colors.bat"
    value1 = str(uuid.uuid4())
    fixture_bat_helper.create_env_file("key1", value1, fixture_battest_path)
    value2 = str(uuid.uuid4())
    fixture_bat_helper.create_env_file("key2", value2, fixture_battest_path, quotes=False)
    # todo read an env from configuration
    fixture_bat_helper.create_env_file("E_SIMPLE", p=fixture_battest_path, quotes=False)
    # assert os.path
    # get the file names
    _env_files = fixture_bat_helper.get_env_files(fixture_battest_path)
    assert len(_env_files) > 0, f"No env files found in {fixture_battest_path}"
    # read the environment
    _env_list = fixture_bat_helper.read_env_files(fixture_battest_path)
    assert isinstance(_env_list, dict)
    assert _env_list.get("key1") == value1, f"Value for key1 should be {value1}"
    assert _env_list.get("key2") == value2, f"Value for key2 should be {value2}"
    assert (
        _env_list.get("E_SIMPLE") == "env_simple_value_example"
    ), "Value for ENV VAR should be env_simple_value_example"
    _env_dict = fixture_bat_helper.read_env_files(fixture_battest_path, as_dict=True)
    assert isinstance(_env_dict, dict)
    # save all created env files in a single env file
    f_save = fixture_bat_helper.save_env_file(fixture_battest_path)
    assert isinstance(f_save, str)
    # test reading the all in one file
    _env_dict = fixture_bat_helper.read_env_files(fixture_battest_path, as_dict=True, prefix="_envs")
    assert len(_env_dict) > 0
    assert len(list(_env_dict.values())[0]) > 0
