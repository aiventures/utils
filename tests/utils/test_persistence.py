""" Testing Persistence Features """

import logging

from util import constants as C
from util.csv_parser import CsvParser
import logging

logger = logging.getLogger(__name__)

def test_data_parsing(fixture_sample_config_json, fixture_sample_stocks_data):
    """ test the parsing of txt files to parse them as dict files """
    csv_parser = CsvParser(f_read=fixture_sample_stocks_data,f_config=fixture_sample_config_json)
    _parsed_list = csv_parser.parse("D_EXAMPLE")
    assert isinstance(_parsed_list,list) and len(_parsed_list) > 0
    _dict_list = csv_parser.content(C.EXPORT_CSV)
    assert isinstance(_dict_list,list) and len(_dict_list) > 0
    _json = csv_parser.content(C.EXPORT_JSON)
    assert isinstance(_json,str) 
    _json_dict = csv_parser.content(C.EXPORT_JSON_DICT)
    assert isinstance(_json_dict,list)     
