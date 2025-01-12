"""Visualizing AST - Can also be used as standalone program
Requirements:
* Graphivz is installed and bin path is added to PATH variable
  https://graphviz.org/download/
  If you can call dot -V in terminal you're fine ...
* Python Graphviz Module is installed
  https://pypi.org/project/graphviz/
* Other sources
  https://earthly.dev/blog/python-ast/
  https://ucb-sejits.github.io/ctree-docs/ipythontips.html
* GraphViz SetUp
  - Shape Options
    https://graphviz.org/doc/info/attrs.html
  - Styling and Examples
    https://graphviz.readthedocs.io/en/stable/manual.html#styling

Troubleshooting:
* Updated PATH IN VSCODE might not be found, check your Application Path (echo $PATH or set PATH)
"""

import ast
from ast import AST as AstNode
import subprocess
from pathlib import Path
from enum import StrEnum
import os
import logging
import sys
from datetime import datetime as DateTime

# Design Decision: You need to manually install GRAPHVIZ into your environment
PY_GRAPHVIZ_INSTALLED = True
try:
    from graphviz import Digraph
except ImportError:
    PY_GRAPHVIZ_INSTALLED = False

logger = logging.getLogger(__name__)

# get log level from environment if given
DEFAULT_LOGLEVEL = int(os.environ.get("CLI_LOG_LEVEL", logging.INFO))
logger.setLevel(DEFAULT_LOGLEVEL)
DATEFORMAT_JJJJMMDDHHMMSS = "%Y%m%d_%H%M%S"


class AstNodeInfo(StrEnum):
    """Metadata for ast"""

    LABEL = "label"
    NAME = "name"
    CODE = "code"
    STYLE = "style"
    COLOR = "color"
    FILLCOLOR = "fillcolor"
    FONTCOLOR = "fontcolor"


# Color Codes https://graphviz.org/docs/attr-types/color/
# x11 https://graphviz.org/doc/info/colors.html#x11
# Shapes https://www.devtoolsdaily.com/graphviz/node-shapes/
FORMAT_DEFAULT = {"style": "filled", "color": "white", "fillcolor": "white", "fontcolor": "black"}
# Formatting the output Nodes
FORMAT_NODES = {
    "Module": {"style": "filled", "color": "darkblue", "fillcolor": "darkblue", "fontcolor": "white"},
    "ClassDef": {"style": "filled", "color": "lime", "fillcolor": "lime", "fontcolor": "black"},
    # function
    "FunctionDef": {
        "style": "filled",
        "color": "darkgreen",
        "fillcolor": "darkgreen",
        "fontcolor": "white",
    },
    "Constant": {"style": "filled", "color": "grey50", "fillcolor": "grey50", "fontcolor": "white"},
    "AnnAssign": {"style": "filled", "color": "lightsalmon1", "fillcolor": "lightsalmon1", "fontcolor": "black"},
    "Attribute": {"style": "filled", "color": "orchid1", "fillcolor": "orchid1", "fontcolor": "black"},
    "Assign": {"style": "filled", "color": "lightsalmon1", "fillcolor": "lightsalmon1", "fontcolor": "black"},
    "arguments": {"style": "filled", "color": "darkorange2", "fillcolor": "darkorange2", "fontcolor": "black"},
    "arg": {"style": "filled", "color": "gold2", "fillcolor": "gold2", "fontcolor": "black"},
    "Import": {"style": "filled", "color": "darkseagreen1", "fillcolor": "darkseagreen1", "fontcolor": "black"},
    "ImportFrom": {"style": "filled", "color": "darkseagreen1", "fillcolor": "darkseagreen1", "fontcolor": "black"},
    "alias": {"style": "filled", "color": "greenyellow", "fillcolor": "greenyellow", "fontcolor": "black"},
    "Expr": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "Pass": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "Store": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "Load": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "BinOp": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "BitOr": {"style": "filled", "color": "gray84", "fillcolor": "gray84", "fontcolor": "gray33"},
    "Call": {"style": "filled", "color": "plum1", "fillcolor": "plum1", "fontcolor": "gray33", "shape": "cds"},
    "Return": {"style": "filled", "color": "plum1", "fillcolor": "plum1", "fontcolor": "gray33", "shape": "larrow"},
    "Name": {"style": "filled", "color": "darkturquoise", "fillcolor": "darkturquoise", "fontcolor": "black"},
}


