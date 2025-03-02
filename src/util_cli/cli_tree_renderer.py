"""rendering the Tree / FilteredTree as rich tree"""

# from pathlib import Path
from pathlib import Path
import logging
import sys

from rich.tree import Tree as RichTree
from rich.text import Text
from rich.style import Style
from rich.emoji import Emoji as RichEmoji
from rich.console import Console
from typing import List, Dict
from urllib.parse import quote as urlquote

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_tree import TreeNodeModel
from model.model_visualizer import ColorSchemaType, RichNodeDisplayInfo
from util_cli.cli_color_schema import ColorSchema

# Filtered Tree is a subclass so this should work out of the box
from util.tree import Tree
from util.utils import Utils

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

GUIDE_STYLE_DEFAULT = "bold bright_black"
STYLE_DEFAULT = "black"
STYLE_HEADER = "deep_sky_blue1"


class TreeRenderer:
    """render a tree"""

    # TODO SAVE THE TREE as HTML File

    # TODO move params to a pydantic structure
    def __init__(
        self,
        tree: Tree,
        max_level: int = None,
        color_schema: ColorSchemaType = None,
        reverse_col_schema: bool = False,
        header_list: List[str] = None,
        default_color: str = None,
        default_guide_color: str = None,
    ):
        self._tree: Tree = tree
        self._max_level = None
        self._set_max_level(max_level)
        self._color_schema: ColorSchema = None
        self._color_dict: dict = {}
        self._color_styles: Dict[object, Style] = {}
        self._set_color_schema(color_schema, reverse_col_schema)
        self._rich_tree = None
        # rich tree refs
        self._rich_tree_dict: Dict[str, RichTree] = {}
        self._rich_tree = None
        self._header_list = header_list
        self._default_color = {"white": False}
        if default_color is not None:
            self._default_color = {default_color: False}
        # TODO PRIO3 Replace by using style
        self._default_style_color = STYLE_DEFAULT
        self._default_guide_color = GUIDE_STYLE_DEFAULT
        if default_guide_color is not None:
            self._default_guide_color = default_guide_color
        # create rich styles
        self._create_rich_tree()

    def _set_color_schema(self, color_schema: ColorSchemaType = None, reverse_col_schema: bool = False):
        """setting colors and color schema"""
        _schema: ColorSchemaType = "spectral" if color_schema is None else color_schema

        self._color_schema = ColorSchema(_schema, reverse_schema=reverse_col_schema)
        # we need to add +1 due to adding level zero to depth of tree
        _colors, _invert_font_color = self._color_schema.colors(num_colors=self._max_level + 1)
        # setting the color dct and the rich color styles
        for _index, _color in enumerate(_colors):
            self._color_dict[_index] = {_color: _invert_font_color[_index]}
            # setting default styles
            self._color_styles[_index] = Style(color=_color, bgcolor=None, bold=False, link=None)
        self._color_schema.colors(num_colors=self._color_schema.num_colors)

    def _set_max_level(self, max_level: int = None) -> None:
        """sets the max depth level for coloring"""
        # max num of levels to render names
        _max_level = max_level
        if _max_level is None:
            _max_level = self._tree.max_level
        if max_level is None:
            _max_level = 4
        self._max_level = _max_level
        logger.debug(f"[TreeRenderer] max levels set to [{self._max_level}]")

    def _render_root_node(self, rtree: RichTree) -> RichTree:
        """renders the root node element"""
        _root_id = self._tree.root_id
        root_node_info = self._tree.get_node(_root_id)
        _node_formatted = self._get_tree_node_display_info(root_node_info)
        self._render_node(node_id=_root_id, node_formatted=_node_formatted, rich_tree_parent=rtree)
        return self._rich_tree_dict[_root_id]

    def _create_rich_tree(self) -> None:
        """also allows for sorting of files"""
        self._rich_tree = self._create_rich_tree_root()
        # add the query info to the tree
        self._render_header(self._rich_tree)
        # create the root node of the tree
        _rich_tree_root = self._render_root_node(self._rich_tree)
        # starting with root id
        # this will recursively create all nodes in the rich tree
        # recursively create the file hierarchy
        self._render_rtree(self._tree.root_id)
        pass

    def _create_rich_tree_root(self) -> RichTree:
        """creates the richt tree node"""
        return RichTree(
            f"[{GUIDE_STYLE_DEFAULT}]TREE VIEW",
            guide_style=GUIDE_STYLE_DEFAULT,
        )

    def _render_header(self, rich_tree_root: RichTree) -> None:
        """renders header information"""
        if not isinstance(self._header_list, list):
            return
        _header_title = RichEmoji.replace(f"[{STYLE_HEADER}]:magnifying_glass_tilted_right: TREE INFO")
        _header_richtree_root = rich_tree_root.add(_header_title, guide_style=STYLE_HEADER, style=STYLE_HEADER)
        for _header_item in self._header_list:
            _header_richtree_root.add(_header_item)

    def post_get_tree_node_display_info(
        self, tree_node: TreeNodeModel, node_formatted: RichNodeDisplayInfo
    ) -> RichNodeDisplayInfo:
        """customization method to allow for alternative formatting, setting emojis etc"""
        _node_formatted = node_formatted
        return _node_formatted

    def _get_tree_node_display_info(self, tree_node: TreeNodeModel) -> RichNodeDisplayInfo:
        """transforms tree_node info into information to be rendered
        use post_get_tree_node_display_info to modify the rendering output

        """
        node_display_info = RichNodeDisplayInfo()
        node_display_info.name = tree_node.name
        node_display_info.id = tree_node.id
        # default text color (= mapping of tree depth)
        _color = self._color_dict.get(tree_node.level, self._default_color)
        _color, _text_invert = next(iter(_color.items()))
        node_display_info.textcolor = _color
        node_display_info.text_invert_font_color = _text_invert
        node_display_info.style = self._color_styles.get(tree_node.level)
        # style guide color (aligned with text color)
        node_display_info.guidecolor = _color
        # default: set name as default text, may be overwritten
        node_display_info.displayed_text = tree_node.name
        node_display_info.link = None
        # unclear whether we have this in Rich ...
        node_display_info.tooltip = "this is a dummy tooltip"
        # allow for adjustment of rendering information
        node_display_info = self.post_get_tree_node_display_info(tree_node, node_display_info)

        # tree_node.level
        return node_display_info

    def _style_from_formatted_node(self, node_formatted: RichNodeDisplayInfo, link: str = None) -> Style:
        """Returns Style from node format"""
        # node_formatted.textcolor
        _color = node_formatted.textcolor
        _bg_color = None
        if node_formatted.text_with_background_color:
            _color = "white"
            if node_formatted.text_invert_font_color:
                _color = "black"
            _bg_color = node_formatted.textcolor
            if node_formatted.bgcolor is not None:
                _bg_color = node_formatted.bgcolor
        return Style(color=_color, bgcolor=_color, link=link)

    def _render_label(self, node_formatted: RichNodeDisplayInfo) -> Text:
        """rendering the text of displayed node, returns tuple of label as Text and style"""
        # first, get the text
        label_text = node_formatted.displayed_text
        # fallback, use name as display test
        if node_formatted.displayed_text is None:
            label_text = node_formatted.name
        # get emoji
        emoji = node_formatted.emoji
        if emoji:
            emoji = emoji.replace(emoji) + " "
        else:
            emoji = ""

        _link = node_formatted.link
        # get a formatted link
        if isinstance(_link, Path):
            _link = str(_link)
        if _link:
            # try to convert into a file path
            if not _link.startswith("http"):
                _link = Utils.get_unspaced_path(_link, is_link=True)
            else:
                # parse spaces
                if " " in _link:
                    _link = urlquote(_link)

        # do the formatting
        style = node_formatted.style
        if style is None:
            style = self._style_from_formatted_node(node_formatted, _link)
        if _link:
            style = style.update_link(link=_link)

        label = Text(emoji) + Text(label_text, style=style)

        return label

    def _render_node(self, node_id: object, node_formatted: RichNodeDisplayInfo, rich_tree_parent: RichTree) -> None:
        """renders the format into rich format"""

        _label = self._render_label(node_formatted)
        _color = node_formatted.textcolor
        _rtree_child = rich_tree_parent.add(label=_label, guide_style=_color)
        self._rich_tree_dict[node_id] = _rtree_child
        pass

    def _render_rtree(self, node_id: str) -> List[str] | None:
        """renders a node in the rich tree"""
        # get the rich parent element so it can be assigned
        _rtree_parent = self._rich_tree_dict.get(node_id)
        _child_ids = self._tree.get_children(node_id)
        _child_dict = {}

        for _child_id in _child_ids:
            _child_info = self._tree.get_node(_child_id)
            if not _child_info:
                logger.warning(f"[TreeRenderer] Node {node_id} has no metadata")
                continue
            # store this in a dict, so there's the possibility to sort it later on
            # example: util_cli.cli_filetree_renderer.FileTreeRenderer _render_rtree
            _child_dict[_child_id] = _child_info

        # this is how to sort a dictionary
        # _child_dict = dict(sorted(_path_dict.items(), key=lambda item: item[1][_sort_key],
        # reverse=self._paths_reverse))
        _children = []
        for _child_id, _node_info in _child_dict.items():
            _children.append(_child_id)
            _node_formatted = self._get_tree_node_display_info(_node_info)
            self._render_node(node_id=_child_id, node_formatted=_node_formatted, rich_tree_parent=_rtree_parent)

        # as long as there are children this method will be called
        for _child_id in _children:
            self._render_rtree(_child_id)

    @property
    def rich_tree(self):
        """returns the rendered tree"""
        return self._rich_tree

    def show_info(self, console: Console):
        """shows info on the tree"""
        console.print("[sky_blue1]### SHOW INFO")
        console.print("[green]### Tree Level Coloring")
        for _num, _col_info in self._color_dict.items():
            _color, _invert = next(iter(_col_info.items()))
            console.print(f"[{_color}]    Level {_num}, code {_color}, invert text {_invert} [/]")
        pass
        print("")


