""" emoji handling, rich already provides codes """
# from rich.emoji import Emoji
from rich._emoji_codes import EMOJI
from rich.console import Console
from util import constants as C
from util.persistence import Persistence

# TODO put everything into a class

def get_emoji_tree(emoji_dict:dict)->dict:
    """ returns the emoji taxonomy """
    main_classes = {}
    for emoji_key,emoji_info in emoji_dict.items():
        _emoji_class = emoji_info['class']
        _emoji_subclass = emoji_info['subclass']
        _main_class_dict = main_classes.get(_emoji_class,{})
        # add the main class
        if len(_main_class_dict) == 0:
            main_classes[_emoji_class]=_main_class_dict
        _subclass_dict = _main_class_dict.get(_emoji_subclass,{})
        if len(_subclass_dict) == 0:
            _main_class_dict[_emoji_subclass] = _subclass_dict
        _subclass_dict[emoji_key]=emoji_info
    return main_classes

def get_emoji_meta()->dict:
    """ gets the meta inforamtion from the json with emoji name as key """
    f_emoji = C.PATH_ROOT.joinpath("resources","emoji.json")
    _emojis = Persistence.read_json(f_emoji)
    out = {}
    for _emoji_meta in _emojis.values():
        _key = _emoji_meta["info"].replace(" ","_")
        _key = _key.replace("-","_")
        out[_key]=_emoji_meta
    return out

def show_rich_emoji_codes(emoji_filter:str|list=None,only_meta:bool=True)->None:
    """ Displays Rich Emoji Codes, filtered,
        flag only_meta will only display items with valid metadata  """
    if isinstance(emoji_filter,str):
        _emoji_filters = [emoji_filter]
    elif isinstance(emoji_filter,list):
        _emoji_filters = emoji_filter
    else:
        _emoji_filters = None
    _emoji_meta = get_emoji_meta()
    _emoji_tree = get_emoji_tree(_emoji_meta)
    _console = Console()
    for emoji_class,emoji_subclass_info in _emoji_tree.items():
        for emoji_subclass,emoji_info in emoji_subclass_info.items():
            _out_list = []
            emoji_keys = sorted(emoji_info.keys())
            for _emoji_key in emoji_keys:
                # check whether this is also contained in rich icon set
                if EMOJI.get(_emoji_key) is None:
                    continue
                _meta = _emoji_meta.get(_emoji_key)
                if _meta:
                    _class = _meta['class']
                    _subclass = _meta['subclass']
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

if __name__ == "__main__":
    show_rich_emoji_codes()
