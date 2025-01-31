"""Models Used for Color Rendering"""

from typing import Optional, Dict, List, Literal, Annotated
from pydantic import BaseModel


# Color Codes https://graphviz.org/docs/attr-types/color/
# pencolor bounding box color
# x11 https://graphviz.org/doc/info/colors.html#x11

# TODO PRIO2 Use Color Schemes to render Trees according to depth level
# Prompts
# graphviz python color scheme
# graphviz set font color according to color scheme automatically
# https://graphviz.org/doc/info/colors.html#brewer
# g = graphviz.Graph()
# g.attr(colorscheme='set38')  # Use the 'set38' color scheme
# g.node('A', color='1', fontcolor='1')
# g.edge('A', 'B', color='3')

# accent8 , blue9, brown blue green11, greens9, bluepurple9,dark2 8,greenblue 9,greens 9,grey9,
# oranges 9, orange red 9,paired 12, pastel1 9, pastel2 8,
# pink yellow green 11, purple green 11, purple blue 9,
# purple blue green 9,purple orange 11,purple red 1,
# purple 9, red blue 11,red grey 9, red purple 9 ,
# red yellow blue 11, red yellow green 11, red 9,
# set1 9, set2 8, set3 12, spectral 11, yellow green 9,
# yellow green blue 9, yello orange brown 9, yellow orange red 9

GraphVizColorScheme = Literal[
    "accent",
    "brbg",
    "blues",
    "bugn",
    "bupu",
    "dark2",
    "gnbu",
    "greens",
    "greys",
    "oranges",
    "orrd" "paired",
    "pastel1",
    "pastel2",
    "piyg",
    "prgn",
    "pubu",
    "pubugn" "puor",
    "purd",
    "purple",
    "rdbu",
    "rdgy",
    "rdpu",
    "rdylbu",
    "rdylgn",
    "reds",
    "set1",
    "set2",
    "set3",
    "spectral",
    "ylgn",
    "ylgnbu",
    "ylorbr",
    "ylorrd",
]
GraphVizColorSchemeType = Annotated[GraphVizColorScheme, "color_scheme"]

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