def main(tree: Tree):
    """showcasing this module"""
    _headers = ["aa", "bb", "ccc"]
    _tree_renderer = TreeRenderer(tree, header_list=_headers)
    _console = Console()
    _tree_renderer.show_info(_console)
    # output the dict tree
    _console.print(_tree_renderer.rich_tree)
    pass


if __name__ == "__main__":
    loglevel = CLI_LOG_LEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1
    # +---2
    # |   +---4
    # |   +---5
    # |
    # +---3
    #     +---6
    #         +---7
    #         +---8
    #             +---[10]
    #             +---[11]
    #         +---9

    tree = {
        1: {"parent": None, "value": "value 1", "object": "OBJ1"},
        2: {"parent": 1, "value": "value 2", "object": "OBJ2"},
        4: {"parent": 2, "value": "value 4", "object": "OBJ4"},
        5: {"parent": 2, "value": "value 5", "object": "OBJ5"},
        3: {"parent": 1, "value": "value 3", "object": "OBJ3"},
        6: {"parent": 3, "value": "value 6", "object": "OBJ6"},
        7: {"parent": 6, "value": "value 7", "object": "OBJ7"},
        8: {"parent": 6, "value": "value 8", "object": "OBJ8"},
        9: {"parent": 6, "value": "value 9", "object": "OBJ9"},
        10: {"parent": 8, "value": "value 10", "object": "OBJ10"},
        11: {"parent": 8, "value": "value 11", "object": "OBJ11"},
    }
    my_tree = Tree()

    my_tree.create_tree(tree, name_field="value", parent_field="parent", analyze_fields=True)
    main(my_tree)
