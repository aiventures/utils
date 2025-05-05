"""Simple Table Model and Command Line Table Editor"""

# from pathlib import Path
# import os
import json
import logging
import sys
import shlex
from enum import StrEnum
import re
from typing import Dict, List, Literal

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
ORIGINAL_ROW_KEY = "ORIGINAL_ROW_KEY"
KEY = "KEY"
ACTIVE = "ACTIVE"
TYPE = "TYPE"
MAX_LENGTH = "MAX_LENGTH"
INDEX = "INDEX"


# regex that matches optional numbers and content, separated by an optional colon
REGEX_TABLE_CONTENT = r"([^:]+)(:)?(.*)"

# min number of digits for column
IDX_MIN_DIGITS = 2


class TABLE_ACTION(StrEnum):
    """allowed table actions"""

    SHOW = "show"
    EDIT_ROW = "edit_row"
    ADD_ROW = "add_row"
    EDIT_COL = "edit_col"
    EDIT_ROW_COL = "edit_row_col"
    EDIT_SWAP_ROW = "swap_row"
    TOGGLE_ROW = "toggle_row"  # activate or deactivate row
    SWAP_ROWS = "swap_rows"
    MARKDOWN = "markdown"
    PLAIN = "plain"
    CSV = "csv"
    JSON = "json"
    WIKI = "wiki"
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
    "m": {
        CODE: TABLE_ACTION.MARKDOWN,
        TEXT: "(m) DISPLAY Markdown",
        REGEX: r"(m)(?!.)",
        EMOJI: "📘",
        ARGS: "NOT_USED",
    },
    "t": {
        CODE: TABLE_ACTION.CSV,
        TEXT: "(t) DISPLAY CSV",
        REGEX: r"(t)(?!.)",
        EMOJI: "📅",
        ARGS: "NOT_USED",
    },
    "j": {
        CODE: TABLE_ACTION.JSON,
        TEXT: "(j) DISPLAY JSON",
        REGEX: r"(j)(?!.)",
        EMOJI: "🤖",
        ARGS: "NOT_USED",
    },
    "w": {
        CODE: TABLE_ACTION.WIKI,
        TEXT: "(w) DISPLAY WIKI",
        REGEX: r"(w)(?!.)",
        EMOJI: "🤖",
        ARGS: "NOT_USED",
    },
    "p": {
        CODE: TABLE_ACTION.PLAIN,
        TEXT: "(p) DISPLAY PLAIN",
        REGEX: r"(p)(?!.)",
        EMOJI: "🦴",
        ARGS: "NOT_USED",
    },
    "q": {CODE: TABLE_ACTION.QUIT, TEXT: "(Q) Quit", REGEX: r"(q)(?!.)", EMOJI: "🛑", ARGS: "NOT_USED"},
}


