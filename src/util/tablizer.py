"""Transforming linear text files into tabular formats"""

import sys
import os
from pathlib import Path
import logging
import re
from util.persistence import Persistence
from util import constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))


class Tablizer:
    """Tablizer: transforming linear informastion in text files into tabular data"""

    def __init__(
        self, f: str, skip_blank_lines: bool = False, comment_marker: str = "^#", strip_lines: bool = False
    ) -> None:
        if not os.path.isfile(f):
            logger.warning(f"[Tablizer] No file [{f}]")
            return
        self._file = Path(os.path.abspath(f))
        self._ignore_blank = skip_blank_lines
        self._comment_marker = comment_marker
        self._skip_blank = skip_blank_lines
        self._strip_lines = strip_lines
        self._lines = {}
        self._max_line = 0
        self._read_lines()

    def _read_lines(self) -> None:
        """reading lines"""
        _lines_dict = Persistence.read_txt_file(
            filepath=self._file,
            comment_marker=None,
            skip_blank_lines=self._skip_blank,
            strip_lines=self._strip_lines,
            with_line_nums=True,
        )
        _regex = re.compile(self._comment_marker)
        # parse and copy lines
        for _num, _line in _lines_dict.items():
            _comments = _regex.findall(_line)
            if len(_comments) > 0:
                continue
            self._lines[_num] = _line
        # save last line
        self._max_line = _num

    def bundle_by_marker(
        self,
        marker: str = None,
        include_marker_line: bool = True,
        sep: str = None,
        ignorecase: bool = True,
        as_dict: bool = False,
    ) -> list | dict:
        """treat multiple lines as if it was one line (start of line contents is indicated by single start marker),
        include/exclude marker line into result
        if separator is set, all line bundles will be put into a string
        ignorecase for regex
        as_dict if set to true, it will return information witj line information
        """
        if as_dict is False:
            out = []
        else:
            out = {}
        if marker is None:
            return

        if ignorecase:
            _regex = re.compile(marker, re.IGNORECASE)
        else:
            _regex = re.compile(marker)

        # find all line indices
        _line_idx_list = [_line for _line in list(self._lines.keys()) if len(_regex.findall(self._lines[_line])) > 0]
        if len(_line_idx_list) == 0:
            return []
        if _line_idx_list[-1] != self._max_line:
            _line_idx_list.append(self._max_line)
        _ranges = []
        for i in range(1, len(_line_idx_list)):
            _from = _line_idx_list[i - 1]
            if _line_idx_list[i] == self._max_line:
                _to = _line_idx_list[i]
            else:
                _to = _line_idx_list[i] - 1
            _ranges.append([_from, _to])

        for _range in _ranges:
            _bundle = []
            if include_marker_line:
                _from = _range[0]
            else:
                _from = _range[0] + 1
            _to = _range[1] + 1
            _min = -1
            _max = -1
            for _idx in range(_from, _to):
                _line = self._lines.get(_idx)
                if isinstance(_line, str):
                    # get first valid line
                    if _min == -1:
                        _min = _idx
                        _max = _min
                    # get last valid line
                    if _idx > _max:
                        _max = _idx
                    _bundle.append(_line)
            if len(_bundle) == 0:
                continue

            if sep is None:
                _lines_out = _bundle
            else:
                _lines_out = sep.join(_bundle)

            if as_dict is False:
                out.append(_lines_out)
            else:
                _line_info = {"line": _lines_out, "from": _min, "to": _max}
                out[_min] = _line_info

        return out


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
