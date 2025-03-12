"""rendering the Tree / FilteredTree as rich tree"""

# from pathlib import Path
import json
from pathlib import Path
import logging
import sys
import os
import subprocess
from datetime import datetime as DateTime

from typing import List
from rich.console import Console

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_tree import TreeNodeModel
from model.model_graph import GraphDictModel, GraphEdge, GraphNode
from model.model_visualizer import ColorSchemaType
from model.model_visualizer import (
    DotFormat,
    DotAttributes,
)
from util.constants import DATEFORMAT_JJJJMMDDHHMMSS
from util.utils import Utils
from util_cli.cli_color_schema import ColorSchema

# Filtered Tree is a subclass so this should work out of the box
from util.tree import Tree

# Design Decision: You need to manually install GRAPHVIZ into your environment
PY_GRAPHVIZ_INSTALLED = True
try:
    from graphviz import Digraph
except ImportError:
    PY_GRAPHVIZ_INSTALLED = False

PY_YAML_INSTALLED = True
try:
    import yaml
except ImportError:
    PY_YAML_INSTALLED = False

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

DATEFORMAT_JJJJMMDDHHMMSS = "%Y%m%d_%H%M%S"

# GUIDE_STYLE_DEFAULT = "bold bright_black"
# STYLE_DEFAULT = "black"
# STYLE_HEADER = "deep_sky_blue1"


