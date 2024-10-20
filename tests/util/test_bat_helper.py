""" Testing the bat_helper module """
import pytest
from util.bat_helper import BatHelper


def test_create_colors_template(fixture_bat_helper):
    """ creating a colors template """
    
    _f_out = fixture_bat_helper.create_colors_template()



