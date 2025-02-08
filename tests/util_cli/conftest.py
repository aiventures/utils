"""ColorMapper setup"""

import pytest

from util.calendar_util import Calendar
from util_cli.cli_calendar_renderer import CalendarTableRenderer
from util_cli.cli_color_mapper import ColorMapper
from util_cli.cli_color_schema import ColorSchema

### [1] Fixtures for Color Mapper


# variations using different themes of the object
@pytest.fixture(params=["neutron", None])
def fixture_color_mapper(request) -> ColorMapper:
    """Sample ColorMapper"""
    yield ColorMapper(theme=request.param)


@pytest.fixture(scope="module")
def fixture_daytype_list() -> list:
    """sample daytype list for calendar"""
    daytype_list = [
        # "@HOME Mo Di Mi Fr 0800-1200 1300-1700",
        # "@WORK Do 1000-1200 1300-1600",
        "@VACA 20240902-20240910",
        "@PART 20240919-20240923",
        "@VACA 20240927",
        "@WORK 20241216 1000-1600 :notebook: 6H Test Info ",
        "@WORK 20241217 1000-1700 :notebook: 7H Test Info ",
        "@HOME 20241218 1000-1800 :notebook: 8H Test Info ",
        "@WORK 20241219 1000-1900 :notebook: 9H Test Info ",
        "@WORK 20241220 1000-2000 :notebook: 10H Test Info ",
        "@WORK 20241201 1000-1800 :notebook: Test Change of Daily Work Regular Time Info @REGULARWORKTIME7.5",
        "@WORK 20240929-20241004 :notebook: Test Info ",
        "@WORK 20240901 :red_circle: :green_square: MORE INFO 1230-1450 1615-1645",
        "@FLEX 20241010 JUST INFO 0934-1134",
    ]
    return daytype_list


@pytest.fixture(scope="module")
def fixture_calendar(fixture_daytype_list) -> Calendar:
    """Sample Calendar"""
    return Calendar(2024, 8, fixture_daytype_list)


@pytest.fixture(scope="module")
def fixture_table_renderer(fixture_calendar) -> CalendarTableRenderer:
    """Sample Calendar"""
    return CalendarTableRenderer(calendar=fixture_calendar, icon_render="all")


@pytest.fixture(scope="module")
def fixture_color_schema() -> ColorSchema:
    """Sample Calendar"""
    return ColorSchema()
