"""Models Used for Color Rendering"""

from typing import Optional, Dict, List, Literal, Annotated
from pydantic import BaseModel


# Color Codes https://graphviz.org/docs/attr-types/color/
# pencolor bounding box color
# x11 https://graphviz.org/doc/info/colors.html#x11

# shapes Attribute
# https://graphviz.org/doc/info/shapes.html
# record "a|b|c"
GraphVizShape = Literal["box", "plaintext", "none", "ellipse", "record"]
GraphVizShapeType = Annotated[GraphVizShape, "shape"]

# splines Attribute
# https://graphviz.org/docs/attrs/splines/
GraphVizSplines = Literal["ortho", "polyline", "curved", "line", "none"]
GraphVizSplinesType = Annotated[GraphVizSplines, "spline"]

GraphVizLineStyles = Literal["solid", "dashed", "dotted", "bold", "invis", "tapered"]
GraphVizLineStylesType = Annotated[GraphVizLineStyles, "linestyles"]

GraphVizDotRankdir = Literal["TB", "LR", "BT", "RL"]
GraphVizDotRankdirType = Annotated[GraphVizDotRankdir, "rankdir"]


class DotFormat(BaseModel):
    """Attributes for Graphviz Rendering"""

    # create a default for node and edge

    # attributes valid for both edges and nodes
    # https://graphviz.org/docs/attrs/id/
    # internal name
    name: Optional[str] = None
    # object identifier, usually name is copied
    id: Optional[str] = None
    # local files also are working using
    # "file://C:\\Program Files (x86)"
    URL: Optional[str] = None
    # should be "_top"
    target: Optional[str] = None
    # tooltip
    tooltip: Optional[str] = None
    # text to be displayed on Node in Graphviz
    label: Optional[str] = "Node"
    style: Optional[str] = "filled"
    # color of shape / frame
    color: Optional[str] = "black"
    fillcolor: Optional[str] = "white"
    fontcolor: Optional[str] = "black"
    fontsize: Optional[str] = "14"
    shape: Optional[GraphVizShapeType] = "box"
    penwidth: Optional[str] = None
