"""emoji handling, rich already provides codes
SOURCES
https://unicode.org/Public/emoji/latest/
rich._emoji_codes import EMOJI contains referenced emojis in Rich
https://rich.readthedocs.io/en/latest/markup.html
EMOJI COLLECTIONS
https://gist.github.com/rxaviers/7360908
https://github.com/datasets/emojis/blob/main/emojis.csv
https://github.com/Fantantonio/Emoji-List-Unicode
FILES EMOJI GROUPS
https://github.com/milesj/emojibase
# emoji list / with groups and subgroup ids
https://github.com/milesj/emojibase/blob/master/packages/data/en/data.raw.json
# group and metadata definition
https://github.com/milesj/emojibase/blob/master/packages/data/meta/groups.json
https://emojibase.dev/docs/datasets/
"""

# from rich.emoji import Emoji
import logging
import os
from pathlib import Path
from typing import List, Literal

import requests
from rich._emoji_codes import EMOJI
from rich.console import Console
from rich.emoji import Emoji
from rich.table import Table

from model.model_emoji import EmojiMetaDictAdapter, EmojiMetaDictType, EmojiMetaType
from model.model_filter import SimpleStrFilterModel
from util import constants as C
from util.constants import PATH_RESOURCE
from util.matrix_list import MatrixList
from util.persistence import Persistence
from util.utils import Utils

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

# Rich Emoji codes
NUMBERS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}

RCLOCK = {
    "0000": "clock12",
    "0030": "clock1230",
    "0100": "clock1",
    "0130": "clock130",
    "0200": "clock2",
    "0230": "clock230",
    "0300": "clock3",
    "0330": "clock330",
    "0400": "clock4",
    "0430": "clock430",
    "0500": "clock5",
    "0530": "clock530",
    "0600": "clock6",
    "0630": "clock630",
    "0700": "clock7",
    "0730": "clock730",
    "0800": "clock8",
    "0830": "clock830",
    "0900": "clock9",
    "0930": "clock930",
    "1000": "clock10",
    "1030": "clock1030",
    "1100": "clock11",
    "1130": "clock1130",
    "1200": "clock12",
}

SQUARE = {
    "blue": "blue_square",
    "green": "green_square",
    "orange": "orange_square",
    "purple": "purple_square",
    "red": "red_square",
    "yellow": "yellow_square",
    "black": "black_large_square",
    "white": "white_large_square",
    "brown": "brown_square",
}

CIRCLE = {
    "blue": "blue_circle",
    "green": "green_circle",
    "orange": "orange_circle",
    "purple": "purple_circle",
    "red": "red_circle",
    "yellow": "yellow_circle",
    "black": "black_circle",
    "white": "white_circle",
    "brown": "brown_circle",
}

# EMOJI_INDICATOR_

SPECTRAL = {
    1: ["black"],
    2: ["red", "green"],
    3: ["red", "yellow", "green"],
    4: ["red", "yellow", "green", "blue"],
    5: ["red", "yellow", "green", "blue", "purple"],
    6: ["red", "orange", "yellow", "green", "blue", "purple"],
}


