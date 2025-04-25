# from pathlib import Path
import os
import json
import logging
import sys
import shlex
from enum import StrEnum
import re
from typing import Dict, List

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL

logger = logging.getLogger(__name__)

# get log level from environment if given
# logger.setLevel(CLI_LOG_LEVEL)

CODE = "CODE"
REGEX = "REGEX"
EMOJI = "EMOJI"
ARGS = "ARGS"
TEXT = "TEXT"
COL = "COL"
COLUMN_META = "COLUMN_META"
ROW = "ROW"
ROWCOL = "ROWCOL"
VALUE = "VALUE"
CONTENT = "CONTENT"
NUM_ROWS = "NUMROWS"
ACTION = "ACTION"
ORIGINAL_KEY = "ORIGINAL_KEY"
KEY = "KEY"
ACTIVE = "ACTIVE"
TYPE = "TYPE"
MAX_LENGTH = "MAX_LENGTH"
INDEX = "INDEX"


# regex that matches optional numbers and content, separated by an optional colon
REGEX_TABLE_CONTENT = r"([^:]+)(:)?(.*)"


class TABLE_ACTION(StrEnum):
    """allowed table actions"""

    SHOW = "show"
    EDIT_ROW = "edit_row"
    ADD_ROW = "edit_row"
    EDIT_COL = "edit_col"
    EDIT_ROW_COL = "edit_row_col"
    EDIT_SWAP_ROW = "swap_row"
    TOGGLE_ROW = "toggle_row"  # activate or deactivate row
    SWAP_ROWS = "swap_rows"
    DEL_ROW = "delete_row"
    QUIT = "quit"


# evaluating regex patterns for input
CMD_INPUT = {}
TABLE_ACTIONS_DICT = {
    "s": {CODE: TABLE_ACTION.SHOW, TEXT: "(S) Show", REGEX: r"^(s)(?!.)", EMOJI: "📅", ARGS: "NOT_USED"},
    "r": {
        CODE: TABLE_ACTION.EDIT_ROW,
        TEXT: "(#[,]) Edit Row",
        REGEX: r"^(\d+)[,]?(?!.)",
        EMOJI: "➡️",
        ARGS: "NOT_USED",
    },
    "a": {
        CODE: TABLE_ACTION.ADD_ROW,
        TEXT: "(A) Add Row",
        REGEX: r"(a)(?!.)",
        EMOJI: "*️⃣",
        ARGS: "NOT_USED",
    },
    "tr": {
        CODE: TABLE_ACTION.TOGGLE_ROW,
        TEXT: "(T#) Toggle Row",
        REGEX: r"^t(\d+)(?!.)",
        EMOJI: "🙈",
        ARGS: "NOT_USED",
    },
    "xr": {
        CODE: TABLE_ACTION.DEL_ROW,
        TEXT: "(x#) Delete Row",
        REGEX: r"^x(\d+)(?!.)",
        EMOJI: "❌",
        ARGS: "NOT_USED",
    },
    "rc": {
        CODE: TABLE_ACTION.EDIT_ROW_COL,
        TEXT: "(#,#) Edit RowCol",
        REGEX: r"^(\d+),(\d+)(?!.)",
        EMOJI: "🔠",
        ARGS: "NOT_USED",
    },
    "c": {
        CODE: TABLE_ACTION.EDIT_COL,
        TEXT: "(,#) Edit Col",
        REGEX: r"^,(\d+)(?!.)",
        EMOJI: "⤵️",
        ARGS: "NOT_USED",
    },
    "sr": {
        CODE: TABLE_ACTION.SWAP_ROWS,
        TEXT: "(S#,#) Swap Rows",
        REGEX: r"^s(\d+),(\d+)(?!.)",
        EMOJI: "🔃",
        ARGS: "NOT_USED",
    },
    "q": {CODE: TABLE_ACTION.QUIT, TEXT: "(Q) Quit", REGEX: r"(q)(?!.)", EMOJI: "🛑", ARGS: "NOT_USED"},
}


