""" creates a demo config file with real paths """

from pathlib import Path
import os 
from util.persistence import Persistence

def create_demo_config()->str:
    """ creates a demo config and returns file path """
    p_testpath = Path(__file__).parent.parent.parent.joinpath("test_data","test_config")
    f_testconfig_template = str(p_testpath.joinpath("config_env_template.json"))
    _sample_config_json = str(os.path.join(p_testpath,"config_env_sample.json"))
    if os.path.isfile(_sample_config_json):
        return _sample_config_json
    # create a sample file
    _sample_dict = Persistence.read_json(f_testconfig_template)
    # populate path
    _sample_dict["P_CONFIGTEST"]["p"]=str(p_testpath)
    # populate configfile 1 file with absolute path
    p_config_test1 = os.path.join(p_testpath,"file1_config.txt")    
    _sample_dict["F_CONFIGTEST1"]["f"]=str(p_config_test1)
    # populate configfile3 with absolute path and file 
    _sample_dict["F_CONFIGTEST3"]["p"]=str(p_testpath)
    Persistence.save_json(_sample_config_json,_sample_dict)
    return _sample_config_json
