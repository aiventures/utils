""" ColorMapper setup """

import pytest
from cli.cli_color_mapper import ColorMapper

### [1] Fixtures for Color Mapper

# variations using different themes of the object 
@pytest.fixture(params=["neutron",None])
def fixture_color_mapper(request)->ColorMapper:
    """ Sample ColorMapper """
    yield ColorMapper(theme=request.param)