class EmojiUtil:
    """Emoji Helper"""

    @staticmethod
    def int2emoji(number: int, num_digits: int = None) -> str:
        """converting an int to an emoji"""
        out = []
        s_int = str(number)
        if num_digits is not None:
            s_int = s_int.zfill(num_digits)
        for s in s_int:
            out.append(Emoji.replace(f":{NUMBERS[int(s)]}:"))
        return " ".join(out)

    @staticmethod
    def code2emoji(emoji_list: List[str]) -> List[str]:
        """converts rich emoji codes into list of eojis"""
        return [Emoji.replace(f":{_code}:") for _code in emoji_list]

    @staticmethod
    def get_emoji_tree(emoji_dict: dict) -> dict:
        """returns the emoji taxonomy"""
        main_classes = {}
        for emoji_key, emoji_info in emoji_dict.items():
            _emoji_class = emoji_info["class"]
            _emoji_subclass = emoji_info["subclass"]
            _main_class_dict = main_classes.get(_emoji_class, {})
            # add the main class
            if len(_main_class_dict) == 0:
                main_classes[_emoji_class] = _main_class_dict
            _subclass_dict = _main_class_dict.get(_emoji_subclass, {})
            if len(_subclass_dict) == 0:
                _main_class_dict[_emoji_subclass] = _subclass_dict
            _subclass_dict[emoji_key] = emoji_info
        return main_classes

    @staticmethod
    def read_emoji_meta() -> dict:
        """gets the meta information from the json with emoji name as key"""
        f_emoji = PATH_RESOURCE.joinpath("emoji.json")
        _emojis = Persistence.read_json(f_emoji)
        out = {}
        for _emoji_meta in _emojis.values():
            _key = _emoji_meta["info"].replace(" ", "_")
            _key = _key.replace("-", "_")
            out[_key] = _emoji_meta
        return out

    @staticmethod
    def show_rich_emoji_codes(emoji_filter: str | list = None, only_meta: bool = False) -> None:
        """Displays Rich Emoji Codes, filtered,
        flag only_meta will only display items with valid metadata"""
        if isinstance(emoji_filter, str):
            _emoji_filters = [emoji_filter]
        elif isinstance(emoji_filter, list):
            _emoji_filters = emoji_filter
        else:
            _emoji_filters = None
        _emoji_meta = EmojiUtil.read_emoji_meta()
        _emoji_tree = EmojiUtil.get_emoji_tree(_emoji_meta)
        _console = Console()
        for emoji_class, emoji_subclass_info in _emoji_tree.items():
            for emoji_subclass, emoji_info in emoji_subclass_info.items():
                _out_list = []
                emoji_keys = sorted(emoji_info.keys())
                for _emoji_key in emoji_keys:
                    # check whether this is also contained in rich icon set
                    if EMOJI.get(_emoji_key) is None:
                        continue
                    _meta = _emoji_meta.get(_emoji_key)
                    if _meta:
                        _class = _meta["class"]
                        _subclass = _meta["subclass"]
                        _add_info = f"\[{_class}:{_subclass}]"
                    else:
                        _add_info = ""
                    _out = f"[:{_emoji_key}:] {_emoji_key}"
                    _search = f"[:{_emoji_key}:] {_add_info} {_emoji_key}"

                    if _emoji_filters:
                        _hits = [f for f in _emoji_filters if f.lower() in _search.lower()]
                        if len(_hits) == 0:
                            continue
                    _out_list.append(_out)
                if len(_out_list) == 0:
                    continue

                _console.print(f"\n[red bold]### EMOJI CLASS [{emoji_class} : {emoji_subclass}]")
                _console.print("\n".join(_out_list))

    @staticmethod
    def show_rich_emoji_table(
        emoji_filter: str | list = None, only_meta: bool = True, num_cols: int = 7, ignore_combinations: bool = True
    ):
        """shows all emojis defined in rich in a table"""

        def _pass_filter(_emoji_name: str) -> bool:
            if ignore_combinations:  # ignore combined emojis
                if "flag_for" in _emoji_name or "skin_tone" in _emoji_name:
                    return False

            if _emoji_filters is None:
                return True
            passes = False
            for _emoji_filter in _emoji_filters:
                if _emoji_filter in _emoji_name:
                    passes = True
            return passes

        def _split_key(key: str, n: int = 15) -> str:
            """adds carriage return for key"""
            if len(key) >= n:
                split_key = [key[i : i + n] for i in range(0, len(key), n)]
                return "\n".join(split_key)
            else:
                return key

        if isinstance(emoji_filter, str):
            _emoji_filters = [emoji_filter]
        elif isinstance(emoji_filter, list):
            _emoji_filters = emoji_filter
        else:
            _emoji_filters = None

        _emoji_list = list(EMOJI.keys())
        _emoji_list = [f"{EMOJI[k]} {_split_key(k)}" for k in _emoji_list if _pass_filter(k)]
        # todo PRIO3 filter
        _emoji_matrix = MatrixList.list2matrix(_emoji_list, num_cols)
        _table = Table(show_lines=True, show_header=False)

        for _emoji_row in _emoji_matrix:
            _table.add_row(*_emoji_row)
        Console().print(_table)

    @staticmethod
    def download_unicode_emoji_sequences(p_emojis: str) -> str:
        """retrieves the unicode emoji sequence file"""

        _p = Path(p_emojis)
        if not _p.is_dir():
            print(f"Path for downloading file [{p_emojis}] has invalid path")
            return
        _url = "https://unicode.org/Public/emoji/latest/"
        _file = "emoji-sequences.txt"
        _f_emoji = str(_p.joinpath(_file))
        _url_file = _url + _file
        _response = requests.get(_url_file, timeout=120)
        if _response.status_code == 200:
            with open(_f_emoji, "w", encoding="UTF-8") as file:
                file.write(_response.text)
            print(f"Download of Emoji File [{_url_file}] to [{_f_emoji}]")
        else:
            print(f"Failed to download the file [{_url_file}], status [{_response.status_code}]")

    @staticmethod
    def emoji(hex: str) -> str:
        """creates emoji from hex number (sequence)"""
        _hex: str = hex
        # complex icons seems not to be worjing in shell
        # U+1F470  => 0001F470
        # U+2642   =>     2642
        if _hex.startswith("U+1"):
            _hex = f"000{_hex[2:]}"
        elif len(_hex) == 6 and _hex.startswith("U+"):
            _hex = f"0000{_hex[2:]}"
        code_point = chr(int(_hex, 16))
        return code_point

    @staticmethod
    def get_emoji_metadata(skip_multi_char: bool = False) -> EmojiMetaDictType:
        """returns the emoji metadata
        parameter allows to skip multi character emojis that
        do not seem to work in shells
        """
        out = {}
        _meta_data_dict = EmojiUtil.read_emoji_meta()
        for _key, _info in _meta_data_dict.items():
            _meta = EmojiMetaType(**_info)
            _code = str(_meta.code)
            if skip_multi_char and " " in _code:
                continue
            _num = str(_meta.num).zfill(4)
            _info = f"[{_meta.class_}:{_meta.subclass}:{_meta.info}]"
            # enrich with descriptions
            _meta.description = f"({_num}) {_info}"
            _meta.short_txt = f"{_meta.char} {_meta.info}"
            out[_key] = _meta
        return out

    @staticmethod
    def filter_emoji_metadata(
        emoji_meta_data: EmojiMetaDictType,
        class_filter: SimpleStrFilterModel | None = None,
        subclass_filter: SimpleStrFilterModel | None = None,
        key_filter: SimpleStrFilterModel | None = None,
        description_filter: SimpleStrFilterModel | None = None,
    ) -> EmojiMetaDictType:
        """Filter Emoji Metadata, returns the filtered keys"""
        _filter = {
            "class_": class_filter,
            "subclass": subclass_filter,
            "info": key_filter,
            "description": description_filter,
        }
        out = {}
        for _key, _meta in emoji_meta_data.items():
            _attributes = list(_filter.keys())
            _match = True
            # check against each of these attributes
            for _attribute in _attributes:
                _value = getattr(_meta, _attribute)
                _simple_filter = _filter[_attribute]
                if not _simple_filter:
                    continue
                _match = Utils.simple_str_filter(_value, _simple_filter)
                # ignore items with None
                if _match is None:
                    continue
            if not _match:
                continue
            out[_key] = _meta
        return out

    @staticmethod
    def emoji_hierarchy(emoji_meta_data: EmojiMetaDictType, simple: bool = False, description: bool = False) -> dict:
        """create a hierarchy dict with either object, simple or long description, or object as leaf"""
        out = {}
        for _key, _meta in emoji_meta_data.items():
            _class = _meta.class_
            _subclass = _meta.subclass
            _class_dict = out.get(_class)
            if _class_dict is None:
                _class_dict = {}
                out[_class] = _class_dict
            _subclass_dict = _class_dict.get(_subclass)
            if _subclass_dict is None:
                _subclass_dict = {}
                _class_dict[_subclass] = _subclass_dict
            if simple:
                _subclass_dict[_key] = _meta.short_txt
            elif description:
                _subclass_dict[_key] = _meta.description
            else:
                _subclass_dict[_key] = _meta
        return out


