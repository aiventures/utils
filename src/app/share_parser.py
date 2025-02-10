"""Parsing Shares, procedure:
- parses files "sample_stocks_..."
- extracts master data and stocks timeseries info from these files using the data definitions
  D_DEPOTHISTORIE / D_DEPOTSTAMM
- lumps everything togethe into a csv file that wwill be saved in test_config folder
"""

import logging
import os
import sys
from copy import deepcopy
from datetime import datetime as DateTime
from cli.bootstrap_env import PATH_ROOT, CLI_LOG_LEVEL
import util.constants as C

from util.config_env import ConfigEnv
from util.csv_parser import CsvParser
from util.file_analyzer import FileAnalyzer
from util.persistence import Persistence

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

# Keys refered in the Config File
CONFIG_PATH_DEPOTHISTORIE = "P_CONFIGTEST"  # this was set by configuration json
CONFIG_DATA_DEPOTHISTORIE = "D_DEPOTHISTORIE"
CONFIG_DATA_DEPOTSTAMM = "D_DEPOTSTAMM"


class ShareParser:
    """Parsing data from a share info text file"""

    def __init__(self, f_config: str) -> None:
        # parsing the configuration
        self._f_config = f_config
        self._config = ConfigEnv(f_config)
        self._p_share_infos = self._config.get_ref(CONFIG_PATH_DEPOTHISTORIE)
        self._file_analyzer = FileAnalyzer(self._p_share_infos)
        # prepare file list
        self._add_filedict()
        self._file_list = []
        _ = self._get_files()
        self._share_histories = {}
        self._export_list = []
        self._dec_separator = C.ENV_DEC_SEPARATOR_DEFAULT
        self._wrap_char = C.ENV_CSV_WRAP_CHAR_DEFAULT

        pass

    @property
    def root_path(self):
        """returns the path"""
        return self._p_share_infos

    def _add_filedict(self) -> None:
        """ " gets the filter expression"""
        _ruledict = deepcopy(C.RULEDICT_FILENAME)
        _ruledict[C.RULE_RULE] = "sample_stocks"  # the search pattern, literal or regex, we filter for sample_stocks
        _ruledict[C.RULE_NAME] = "files matching sample_stocks"  # rule name
        _ruledict[C.RULE_FILE] = C.RULE_FILENAME
        self._file_analyzer.add_rule(_ruledict)

    def _get_files(self):
        """get all files in the shares subfolder"""
        _file_objects = list(self._file_analyzer.find_file_objects().keys())
        self._file_list = _file_objects
        return self._file_list

    @property
    def files(self) -> list:
        """getter for file list"""
        return self._file_list

    def _get_share_history(self, f: str, masterdata: list) -> list:
        """parse share history from a file and combine with master data"""
        csv_parser = CsvParser(f_read=f, f_config=self._f_config)
        csv_parser.add_ext_columns(masterdata)
        _parsed_list = csv_parser.parse(CONFIG_DATA_DEPOTHISTORIE, f, C.EXPORT_JSON_DICT)
        self._export_list = csv_parser.get_export_info()
        _config = csv_parser.config.get(C.ConfigAttribute.ENV.value, {})
        self._dec_separator = _config.get(C.ENV_DEC_SEPARATOR, C.ENV_DEC_SEPARATOR_DEFAULT)
        self._wrap_char = _config.get(C.ENV_CSV_WRAP_CHAR, C.ENV_CSV_WRAP_CHAR_DEFAULT)
        return _parsed_list

    def _get_share_masterdata(self, f: str) -> list:
        """parse share master data from a file"""
        out = []
        csv_parser = CsvParser(f_read=f, f_config=self._f_config)
        _parsed_list = csv_parser.parse(CONFIG_DATA_DEPOTSTAMM, f, C.EXPORT_JSON_DICT)
        _export_info = csv_parser.get_export_info()
        if isinstance(_parsed_list, list):
            for _parsed in _parsed_list:
                for k, v in _parsed.items():
                    if isinstance(v, str):
                        v = v.strip()
                    _info = _export_info.get(k)
                    if _info is None:
                        _info = {C.ConfigAttribute.KEY.value: k, C.ConfigAttribute.TYPE.value: C.DataType.STR}
                    _info[C.ConfigAttribute.VALUE.value] = v
                    out.append(_info)
        return out

    def read_share_history(self, f: str) -> dict:
        """gets share history and master data"""
        out = {}
        _masterdata = self._get_share_masterdata(f)
        out = self._get_share_history(f, _masterdata)
        return out

    def read_share_histories(self) -> dict:
        """reads or returns all share histories"""

        if len(self._share_histories) > 0:
            return self._share_histories

        self._share_histories = {}
        for f in self._file_list:
            self._share_histories[f] = self.read_share_history(f)
        return self._share_histories

    def _get_xls_data_today(self) -> int:
        """returns the datetime as xls int value"""
        days_passed = (DateTime.now() - DateTime(1970, 1, 1)).days
        return C.DATE_INT_19700101 + days_passed

    def csv(self, include_file: bool = False, include_export_date: bool = True, include_index: bool = True):
        """return as csv list"""
        out = []
        file_key = C.FILE.upper()
        index_key = C.INDEX.upper()
        date_export_key = "DATUM_EXPORT"
        date_today = self._get_xls_data_today()
        _histories = self.read_share_histories()
        if include_index:
            _export_keys = [index_key]
        else:
            _export_keys = []
        _export_keys.extend(list(self._export_list.keys()))
        if include_export_date:
            _export_keys.append(date_export_key)
        if include_file:
            _export_keys.append(file_key)

        _out_dict = []
        num = 1

        _history_lines = []
        for _file, _history_items in _histories.items():
            for _history in _history_items:
                _line = {}
                for key in _export_keys:
                    if key == file_key:
                        v = _file
                    elif key == index_key:
                        v = str(num).zfill(3)
                    elif key == date_export_key:
                        v = date_today
                    else:
                        v = _history.get(key)
                    _line[key] = v
                num += 1
                _history_lines.append(_line)

        out = Persistence.dicts2csv(
            _history_lines, csv_sep=self._dec_separator, wrap_char=self._wrap_char, keys=_export_keys
        )
        return out

    def create_csv(self, f_csv) -> str:
        """creates the csv file in the original folder, returns the filename"""
        _csv = self.csv(include_file=True)
        Persistence.save_list(f_csv, _csv)
        print(f"CSV File saved here: [{f_csv}]")
        return f_csv


def main():
    """main program"""
    # read configuration, parse all information and export it as csv to original path
    # read sample configuration
    p_testconfig = PATH_ROOT.joinpath("test_data", "test_config")
    # you need to run the unit tests before this
    f_config = os.path.join(p_testconfig, "config_env_sample.json")
    _date_s = DateTime.now().strftime(C.DATEFORMAT_JJJJMMDD)
    f_csv = os.path.join(p_testconfig, _date_s + "_shares.csv")
    share_parser = ShareParser(f_config)
    share_parser.create_csv(f_csv)


if __name__ == "__main__":
    loglevel = logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
