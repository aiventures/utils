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
from model.model_tree import TreeNodeModel
from model.model_rendering import DotFormat
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
            logger.error("[AstVisualizer] pyYAML is not installed, will return empty dict")
            return {"ERROR": "NO_PYYAML_INSTALLED"}
        with open(f, "r", encoding="UTF-8") as _f:
            _dict = yaml.safe_load(_f)
        return _dict

    def _load_json(self, f: str) -> dict:
        """loads the json"""
        with open("data.json", "r", encoding="UTF-8") as f:
            _dict = json.load(f)
        return _dict

    def _create_dot(self):
        """creates the Digraph model"""
        # Digraph is a directed graph
        self._dot = Digraph(engine="dot")
        self._dot.format = self._file_format
        # global graph settings
        # rankdir only applicable to dot engine
        self._dot.attr(rankdir="LR")
        # stagger: Stagger the minimum length of leaf edges between 1 and the specified value.
        # fanout: Enable staggering for nodes with indegree and outdegree of 1.
        # chain: Form disconnected nodes into chains of up to the specified length
        # https://graphviz.org/pdf/unflatten.1.pdf
        self._dot.unflatten(stagger=3, fanout=True, chain=20)
        # global attributes for nodes
        self._dot.attr("node", shape="box", fontname="Monospace")
        # global attributes for edges
        self._dot.attr("edge", color="black", style="bold", splines="curved", penwidth="2.0")

    def render(self) -> None:
        """render the output tree"""
        self._dot.render(Path(self._save_path), view=self._view)
        logger.info(f"[AstVisualizer] Saved GraphViz File, path [{self._save_path}]")

    def _render_node(self, tree_node: TreeNodeModel) -> dict:
        """adds a node to the Digraph"""

        # model = MyModel(field1="value", field2=None, field3="another value")
        # cleaned_dict = model.dict(exclude_none=True)
        # print(cleaned_dict)

        return {}

    def _render_edge(self, from_node: TreeNodeModel, to_node: TreeNodeModel) -> dict:
        """adds an edge to the Digraph"""
        return {}

    def _add_node(self, node_id: object, parent_id: object = None) -> None:
        """recursively add nodes"""
        _parent_node = None
        if parent_id:
            _parent_node = self._tree_node_dict.get(parent_id)
        _node = self._tree_node_dict.get(node_id)
        _node_id = _node.id
        _node_rendering = self._render_node(_node)
        # add the node
        self._dot.node(**_node_rendering)
        # add the edge to the parent
        if _parent_node:
            _edge_rendering = self._render_edge(from_node=_parent_node, to_node=_node)
            # add the edge
            self._dot.edge(**_edge_rendering)

        for _child_node in _node.children:
            self._add_node(node_id=_child_node, parent_id=_node_id)

    # label='Edge Label')

    @property
    def is_executable(self):
        """returns if graphs can be drawn"""
        return self._is_executable


# def visualize(
#     code: str | AstNode | dict,
#     show_code: bool = True,
#     add_date: bool = False,
#     filename: str = None,
#     path: str = None,
#     view: bool = True,
#     max_chars: int = None,
# ):
#     """convenience method to render a python code snippet"""
#     _visualizer = AstVisualizer(show_code, add_date, filename, path, view, max_chars)
#     _visualizer.code = code
#     _visualizer.render()


def main(tree: Tree):
    """do something"""
    root_id = tree.root_id
    hierarchy = tree.hierarchy
    visualizer = TreeVisualizer(root_node_id=root_id, tree_node_dict=hierarchy)

    # visualize(code=code_s, max_chars=None)
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
