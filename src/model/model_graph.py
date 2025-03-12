"""meta model for graph"""

from typing import Optional, Annotated, Literal, Dict
from pydantic import BaseModel, TypeAdapter

GraphLiteral = Literal["edge", "node", "node_in", "node_out"]


class GraphElement(BaseModel):
    """simple definition of a graph element"""

    id: Optional[object] = None
    graphtype: Optional[GraphLiteral] = None
    name: Optional[str] = None
    obj: Optional[object] = None


class GraphNode(GraphElement):
    """a graph node"""

    # relations, list to edges
    relations: Optional[Dict[GraphLiteral, object]] = []


class GraphEdge(GraphElement):
    """a graph edge"""

    # edges should point to nodes ods
    id_in: Optional[object] = None
    id_out: Optional[object] = None


# derived models
GraphDictModel = Dict[object, GraphElement]
GraphDictAdapter = TypeAdapter(GraphDictModel)
GraphDictType = Annotated[GraphDictModel, GraphDictAdapter]
