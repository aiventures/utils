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
import os
from pathlib import Path

import requests
from rich._emoji_codes import EMOJI
from rich.console import Console
from rich.emoji import Emoji
from rich.table import Table

from util import constants as C
from util.matrix_list import MatrixList
from util.persistence import Persistence

EMOJI_NUMBERS = {0:"zero", 1:"one",10:"ten",2:"two",3:"three",4:"four",
                 5:"five", 6:"six",7:"seven", 8:"eight", 9:"nine"}

class EmojiUtil:
    """ Emoji Helper """

    @staticmethod
    def int2emoji(number:int)->str:
        """ converting an int to an emoji """
        out=""
        s_int = str(number)
        for s in s_int:
            out += Emoji.replace(f":{EMOJI_NUMBERS[int(s)]}:")
        return out

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
    def get_emoji_meta() -> dict:
        """gets the meta information from the json with emoji name as key"""
        f_emoji = C.PATH_ROOT.joinpath("resources", "emoji.json")
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
        _emoji_meta = EmojiUtil.get_emoji_meta()
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
    def show_emoji_table(
        emoji_filter: str | list = None, only_meta: bool = True, num_cols: int = 7, ignore_combinations: bool = True
    ):
        """shows all emojis in a table"""

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
        # todo filter
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

    # @staticmethod
    # def parse_sequences(f_emojis:str,f_emojis_json:str)->dict:
    #     """ parse the sequence file from the uniode page
    #         use the download_unicode_emoji_sequences function to download it
    #     """
    #     # download the file if not present
    #     if not os.path.isfile(f_emojis):
    #         EmojiUtil.download_unicode_emoji_sequences(str(Path(f_emojis).parent))
    #     _sequences = Persistence.read_txt_file(f_emojis)
    #     for _sequence in _sequences:
    #         pass

    @staticmethod
    def emoji(hex: str) -> str:
        """creates emoji from hex number (sequence)"""
        _hex = "2705"
        code_point = chr(int(_hex, 16))
        return code_point


if __name__ == "__main__":
    # python -m rich.emoji
    # LANG=en_US.UTF-8
    # export LC_ALL=en_US.UTF-8
    # export LANG=en_US.UTF-8
    # "de_DE.UTF-8" für Deutsch mit Unicode-Zeichensatz
    # show_rich_emoji_codes()
    # EmojiUtil.show_emoji_table(emoji_filter=["circ","sq"])
    # EmojiUtil.emoji("sss")
    # EmojiUtil.parse_sequences(r"...")
    print(EmojiUtil.int2emoji(1234))
    pass