class SimpleTableModel:
    """simple table model using json as input"""

    def __init__(
        self,
        table: Dict[object, dict] | List[dict] = None,
        column_dict: Dict[int, dict] | None = None,
        csv_sep: str = ";",
        csv_quote: str = '"',
    ):
        logger.debug("start")
        self._table = {}
        self._row_index_dict = {}
        self._column_meta_dict = {}
        self._column_key_idx_map = {}
        self._column_idx_key_map = {}

        # mapping original row key to index key
        self._index_key_map = None
        self._is_list = False
        self.set_table(table, column_dict)
        self._max_idx = -1
        if len(self._table) >= 0:
            self._max_idx = len(self._table)
        self._csv_sep = csv_sep
        self._csv_quote = csv_quote

    @property
    def column_key_idx_map(self) -> dict:
        """getter for column key index map"""

        return self._column_key_idx_map

    @property
    def column_idx_key_map(self) -> dict:
        """getter for column index key map"""
        return self._column_idx_key_map

    @property
    def table(self, only_active: bool = False) -> Dict[object, dict] | List[dict]:
        """returns the table as dict or list"""
        logger.debug("start")
        if self._is_list:
            out = []
        else:
            out = {}
        # return a validated model in original shape
        for _idx, _item in self._table.items():
            # check if it should be imported
            _index_info = self._row_index_dict[_idx]
            if _index_info[ACTIVE] is False and only_active is True:
                continue
            if self._is_list:
                out.append(_item)
            else:
                out[_index_info[ORIGINAL_ROW_KEY]] = _item

        return out

    def get_table_values(self, as_string: bool = False, index: bool = True) -> List[list]:
        """gets the values of the table in a matrix array"""
        _columns = self.column_keys
        out = []
        for _idx, _row in enumerate((self.rows), start=1):
            _s_idx = str(_idx).zfill(IDX_MIN_DIGITS)
            _out_row = [_s_idx] if index else []
            for _col in _columns:
                _value = _row.get(_col, "")
                if as_string:
                    _value = str(_value)
                _out_row.append(_value)
            out.append(_out_row)
        return out

    @property
    def csv(self) -> List[str]:
        """returns table in csv format"""
        _out = []
        _columns = self.column_keys
        _wrapper = "" if self._csv_quote is None else self._csv_quote
        # convert to string
        _table_values = self.get_table_values(as_string=True)
        for _idx, _row in enumerate(_table_values):
            _s_idx = f"{_wrapper}{str(_idx).zfill(IDX_MIN_DIGITS)}{_wrapper}"
            _out_row = [_s_idx]
            _s_rows = [f"{_wrapper}{_value}{_wrapper}" for _value in _row]
            _out_row.extend(_s_rows)
            _out.append(_out_row)

        _columns.insert(0, "#")
        _columns = [f"{_wrapper}{_c}{_wrapper}" for _c in _columns]
        _out.insert(0, _columns)
        out = [self._csv_sep.join(_line) for _line in _out]
        return out

    @property
    def json(self) -> str:
        """returns the table as json string"""
        return json.dumps(self._table, indent=4)

    @property
    def rows(self) -> List[dict]:
        """returns table as list of dicts"""
        return list(self._table.values())

    @property
    def row_dict(self) -> Dict[int, dict]:
        """returns the row indices"""
        return self._row_index_dict

    @property
    def column_keys(self) -> List[str]:
        """returns the column keys"""
        out = [_col_info[COL] for _col_info in list(self._column_meta_dict.values())]
        return out

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

        self._row_index_dict = {}
        _table: dict = {}
        # create the model and build index
        self._is_list = False

        if isinstance(table, list):
            self._is_list = True
            for _idx, _item in enumerate(table):
                _table[_idx] = _item
                # map the index
                self._row_index_dict[_idx] = {ORIGINAL_ROW_KEY: _idx, KEY: _idx, ACTIVE: True}
        elif isinstance(table, dict):
            self._index_key_map = {}
            for _idx, (_key, _item) in enumerate(table.items()):
                _table[_idx] = _item
                self._index_key_map[_key] = _idx
                self._row_index_dict[_idx] = {ORIGINAL_ROW_KEY: _key, KEY: _idx, ACTIVE: True}
        self._table = _table
        self.set_column_index(column_dict)
        # now set the max length
        for _, _row in self._table.items():
            self._set_column_width_single(_row)

    def _set_column_map_dict(self) -> None:
        """sets the column key dict (key to index)"""
        logger.debug("start")
        self._column_key_idx_map = {}
        self._column_idx_key_map = {}

        for _idx, _info in self._column_meta_dict.items():
            _info[MAX_LENGTH] = len(_info[COL])
            self._column_key_idx_map[_info[COL]] = _idx
            self._column_idx_key_map[_idx] = _info[COL]

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
            # adding a length to be used for display, at least the length of the key
            _column_meta[MAX_LENGTH] = len(_key)
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

    def get_column_key(self, key: object) -> object | None:
        """gets the column key either from a key or from column index"""

        _key = None
        _idx = None
        try:
            _key = key
            _idx = self._column_key_idx_map[_key]
        except KeyError:
            try:
                _idx = int(key)
                _key = self._column_idx_key_map[_idx]
            except ValueError:
                _idx = None
                _key = None
        if _idx is None or _key is None:
            logger.debug(f"[SimpleTableModel] Can't find key [{key}] in column maps")
            return None
        return _key

    def swap_rows(self, rows_to_swap: tuple) -> None:
        """swapping index of rows"""
        logger.debug(f"swap_rows, {rows_to_swap}")
        try:
            _key1, _key2 = rows_to_swap
        except (ValueError, IndexError):
            logger.info(f"Error swapping rows {rows_to_swap}")
            return
        try:
            _row_info1 = self.get_row(_key1).copy()
            _row_info2 = self.get_row(_key2).copy()
        except AttributeError:
            logger.warning(f"Invalid rows to swap {rows_to_swap}, skip process")
            return

        # we also need to swap the indices
        _index_info1 = self.get_index_info(_key1).copy()
        _index_info2 = self.get_index_info(_key2).copy()
        _idx1 = _index_info1[KEY]
        _idx2 = _index_info2[KEY]
        _index_info1[KEY] = _idx2
        _index_info2[KEY] = _idx1
        self._row_index_dict[_idx1] = _index_info2
        self._row_index_dict[_idx2] = _index_info1
        # swap rows
        self.update_row(_key1, _row_info2, overwrite=True)
        self.update_row(_key2, _row_info1, overwrite=True)
        logger.debug(f"Swapped rows {rows_to_swap}, indices [{_idx1, {_idx2}}]")

    def update_row(self, row_key: object, col_dict: dict, overwrite: bool = False) -> None:
        """updates a given row from information passed"""
        logger.debug(f"update_row {row_key}")

        _index_info = self.get_index_info(row_key)
        if _index_info is None:
            return

        if overwrite:
            _row = {}
        else:
            _row = self.get_row(row_key)

        # only update columns that are in the model
        # eventually parse it as number
        _col_dict = {}
        for _content_key in list(col_dict.keys()):
            _key = self.get_column_key(_content_key)
            if _key is None:
                continue
            _col_dict[_key] = col_dict[_content_key]

        _row.update(_col_dict)
        _key = _index_info[KEY]
        self._table[_key] = _row
        self._set_column_width_single(_row)
        logger.debug(f"Updated row [{_key}], {_col_dict}")

    def get_row(self, key: object) -> dict | None:
        """reads the row index  / key  and returns the row dict"""
        # first try to get the value from index map
        logger.debug(f"get_row {key}")

        out: dict = None
        _index_info = self.get_index_info(key)
        if _index_info is None:
            return out
        _key = _index_info[KEY]

        try:
            out = self._table[_key]
        except (IndexError, ValueError):
            logger.debug(f"There is no index [{key}] in table")

        return out.copy()

    def add_row(self, col_dict: dict, key: object = None) -> None:
        """add a row information passed"""
        logger.debug(f"add_row {key}, {col_dict}")
        if isinstance(col_dict, dict) and len(col_dict) == 0:
            logger.info("Trying to addd an empty dict, adding row will be skipped")
            return

        # check that key is not already in list
        if self.get_index_info(key) is not None:
            return

        _key = self._max_idx
        _original_key = key if key is not None else _key

        _col_dict = {}
        # fill up missing columns
        for _col_key in list(self._column_key_idx_map.keys()):
            _col_dict[_col_key] = col_dict.get(_col_key)

        if isinstance(col_dict, dict):
            self._table[_key] = _col_dict
            self._set_column_width_single(_col_dict)
        else:
            logger.warning("Empty dict was passed")
            return

        if self._index_key_map is not None:
            self._index_key_map[_original_key] = _key
            self._row_index_dict[_key] = {ORIGINAL_ROW_KEY: _original_key, KEY: _key, ACTIVE: True}

        self._max_idx += 1

    def get_index_info(self, key: object) -> dict | None:
        """returns the row index dict entry"""
        # try to find whether we have original or index key
        out = None
        logger.debug(f"start, key [{key}]")
        _row_index = None
        if isinstance(self._index_key_map, dict):
            _row_index = self._index_key_map.get(key)
        if _row_index is None:
            _row_index = key
        try:
            _row_index = int(_row_index)
        except (ValueError, TypeError):
            logger.debug(f"Can't find row index for key [{key}]")
            return None
        if _row_index is None:
            logger.debug(f"There is no index [{key}] in table")
            return None
        out = self._row_index_dict.get(_row_index)
        logger.debug(f"_get_index_info [{key}]: index info [{out}] ")
        return out

    def delete_row(self, key: object) -> dict | None:
        """delete row, returns deleted key if existing"""
        logger.debug(f"start delete row {key}")
        _index_info = self.get_index_info(key)

        if _index_info is None:
            return

        _original_key = _index_info[ORIGINAL_ROW_KEY]
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
        _ = self._row_index_dict.pop(_key)
        # remove item
        _ = self._table.pop(_key)
        logger.debug(f"deleted item {out}")
        return out

    def toggle_row(self, key: object, active: bool = None) -> None:
        """activate/deactivate or set status row"""
        logger.debug(f"start toggle row {key}")
        _index_info = self.get_index_info(key)
        if _index_info is None:
            return
        _active = _index_info[ACTIVE]
        _active = not _active
        _active = active if active is not None else _active
        _index_info[ACTIVE] = _active
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
        self._table_model: SimpleTableModel = SimpleTableModel(table)
        self._table_stats = self._table_model.stats
        # formatting number of zeroes for index / minwidth of 4
        self._idx_zeroes = max(len(str(self._table_stats[NUM_ROWS])), 2)
        # getting the column meta dict
        self._column_dict = {_col[COL]: _col for _col in self._table_stats[COLUMN_META]}

        # flag whether to output row numbers
        self._render_index = render_index

    @property
    def table_model(self) -> SimpleTableModel:
        """returns the table model"""
        return self._table_model

    def _show_help(self) -> None:
        """Shows info"""
        _cmd = "CMD: ➡️ ⤵️ 🔠 ([#],[#]) 🔃 (s#,#)*️⃣ (a)🙈(t#)❌ (x#) [:[idx|col:value]]  🛑(q) 📅📘🤖(mwtjp) output.."
        print(_cmd)

    def _input_cmd(self) -> str:
        """get the input"""
        self._show_help()
        _s_input = "👷 CMD > "
        return input(_s_input)

    def _render_rows(self) -> List[str]:
        """renders rows as string output"""
        out = []

        for _row_key, _row_info in self._table_model.table.items():
            _rendered = self._render_row(row_info=_row_info, key=_row_key)
            if _rendered is None:
                continue
            out.extend(_rendered)

        return out

    def _render_row(self, row_info: dict, key: int) -> List[List[str]] | None:
        """renders a single row for output and splits it into multiple rows if needed"""
        logger.debug(f"start, row_info: {row_info}")
        out = []
        # try to get index info first
        _index_info = self.table_model.get_index_info(key)
        if _index_info is None:
            return None
        _index = _index_info.get(KEY, "NA")

        # get number of lines for each cell in this row
        _max_chars = max([len(str(_v)) for _v in list(row_info.values())])

        # check whether we need more than 1 row to display the cell
        _num_lines = 1
        if self._max_cell_width is not None:
            _num_lines = max(_max_chars // self._max_cell_width, 1)

        _cell_out = {}

        if self._render_index:
            _num_spaces = len(str(self._table_stats[NUM_ROWS]).zfill(IDX_MIN_DIGITS)) + 2
            _lines = [_num_spaces * " "] * _num_lines
            # Add a hint using brackets whether an itm is toggled inactive or not
            _row_is_active = _index_info.get(ACTIVE, True)
            _index_str = str(_index).zfill(self._idx_zeroes)
            _index_str = f"{_index_str}  " if _row_is_active else f"({_index_str})"
            _lines.insert(0, _index_str)
            _lines.pop()
            _cell_out["index"] = _lines

        _num_rows_in_cell = 1
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
            _table_value = row_info.get(_col_key)
            _cell_value = "*" if _table_value is None else str(_table_value)
            _cell_value = _cell_value + ((_cell_width * _num_lines) - len(_cell_value)) * " "
            # split it into lines

            _cell_lines = [_cell_value[_i : _i + _cell_width] for _i in range(0, len(_cell_value), _cell_width)]
            _cell_out[_col_key] = _cell_lines
            _cell_out[_col_key] = _cell_lines
            if _num_rows_in_cell < len(_cell_lines):
                _num_rows_in_cell = len(_cell_lines)

        # lines need to be filled up with blanks
        _corrected_lines = {}
        for _col, _lines in _cell_out.items():
            _blanks = [len(_lines[0]) * " "]
            _num_add_lines = _num_rows_in_cell - len(_lines)
            if _num_add_lines > 0:
                _lines.extend(_blanks * _num_add_lines)
            # UGLY FIX: mismatching line length for last item
            _length = len(_blanks[0])
            _out_lines = []
            for _line in _lines:
                if len(_line) == _length:
                    _out_lines.append(_line)
                    continue
                _spaces = (_length - len(_line)) * " "

                _out_lines.append(_line + _spaces)
            _corrected_lines[_col] = _out_lines
        _cell_out = _corrected_lines

        # for _line_num in range(_num_lines):
        for _line_num in range(_num_rows_in_cell):
            _line = []
            for _, cell_list in _cell_out.items():
                _line.append(cell_list[_line_num])
            out.append(_line)

        logger.debug(f"end, rendered: {out}")
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

    def markdown(
        self, md_type: Literal["markdown", "wiki", "plain", "csv"] = "markdown", columns: bool = True
    ) -> List[str]:
        """renders the table as markdown or CSV"""
        out = []
        if md_type == "csv":
            return self._table_model.csv
        _table_separator = ","
        _wrap_char = ""
        _title_separator = ""

        if md_type == "markdown" or md_type == "wiki":
            _table_separator = "|"
            _wrap_char = "|"
            _title_separator = "|" if md_type == "markdown" else "||"

        _columns = self._table_model.column_keys
        if self._render_index:
            _columns.insert(0, "#")
        _rendered_rows = self._render_rows()

        # assemble the column titles
        if columns and len(_rendered_rows) > 0:
            # _separator
            _col_titles = []
            _titlerow_separators = []
            _col_widths = [len(_col) for _col in _rendered_rows[0]]
            for _idx, _col_width in enumerate(_col_widths):
                _col = _columns[_idx]
                _col += (_col_width - len(_col)) * " "
                _col_titles.append(_col)
                _titlerow_separators.append("-" * _col_width)
            out.append(f"{_title_separator}{_title_separator.join(_col_titles)}{_title_separator}")
            # out.append(_title_separator.join(_columns))
            if md_type == "markdown":
                out.append(f"{_title_separator}{_title_separator.join(_titlerow_separators)}{_title_separator}")
        _rows = [f"{_table_separator}{_table_separator.join(_line)}{_table_separator}" for _line in _rendered_rows]
        out.extend(_rows)
        return out

    def _parse_content_input(self, content: dict) -> dict:
        """validates / parses content from input into dict
        (=transforms into column keys )"""
        out = {}
        if content is None:
            return out
        # get the column key index
        for _key, _value in content.items():
            _col_key = None
            _col_idx = None
            # first try to get it as column key
            try:
                _col_key = _key
                _col_idx = self._table_model.column_key_idx_map[_col_key]
            # access failed try to interpret _key as columm index
            except KeyError:
                _col_idx = _key
                _col_key = self._table_model.column_idx_key_map.get(_col_idx)
            if _col_idx is None or _col_key is None:
                logger.debug(f"[SimpleTableViewer] Can't find key [{_key}] in column maps, value [{_value}] is skipped")
                continue
            out[_col_key] = _value
        return out

    def _add_row(self, content: dict) -> None:
        """adding a row to the table"""
        logger.debug(f"[SimpleTableViewer] add_row ({content})")
        _col_dict = self._parse_content_input(content)
        self._table_model.add_row(_col_dict)

    def _edit_row(self, row: int, content: dict) -> None:
        """adding a row to the table"""
        logger.debug(f"Start Edit Row [{row}]:{content}")
        self._table_model.update_row(row_key=row, col_dict=content, overwrite=False)

    def _del_row(self, row: int) -> None:
        """adding a row to the table"""
        logger.debug(f"[SimpleTableViewer] del_row ({row})")
        self._table_model.delete_row(int(row))

    def _swap_rows(self, rows: tuple) -> None:
        """swap rows"""
        _swap_rows = rows
        logger.debug(f"[SimpleTableViewer] swap_rows ({_swap_rows})")
        self._table_model.swap_rows(rows_to_swap=_swap_rows)

    def _toggle_row(self, row: int) -> None:
        """swap rows"""
        logger.debug(f"[SimpleTableViewer] toggle_row ({row})")
        self._table_model.toggle_row(int(row))

    def _edit_row_col(self, row: int, col: object, content: dict) -> None:
        """edit a specific cell"""
        logger.debug(f"[SimpleTableViewer] edit_row_col ({row},{col}):[{content}]")

        _col_key = self._table_model.get_column_key(col)
        if _col_key is None:
            return
        _row = self._table_model.get_row(row)
        try:
            _row[_col_key] = next(iter(content.values()))
            self._table_model.update_row(row_key=row, col_dict=_row, overwrite=True)
        except (KeyError, ValueError):
            logger.debug(f"[SimpleTableViewer] No VALUE found in content {content}")

    def _edit_col(self, col: object, content: dict) -> None:
        """edit a specific cell"""
        logger.debug(f"[SimpleTableViewer] edit_col (,{col}):[{content}]")

        _row_indices = list(self._table_model.column_idx_key_map.keys())
        for _row in _row_indices:
            self._edit_row_col(row=_row, col=col, content=content)

    def _output(self, out_format: str) -> None:
        """show formatted table"""
        _out = None
        if out_format == TABLE_ACTION.CSV:
            _out = "\n".join(self._table_model.csv)
        elif out_format == TABLE_ACTION.JSON:
            _out = self._table_model.json
        elif out_format == TABLE_ACTION.WIKI:
            _out = "\n".join(self.markdown(md_type="wiki"))
        elif out_format == TABLE_ACTION.MARKDOWN:
            _out = "\n".join(self.markdown(md_type="markdown"))
        elif out_format == TABLE_ACTION.PLAIN:
            _out = "\n".join(self.markdown(md_type="plain"))
        else:
            return
        print("\n" + _out + "\n")

    def input_loop(self) -> None:
        """Input Loop"""
        _finished = False
        while _finished is False:
            print("\n".join(self.markdown(md_type="markdown", columns=True)))
            _s_input = self._input_cmd()
            _parsed_input = self._parse_input(_s_input)
            # print("PARSED INPUT ", _parsed_input)
            if _parsed_input is None:
                _finished = True
                continue
            _action = _parsed_input.get(ACTION, {}).get(CODE, "NA")
            _content = _parsed_input.get(CONTENT, {})
            _row = _parsed_input.get(ACTION, {}).get(ROW)
            _col = _parsed_input.get(ACTION, {}).get(COL)

            if _action == TABLE_ACTION.ADD_ROW:
                self._add_row(_content)
            elif _action == TABLE_ACTION.TOGGLE_ROW:
                self._toggle_row(_row)
            elif _action == TABLE_ACTION.EDIT_ROW:
                self._edit_row(_row, _content)
            elif _action == TABLE_ACTION.DEL_ROW:
                self._del_row(_row)
            elif _action == TABLE_ACTION.SWAP_ROWS:
                self._swap_rows(_row)
            elif _action == TABLE_ACTION.EDIT_ROW_COL:
                self._edit_row_col(_row, _col, _content)
            elif _action == TABLE_ACTION.EDIT_COL:
                self._edit_col(_col, _content)
            elif (
                _action == TABLE_ACTION.MARKDOWN
                or _action == TABLE_ACTION.CSV
                or _action == TABLE_ACTION.JSON
                or _action == TABLE_ACTION.WIKI
                or _action == TABLE_ACTION.PLAIN
            ):
                self._output(out_format=_action)
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


def main():
    """do something"""
    SAMPLE_TABLE = {
        "xx": {"a": "col a1 sdfsfd", "b": 15, "c": "hugoc1 sdghsdg dsjhgshd ghjs gjshdg jsgd"},
        "yy": {"a": "col a2", "b": 25, "c": "hugoc2"},
        "zz": {"a": "col a3", "b": 35, "c": "hugoc3"},
    }
    # _table_viewr = SimpleTableViewer()
    # _table_viewr.input_loop()
    # _st_model = SimpleTableModel(_sample_table)
    # print(json.dumps(_st_model.stats, indent=4))
    table_viewer = SimpleTableViewer(table=SAMPLE_TABLE, max_cell_width=10)
    table_viewer.input_loop()
    # finally get the table content
    # _rows = _table_viewer._render_rows()
    # _table_viewer.markdown()
    # print(_rows)
    # _csv = _table_viewer.table_model.csv

    pass


if __name__ == "__main__":
    loglevel = CLI_LOG_LEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=logging.INFO,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