class AstVisualizer:
    """Visualize code as Abstract Syntax Tree"""

    def run_cmd(self, _cmd):
        """runs os command"""
        proc = subprocess.Popen(
            _cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True
        )
        std_out, std_err = proc.communicate()
        return proc.returncode, std_out, std_err

    def _read_source(self, f: str) -> str:
        """loads code"""
        if not os.path.isfile(f):
            logger.warning(f"[AstVisualizer] [{f}] Is not a file")
            return None
        content = None
        with open(f, "r", encoding="UTF-8") as _file:
            content = _file.read()
        if content is not None:
            logger.info(f"[AstVisualizer] reading [{f}], length [{len(content)}]")
        return content

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

    def __init__(
        self, show_code: bool = True, add_date: bool = False, filename: str = None, path: str = None, view: bool = True
    ):
        """Constructor"""
        self._is_executable = self._check_graphviz_executable()
        if self._is_executable is False:
            return

        if PY_GRAPHVIZ_INSTALLED is False:
            logger.warning(
                "[AstVisualizer] GRAPHVIZ PYTHON LIB IS NOT INSTALLED, INSTALL GRAPHVIZ https://pypi.org/project/graphviz"
            )
            self._is_executable = False
            return

        self._code = None
        # export format
        self._file_format = "svg"
        self._tree = None
        self._dot = None
        # display options
        self._show_code = show_code
        # save options
        # adding date to file name
        self._add_date = add_date
        self._filename = filename
        self._path = path
        self._save_path = None
        self._view = view
        self._set_save_path()

    def _set_code(self, code: str) -> None:
        """setting the code"""
        _code = code
        if os.path.isfile(code):
            _code = self._read_source(code)
        self._code = code

    def _get_format(self, node_type: str) -> dict:
        """returns the formatting dict"""
        return FORMAT_DEFAULT

    # get metadata
    def _get_node_dict(self, node) -> dict:
        out = {}
        _name = str(id(node))
        _label = str(node.__class__.__name__)
        _format_dict = FORMAT_NODES.get(_label, FORMAT_DEFAULT)
        _original_s = str(ast.unparse(node))
        out[AstNodeInfo.NAME.value] = _name
        if self._show_code:
            _label += "\n" + _original_s
        out[AstNodeInfo.LABEL.value] = _label
        # out[AstNodeInfo.CODE.value] = _original_s
        out.update(_format_dict)
        return out

    # Recursively add nodes to the Digraph
    def _add_node(self, node: AstNode, parent: AstNode | None = None) -> None:
        # add node
        _node_info = self._get_node_dict(node)
        _node_id = _node_info[AstNodeInfo.NAME.value]
        _node_label = _node_info[AstNodeInfo.LABEL.value]
        _node_name = None
        # get all fields of the node in a dict / just in here for future use
        # get metadata from node
        if hasattr(node, "name"):
            _node_name = node.name
            _node_info[AstNodeInfo.LABEL.value] = f"NODE ({_node_name})\n{_node_label}"
            logger.debug(f"[AstVisualizer] Parsing Node [{_node_name}], code [{_node_label}]")
        _field_dict = dict(list(ast.iter_fields(node)))
        _decorator_list = None
        if _field_dict:
            _body = _field_dict.get("body")
            _name = _field_dict.get("name")
            _args = _field_dict.get("args")
            _decorator_list = _field_dict.get("decorator_list")
            # extract decorators
            if isinstance(_decorator_list, list) and len(_decorator_list) > 0:
                _node_decorators = []
                for _decorator in _decorator_list:
                    _node_decorators.append(_decorator.id)
                _node_label = _node_info[AstNodeInfo.LABEL.value]
                _node_info[AstNodeInfo.LABEL.value] = f"{_node_decorators} {_node_label}"

            _returns = _field_dict.get("returns")
            _type_comment = _field_dict.get("type_comment")
            pass

        self._dot.node(**_node_info)

        _parent_info = None
        if parent:
            _parent_info = self._get_node_dict(parent)
        # draw relation to parent
        if _parent_info:
            _parent_id = _parent_info[AstNodeInfo.NAME.value]
            self._dot.edge(_parent_id, _node_id)

        # process all children
        for _child in ast.iter_child_nodes(node):
            self._add_node(_child, node)

    def _render(self) -> None:
        """viusalize the graph recursively"""
        if self._tree is None:
            logger.warning("[AstVisualizer] Nothing to parse")
            return
        self._dot = Digraph()
        # render as boxes

        self._dot.attr("node", shape="box", fontname="Monospace")

        self._dot.format = self._file_format
        # process the parsed code tree
        # ast.dump(self._tree)
        self._add_node(self._tree)
        # render the tree
        self._dot.render(Path(self._save_path), view=self._view)

        logger.info(f"[AstVisualizer] Saved GraphViz File, path [{self._save_path}]")

    def render(self, code: str = None) -> None:
        """visualize string or file"""
        if code is not None:
            self.code = code

        if self._code is None:
            self._tree = None
            logger.warning("[AstVisualizer] No code was loaded, check your settings")
            return

        # if called externally and parts are not ready  do nothing
        if self.is_executable is False:
            logger.debug("[AstVisualizer] Graphviz not set up properly, pls check")
            return
        self._render()

    @property
    def is_executable(self):
        """returns if ast graphs can be drawn"""
        return self._is_executable

    @property
    def code(self) -> str:
        """return code string"""
        return self._code

    @code.setter
    def code(self, code: str) -> None:
        """setting the code string"""
        _code = code
        if os.path.isfile(code):
            _code = self._read_source(code)
        self._code = _code
        # get the ast tree
        try:
            self._tree = ast.parse(_code)
        except SyntaxError as e:
            logger.error(f"[AstVisualizer] Code is not valid [{str(e.args)}]")
            self._tree = None
            self._code = None

    def dump(self) -> str | None:
        """gets the object tree as string dump"""
        if self._tree:
            return ast.dump(self._tree, indent=2, include_attributes=True)
        else:
            return None


