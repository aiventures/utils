"""Testing the generation of Color Schemas"""

from typing import List
from model.model_visualizer import (
    ColorSchemaSetType,
    SchemaColorType,
    ColorSchemaData,
)


def test_color_schema(fixture_color_schema):
    """testing instanciation of Color Schema"""
    _color_schema = fixture_color_schema
    _metadata = _color_schema.metadata
    assert isinstance(_metadata, dict)
    _schema = _color_schema.get_schema_info(schema="accent")
    assert isinstance(_schema, dict)
    _colors, _invert_fonts = _color_schema.colors(num_colors=5)
    assert isinstance(_colors, list)
    assert isinstance(_invert_fonts, list)


def test_color_schema_filter(fixture_color_schema):
    """assembling a schema filter"""
    _color_schema = fixture_color_schema
    _colors: List[SchemaColorType] = ["green"]
    _num_colors: List[int] = [1]
    color_schema_sets: List[ColorSchemaSetType] = ["all"]
    _schemas = _color_schema.filter_schemas(
        color_filters=_colors, num_colors=_num_colors, color_schema_sets=color_schema_sets
    )
    assert isinstance(_schemas, list)


def test_color_schema_as_model(fixture_color_schema):
    """getting a schema as pydantic model"""
    _color_schema = fixture_color_schema
    _color_schema_data: ColorSchemaData = _color_schema.get_color_schema(schema="blues")
    assert isinstance(_color_schema_data, ColorSchemaData)


def test_color_schema_model_dump(fixture_color_schema):
    """getting a schema as pydantic model"""
    _color_schema = fixture_color_schema
    _all_color_schemas = _color_schema.get_color_schema_map(color_schemas=["blues", "brbg"])
    # get it as dict
    _all_color_schemas_dict = _all_color_schemas.model_dump()
    assert isinstance(_all_color_schemas_dict, dict)
