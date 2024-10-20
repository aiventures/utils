""" Testing the bat_helper module """
import pytest
from pathlib import Path
import os
from util.bat_helper import BatHelper
from util import constants as C


def test_create_colors_template(fixture_battest_path,fixture_bat_helper):
    """ creating a colors template """
    _f_bat_set_colors=Path(fixture_battest_path).joinpath("test_bat_set_colors.bat")
    # clean up previous test file
    if os.path.isfile(_f_bat_set_colors):
        os.remove(_f_bat_set_colors)
    _theme = "vscode"
    _f_out = fixture_bat_helper.create_colors_template(_f_bat_set_colors,_theme)
    assert os.path.isfile(_f_bat_set_colors)