class EmojiIndicator:
    """calculating an EMOJI indicator based on valuesy"""

    def __init__(
        self,
        emojis: List[str] = None,
        min_value: int | float = None,
        max_value: int | float = None,
        reverse_emojis: bool = False,
    ):
        # upper and lower bounds
        self._min_value = min_value
        self._max_value = max_value
        # reverse the color schema#
        self._emojis = emojis
        if self._emojis is None:
            self._emojis = EmojiIndicator.render_list(5, "square")
        if reverse_emojis:
            self._emojis = list(reversed(self._emojis))
        self._num_emojis = len(self._emojis)

    @staticmethod
    def render_list(
        num_values: int = None,
        emoji_type: Literal["square", "circle"] = "square",
        rendering: Literal["spectral", "numbers_from_zero", "numbers_from_one", "percentage"] = "spectral",
    ) -> list:
        """returns a list of rendered emojis"""
        # get the rendering map
        _emoji_codes = []
        _num_values = num_values if isinstance(num_values, int) else 99999
        # get the list of emoji codes
        if rendering == "spectral":
            _num_colors = min(_num_values, len(SPECTRAL))
            _color_list = SPECTRAL[_num_colors]
            if emoji_type == "circle":
                _emoji_dict = CIRCLE
            else:
                _emoji_dict = SQUARE
            _emoji_codes = [_emoji_dict[_col] for _col in _color_list]
        elif "numbers" in rendering:
            _offset = 0  # offset when starting from 1
            if rendering == "numbers_from_one":
                _offset = 1
            _num_emojis = min(_num_values, len(NUMBERS) - _offset)
            _from = 0 + _offset
            _to = _num_emojis + _offset
            _emoji_codes = list(NUMBERS.values())[_from:_to]
        elif "percentage" in rendering:
            _percentages = [f"{EmojiUtil.int2emoji(_n, 2)}  " for _n in range(0, 100)]
            # special rendering for 100
            _percentages.append(f'{Emoji.replace(":ten::zero:")}  ')
            return _percentages

        return [Emoji.replace(f":{_emoji_code}:") for _emoji_code in _emoji_codes]

    def set_minmax_values(self, min_value: float | int = None, max_value: float | int = None):
        """set boundary numerical values for directly calculating index number"""
        self._min_value = min_value if min_value is not None else 0
        self._max_value = max_value if max_value is not None else (self._num_emojis - 1)

    def get_minmax_values(self) -> list:
        """return limit values"""
        return [self._min_value, self._max_value]

    @property
    def num_icons(self):
        """return num of icons"""
        return self._num_emojis

    def render(
        self,
        value: int | float,
        min_value: float | int = None,
        max_value: float | int = None,
        add_percentage: bool = False,
    ) -> str | list:
        """calculates emoji"""
        # set min max values
        if min_value is not None and max_value is not None:
            self.set_minmax_values(min_value, max_value)
        _num_icons = self._num_emojis
        if value > self._max_value:
            value = self._max_value
        elif value < self._min_value:
            value = self._min_value
        _percentage = (value - self._min_value) / (self._max_value - self._min_value)
        _index = int(round(_percentage * (_num_icons - 1), 0))
        _icon = self._emojis[_index]
        if add_percentage:
            return [_icon, round(100 * _percentage, 0)]
        else:
            return _icon


