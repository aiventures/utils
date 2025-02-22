"""Tree with simple filter"""

import logging
import sys
from typing import Dict, Optional
from cli.bootstrap_env import CLI_LOG_LEVEL
from util.tree import Tree, valid_node_id
from model.model_tree import TreeNodeModel

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


class TreeFiltered(Tree):
    """Tree with filtered sublassed from tree"""

    def __init__(self):
        """constructor"""
        super().__init__()
        # filtered keys
        self._filtered_nodes: Optional[Dict[object, TreeNodeModel]] = {}

    @valid_node_id
    def _is_filtered(self, node_id: object) -> bool:
        """filters tree. if node_id is either in dict of filtered nodes or
        a child of
        """
        # check if this is in keys already
        try:
            _ = self._filtered_nodes[node_id]
            return True
        except KeyError:
            pass

        # TODO PRIO4 maybe add a progress indicator
        for _node_id, _children_nodes in self._filtered_nodes.items():
            if node_id in _children_nodes:
                return True
        return False

    @valid_node_id
    def get_node(self, node_id: object) -> TreeNodeModel | None:
        """overwriting the get node method.
        get_node is used to retrieve the node in the superclass
        so overwriting allows to filter the tree
        """
        if self._is_filtered(node_id):
            return None
        else:
            return super().get_node(node_id)

    @valid_node_id
    def add_filter(self, node_id: object):
        """adds a filter id to the filtered_nodes"""
        _node = self._hierarchy_nodes_dict[node_id]
        # add all children as values
        self._filtered_nodes[node_id] = set(_node.children)

    @valid_node_id
    def remove_filter(self, node_id: object):
        """removes a filter id from the filtered_nodes"""
        try:
            _ = self._filtered_nodes.pop(node_id)
        except KeyError:
            logger.info(f"[TreeFiltered] No Node Key [{node_id}] in filtered nodes")


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    pass
