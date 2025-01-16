"""Rendering the File Tree"""

import logging
import os
from pathlib import Path
from typing import Dict, Literal, List

from rich.console import Console
from rich.emoji import Emoji as RichEmoji
from rich.filesize import decimal
from rich.logging import RichHandler
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree as RichTree

from cli.bootstrap_env import LOG_LEVEL
from model.model_tree import FileTreeNodeRenderModel, ParamsFileTreeModel
from model.model_persistence import ParamsFind
from util import constants as C

from util.file_tree import FileTree
from util.utils import PARENT, ROOT, SIZE, TOTAL_SIZE, VALUE, IS_FILE, CHDATE, PERMISSION_CHMOD, Utils, is_win

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

DEFAULT = "default"
COLOR = "color"
ICON = "icon"
FOLDER_OPEN = "folder_open"
FOLDER_CLOSE = "folder_close"
STYLE_QUERY = "deep_sky_blue1"
GUIDE_STYLE_DEFAULT = {"guide_style": "bold bright_black"}
GUIDE_STYLE_BY_LEVEL = {
    0: {"guide_style": "bold orange_red1"},
    1: {"guide_style": "bold green"},
    2: {"guide_style": "bold dodger_blue3"},
    3: {"guide_style": "bold purple4"},
    4: {"guide_style": "light_steel_blue3"},
    5: {"guide_style": "gray70"},
}

SKINS_FILE_EXTENSIONS = {
    "py": {ICON: "snake", COLOR: "green"},
    "dockerfile": {ICON: "whale", COLOR: "white"},
    "bak": {ICON: "anchor", COLOR: "bright_black"},
    "jpg": {ICON: "framed_picture", COLOR: "cyan"},
    "png": {ICON: "framed_picture", COLOR: "cyan"},
    "pdf": {ICON: "open_book", COLOR: "bright_red"},
    "mp3": {ICON: "headphone", COLOR: "bright_blue"},
    "xls": {ICON: "abacus", COLOR: "bright_green"},
    "xlsx": {ICON: "abacus", COLOR: "bright_green"},
    "txt": {ICON: "memo", COLOR: "white"},
    "log": {ICON: "scroll", COLOR: "bright_black"},
    "md": {ICON: "blue_book", COLOR: "bright_cyan"},
    "ppt": {ICON: "books", COLOR: "bright_red"},
    "pptx": {ICON: "books", COLOR: "bright_red"},
    FOLDER_CLOSE: {ICON: "file_folder", COLOR: "#606060"},
    FOLDER_OPEN: {ICON: "open_file_folder", COLOR: "#ffc706"},
    "zip": {ICON: "package", COLOR: "bright_black"},
    "tar": {ICON: "package", COLOR: "bright_black"},
    "gzip": {ICON: "package", COLOR: "bright_black"},
    "exe": {ICON: "gear", COLOR: "bright_yellow"},
    "bat": {ICON: "gear", COLOR: "bright_yellow"},
    "sh": {ICON: "gear", COLOR: "bright_yellow"},
    "ps1": {ICON: "gear", COLOR: "bright_yellow"},
    "svg": {ICON: "globe_with_meridians", COLOR: "cyan"},
    "htm": {ICON: "globe_with_meridians", COLOR: "cyan"},
    "html": {ICON: "globe_with_meridians", COLOR: "cyan"},
    "lnk": {ICON: "globe_with_meridians", COLOR: "cyan"},
    "vscode": {ICON: "notebook", COLOR: "blue"},
    "json": {ICON: "orange_book", COLOR: "#ffc706"},  # orange
    "plantuml": {ICON: "orange_book", COLOR: "#39b54a"},  # green
    "yaml": {ICON: "closed_book", COLOR: "#de382b"},  # red
    "toml": {ICON: "bookmark", COLOR: "#de382b"},  # red
    DEFAULT: {ICON: "page_facing_up", COLOR: "bright_black"},
}

# maps internal fields and sorting keys
SORT_KEY_MAP = {"permission": "chmod", "date": "chdate"}