class TreeRendererGraphViz:
    """render a tree"""

    # TODO SAVE THE TREE as HTML File
    # TODO move params to a pydantic structure
    def __init__(
        self,
        tree: Tree,
        max_level: int = None,
        color_schema: ColorSchemaType = None,
        reverse_col_schema: bool = False,
        info_list: List[str] = None,
        add_date: bool = False,
        filename: str = None,
        path: str = None,
        view: bool = True,
        max_chars: int = None,
        dot_attributes: DotAttributes = None,
    ):
        # graphviz needs to be in path
        self._is_executable = self._check_graphviz_executable()
        if self._is_executable is False:
            return
        # graphviz python lib needs to be installed
        if PY_GRAPHVIZ_INSTALLED is False:
            logger.warning(
                "[AstVisualizer] GRAPHVIZ PYTHON LIB IS NOT INSTALLED, INSTALL GRAPHVIZ https://pypi.org/project/graphviz"
            )
            self._is_executable = False
            return

        self._tree: Tree = tree

        # save options
        # adding date to file name
        self._add_date: bool = add_date
        self._filename: str = filename
        self._path: str = path
        self._save_path: str = None
        self._view: bool = view
        self._set_save_path()
        self._in_file: str = None
        self._in_filetype: str = None
        # max num of chars to display
        self._max_chars: int = max_chars

        self._max_level = None
        self._set_max_level(max_level)
        self._color_schema: ColorSchema = None
        self._color_dict: dict = {}
        self._set_color_schema(color_schema, reverse_col_schema)
        #         self._rich_tree = None
        #         # rich tree refs
        #         self._rich_tree_dict: Dict[str, RichTree] = {}
        #         self._rich_tree = None
        self._info_list = info_list

        # now traverse the items
        # TODO PRIO3 python rich progress bar for recursive functions
        self._num_nodes_processed = 0
        self._num_nodes = len(self._tree._hierarchy_nodes_dict)

        # setting up the DiGraph Model / with optional default
        self._dot_attributes = dot_attributes if dot_attributes is not None else DotAttributes()
        self._dot: Digraph = None  #
        self._dot_root_id: str = None
        self._graph_dict: GraphDictModel = {}
        # dictionary that hosts
        # rendering attributes
        self._create_dot()
        # creating root id and header elements
        self._add_headers()
        # recursively create nodes

        # self._create_dot()
        # self._add_node(self._root_node_id)

    #         self._default_color = {"white": False}
    #         if default_color is not None:
    #             self._default_color = {default_color: False}
    #         # TODO PRIO3 Replace by using style
    #         self._default_style_color = STYLE_DEFAULT
    #         self._default_guide_color = GUIDE_STYLE_DEFAULT
    #         if default_guide_color is not None:
    #             self._default_guide_color = default_guide_color
    #         # create rich styles
    #         self._create_rich_tree()

    def _create_dot(self):
        """creates the Digraph model"""
        # Digraph is a directed graph
        _attributes = self._dot_attributes
        self._dot = Digraph(engine=_attributes.engine, comment=_attributes.comment, format=_attributes.format)
        # global graph settings
        self._dot.attr(
            rankdir=_attributes.rankdir,
            bgcolor=_attributes.bgcolor,
            labelloc=_attributes.labelloc,
            labeljust=_attributes.labeljust,
            label=_attributes.label,
            fontname=_attributes.fontname,
            fontsize=_attributes.fontsize,
            URL=_attributes.URL,
        )
        # stagger: Stagger the minimum length of leaf edges between 1 and the specified value.
        # fanout: Enable staggering for nodes with indegree and outdegree of 1.
        # chain: Form disconnected nodes into chains of up to the specified length
        # https://graphviz.org/pdf/unflatten.1.pdf
        self._dot.unflatten(stagger=_attributes.stagger, fanout=_attributes.fanout, chain=_attributes.chain)
        # global attributes for nodes
        # font mono Cascadia Code
        self._dot.attr("node", shape=_attributes.node_shape, fontname=_attributes.node_fontname)
        # global attributes for edges
        self._dot.attr(
            "edge",
            color=_attributes.edge_color,
            style=_attributes.edge_style,
            splines=_attributes.edge_splines,
            penwidth=_attributes.edge_penwidth,
            fontname=_attributes.edge_fontname,
        )

    @staticmethod
    def graphviz_id(node: TreeNodeModel | str, to_node: TreeNodeModel | str = None) -> str:
        """calculates hash from id so that you could
        get the node from the graphviz tree. Update is being done
        by creating it again
        if is edge is true it will calculate the hash from parent id as well
        """
        # also allow strings to be used to create graphviz ids
        _node_id = None
        if isinstance(node, TreeNodeModel):
            _node_id = str(node.id)
        else:
            _node_id = str(node)

        if to_node is not None:
            _to_node_id = None
            if isinstance(to_node, TreeNodeModel):
                _to_node_id = str(to_node.id)
            else:
                _to_node_id = str(to_node)
            _s = _node_id + _to_node_id
        else:
            _s = _node_id

        return Utils.get_hash(_s)

    def _create_dot_format_edge(self) -> DotFormat:
        """create a default edge dot_format"""
        # right now only prvide the predefined edge, can also be changed
        _dot_format = DotFormat()
        _dot_format.label = None
        _dot_format.fillcolor = "black"
        return _dot_format

    def _render_edge(self, from_node: TreeNodeModel, to_node: TreeNodeModel) -> DotFormat:
        """adds an edge to the Digraph"""
        # edges are specified by connecting nodes, but can have can id but not a name
        # adapt the default DotFormat / None values will be deleted later on
        _dot_format = DotFormat()
        # graphviz: only nodes have an id ( hash(DotFormat.id) = GraphViz.name)
        _dot_format.id = TreeRendererGraphViz.graphviz_id(from_node, to_node)
        # todo PRIO2 put this into a default structure
        _dot_format.shape = None
        _dot_format.fillcolor = "black"
        _dot_format.color = "black"
        _dot_format.label = None
        # TODO put this into a structure
        _dot_format.fontsize = "9"
        _tooltip = f"{from_node.name}->{to_node.name}"
        _dot_format.tooltip = f"{_tooltip}\n[{_dot_format.id}]"

        return _dot_format

    def _add_graph_element(
        self, node_id: object = None, node_to_id: object = None, dot_format: DotFormat = None
    ) -> None:
        """adds an element to the graph dict"""
        _graph_element = None
        _node_id = node_id
        # try to get node id directly or from dot_format
        if _node_id is None:
            _node_id = dot_format.id
            if _node_id is None:
                _name = dot_format.name
                # recreate _node_id
                if _name is not None:
                    _node_id = TreeRendererGraphViz.graphviz_id(_name)
                    dot_format.id = _node_id
        if _node_id is None:
            logger.warning(f"[TreeRendererGraphViz] Object {dot_format} has no id")
            return

        if node_to_id is None:
            _graph_element = GraphNode()
            _graph_element.graphtype = "node"
        else:
            _graph_element = GraphEdge()
            _graph_element.graphtype = "edge"
            _graph_element.id_in = _node_id
            _graph_element.id_out = node_to_id

        _graph_element.id = dot_format.id
        _graph_element.name = dot_format.name
        _graph_element.obj = dot_format.label
        self._graph_dict[_graph_element.id] = _graph_element

    def _add_graphviz_node(self, dot_format: DotFormat) -> object:
        """adds node to Graphviz dot returns the node id"""
        # unique id to be found in name attribute
        _id = dot_format.id
        if _id is None:
            # create id from label
            _id = TreeRendererGraphViz.graphviz_id(str(dot_format.label))
            dot_format.id = _id
        # name is used as id in Graphviz / label is used for display
        dot_format.name = _id
        _node_dict = dot_format.model_dump(exclude_none=True)
        self._add_graph_element(dot_format=dot_format)
        self._dot.node(**_node_dict)
        return _id

    def _add_graphviz_edge(self, from_node: object, to_node: object, dot_format: DotFormat) -> None:
        """adds edge to Graphviz Dot"""
        if self._graph_dict.get(from_node) is None or self._graph_dict.get(to_node) is None:
            logger.warning(
                f"[TreeRendererGraphViz] There are no nodes from_node [{from_node}] or to_node [{to_node}] to link"
            )
            return
        # create the id
        _id = TreeRendererGraphViz.graphviz_id(from_node, to_node)
        dot_format.id = _id
        _dot_dict = dot_format.model_dump(exclude_none=True)
        self._add_graph_element(node_id=from_node, node_to_id=to_node, dot_format=dot_format)
        try:
            _ = _dot_dict.pop("id")
            _ = _dot_dict.pop("name")
        except KeyError:
            pass
        self._dot.edge(tail_name=from_node, head_name=to_node, **_dot_dict)

    def _add_headers(self) -> None:
        """addding headers"""
        _headers = ["ROOT"]
        if self._info_list is not None:
            _headers.append("INFORMATION")
        _dot_formats = [DotFormat(label=_header) for _header in _headers]
        # TODO modify Dot Formats
        _ids = [self._add_graphviz_node(_dot_format) for _dot_format in _dot_formats]
        # formatting

        # adding the root id
        self._dot_root_id = _ids[0]
        _header_id = None
        _dot_edge = None
        try:
            _header_id = _ids[1]
            # add relation root to header
            _dot_edge = self._create_dot_format_edge()
            self._add_graphviz_edge(from_node=self._dot_root_id, to_node=_header_id, dot_format=_dot_edge)
        except IndexError:
            pass

        # add supplementary information to info
        for _info in self._info_list:
            _dot_format = DotFormat(label=_info)
            # add node and edge
            _id = self._add_graphviz_node(_dot_format)
            self._add_graphviz_edge(from_node=_header_id, to_node=_id, dot_format=_dot_edge)

    def run_cmd(self, _cmd):
        """runs os command"""
        proc = subprocess.Popen(
            _cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True
        )
        std_out, std_err = proc.communicate()
        return proc.returncode, std_out, std_err

    def _check_graphviz_executable(self) -> bool:
        """checks if graphviz is executable"""
        is_executable = True
        _cmd = ["dot", "-V"]
        # _cmd = ["which", "dot"]
        _code, _, _info = self.run_cmd(_cmd)
        if _code == 0:
            logger.info(f"[AstVisualizer] GRAPHVIZ FOUND: [{_info}]")
        else:
            logger.warning(f"[AstVisualizer] GRAPHVIZ NOT FOUND, code [{_code}] ({_info})")
            is_executable = False
        return is_executable

    def _check_graphviz_executable(self) -> bool:
        """checks if graphviz is executable"""
        is_executable = True
        _cmd = ["dot", "-V"]
        # _cmd = ["which", "dot"]
        _code, _, _info = self.run_cmd(_cmd)
        if _code == 0:
            logger.info(f"[AstVisualizer] GRAPHVIZ FOUND: [{_info}]")
        else:
            logger.warning(f"[AstVisualizer] GRAPHVIZ NOT FOUND, code [{_code}] ({_info})")
            is_executable = False
        return is_executable

    def _set_save_path(self) -> None:
        """setting the save path"""
        if self._path is None or not os.path.isdir(self._path):
            self._path = os.getcwd()
        if self._filename is None:
            self._filename = "graphviz"
        if self._add_date:
            _date_s = DateTime.now().strftime(DATEFORMAT_JJJJMMDDHHMMSS)
            self._filename = f"{_date_s}_{self._filename}"
        self._save_path = os.path.join(self._path, self._filename)

    def _load_yaml(self, f: str) -> dict:
        """loads the yaml"""
        if PY_YAML_INSTALLED is False:
            logger.error("[TreeVisualizer] pyYAML is not installed, will return empty dict")
            return {"ERROR": "NO_PYYAML_INSTALLED"}
        with open(f, "r", encoding="UTF-8") as _f:
            _dict = yaml.safe_load(_f)
        return _dict

    def _load_json(self, f: str) -> dict:
        """loads the json"""
        with open("data.json", "r", encoding="UTF-8") as f:
            _dict = json.load(f)
        return _dict

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
            # self._color_styles[_index] = Style(color=_color, bgcolor=None, bold=False, link=None)
        _ = self._color_schema.colors(num_colors=self._color_schema.num_colors)

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

    @property
    def is_executable(self):
        """returns if graphs can be drawn"""
        return self._is_executable

    #     def _render_root_node(self, rtree: RichTree) -> RichTree:
    #         """renders the root node element"""
    #         _root_id = self._tree.root_id
    #         root_node_info = self._tree.get_node(_root_id)
    #         _node_formatted = self._get_tree_node_display_info(root_node_info)
    #         self._render_node(node_id=_root_id, node_formatted=_node_formatted, rich_tree_parent=rtree)
    #         return self._rich_tree_dict[_root_id]

    #     def _create_rich_tree(self) -> None:
    #         """also allows for sorting of files"""
    #         self._rich_tree = self._create_rich_tree_root()
    #         # add the query info to the tree
    #         self._render_header(self._rich_tree)
    #         # create the root node of the tree
    #         _rich_tree_root = self._render_root_node(self._rich_tree)
    #         # starting with root id
    #         # this will recursively create all nodes in the rich tree
    #         # recursively create the file hierarchy
    #         self._render_rtree(self._tree.root_id)
    #         pass

    #     def _create_rich_tree_root(self) -> RichTree:
    #         """creates the richt tree node"""
    #         return RichTree(
    #             f"[{GUIDE_STYLE_DEFAULT}]TREE VIEW",
    #             guide_style=GUIDE_STYLE_DEFAULT,
    #         )

    #     def _render_header(self, rich_tree_root: RichTree) -> None:
    #         """renders header information"""
    #         if not isinstance(self._header_list, list):
    #             return
    #         _header_title = RichEmoji.replace(f"[{STYLE_HEADER}]:magnifying_glass_tilted_right: TREE INFO")
    #         _header_richtree_root = rich_tree_root.add(_header_title, guide_style=STYLE_HEADER, style=STYLE_HEADER)
    #         for _header_item in self._header_list:
    #             _header_richtree_root.add(_header_item)

    #     def post_get_tree_node_display_info(
    #         self, tree_node: TreeNodeModel, node_formatted: RichNodeDisplayInfo
    #     ) -> RichNodeDisplayInfo:
    #         """customization method to allow for alternative formatting, setting emojis etc"""
    #         _node_formatted = node_formatted
    #         return _node_formatted

    #     def _get_tree_node_display_info(self, tree_node: TreeNodeModel) -> RichNodeDisplayInfo:
    #         """transforms tree_node info into information to be rendered
    #         use post_get_tree_node_display_info to modify the rendering output

    #         """
    #         node_display_info = RichNodeDisplayInfo()
    #         node_display_info.name = tree_node.name
    #         node_display_info.id = tree_node.id
    #         # default text color (= mapping of tree depth)
    #         _color = self._color_dict.get(tree_node.level, self._default_color)
    #         _color, _text_invert = next(iter(_color.items()))
    #         node_display_info.textcolor = _color
    #         node_display_info.text_invert_font_color = _text_invert
    #         node_display_info.style = self._color_styles.get(tree_node.level)
    #         # style guide color (aligned with text color) / look better if this is set to color of children
    #         _guide_color = self._color_dict.get(tree_node.level + 1, self._default_color)
    #         node_display_info.guidecolor = next(iter(_guide_color))
    #         # default: set name as default text, may be overwritten
    #         node_display_info.displayed_text = tree_node.name
    #         node_display_info.link = None
    #         # unclear whether we have this in Rich ...
    #         node_display_info.tooltip = "this is a dummy tooltip"
    #         # allow for adjustment of rendering information
    #         node_display_info = self.post_get_tree_node_display_info(tree_node, node_display_info)

    #         # tree_node.level
    #         return node_display_info

    #     def _style_from_formatted_node(self, node_formatted: RichNodeDisplayInfo, link: str = None) -> Style:
    #         """Returns Style from node format"""
    #         # node_formatted.textcolor
    #         _color = node_formatted.textcolor
    #         _bg_color = None
    #         if node_formatted.text_with_background_color:
    #             _color = "white"
    #             if node_formatted.text_invert_font_color:
    #                 _color = "black"
    #             _bg_color = node_formatted.textcolor
    #             if node_formatted.bgcolor is not None:
    #                 _bg_color = node_formatted.bgcolor
    #         return Style(color=_color, bgcolor=_color, link=link)

    #     def _render_label(self, node_formatted: RichNodeDisplayInfo) -> Text:
    #         """rendering the text of displayed node, returns tuple of label as Text and style"""
    #         # first, get the text
    #         label_text = node_formatted.displayed_text
    #         # fallback, use name as display test
    #         if node_formatted.displayed_text is None:
    #             label_text = node_formatted.name
    #         # get emoji
    #         emoji = node_formatted.emoji
    #         if emoji:
    #             emoji = emoji.replace(emoji) + " "
    #         else:
    #             emoji = ""

    #         _link = node_formatted.link
    #         # get a formatted link
    #         if isinstance(_link, Path):
    #             _link = str(_link)
    #         if _link:
    #             # try to convert into a file path
    #             if not _link.startswith("http"):
    #                 _link = Utils.get_unspaced_path(_link, is_link=True)
    #             else:
    #                 # parse spaces
    #                 if " " in _link:
    #                     _link = urlquote(_link)
    #         # do the formatting
    #         style = node_formatted.style
    #         if style is None:
    #             style = self._style_from_formatted_node(node_formatted, _link)
    #         if _link:
    #             style = style.update_link(link=_link)
    #         label = Text(emoji) + Text(label_text, style=style)
    #         return label
    #     def _render_node(self, node_id: object, node_formatted: RichNodeDisplayInfo, rich_tree_parent: RichTree) -> None:
    #         """renders the format into rich format"""

    #         _label = self._render_label(node_formatted)
    #         _rtree_child = rich_tree_parent.add(label=_label, guide_style=node_formatted.guidecolor)
    #         self._rich_tree_dict[node_id] = _rtree_child
    #         pass

    #     def _render_rtree(self, node_id: str) -> List[str] | None:
    #         """renders a node in the rich tree"""
    #         # get the rich parent element so it can be assigned
    #         _rtree_parent = self._rich_tree_dict.get(node_id)
    #         _child_ids = self._tree.get_children(node_id)
    #         _child_dict = {}

    #         for _child_id in _child_ids:
    #             _child_info = self._tree.get_node(_child_id)
    #             if not _child_info:
    #                 logger.warning(f"[TreeRenderer] Node {node_id} has no metadata")
    #                 continue
    #             # store this in a dict, so there's the possibility to sort it later on
    #             # example: util_cli.cli_filetree_renderer.FileTreeRenderer _render_rtree
    #             _child_dict[_child_id] = _child_info

    #         # this is how to sort a dictionary
    #         # _child_dict = dict(sorted(_path_dict.items(), key=lambda item: item[1][_sort_key],
    #         # reverse=self._paths_reverse))
    #         _children = []
    #         for _child_id, _node_info in _child_dict.items():
    #             _children.append(_child_id)
    #             _node_formatted = self._get_tree_node_display_info(_node_info)
    #             self._render_node(node_id=_child_id, node_formatted=_node_formatted, rich_tree_parent=_rtree_parent)

    #         # as long as there are children this method will be called
    #         for _child_id in _children:
    #             self._render_rtree(_child_id)

    def render(self) -> None:
        """renders the graph"""
        self._dot.render(Path(self._save_path), view=self._view)
        logger.info(f"[TreeVisualizer] Saved GraphViz File, path [{self._save_path}]")

    def _create_dot_tree(self) -> None:
        """Creates the tree"""

        pass

        # self._rich_tree = self._create_rich_tree_root()
        # # add the query info to the tree
        # self._render_header(self._rich_tree)
        # # create the root node of the tree
        # _rich_tree_root = self._render_root_node(self._rich_tree)
        # # starting with root id
        # # this will recursively create all nodes in the rich tree
        # # recursively create the file hierarchy
        # self._render_rtree(self._tree.root_id)

    def show_info(self):
        """shows info on the tree"""
        _console = Console()
        _console.print("[sky_blue1]### SHOW INFO")
        _console.print("[green]### Tree Level Coloring")
        for _num, _col_info in self._color_dict.items():
            _color, _invert = next(iter(_col_info.items()))
            _console.print(f"[{_color}]    Level {_num}, code {_color}, invert text {_invert} [/]")
        print("")


def main(tree: Tree):
    """showcasing this module"""
    _headers = ["aa", "bb", "ccc"]
    # _headers = None
    # basic call: in case nothing furher is specified, name field will be rendered
    _tree_renderer = TreeRendererGraphViz(tree, info_list=_headers)
    _tree_renderer.show_info()
    _tree_renderer.render()
    # output the dict tree
    # _console.print(_tree_renderer.rich_tree)
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
