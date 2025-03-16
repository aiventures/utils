"""Models Used for Color Rendering"""

from typing import Optional, Dict, Literal, Annotated, Iterable
from pydantic import BaseModel, RootModel

from model.model_colors import COLORS_GRAPHVIZ


# Color Encoding
# TODO PRIO4 adapt cli_color_mapper
# - code ANSI Code Number
# - rgb  RGB tuple
# - hex  HEX code string
# https://graphviz.org/docs/attr-types/color/
# color names
# https://graphviz.org/doc/info/colors.html
ColorEncoding = Literal["code", "rgb", "hex"]
ColorEncodingType = Annotated[ColorEncoding, "color_encoding"]

# GraphViz Gallery
# https://graphviz.org/gallery/
# Graphviz Engines
# https://graphviz.org/docs/layouts/
GraphVizEngine = Literal["dot", "neato", "fdp", "sfdp", "circo", "twopi", "nop", "nop2", "osage", "patchwork"]
GraphVizEngineType = Annotated[GraphVizEngine, "engine"]
# https://graphviz.org/docs/outputs/
GraphVizFileFormat = Literal["svg"]
# https://graphviz.org/docs/attrs/fontname/
GraphVizFontName = Literal["mono", "Arial", "Courier New"]

# https://graphviz.org/docs/attrs/labelloc/
GraphVizLabelLoc = Literal["t", "b", "c"]
# https://graphviz.org/docs/attrs/labeljust/
GraphVizLabelJust = Literal["r", "l", "c"]

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
ColorSchemaSet = Literal["divergent", "qualitative", "sequential", "all"]
ColorSchemaSetType = Annotated[ColorSchemaSet, "color_set"]
# available color schemes

# default line color
DEFAULT_LINE_COLOR = "grey40"
DEFAULT_BACKGROUND_COLOR = "grey70"