class SimpleTableModel:
    """simple table model using json as input"""

    def __init__(self, table: Dict[object, dict] | List[dict] = None, column_dict: Dict[int, dict] | None = None):
        logger.debug("start")
        self._table = {}
        self._index_dict = {}
        self._column_meta_dict = {}
        self._column_map_dict = {}
        # mapping original row key to index key
        self._index_key_map = None
        self._is_list = False
        self.set_table(table, column_dict)
        self._max_idx = -1
        if len(self._table) >= 0:
            self._max_idx = len(self._table)

    @property
    def table(self) -> Dict[object, dict] | List[dict]:
        """returns the table as dict or list"""
        logger.debug("start")
        if self._is_list:
            out = []
        else:
            out = {}
        # return a validated model in original shape
        for _idx, _item in self._table.items():
            # check if it should be imported
            _index_info = self._index_dict[_idx]
            if _index_info[ACTIVE] is False:
                continue
            if self._is_list:
                out.append(_item)
            else:
                out[_index_info[ORIGINAL_KEY]] = _item

        return out

    @property
    def rows(self) -> List[dict]:
        """returns table as list of dicts"""
        return list(self._table.values())

    @property
    def stats(self):
        """returns stats on current table"""
        _column_infos = list(self._column_meta_dict.values())
        for _col_info in _column_infos:
            _col_info[TYPE] = _col_info[TYPE].__name__
        return {NUM_ROWS: len(self._table), COLUMN_META: _column_infos}

    def set_table(self, table: Dict[object, dict] | List[dict], column_dict: Dict[int, dict] | None = None) -> None:
        """model setter"""
        logger.debug("start")

        self._index_dict = {}
        _table: dict = {}
        # create the model and build index
        self._is_list = False

        if isinstance(table, list):
            self._is_list = True
            for _idx, _item in enumerate(table):
                _table[_idx] = _item
                # map the index
                self._index_dict[_idx] = {ORIGINAL_KEY: _idx, KEY: _idx, ACTIVE: True}
        elif isinstance(table, dict):
            self._index_key_map = {}
            for _idx, (_key, _item) in enumerate(table.items):
                _table[_idx] = _item
                self._index_key_map[_key] = _idx
                self._index_dict[_idx] = {ORIGINAL_KEY: _key, KEY: _idx, ACTIVE: True}
        self._table = _table
        self.set_column_index(column_dict)
        # now set the max length
        for _, _row in self._table.items():
            self._set_column_width_single(_row)

    def _set_column_map_dict(self) -> None:
        """sets the column key dict (key to index)"""
        logger.debug("start")
        self._column_map_dict = {}
        for _idx, _info in self._column_meta_dict.items():
            self._column_map_dict[_info[COL]] = _idx

    def _set_column_meta_from_table(self) -> None:
        """set columns index from model"""
        logger.debug("start")
        self._column_meta_dict = {}

        try:
            _first_line = self._table[0]
        except IndexError:
            logger.error("Table seems not to be initialized")
            return

        for _idx, (_key, _value) in enumerate(_first_line.items()):
            _column_meta = {}
            _column_meta[INDEX] = _idx
            _column_meta[COL] = _key
            # will only work if there are any values
            _column_meta[TYPE] = type(_value)
            # adding a length to be sued for display
            _column_meta[MAX_LENGTH] = None
            self._column_meta_dict[_idx] = _column_meta
        logger.debug(f"Column Dict: {self._column_meta_dict}")

    def _set_column_width_single(self, row: dict) -> None:
        """sets the max column width based on a single row"""
        for _, _col_info in self._column_meta_dict.items():
            _value = row.get(_col_info[COL])
            if _value is None:
                continue
            _max_length = _col_info.get(MAX_LENGTH, 0)
            _len = len(str(_value))
            if not isinstance(_max_length, int) or _len > _max_length:
                _col_info[MAX_LENGTH] = _len

    def set_column_index(self, column_dict: Dict[int, dict] | None) -> None:
        """sets the column index. if None is set, then it will be created from the
        first line of the table
        Otherwise it will be a dict of column index with an information dict
        containing a column key COL and optional TYPE (=directly containing type
        like int, str, ...)
        """
        logger.debug("start")
        if isinstance(column_dict, dict):
            self._column_meta_dict = column_dict
        else:
            self._set_column_meta_from_table()
        self._set_column_map_dict()

    def swap_rows(self, rows_to_swap: tuple) -> None:
        """swapping index of rows"""
        logger.debug(f"swap_rows, {rows_to_swap}")
        try:
            _key1, _key2 = rows_to_swap
        except (ValueError, IndexError):
            logger.info(f"Error swapping rows {rows_to_swap}")
            return
        _row_info1 = self.get_row(_key1).copy()
        _row_info2 = self.get_row(_key2).copy()
        # we also need to swap the indices
        _index_info1 = self._get_index_info(_key1).copy()
        _index_info2 = self._get_index_info(_key2).copy()
        _idx1 = _index_info1[KEY]
        _idx2 = _index_info2[KEY]
        _index_info1[KEY] = _idx2
        _index_info2[KEY] = _idx1
        self._index_dict[_idx1] = _index_info2
        self._index_dict[_idx2] = _index_info1
        # swap rows
        self.update_row(_key1, _row_info2, overwrite=True)
        self.update_row(_key2, _row_info1, overwrite=True)
        logger.debug(f"Swapped rows {rows_to_swap}, indices [{_idx1, {_idx2}}]")

    def update_row(self, key: object, col_dict: dict, overwrite: bool = False) -> None:
        """updates a given row from information passed"""
        logger.debug(f"update_row {key}")

        _index_info = self._get_index_info(key)
        if overwrite:
            _row = {}
        else:
            _row = self.get_row(key)
        _row.update(col_dict)
        _key = _index_info[KEY]
        self._table[_key] = _row
        self._set_column_width_single(_row)
        logger.debug(f"Updated row [{_key}]")

    def get_row(self, key: object) -> dict | None:
        """reads the row index  / key  and returns the row dict"""
        # first try to get the value from index map
        logger.debug(f"get_row {key}")

        out = None
        _index_info = self._get_index_info(key)
        if _index_info is None:
            logger.debug(f"There is no index [{key}] in _index_info")
            return out
        _key = _index_info[KEY]

        try:
            out = self._table[_key]
        except (IndexError, ValueError):
            logger.debug(f"There is no index [{key}] in table")
        return out

    def add_row(self, col_dict: dict, key: object = None) -> None:
        """add a row information passed"""
        logger.debug(f"add_row {key}, {col_dict}")

        # check that key is not already in list
        if self._get_index_info(key) is not None:
            logger.warning(f"Key [{key}] already exists, will not add item, use update unstead")
            return

        self._max_idx += 1
        _key = self._max_idx
        _original_key = key if key is not None else _key

        if isinstance(col_dict, dict):
            self._table[_key] = col_dict
            self._set_column_width_single(col_dict)

        else:
            logger.warning("Empty dict was passed")
            return

        if self._index_key_map is not None:
            self._index_key_map[_original_key] = _key
            self._index_dict[_key] = {ORIGINAL_KEY: _original_key, KEY: _key, ACTIVE: True}

    def _get_index_info(self, key: object) -> dict:
        """returns the index dict entry"""
        # try to find whether we have original or index key
        logger.debug(f"_get_index_info {key}")
        _index = None
        if isinstance(self._index_key_map, dict):
            _index = self._index_key_map.get(key)
        if _index is None:
            _index = key
        _index_info = self._index_dict.get(_index)
        if _index_info is None:
            logger.debug(f"There is no index [{key}] in table")
        return _index_info

    def delete_row(self, key: object) -> dict | None:
        """delete row, returns deleted key if existing"""
        logger.debug(f"start delete row {key}")
        _index_info = self._get_index_info(key)
        _original_key = _index_info[ORIGINAL_KEY]
        _key = _index_info[KEY]

        if _index_info is None:
            return

        out = self.get_row(_key)
        if out is None:
            logger.debug(f"There is no key [{key}] in table")
            return

        # clean up index map if there is one
        if self._index_key_map is not None:
            _ = self._index_key_map.pop(_original_key)
        # clean up index
        _ = self._index_dict.pop(_key)
        # remove item
        _ = self._table.pop(_key)
        logger.debug(f"deleted item {out}")
        return out

    def toggle_row(self, key: object, active: bool = None) -> None:
        """activate/deactivate or set status row"""
        logger.debug(f"start toggle row {key}")
        _index_info = self._get_index_info(key)
        _active = _index_info[ACTIVE]
        _active = not _active
        _active = active if active is not None else _active
        _index_info[ACTIVE] = _active
        # self._index_dict[_index_info[KEY]] = _
        logger.debug(f"Setting Row [{_index_info}] Active to [{_active}]")