if __name__ == "__main__":
    # python -m rich.emoji
    # LANG=en_US.UTF-8
    # export LC_ALL=en_US.UTF-8
    # export LANG=en_US.UTF-8
    # "de_DE.UTF-8" für Deutsch mit Unicode-Zeichensatz
    # show_rich_emoji_codes()
    # EmojiUtil.show_emoji_table(emoji_filter=["circ", "sq"])
    # print(EmojiUtil.emoji("U+1F233"))
    # print(EmojiUtil.emoji("U+2640"))
    # _emoji_dict = EmojiUtil.show_unicode_emojis()
    # _console = Console()
    # _console.print(_emoji_dict)
    # parse emoji metadata as model and back to json
    metadata: EmojiMetaDictType = EmojiUtil.get_emoji_metadata(skip_multi_char=True)
    # converting it into bytes and into string
    _json = EmojiMetaDictAdapter.dump_json(metadata).decode(encoding="UTF-8")
    _dict = EmojiMetaDictAdapter.dump_python(metadata)
    pass
    # EmojiUtil.show_rich_emoji_table()
    class_filter = SimpleStrFilterModel(str_filter="symb")
    description_filter = SimpleStrFilterModel(str_filter="symb")
    metadata_list_filtered = EmojiUtil.filter_emoji_metadata(metadata, class_filter=class_filter)
    metadata_hierarchy = EmojiUtil.emoji_hierarchy(metadata_list_filtered, simple=True)
    # for _key, _info in metadata_list_filtered.items():
    #     print(_info.short_txt)
    # for _key, _icon in EMOJI_NUMBERS.items():
    #     print(Emoji.replace(f":{_icon}:"))
    print(EmojiUtil.code2emoji(list(SQUARE.values())))
    # pass
    emoji_list = EmojiIndicator.render_list(num_values=10, rendering="percentage")
    emoji_indicator = EmojiIndicator(min_value=0, max_value=100, emojis=emoji_list)
    for n in range(0, 101, 5):
        print(f"VALUE {str(n).zfill(3)} {emoji_indicator.render(n)}%")
