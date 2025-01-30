"""Models Used for Color Rendering"""

from typing import Optional, Dict, List, Literal, Annotated
from pydantic import BaseModel


# Color Codes https://graphviz.org/docs/attr-types/color/
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

    # https://graphviz.org/docs/attrs/id/
    # internal name
    name: Optional[str] = None
    # object identifier
    id: Optional[str] = None
    # text to be displayed on Node in Graphviz
    label: Optional[str] = "Node"
    style: Optional[str] = "filled"
    color: Optional[str] = "black"
    fillcolor: Optional[str] = "white"
    fontcolor: Optional[str] = "black"
    shape: Optional[GraphVizShapeType] = "box"
    url: Optional[str] = None
