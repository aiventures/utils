""" Testing Persistence Features """

import logging

from copy import deepcopy
from util import constants as C
from util.csv_parser import CsvParser
import logging

logger = logging.getLogger(__name__)

def test_csv_parser(fixture_sample_config_json, fixture_sample_stocks_data):
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

def test_csv_parser_ext_columns(fixture_sample_config_json, fixture_sample_stocks_data):
    """ test the parsing of txt files to parse them as dict files """
    ext_columns = ["EXT_COLUMN_NONE",
                   {"k":"EXT_COLUMN_INT","t":"int"},
                   {"k":"EXT_COLUMN_VALUE","v":5.3},
                   {"k":"EXT_COLUMN_VAL_N","v":55555}]
    csv_parser = CsvParser(f_read=fixture_sample_stocks_data,f_config=fixture_sample_config_json)
    csv_parser.add_ext_columns(ext_columns)
    _parsed_list = csv_parser.parse("D_EXAMPLE")
    assert isinstance(_parsed_list,list) and len(_parsed_list) > 0
    _parsed_csv = csv_parser.content(export_format=C.EXPORT_CSV)
    assert isinstance(_parsed_csv,list) and len(_parsed_list) > 0
    _parsed_csv_titles = _parsed_csv[0].split(",")
    # assert all columns are in output as well
    ext_cols_csv = [c for c in _parsed_csv_titles if "EXT_COLUMN" in c]
    assert len(ext_cols_csv) == len(ext_columns)
    _parsed_json_dict = csv_parser.content(export_format=C.EXPORT_JSON_DICT)

    assert isinstance(_parsed_json_dict,list) and len(_parsed_json_dict) > 0
    _parsed_json = csv_parser.content(export_format=C.EXPORT_JSON)
    assert isinstance(_parsed_json,str) and len(_parsed_json) > 0
    assert True


def test_csv_parser_wrong_configs(fixture_sample_config_json, fixture_sample_stocks_data):
    """ test wrong configurations / created by adjustments of the correct one """
    csv_parser = CsvParser(f_read=fixture_sample_stocks_data,f_config=fixture_sample_config_json)
    # _copy existing and working configuration
    _config = csv_parser._config._config["D_EXAMPLE"]
    _msg_list = CsvParser.validate_config(_config)
    assert len(_msg_list) == 0
    _config_wrong = deepcopy(_config)
    # no regex
    _ = _config_wrong.pop(C.ConfigAttribute.REGEX.value)
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # wrong regex
    _config_wrong = deepcopy(_config)
    _config_wrong[C.ConfigAttribute.REGEX.value] = "wrong regex"
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # missing  column data
    _config_wrong = deepcopy(_config)
    _config_data = _config_wrong[C.ConfigAttribute.DATA.value]
    _config_data["wrong_key"] = "wrong key"
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # incorrect column data
    _config_wrong = deepcopy(_config)
    _config_wrong[C.ConfigAttribute.EXPORT.value] = "x"
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # testing wrong export key
    _config_wrong = deepcopy(_config)
    _config_wrong[C.ConfigAttribute.EXPORT.value].append({"k":"WRONG_EXPORT_KEY","t":"str"})
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # bogus data element
    _config_wrong = deepcopy(_config)
    _config_wrong[C.ConfigAttribute.EXPORT.value].append(5)
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # dict having no key value
    _config_wrong = deepcopy(_config)
    _config_wrong[C.ConfigAttribute.EXPORT.value].append({"b":"no key value","t":"str"})
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
    # testing environment keys
    _config_wrong = deepcopy(_config)
    _env = _config_wrong[C.ConfigAttribute.ENV.value]
    _env["WRONG_ENV_KEY"] = "INVALID_ENV_KEY"
    _msg_list = CsvParser.validate_config(_config_wrong)
    assert len(_msg_list) > 0
