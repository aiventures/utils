"""  testing the share parser """

from app.share_parser import ShareParser
from util import constants as C
from util.persistence import Persistence
from datetime import datetime as DateTime
from pathlib import Path
import logging
import os


logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

def test_create_csv(fixture_sample_config_json,fixture_config_testpath):
    """ main program """
    # read configuration, parse all information and export it as csv to original path
    # read sample configuration 
    # you need to run the unit tests before this
    f_config = fixture_sample_config_json
    share_parser = ShareParser(f_config)
    _date_s = DateTime.now().strftime(C.DATEFORMAT_JJJJMMDD)
    f_csv = os.path.join(fixture_config_testpath,_date_s+"_shares.csv")
    # remove itewm to ensure that a file is created
    if os.path.isfile(f_csv):
        os.remove(f_csv)
    f_csv = share_parser.create_csv(f_csv)    
    assert os.path.isfile(f_csv), "[ShareParser] CSV was written"
    _lines = Persistence.read_txt_file(f_csv)
    _header = _lines[0].split(",")
    _header = [h.replace('"','') for h in _header]
    num_header = len(_header)
    _lines = _lines[1:]
    _dict_list = []
    # ensure that lines can be transformed into dicts again
    s = "\"xxx  sfsf sffsf\",\"hugo\",\"hhhh\""
    for _line in _lines:
        _elems = _line.split('","')
        _elems = [e.replace('"','') for e in _elems]
        assert len(_elems) == num_header
        _dict_list.append(dict(zip(_header,_elems)))
    assert len(_dict_list) > 0