class SimpleTableViewer:
    """simple table viewer with elementary input"""

    re_table_content = re.compile(REGEX_TABLE_CONTENT, re.IGNORECASE)

    def __init__(
        self,
        table: Dict[object, dict] | List[dict] = None,
        cmd_sep: str = ":",
        max_cell_width: int = None,
        render_index: bool = True,
    ):
        """constructor"""

        logger.debug("start")
        self._cmd_sep = cmd_sep
        self._max_cell_width = max_cell_width  # max cell width
        self._table: SimpleTableModel = SimpleTableModel(table)
        self._table_stats = self._table.stats
        # formatting number of zeroes for index
        self._idx_zeroes = max(len(str(self._table_stats[NUM_ROWS])), 2)
        # getting the column meta dict
        self._column_dict = {_col[COL]: _col for _col in self._table_stats[COLUMN_META]}

        # flag whether to output row numbers
        self._render_index = render_index

    def _show_help(self) -> None:
        """Shows info"""
        _cmd = "CMD: ➡️ ⤵️ 🔠 ([#],[#]) 🔃(s#,#)🙈(t#)❌(x#)🛑(q)[:[idx:value],...]"
        print(_cmd)

    def _input_cmd(self) -> str:
        """get the input"""
        self._show_help()
        _s_input = "👷 CMD > "
        return input(_s_input)

    def _render_rows(self) -> List[str]:
        """renders rows as string output"""
        out = []
        for _idx, _row_dict in enumerate(self._table.rows):
            out.extend(self._render_row(_row_dict, _idx))
        return out

    def _render_row(self, _row_dict: dict, index: int) -> List[List[str]]:
        """renders a single row for output and splits it into multiple rows if needed"""
        out = []

        if self._render_index:
            _idx = str(index).zfill(self._idx_zeroes)
        # get number of lines for each cell in this row
        _max_chars = max([len(str(_v)) for _v in list(_row_dict.values())])
        # check whether we need more than 1 row to display the cell
        _num_lines = 1
        if self._max_cell_width is not None:
            _num_lines = _max_chars // self._max_cell_width + 1
        _cell_out = {}
        if self._render_index:
            _lines = [""] * _num_lines
            _lines.insert(0, str(index).zfill(self._idx_zeroes))
            _lines.pop()
            _cell_out["index"] = _lines
        for _col_key, _col_info in self._column_dict.items():
            # max length in this column
            # if maximum length of this column is smaller than max cell
            # width, use this value otherwise use max cell width as cell width
            if self._max_cell_width is None:
                _cell_width = _col_info[MAX_LENGTH]
            else:
                _cell_width = (
                    _col_info[MAX_LENGTH] if _col_info[MAX_LENGTH] < self._max_cell_width else self._max_cell_width
                )
            # fill content up with spaces
            _cell_value = str(_row_dict.get(_col_key, ""))
            _cell_value = _cell_value + ((_cell_width * _num_lines) - len(_cell_value)) * " "
            # split it into lines
            _cell_lines = [_cell_value[_i : _i + _cell_width] for _i in range(0, len(_cell_value), _cell_width)]
            _cell_out[_col_key] = _cell_lines
        for _line_num in range(_num_lines):
            _line = []
            for _, cell_list in _cell_out.items():
                _line.append(cell_list[_line_num])
            out.append(_line)
        return out

    @staticmethod
    def parse_content(s_content: str) -> dict | None:
        """parse the content
        expected: comma separated list with optional index
        [idx1]:content,[idx2]:content
        otherwise index will be determined by position
        """
        logger.debug(f"start, parse [{s_content}]")
        if s_content is None or len(s_content) == 0:
            return None

        out = {}
        # force shlex to split at commas
        shlex_parser = shlex.shlex(s_content, posix=True)
        shlex_parser.whitespace += ","  # Treat commas as whitespace
        shlex_parser.whitespace_split = True  # Split at whitespace (including commas)
        _items = list(shlex_parser)

        logger.debug(f"Parsing Content: {_items}")
        _idx = 0
        for _item in _items:
            _item = _item.strip()
            _match = SimpleTableViewer.re_table_content.findall(_item)
            if len(_match) == 0:
                continue
            # only evaluate the first match
            _match = _match[0]
            # if theres a colon, then its a dict, otherwise only a value
            if len(_match[1]) > 0:
                _col = _match[0]  # index = key
                _content = _match[2]
            else:
                _col = _idx  # index = positional value
                _content = _match[0]
            try:
                _col = int(_col)
            except ValueError:
                pass

            if len(_content) == 0:
                _content = None
            out[_col] = _content
            _idx += 1
        logger.debug(f"Parsed Content [{s_content}]: {out}")
        return out

    def input_loop(self) -> None:
        """Input Loop"""
        _finished = False
        while _finished is False:
            _s_input = self._input_cmd()
            _parsed_input = self._parse_input(_s_input)
            # print("PARSED INPUT ", _parsed_input)
            if _parsed_input is None:
                _finished = True
            pass

    def _parse_input(self, s_input: str) -> dict | None:
        """parses input, split into command and content, parse separately
        returns raw input
        """
        # split into command and content
        logger.debug("start")

        _input_list = s_input.split(self._cmd_sep, maxsplit=1)
        # get action
        _cmd = _input_list[0]
        _match = None
        _action = {}
        _action_info = None
        _regex_match = False
        for _action, _action_info in TABLE_ACTIONS_DICT.items():
            _match = re.findall(_action_info[REGEX], _cmd)
            if len(_match) == 0:
                _match = None
                continue
            _regex_match = True
            # use the first match
            break
        if _regex_match is False:
            _ = input("Invalid Input, try again, key to continue")
            return {}

        logger.debug(f"Found Action ({_action}):{_match}")
        _action_code = _action_info[CODE]
        _row_action = None
        _col_action = None
        if (
            _action_code == TABLE_ACTION.EDIT_ROW
            or _action_code == TABLE_ACTION.TOGGLE_ROW
            or _action_code == TABLE_ACTION.DEL_ROW
        ):
            _row_action = _match[0]
        elif _action_code == TABLE_ACTION.EDIT_ROW_COL:
            _row_action = _match[0][0]
            _col_action = _match[0][1]
        elif _action_code == TABLE_ACTION.EDIT_COL:
            _col_action = _match[0]
        elif _action_code == TABLE_ACTION.SWAP_ROWS:
            _row_action = (_match[0][0], _match[0][1])
        elif _action_code == TABLE_ACTION.QUIT:
            return None

        # get content
        _content = None
        _content_dict = {}
        try:
            _content = _input_list[1]
            _content_dict = SimpleTableViewer.parse_content(_content)
        except IndexError:
            pass
        _content_dict = SimpleTableViewer.parse_content(_content)
        out = {ACTION: {ROW: _row_action, COL: _col_action, CODE: _action_code.value}, CONTENT: _content_dict}
        logger.debug(f"Parsed Action {out}")
        return out


_sample_table = [
    {"a": "col a1 sdfsfd", "b": 15, "c": "hugoc1 sdghsdg dsjhgshd ghjs gjshdg jsgd "},
    {"a": "col a2", "b": 25, "c": "hugoc2"},
    {"a": "col a3", "b": 35, "c": "hugoc3"},
]


def main():
    """do something"""
    print("🙃")
    # _table_viewr = SimpleTableViewer()
    # _table_viewr.input_loop()
    # _st_model = SimpleTableModel(_sample_table)
    # print(json.dumps(_st_model.stats, indent=4))
    _table_viewer = SimpleTableViewer(table=_sample_table, max_cell_width=10)
    _rows = _table_viewer._render_rows()
    print(_rows)

    pass


if __name__ == "__main__":
    loglevel = CLI_LOG_LEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=logging.DEBUG,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
