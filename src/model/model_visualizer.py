"""Models Used for Color Rendering"""

from typing import Optional, Dict, List, Literal, Annotated
from pydantic import BaseModel


# GraphViz Gallery
# https://graphviz.org/gallery/
# Graphviz Engines
# https://graphviz.org/docs/layouts/
GraphVizEngine = Literal["dot", "neato", "fdp", "sfdp", "circo", "twopi", "nop", "nop2", "osage", "patchwork"]
GraphVizEngineType = Annotated[GraphVizEngine, "engine"]
# TODO PRIO3 write a patchwork model using brewer colors

# Color Codes https://graphviz.org/docs/attr-types/color/
# pencolor bounding box color
# x11 https://graphviz.org/doc/info/colors.html#x11


# TODO PRIO2 Use Color Schemes to render Trees according to depth level
# Graphviz Color Schemes correspond to Brewer Colors
# https://colorbrewer2.org/colorbrewer_schemes.js
# Graphviz source location of brewer colors
# https://gitlab.com/graphviz/graphviz/-/blob/main/lib/common/brewer_colors
# Prompts
# graphviz python color scheme
# graphviz set font color according to brewer color scheme automatically
# https://graphviz.org/doc/info/colors.html#brewer
# g = graphviz.Graph()
# g.attr(colorscheme='set38')  # Use the 'set38' color scheme
# g.node('A', color='1', fontcolor='1')
# g.edge('A', 'B', color='3')
# For examples check https://colorbrewer2.org
# /util/cli/cli_colorbrewer.py contains the color codes
ColorSchemaSet = Literal["divergent", "qualitative", "sequential"]
ColorSetType = Annotated[ColorSchemaSet, "color_set"]
# available color schemes

# Brewer color sets are also used in seaborn
# https://seaborn.pydata.org/tutorial/color_palettes.html
# Color Codes as JSON https://github.com/uncommoncode/color_palettes_json/tree/master
# You'll find the RGB codes in /resources/colorbrewer.json
# TODO PRIO3 OUTPUT COLORS
GraphVizColorScheme = Literal[
    # divergent
    "brbg",
    "piyg",
    "prgn",
    "puor",
    "rdbu",
    "rdgy",
    "rdylbu",
    "rdylgn",
    "spectral",
    # qualitative
    "accent",
    "dark2",
    "paired",
    "pastel1",
    "pastel2",
    "set1",
    "set2",
    "set3",
    # sequential
    "blues",
    "bugn",
    "bupu",
    "gnbu",
    "greens",
    "greys",
    "oranges",
    "orrd",
    "pubu",
    "pubugn",
    "purd",
    "purples",
    "rdpu",
    "reds",
    "ylgn",
    "ylgnbu",
    "ylorbr",
    "ylorrd",
]
GraphVizColorSchemaType = Annotated[GraphVizColorScheme, "color_schema"]

# shapes Attribute
# https://graphviz.org/doc/info/shapes.html
# record "a|b|c"
GraphVizShape = Literal["box", "plaintext", "none", "ellipse", "record"]
GraphVizShapeType = Annotated[GraphVizShape, "shape"]

# GraphViz Attributes
# https://graphviz.org/docs/attr-types/
# https://graphviz.org/doc/info/attrs.html

# splines Attribute
# https://graphviz.org/docs/attrs/splines/
GraphVizSplines = Literal["ortho", "polyline", "curved", "line", "none"]
GraphVizSplinesType = Annotated[GraphVizSplines, "spline"]

GraphVizLineStyles = Literal["solid", "dashed", "dotted", "bold", "invis", "tapered"]
GraphVizLineStylesType = Annotated[GraphVizLineStyles, "linestyles"]

# https://graphviz.org/docs/attr-types/rankdir/
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