class FileTreeRenderer:
    """Rendering A File Tree"""

    def __init__(
        self,
        params_file_tree: ParamsFileTreeModel,
        filetree_skin_dict: dict = None,
        show_query_info: bool = True,
        files_sorted_by: Literal["name", "size", "permission", "date", "extension"] = "name",
        files_reverse: bool = False,
        paths_sorted_by: Literal["name", "size", "permission", "date"] = "name",
        paths_reverse: bool = False,
    ):
        """render a file Tree object"""

        # also show the query information
        self._show_query_info = show_query_info
        # sorting options
        self._files_sorted_by = files_sorted_by
        self._files_reverse = files_reverse
        self._paths_sorted_by = paths_sorted_by
        self._paths_reverse = paths_reverse
        # gets the rendering skin and creates default values
        self._default_icon = None
        self._default_color = None
        self._icon_folder_open = None
        self._icon_folder_close = None
        if filetree_skin_dict is None:
            filetree_skin_dict = SKINS_FILE_EXTENSIONS
        self._filetree_skin = FileTreeRenderer._get_filetree_skin(self, filetree_skin_dict)
        # renders the tree
        self._params_file_tree: ParamsFileTreeModel = params_file_tree
        # root paths (righ now unclear whether this also works for multiple root paths)
        self._root_paths = self._params_file_tree.file_filter_params.p_root_paths
        self._folder_depth_root = None
        if isinstance(self._root_paths, str):
            self._folder_depth_root = len(Path(self._root_paths).parts)

        self._file_tree: FileTree = FileTree(params_file_tree)
        # node hierarchy
        # self._hierarchy: Dict[str, Dict] = self._file_tree.tree.hierarchy

        # gets the tree dictionary
        self._file_tree_dict: Dict[str, dict] = self._file_tree.tree_dict
        # rich tree refs
        self._rich_tree_dict: Dict[str, RichTree] = {}
        self._rich_tree: RichTree = None
        self._create_rich_tree()

    def _get_filetree_skin(self, file_extension_skin: dict) -> Dict[str, FileTreeNodeRenderModel]:
        """Returns a default dict for rendering the various file types"""
        # preset Values
        _default = file_extension_skin.get(DEFAULT, SKINS_FILE_EXTENSIONS[DEFAULT])
        _default_color = _default.get(COLOR, SKINS_FILE_EXTENSIONS[DEFAULT][COLOR])
        _icon_default = _default.get(ICON, SKINS_FILE_EXTENSIONS[DEFAULT][ICON])
        _icon_folder_open = file_extension_skin.get(FOLDER_OPEN, {}).get(ICON, SKINS_FILE_EXTENSIONS[FOLDER_OPEN][ICON])
        _icon_folder_close = file_extension_skin.get(FOLDER_CLOSE, {}).get(
            ICON, SKINS_FILE_EXTENSIONS[FOLDER_CLOSE][ICON]
        )
        self._default_color = _default_color
        self._default_icon = RichEmoji.replace(f":{_icon_default}:")
        self._icon_folder_open = RichEmoji.replace(f":{_icon_folder_open}:")
        self._icon_folder_close = RichEmoji.replace(f":{_icon_folder_close}:")

        out = {}

        for _ext in file_extension_skin:
            _skin_info = file_extension_skin.get(_ext, {COLOR: _default_color, ICON: self._default_icon})
            _skin_info[COLOR] = _skin_info.get(COLOR, self._default_color)
            _skin_info[ICON] = RichEmoji.replace(f":{_skin_info.get(ICON, self._default_icon)}:")
            out[_ext] = FileTreeNodeRenderModel(**_skin_info)

        return out

    def _render_node(self, _node_id, node_info: dict) -> dict:
        """renders the tree node"""
        out = ""
        _is_file = node_info.get(IS_FILE, None)
        _path = Path(node_info.get(VALUE, None))
        _name = _path.name
        # If there is a link with spaces convert it to windows
        # if path contains spaces get proper path (might not work on 'nix)
        _link_path = Utils.get_unspaced_path(str(_path), is_link=True)

        _change_date = node_info.get(CHDATE, None)
        _chdate_s = _change_date.strftime(C.DATEFORMAT_DD_MM_JJJJ_HH_MM)
        _permissions = node_info.get(PERMISSION_CHMOD)
        _level_depth = len(_path.parts) - self._folder_depth_root
        # for file we use hte same chmod color as its parent
        if _is_file:
            _level_depth -= 1
        # guide color to be used for CHMOD
        _guide_color = GUIDE_STYLE_BY_LEVEL.get(_level_depth, GUIDE_STYLE_DEFAULT)["guide_style"]
        _permissions_text = f"[{_guide_color}] [{_permissions}] "

        # _text_permissions = Text(_permissions, "")

        _icon = None
        _color = None
        _size = None
        # file
        if _is_file:
            _size = node_info.get(SIZE, None)
            _suffix = _path.suffix[1:]
            # if there is no suffix try with filename
            if len(_suffix) == 0:
                _suffix = _name
            _skin = self._filetree_skin.get(_suffix.lower(), self._default_icon)
            _color = _skin.color
            if _color is None:
                _color = self._default_color
            _icon = _skin.icon
            if _icon is None:
                _icon = self._default_icon
            _text_chdate = Text(f"{_chdate_s}", _color)
            _text_filename = Text(f"{_name}", _color)
            # TODO PRIO3 ADD HIGHLIGHTS DEOPENDING ON SEARCh ITEMS WHEN SEARCHING
            # text_filename.highlight_regex(r"\..*$", "bold bright_blue")
            _text_filename.stylize(f"link {_link_path}")
            _text_filename.append(f" ({decimal(_size)})", _color)
            _label = Text(f"[{_permissions}] ", _guide_color) + _text_chdate + " " + Text(_icon) + " " + _text_filename
            out = {"label": _label}
        # path
        else:
            # todo change color depending on level depth
            out = GUIDE_STYLE_BY_LEVEL.get(_level_depth, GUIDE_STYLE_DEFAULT)
            _path_is_empty = not self._file_tree.tree.has_children(_node_id)
            _style = "dim" if (_name.startswith("__") or _name.startswith(".")) else ""
            # set name depending on whether it's root or other
            if node_info.get("parent", "") == ROOT:
                _name = str(_path)
            if _path_is_empty:
                _skin = self._filetree_skin.get(FOLDER_CLOSE, {})
                _color = _skin.color
                _icon = _skin.icon
                _default_icon = self._icon_folder_close
                _size = 0
                _extra_format = ""
            else:
                _skin = self._filetree_skin.get(FOLDER_OPEN, {})
                _color = _skin.color
                _icon = _skin.icon
                _default_icon = self._icon_folder_close
                _size = node_info.get(TOTAL_SIZE, 0)
                _extra_format = "[bold]"

            if _color is None:
                _color = self._default_color
            if _icon is None:
                _icon = _default_icon
            _label = f"{_extra_format}{_icon}{_permissions_text}[{_color}]{_chdate_s} [link {_link_path}]{escape(_name)} ({decimal(_size)})"
            out["label"] = _label
            out["style"] = _style

        return out

    def _render_query_info(self, rich_tree_root: RichTree) -> None:
        """Renders the query information to be added to the output tree"""
        if self._show_query_info is False:
            return

        _query_title = RichEmoji.replace(f"[{STYLE_QUERY}]:magnifying_glass_tilted_right: QUERY PARAMS")
        _query_richtree_root = rich_tree_root.add(_query_title, guide_style=STYLE_QUERY, style=STYLE_QUERY)

        _excluded_fields = ["paths_only", "show_progress", "paths", "files", "as_dict"]
        _params = {}
        _filter_params = self._params_file_tree.file_filter_params
        _model_fields_set = _filter_params.model_fields_set
        _query_fields = ParamsFind.model_fields
        for _field in _query_fields:
            if not hasattr(_filter_params, _field):
                continue
            if _field in _excluded_fields:
                continue
            _value = getattr(_filter_params, _field)
            # only process supplied fields
            if _value is None:
                continue
            _params[_field] = _value
        _order = "DESCENDING" if self._paths_reverse else "ASCENDING"
        _paths_sorted_by = f"Paths sorted by \[{self._paths_sorted_by.upper()}] {_order}"
        _order = "DESCENDING" if self._files_reverse else "ASCENDING"
        _files_sorted_by = f"Files sorted by \[{self._files_sorted_by.upper()}] {_order}"

        _lines = [
            _paths_sorted_by,
            _files_sorted_by,
            f'Only Root Path [{_params.get("root_path_only","NA")}], Add Empty Paths [{_params.get("add_empty_paths","NA")}]',
            f'Match All [{_params.get("match_all","NA")}], Ignore Case [{_params.get("ignore_case","NA")}]',
        ]
        _keys = [
            "include_abspaths",
            "exclude_abspaths",
            "include_files",
            "exclude_files",
            "include_paths",
            "exclude_paths",
        ]
        for _key in _keys:
            _value = _params.get(_key)
            if _value is None:
                continue
            _lines.append(f"Filter ({_key}): {_value}")
        for _line in _lines:
            _query_richtree_root.add(_line)

    def _create_rich_tree_root(self) -> RichTree:
        """creates the richt tree node"""
        return RichTree(
            f"[{GUIDE_STYLE_DEFAULT['guide_style']}]FILE QUERY",
            guide_style=GUIDE_STYLE_DEFAULT["guide_style"],
        )

    def _render_rtree(self, node_id: str) -> List[str] | None:
        """renders a node in the rich tree"""
        _children = []
        # get the rich parent element so it can be assigned
        _rtree_parent = self._rich_tree_dict.get(node_id)
        _child_ids = self._file_tree.tree.get_children(node_id)
        _path_dict = {}
        _file_dict = {}

        for _child_id in _child_ids:
            _child_info = self._file_tree_dict.get(_child_id)
            if not _child_info:
                logger.warning(f"[FileTreeRenderer] Node {node_id} has no metadata")
                continue
            # process file
            if _child_info[IS_FILE]:
                if self._files_sorted_by == "name":
                    _child_info["name"] = Path(_child_info[VALUE]).name
                elif self._files_sorted_by == "extension":
                    _child_info["extension"] = Path(_child_info[VALUE]).suffix
                _file_dict[_child_id] = _child_info
            # process path
            else:
                if self._paths_sorted_by == "name":
                    _child_info["name"] = Path(_child_info[VALUE]).name
                elif self._paths_sorted_by == "extension":
                    _child_info["extension"] = Path(_child_info[VALUE]).suffix
                _path_dict[_child_id] = _child_info
                # folder with children, add id
                if self._file_tree.tree.has_children(_child_id):
                    _children.append(_child_id)

        # sort files and paths
        _sort_key = SORT_KEY_MAP.get(self._paths_sorted_by, self._paths_sorted_by)
        _path_dict = dict(sorted(_path_dict.items(), key=lambda item: item[1][_sort_key], reverse=self._paths_reverse))
        _sort_key = SORT_KEY_MAP.get(self._files_sorted_by, self._files_sorted_by)
        _file_dict = dict(
            sorted(_file_dict.items(), key=lambda item: item[1][self._files_sorted_by], reverse=self._files_reverse)
        )

        # render the rich tree children: process paths and files
        for _path_obj_dict in [_path_dict, _file_dict]:
            for _child_id, _pathobj_info in _path_obj_dict.items():
                _rendered_node = self._render_node(_child_id, _pathobj_info)
                _rtree_child = _rtree_parent.add(**_rendered_node)
                self._rich_tree_dict[_child_id] = _rtree_child

        # as long as there are children this method will be called
        for _child_id in _children:
            self._render_rtree(_child_id)

    def _create_rich_tree(self) -> None:
        """also allows for sorting of files"""
        self._rich_tree = self._create_rich_tree_root()
        # add the query info to the tree
        self._render_query_info(self._rich_tree)
        self._rich_tree_dict[ROOT] = self._rich_tree
        # this will recursively create all nodes in the rich tree
        # recursively create the file hierarchy
        self._render_rtree(ROOT)

    @property
    def rich_tree(self):
        """returns the rendered tree"""
        return self._rich_tree


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    # get the test folder for display
    p = str(Path(__file__).parents[2].joinpath("test_data", "test_path"))
    show_progress = True
    add_filesize = True
    file_filter = ParamsFind(p_root_paths=p, show_progress=show_progress)
    add_metadata = True
    params_file_tree = ParamsFileTreeModel(
        file_filter_params=file_filter, add_metadata=add_metadata, add_filesize=add_filesize
    )
    file_tree_renderer = FileTreeRenderer(params_file_tree, paths_sorted_by="date")
    console = Console()
    console.print(file_tree_renderer.rich_tree)