# Brewer color sets are also used in seaborn
# https://seaborn.pydata.org/tutorial/color_palettes.html
# Color Codes as JSON https://github.com/uncommoncode/color_palettes_json/tree/master
# You'll find the RGB codes in /resources
# TODO PRIO3 OUTPUT COLORS
ColorSchemaKey = Literal[
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
ColorSchemaType = Annotated[ColorSchemaKey, "color_schema"]
MULTICOLOR_SCHEMA = 99

# Available Colors in Schema
SchemaColor = Literal[
    "all",
    "blue",
    "bluegreen",
    "brown",
    "green",
    "grey",
    "multicolor",
    "orange",
    "pink",
    "purple",
    "red",
    "yellow",
    "yellowgreen",
]
SchemaColorType = Annotated[SchemaColor, "schema_color"]


class ColorSchemaMetaData(BaseModel):
    """Metadata of Color Schema"""

    name: Optional[ColorSchemaType] = None
    schema_set: Optional[ColorSchemaSetType] = None
    # max number of colors in a schema
    num_max_colors: Optional[int] = None
    # number of colors in a schema 1,2,3,multicolor ...
    num_colorset: Optional[int] = None
    # colors in colorset
    color_list: Optional[list] = None
    # description
    description: Optional[str] = None


# class ColorMapItem(BaseModel):
#     """ Structure in Schema Data to host color list and font color info """


class ColorSchemaData(ColorSchemaMetaData):
    """Adding the Meta Data"""

    encoding: Optional[ColorEncodingType] = None
    # NUm of colors in map / Color and info whether font is inverted
    # "3":[{#123456:True},{#aabbcc:False}..] (3 Elemets)
    # "4":...
    # ...
    color_schema_map: Optional[Dict[str, Dict[object, bool]]] = None


class ColorSchemaDataDict(RootModel):
    """ColorSchemaData Dict as root model to be able to export as dict
    directly address the root node of the pydantic class
    """

    root: Dict[ColorSchemaType, ColorSchemaData] = {}

    def __getitem__(self, key: ColorSchemaType):
        return self.root[key]

    def __setitem__(self, key: ColorSchemaType, value: ColorSchemaData):
        self.root[key] = value

    def __iter__(self):
        return iter(self.root.items())

    def items(self) -> Iterable[tuple[ColorSchemaType, ColorSchemaData]]:
        """directly get items so as if it was a real dict"""
        return self.root.items()


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
GraphVizSpline = Literal["ortho", "polyline", "curved", "line", "none"]
GraphVizSplineType = Annotated[GraphVizSpline, "spline"]

GraphVizLineStyle = Literal["solid", "dashed", "dotted", "bold", "invis", "tapered"]
GraphVizLineStyleType = Annotated[GraphVizLineStyle, "linestyles"]

# https://graphviz.org/docs/attr-types/rankdir/
GraphVizDotRankdir = Literal["TB", "LR", "BT", "RL"]
GraphVizDotRankdirType = Annotated[GraphVizDotRankdir, "rankdir"]


class NodeFormat(BaseModel):
    """Joint Model attirbutes for rendering node in both graphviz and rich"""

    # internal name / in graphviz is used as a key
    name: Optional[str] = None
    # object identifier, usually name is copied
    id: Optional[str] = None
    # local files also are working using
    # "file://C:\\Program Files (x86)"
    # link
    # displayed text
    displayed_text: Optional[str] = None
    # url / Link
    # local files also are working using
    # "file://C:\\Program Files (x86)"
    link: Optional[str] = None
    # tooltip
    tooltip: Optional[str] = None
    # text is inverted (= text color becomes background color)
    text_with_background_color: Optional[bool] = None
    # text is bold
    bold: Optional[bool] = None
    # invert text for texts with background
    text_invert_font_color: Optional[bool] = None


class RichNodeDisplayInfo(NodeFormat):
    """enhancements for Rich"""

    # formatting, defined as rich Style
    style: Optional[object] = None
    # text color
    textcolor: Optional[str] = None
    # styleguide color
    guidecolor: Optional[str] = None
    # background color
    bgcolor: Optional[str] = None
    # Emoji to be prepended
    emoji: Optional[str] = None


class GraphVizNode(NodeFormat):
    """Attributes for Graphviz Rendering"""

    # create a default for node and edge
    # attributes valid for both edges and nodes
    # https://graphviz.org/docs/attrs/id/

    # html should be "_top"
    target: Optional[str] = None
    # text to be displayed on Node in Graphviz
    # https://graphviz.org/docs/attrs/label/
    label: Optional[str] = "Node"
    # https://graphviz.org/docs/attrs/style/
    style: Optional[str] = "filled"
    # color of shape / frame
    # https://graphviz.org/docs/attrs/fontcolor/
    fontcolor: Optional[str] = "black"
    # https://graphviz.org/docs/attrs/color/
    color: Optional[str] = DEFAULT_LINE_COLOR
    # https://graphviz.org/docs/attrs/fillcolor/
    fillcolor: Optional[str] = "white"
    # https://graphviz.org/docs/attrs/fontsize/
    fontsize: Optional[str] = "14"
    # https://graphviz.org/docs/attrs/shape/
    shape: Optional[GraphVizShapeType] = "box"
    # https://graphviz.org/docs/attrs/penwidth/
    penwidth: Optional[str] = "2.0"
    # https://graphviz.org/docs/attrs/arrowhead/
    # can also be None
    arrowhead: Optional[str] = "normal"


class GraphVizAttributes(BaseModel):
    """Attributes for initialization of Digraph Model

    rankdir only applicable to dot engine
    https://graphviz.org/docs/attrs/rankdir/
    https://graphviz.org/docs/attrs/fontname/
    https://graphviz.org/docs/attrs/labelloc/
    https://graphviz.org/docs/attrs/labeljust/
    https://graphviz.org/docs/outputs/
    """

    engine: Optional[GraphVizEngine] = "dot"
    comment: Optional[str] = "Title"
    label: Optional[str] = "Tree"
    # "file://C:\\Program Files (x86)"
    URL: Optional[str] = None
    fontname: Optional[GraphVizFontName] = "mono"
    fontsize: Optional[str] = "12"
    rankdir: Optional[GraphVizDotRankdir] = "TB"
    # https://graphviz.org/doc/info/colors.html
    bgcolor: Optional[str] = DEFAULT_BACKGROUND_COLOR
    labelloc: Optional[GraphVizLabelLoc] = "b"
    labeljust: Optional[GraphVizLabelJust] = "l"
    format: Optional[GraphVizFileFormat] = "svg"
    # unflatten tweak
    # stagger: Stagger the minimum length of leaf edges between 1 and the specified value.
    # fanout: Enable staggering for nodes with indegree and outdegree of 1.
    # chain: Form disconnected nodes into chains of up to the specified length
    # https://graphviz.org/pdf/unflatten.1.pdf
    stagger: Optional[int] = 3
    fanout: Optional[bool] = True
    chain: Optional[int] = 20
    # default node attributes
    node_shape: Optional[GraphVizShape] = "box"
    node_fontname: Optional[GraphVizFontName] = "mono"
    # default edge attributes
    edge_color: Optional[COLORS_GRAPHVIZ] = "grey40"
    edge_style: Optional[GraphVizLineStyle] = "bold"
    edge_splines: Optional[GraphVizSpline] = "curved"
    edge_penwidth: Optional[str] = "2.0"
    edge_fontname: Optional[GraphVizFontName] = "mono"