def main(code_s: str):
    """do something"""
    _viusalizer = AstVisualizer()
    # assure everything is set up
    if not _viusalizer.is_executable:
        exit(1)
    _viusalizer.code = code_s
    _viusalizer.render()


# code snippet to show what is going on
# TODO PRIO 4 to add annotations "How can I visualize Python function annotations using Graphviz"
# https://www.perplexity.ai/search/python-graphviz-annotation-chKB3KD9QryBiRWfGXX91A

_sample_imports = """
import sys
from os import chdir
from pathlib import Path as MyPath
"""

_sample_hello_world = """
def hello(param_name:str="John Doe"):
    # sample code
    print("Hello " + param_name)
hello("Karl-Heinz")
"""

# note: for each node there is also a decorator list allowing to read out decorators
_sample_class = """
class MyClass:
    class_att:int = 5
    def __init__(self):
        self.attr:str = "hello"
        pass        
    def meth(self,p1:str,p2:str="xxx"):
        myvar = "5"
        pass
    @mydecorator1
    @mydecorator2
    def myprop(self)->str|None:
        return self.attr
"""

_sample_decorator = """
@mydecorator1
@mydecorator2
def myprop(myparam0:int,myparam1:str="default")->str|None:
    return "HUGO"    
"""

_sample_error = """
no valid python  
"""

SAMPLE_CODE = _sample_class

if __name__ == "__main__":
    loglevel = DEFAULT_LOGLEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main(SAMPLE_CODE)
