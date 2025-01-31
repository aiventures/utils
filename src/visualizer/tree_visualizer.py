"""Visualizing Tree Class
Requirements:
* Graphivz is installed and bin path is added to PATH variable
  https://graphviz.org/download/
  If you can call dot -V in terminal you're fine ...
* Python Graphviz Module is installed
  https://pypi.org/project/graphviz/
* GraphViz SetUp
  - Shape Options
    https://graphviz.org/doc/info/attrs.html
  - Styling and Examples
    https://graphviz.readthedocs.io/en/stable/manual.html#styling

Troubleshooting:
* Updated PATH IN VSCODE might not be found, check your Application Path (echo $PATH or set PATH)
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict
from enum import StrEnum
import json
import os
import logging
import sys
from datetime import datetime as DateTime
from util.constants import DATEFORMAT_JJJJMMDDHHMMSS, DEFAULT_COLORS
from model.model_tree import TreeNodeModel, DICT_TREE_NODE_MODEL, DICT_PATH
from model.model_visualizer import DotFormat
from util.tree import Tree
from util.utils import Utils

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
DEFAULT_LOGLEVEL = int(os.environ.get("CLI_LOG_LEVEL", logging.INFO))
logger.setLevel(DEFAULT_LOGLEVEL)
DATEFORMAT_JJJJMMDDHHMMSS = "%Y%m%d_%H%M%S"


class TreeVisualizer:
    """Class to visualize Trees using Graphviz"""

    def __init__(
        self,
        root_node_id: object,
        tree_node_dict: Dict[object, TreeNodeModel],
        add_date: bool = False,
        filename: str = None,
        path: str = None,
        view: bool = True,
        max_chars: int = None,
    ):
        """constructor"""
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

        # contains compiled tree information
        self._root_node_id: object = root_node_id
        self._tree_node_dict: Dict[object, TreeNodeModel] = tree_node_dict

        # export format
        self._file_format: str = "svg"
        self._dot: Digraph = None
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
        # now traverse the items
        # TODO PRIO3 python rich progress bar for recursive functions
        self._num_nodes_processed = 0
        self._num_nodes = len(self._tree_node_dict)
        self._create_dot()
        self._add_node(self._root_node_id)
        pass

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

    def _format_label(self, dot_format: DotFormat, bold: bool = False, underline: bool = False) -> None:
        """formats the label"""
        _label = dot_format.label
        _format = any([bold, underline])
        if bold:
            _label = f"<b>{_label}</b>"
        if underline:
            _label = f"<u>{_label}</u>"
        if _format:
            _label = f"<{_label}>"
        dot_format.label = _label

    def _create_dot(self):
        """creates the Digraph model"""
        # Digraph is a directed graph
        self._dot = Digraph(engine="dot", comment="Title")
        self._dot.format = self._file_format
        # TODO clean up and put into a structure
        # global graph settings
        # rankdir only applicable to dot engine
        self._dot.attr(rankdir="TB", bgcolor="skyblue", fontname="mono")
        # Title
        self._dot.attr(
            labelloc="b", labeljust="l", label="HUGO TITLE", fontsize="12", URL="file://C:\\Program Files (x86)"
        )

        # Set background color for the
        # stagger: Stagger the minimum length of leaf edges between 1 and the specified value.
        # fanout: Enable staggering for nodes with indegree and outdegree of 1.
        # chain: Form disconnected nodes into chains of up to the specified length
        # https://graphviz.org/pdf/unflatten.1.pdf
        self._dot.unflatten(stagger=3, fanout=True, chain=20)
        # global attributes for nodes
        # font mono Cascadia Code
        self._dot.attr("node", shape="box", fontname="mono")
        # global attributes for edges
        self._dot.attr("edge", color="black", style="bold", splines="curved", penwidth="2.0", fontname="mono")

    @staticmethod
    def graphviz_id(node: TreeNodeModel, to_node: TreeNodeModel = None) -> str:
        """calculates hash from id so that you could
        get the node from the graphviz tree. Update is being done
        by creating it again
        if is edge is true it will calculate the hash from parent id as well
        """
        if to_node:
            _s = str(node.id) + str(to_node.id)
        else:
            _s = str(node.id)

        return Utils.get_hash(_s)

    def _render_node(self, tree_node: TreeNodeModel) -> DotFormat:
        """adds a node to the Digraph"""
        _id = TreeVisualizer.graphviz_id(tree_node)
        _name = tree_node.name
        # adding bold and underline style to font
        # todo put this into a default structure

        _dot_format = DotFormat(name=_id, label=_name)
        # add a tooltip with navigation path
        _obj_type = tree_node.obj_type
        _path = ""
        if _obj_type == DICT_TREE_NODE_MODEL:
            _path = "PATH " + str(getattr(tree_node.obj, DICT_PATH)) + "\n"
        _dot_format.tooltip = f"{_path}OBJECT {_name}\nTYPE [{_obj_type}]\n[{_id}]"
        return _dot_format

    def _render_parent_edge(self, from_node: TreeNodeModel, to_node: TreeNodeModel) -> DotFormat:
        """adds an edge to the Digraph"""
        # edges are specified by connecting nodes, but can have can id but not a name
        # adapt the default DotFormat / None values will be deleted later on
        _dot_format = DotFormat()
        _dot_format.id = TreeVisualizer.graphviz_id(from_node, to_node)
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

    def _add_node(self, node_id: object, parent_id: object = None) -> None:
        """recursively add nodes"""
        _parent_node = None
        if parent_id is not None:
            _parent_node = self._tree_node_dict.get(parent_id)
        _node = self._tree_node_dict.get(node_id)
        _node_graphviz_id = TreeVisualizer.graphviz_id(_node)
        _node_id = _node.id
        _node_rendering = self._render_node(_node)
        _node_dict = _node_rendering.model_dump(exclude_none=True)
        # add the node
        self._dot.node(**_node_dict)
        # add the edge to the parent
        if _parent_node:
            _parent_graphviz_id = TreeVisualizer.graphviz_id(_parent_node)

            _edge_rendering = self._render_parent_edge(from_node=_parent_node, to_node=_node)
            _edge_dict = _edge_rendering.model_dump(exclude_none=True)
            # add the edge
            self._dot.edge(tail_name=_parent_graphviz_id, head_name=_node_graphviz_id, **_edge_dict)

        for _child_node in _node.children:
            self._add_node(node_id=_child_node, parent_id=_node_id)

    def render(self) -> None:
        """renders the graph"""
        self._dot.render(Path(self._save_path), view=self._view)
        logger.info(f"[TreeVisualizer] Saved GraphViz File, path [{self._save_path}]")

    @property
    def is_executable(self):
        """returns if graphs can be drawn"""
        return self._is_executable


def main(tree: Tree):
    """do something"""
    root_id = tree.root_id
    hierarchy = tree.hierarchy
    visualizer = TreeVisualizer(root_node_id=root_id, tree_node_dict=hierarchy)
    visualizer.render()
    pass


if __name__ == "__main__":
    loglevel = DEFAULT_LOGLEVEL
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
    my_tree.create_tree(tree, name_field="value", parent_field="parent")
    main(my_tree)
