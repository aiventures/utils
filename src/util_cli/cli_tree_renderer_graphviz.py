"""rendering the Tree / FilteredTree as rich tree"""

# from pathlib import Path
import json
import logging
import os
import subprocess
import sys
from datetime import datetime as DateTime
from pathlib import Path
from typing import List

from rich.console import Console

# import typer
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_graph import GraphDictModel, GraphEdge, GraphNode
from model.model_tree import TreeNodeModel
from model.model_visualizer import (
    ColorSchemaType,
    GraphVizAttributes,
    GraphVizNode,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_LINE_COLOR,
)
from util.constants import DATEFORMAT_JJJJMMDDHHMMSS

# Filtered Tree is a subclass so this should work out of the box
from util.tree import Tree
from util.tree_iterator import TreeIterator
from util.utils import Utils
from util_cli.cli_color_schema import ColorSchema

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
        tree_name: str = "TREE",
        tree_info: str = "TREE INFO",
        max_level: int = None,
        color_schema: ColorSchemaType = None,
        reverse_col_schema: bool = False,
        info_list: List[str] = None,
        add_date: bool = False,
        filename: str = None,
        path: str = None,
        view: bool = True,
        max_chars: int = None,
        graphviz_attributes: GraphVizAttributes = None,
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
        self._tree_name = tree_name
        self._tree_info = tree_info
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
        self._default_color = {DEFAULT_LINE_COLOR: True}
        self._info_list = info_list

        # now traverse the items
        # TODO PRIO3 python rich progress bar for recursive functions
        self._num_nodes_processed = 0
        self._num_nodes = len(self._tree._hierarchy_nodes_dict)

        # setting up the DiGraph Model / with optional default
        self._graphviz_attributes = graphviz_attributes if graphviz_attributes is not None else GraphVizAttributes()
        self._dot: Digraph = None  #
        self._graphviz_root_id: str = None
        self._graphviz_dict: GraphDictModel = {}
        # dictionary that hosts
        # rendering attributes
        self._create_dot()
        # creating root id and header elements
        self._add_headers()
        # recursively create nodes
        self._create_graphviz_tree()

    def _create_dot(self):
        """creates the Digraph model"""
        # Digraph is a directed graph
        _attributes = self._graphviz_attributes
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
    def graphviz_id(node: TreeNodeModel | object, to_node: TreeNodeModel | str = None) -> str:
        """calculates hash from id so that you could
        get the node from the graphviz tree. Update is being done
        by creating it again
        if is edge is true it will calculate the hash from parent id as well
        """
        # also allow strings to be used to create graphviz ids
        _node_id = None
        if isinstance(node, TreeNodeModel):
            _node_id = node.id
            if _node_id is None:
                logger.warning(f"[TreeRendererGraphViz] no node.id for [{node}], skipping")
                return None
            _node_id = str(_node_id)
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

    def _add_to_graphviz_dict(
        self, node_id: object = None, node_to_id: object = None, graphviz_node: GraphVizNode = None
    ) -> object:
        """adds an element to the graph dict returns the node id"""
        _graph_element = None
        _node_id = node_id
        # try to get node id directly or from graphviz_format
        if _node_id is None:
            _node_id = graphviz_node.id
            if _node_id is None:
                _name = graphviz_node.name
                # recreate _node_id
                if _name is not None:
                    _node_id = TreeRendererGraphViz.graphviz_id(_name)
                    graphviz_node.id = _node_id
        if _node_id is None:
            logger.warning(f"[TreeRendererGraphViz] Object {graphviz_node} has no id")
            return

        if node_to_id is None:
            _graph_element = GraphNode()
            _graph_element.graphtype = "node"
        else:
            _graph_element = GraphEdge()
            _graph_element.graphtype = "edge"
            _graph_element.id_in = _node_id
            _graph_element.id_out = node_to_id

        _graph_element.id = graphviz_node.id
        _graph_element.name = graphviz_node.name
        _graph_element.obj = graphviz_node.label
        self._graphviz_dict[_graph_element.id] = _graph_element
        return _graph_element.id

    def instanciate_graphviz_edge(self, arrowhead: bool = True) -> GraphVizNode:
        """create a default edge graphviz_format, could also be overwritten in subclass"""
        # right now only prvide the predefined edge, can also be changed
        _graphviz_node = GraphVizNode()
        _graphviz_node.label = None  # do not show a label
        _graphviz_node.fillcolor = "black"
        # drop the arrowhead
        if arrowhead is not True:
            _graphviz_node.arrowhead = "none"
        return _graphviz_node

    # def _create_graphviz_edge_from_tree_node_ids(self, from_node: object, to_node: object) -> GraphVizNode:
    #     """creates the GraphViz Nodes using the ids from parent and child """
    #     # edges are specified by connecting nodes, but can have can id but not a name
    #     # adapt the default DotFormat / None values will be deleted later on
    #     _graphviz_node = self.instanciate_graphviz_edge()
    #     # graphviz: only nodes have an id ( hash(DotFormat.id) = GraphViz.name)
    #     _graphviz_node.id = TreeRendererGraphViz.graphviz_id(from_node, to_node)
    #     # todo PRIO2 put this into a default structure
    #     _graphviz_node.shape = None
    #     _graphviz_node.fillcolor = "black"
    #     _graphviz_node.color = "black"
    #     _graphviz_node.label = None
    #     # TODO put this into a structure
    #     _graphviz_node.fontsize = "9"
    #     _tooltip = f"{from_node.name}->{to_node.name}"
    #     _graphviz_node.tooltip = f"{_tooltip}\n[{_graphviz_node.id}]"
    #     return _graphviz_node

    def _create_graphviz_dot_edge(
        self, from_node: object, to_node: object, graphviz_edge: GraphVizNode, arrowhead: bool = True
    ) -> None:
        """adds edge to Graphviz Dot"""
        # _graphviz_edge = self.instanciate_graphviz_edge(arrowhead)
        if self._graphviz_dict.get(from_node) is None or self._graphviz_dict.get(to_node) is None:
            logger.warning(
                f"[TreeRendererGraphViz] There are no nodes from_node [{from_node}] or to_node [{to_node}] to link"
            )
            return
        # create the id
        _id = TreeRendererGraphViz.graphviz_id(from_node, to_node)
        graphviz_edge.id = _id
        graphviz_edge.name = _id
        _graphviz_node_dict = graphviz_edge.model_dump(exclude_none=True)
        self._add_to_graphviz_dict(node_id=from_node, node_to_id=to_node, graphviz_node=graphviz_edge)
        try:
            _ = _graphviz_node_dict.pop("id")
            _ = _graphviz_node_dict.pop("name")
        except KeyError:
            pass
        self._dot.edge(tail_name=from_node, head_name=to_node, **_graphviz_node_dict)

    def instanciate_graphviz_node(self, obj_id: None | TreeNodeModel | str = None, label: str = None) -> GraphVizNode:
        """create a default edge node for further refinement, could also be overwritten in subclass"""
        # create id if supplied
        _id = obj_id
        _graphviz_node = GraphVizNode()
        # adjust frame color
        _graphviz_node.color = DEFAULT_LINE_COLOR
        if _id is not None:
            _id = self.graphviz_id(_id)
            _graphviz_node.id = _id
            _graphviz_node.name = _id
        if label is None:
            _graphviz_node.label = f"NODE (LABEL NOT SET)\nObject [{str(obj_id)[:50]}...]"
        else:
            _graphviz_node.label = label
        # ... do some adjustments for a default node
        #     for now we'll leave it as it is
        return _graphviz_node

    def postprocess_graphviz_node(self, tree_node: TreeNodeModel, graphviz_node: GraphVizNode) -> GraphVizNode:
        """customization method to allow for alternative formatting"""
        _graphviz_node = graphviz_node
        # ... do adjustments in a subclass
        return _graphviz_node

    def _create_graphviz_node(self, tree_node: TreeNodeModel) -> GraphVizNode:
        """transforms tree_node info into information to be rendered
        use post_tree_node_display_info to modify the rendering output
        """
        # do a defeult implementation for rendering the node
        _graphviz_node = self.instanciate_graphviz_node(tree_node)
        _id = _graphviz_node.id
        # _id = self.graphviz_id(tree_node)
        # _graphviz_node.name = _id
        # _graphviz_node.id = _id
        _graphviz_node.displayed_text = tree_node.name
        _graphviz_node.label = _graphviz_node.displayed_text
        _tooltip = f"[{_id}]\n{_graphviz_node.displayed_text}"
        _graphviz_node.tooltip = _tooltip
        # do the color formatting based on depth level
        _color = self._color_dict.get(tree_node.level, self._default_color)
        _color, _text_invert = next(iter(_color.items()))
        _graphviz_node.text_invert_font_color = _text_invert
        if _text_invert is True:
            _graphviz_node.fontcolor = "white"
        else:
            _graphviz_node.fontcolor = "black"
        _graphviz_node.fillcolor = _color
        # node_display_info.style = self._color_styles.get(tree_node.level)
        # allow for readjustment in post processing
        _graphviz_node = self.postprocess_graphviz_node(tree_node, _graphviz_node)
        return _graphviz_node

    def _create_graphviz_node_from_tree_node(self, node_id: object) -> None:
        """creates the dot node element from a tree elements"""
        _node_info = self._tree.hierarchy[node_id]
        _parent_node_id = _node_info.parent_id
        _parent_graphviz_id = None
        try:
            _parent_node_info = self._tree.hierarchy[_parent_node_id]
            _parent_graphviz_id = self.graphviz_id(_parent_node_info.id)
        except KeyError:
            # add root element
            if _parent_node_id is None:
                _parent_graphviz_id = self._graphviz_root_id
        # gets the node in dot format
        _graphviz_node = self._create_graphviz_node(_node_info)
        self._create_graphviz_dot_node(_graphviz_node)
        # addng the node edges
        _graphviz_edge = self.instanciate_graphviz_edge()
        # change color of edge according to node level
        _edge_color_dict = self._color_dict.get(_node_info.level - 1, self._default_color)
        _edge_color = next(iter(_edge_color_dict))
        _graphviz_edge.color = _edge_color
        _graphviz_edge.fillcolor = _edge_color

        self._create_graphviz_dot_edge(
            from_node=_parent_graphviz_id, to_node=_graphviz_node.id, graphviz_edge=_graphviz_edge
        )
        # self._create_graphviz_edge_from_tree_nodes(from_node=_parent_graphviz_id, to_node=_graphviz_node.id)

    def _create_graphviz_dot_node(self, graphviz_node: GraphVizNode) -> None:
        """creates the dot node element"""
        # adds the node to the node dict
        self._add_to_graphviz_dict(graphviz_node=graphviz_node)
        # some fields need to be excluded
        _graphviz_node_dict = graphviz_node.model_dump(
            exclude_none=True, exclude=["text_invert_font_color", "text_with_background_color"]
        )
        self._dot.node(**_graphviz_node_dict)

    def _add_headers(self) -> None:
        """addding headers and element for storing information"""
        _info_list = []
        _headers = [self._tree_name]
        if self._info_list is not None:
            _info_list = self._info_list
            _headers.append(self._tree_info)
        _graphviz_nodes = []
        for _header in _headers:
            _graphviz_nodes = [self.instanciate_graphviz_node(obj_id=_h, label=_h) for _h in _headers]
        _root_node = _graphviz_nodes[0]
        _root_node.fillcolor = "slategray4"
        _root_node.color = "slategray4"
        _root_node.fontcolor = "white"
        self._create_graphviz_dot_node(_root_node)
        self._graphviz_root_id = _root_node.id
        _info_root = None
        try:
            _info_root = _graphviz_nodes[1]
            _info_root.fillcolor = "slategray2"
            _info_root.color = "slategray2"
            _info_root.fontcolor = "black"
            self._create_graphviz_dot_node(_info_root)
            _graphviz_edge = self.instanciate_graphviz_edge(arrowhead=False)
            self._create_graphviz_dot_edge(from_node=_root_node.id, to_node=_info_root.id, graphviz_edge=_graphviz_edge)
        # self._add_graphviz_edge(from_node=:)
        except IndexError:
            pass

        # adding the headers
        for _info in _info_list:
            _info_node = self.instanciate_graphviz_node(obj_id=_info, label=_info)
            _info_node.shape = "none"
            _info_node.fillcolor = "none"
            self._create_graphviz_dot_node(_info_node)
            _graphviz_edge = self.instanciate_graphviz_edge(arrowhead=False)
            self._create_graphviz_dot_edge(from_node=_info_root.id, to_node=_info_node.id, graphviz_edge=_graphviz_edge)

    def _create_graphviz_tree(self) -> None:
        """Creates the tree"""
        _tree_iterator = TreeIterator(self._tree)
        _finished = False
        while not _finished:
            try:
                _node_id = next(_tree_iterator)
                self._create_graphviz_node_from_tree_node(_node_id)
            except StopIteration:
                _finished = True

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

    def _set_color_schema(self, color_schema: ColorSchemaType = None, reverse_col_schema: bool = False):
        """setting colors and color schema"""
        _schema: ColorSchemaType = "pastel2" if color_schema is None else color_schema

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

    def render(self) -> None:
        """renders the graph"""
        self._dot.render(Path(self._save_path), view=self._view)
        logger.info(f"[TreeVisualizer] Saved GraphViz File, path [{self._save_path}]")

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
