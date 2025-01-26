"""Testing the calendar renderer"""

from util_cli.cli_calendar_renderer import CalendarRenderer, CalendarTableRenderer


def test_markdown_list(fixture_table_renderer):
    """testing creation of markdown"""
    # testing _markdown without filter
    _markdown = fixture_table_renderer.get_markdown()
    _num_markdown_no_filter = len(_markdown)
    assert _num_markdown_no_filter > 300


def test_markdown_list_filtered(fixture_table_renderer):
    """testing creation of markdown"""
    # testing with filter
    fixture_table_renderer.set_calendar_filter("20240915-20241130")
    _markdown2 = fixture_table_renderer.get_markdown()
    _num_markdown_filter2 = len(_markdown2)
    # reset filter
    fixture_table_renderer.set_calendar_filter()
    _markdown3 = fixture_table_renderer.get_markdown()
    _num_markdown_filter3 = len(_markdown3)
    assert _num_markdown_filter3 > _num_markdown_filter2

    pass
