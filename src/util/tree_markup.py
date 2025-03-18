"""Nesting tree elements, to be used for nested tree output for creating markup structures such as xmls, plantuml or markdown"""

# from pathlib import Path
import logging
import sys

# import typer
from typing import Dict
from cli.bootstrap_env import CLI_LOG_LEVEL
from model.model_tree import TreeNodeModel
from util.tree import Tree

logger = logging.getLogger(__name__)

# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class TreeMarkup:
    """Nesting Tree Elements to create nested tree amrkup"""

    def __init__(self, tree: Tree, num_spaces: int = 4):
        self._tree: Tree = tree
        self._start_tag: str = "{"
        self._end_tag: str = "}"
        self._rendered_elements: Dict[object, str] = {}
        self._render_stack: list = []
        self._indent: str = num_spaces * " "
        self._rendered_tree = None
        self._render_leaves()
        self._render_nodes()

    def render_leaf(self, node: TreeNodeModel) -> str:
        """render a single leaf can be used for overwriting"""
        _indent = node.level * self._indent
        # for now we only implement a minimal implementation
        return f"{_indent}[{node.name}]"

    def _render_leaf(self, node_id: object) -> None:
        """renders content of a single node, van be subclassed"""
        _node = self._tree.get_node(node_id)
        if _node is None:
            return
        _content = self.render_leaf(_node)
        self._rendered_elements[node_id] = _content
        # add parent to be rendered if not already done
        _parent_id = _node.parent_id
        if _parent_id is not None and self._rendered_elements.get(_parent_id) is None:
            if _parent_id not in self._render_stack:
                self._render_stack.append(_parent_id)

    def _render_leaves(self):
        """renders all nodes"""
        # initialize the stack with all children
        _node_ids = self._tree.get_all_children(self._tree.root_id, only_leaves=True)
        for _node_id in _node_ids:
            self._render_leaf(_node_id)

    def join_rendered_children(self, rendered_children: list) -> str:
        """join children (eg add commata or simple add them, whatever) ..."""
        out = "\n".join(rendered_children)
        return out

    def render_node(self, node: TreeNodeModel) -> str:
        """renders the node"""
        _indent = node.level * self._indent
        out = f"{_indent}{self._start_tag}{node.name}\n"
        return out

    def render_close_tag(self, node: TreeNodeModel) -> str:
        """renders the close tag, depends on used markup"""
        _indent = node.level * self._indent
        out = f"\n{_indent}{self._end_tag}"
        return out

    def _render_node(self, node_id: object):
        """render the node.
        we can assume that all children nodes were parsed before"""
        if node_id is None:
            return
        _out = ""
        _node = self._tree.get_node(node_id)
        _indent = _node.level * self._indent
        _parent_id = _node.parent_id
        # add the parent to the stack
        if _parent_id and _parent_id not in self._render_stack:
            self._render_stack.append(_parent_id)
        _child_ids = _node.children
        _rendered_children = []
        for _child_id in _child_ids:
            s_child = self._rendered_elements.pop(_child_id)
            _rendered_children.append(s_child)
        _rendered_node = self.render_node(_node)
        _rendered_children = self.join_rendered_children(_rendered_children)
        _close_tag = self.render_close_tag(_node)
        _out = _rendered_node + _rendered_children + _close_tag
        self._rendered_elements[node_id] = _out

    def _render_nodes(self):
        # continue as long as there are nodes to render
        while len(self._render_stack) > 0:
            # go through in reverse order
            _next_element = None
            _children = None
            for _idx in range(len(self._render_stack) - 1, -1, -1):
                # find the next element where all children are rendered
                _node_id = self._render_stack[_idx]
                _node = self._tree.get_node(_node_id)
                _children = _node.children
                _unrendered_children = [_child for _child in _children if self._rendered_elements.get(_child) is None]
                # this element has all childrens rendered, so it can be rendered
                if len(_unrendered_children) == 0:
                    _next_element = self._render_stack[_idx]
                    break
            if _next_element:
                # remove the current index
                self._render_stack.pop(_idx)
                self._render_node(_next_element)

        if len(self._rendered_elements) != 1:
            logger.error(f"[TreeNester] There are {len(self._rendered_elements)}, expected one, quit")
            return
        self._rendered_tree = next(iter((self._rendered_elements.values())))

    @property
    def rendered(self) -> str:
        """rendered output"""
        return self._rendered_tree

    def __str__(self):
        return self.rendered


if __name__ == "__main__":
    loglevel = CLI_LOG_LEVEL
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # tree = {
    #     1: {"parent": None, "value": "value 1"},
    #     2: {"parent": 1},
    #     4: {"parent": 2},
    #     5: {"parent": 2},
    #     3: {"parent": 1},
    #     6: {"parent": 3},
    #     7: {"parent": 6},
    #     8: {"parent": 6},
    #     9: {"parent": 6},
    # }

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
    # use name to get a different field
    # defining fields where parent and values (for display) are stored
    my_tree.create_tree(tree, name_field="value", parent_field="parent", analyze_fields=True)
    tree_nester = TreeMarkup(my_tree)
    # get the out put
    print(str(tree_nester))
