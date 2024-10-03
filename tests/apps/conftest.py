import pytest
import sys
import os
from copy import deepcopy
from pathlib import Path
import logging
from util import constants as C
from util.persistence import Persistence

### [1] Fixtures for File Analyzer

@pytest.fixture
def fixture_config_testpath()->Path:
    """ Sample Path """
    p_testpath = C.PATH_ROOT.joinpath("test_data","test_config")
    return p_testpath

@pytest.fixture
def fixture_config_env_testconfig_template(fixture_config_testpath)->Path:
    """ Sample Path to configuration file """
    return str(fixture_config_testpath.joinpath("config_env_template.json"))

@pytest.fixture
def fixture_sample_config_json(fixture_config_testpath,fixture_config_env_testconfig_template):
    """ creates a sample json config file from existing one in test folder
        replacing absolute test paths, returns path to sample config json
    """
    _sample_config_json = str(os.path.join(fixture_config_testpath,"config_env_sample.json"))
    if os.path.isfile(_sample_config_json):
        return _sample_config_json
    # create a sample file
    _sample_dict = Persistence.read_json(fixture_config_env_testconfig_template)
    # populate path
    _sample_dict["P_CONFIGTEST"]["p"]=str(fixture_config_testpath)
    # populate configfile 1 file with absolute path
    p_config_test1 = os.path.join(fixture_config_testpath,"file1_config.txt")
    _sample_dict["F_CONFIGTEST1"]["f"]=str(p_config_test1)
    # populate configfile3 with absolute path and file
    _sample_dict["F_CONFIGTEST3"]["p"]=str(fixture_config_testpath)
    Persistence.save_json(_sample_config_json,_sample_dict)
    return _sample_config_json