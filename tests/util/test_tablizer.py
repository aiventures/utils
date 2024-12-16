"""testing tablizer.py"""

from util.tablizer import Tablizer


def test_tablizer_bundle_by_marker(fixture_testfile_tablizer):
    """testing the tablizer"""
    _tablizer = Tablizer(fixture_testfile_tablizer, skip_blank_lines=True, strip_lines=True)
    _as_dict = True
    _bundled = _tablizer.bundle_by_marker(marker="MARKER_NEW", include_marker_line=False, sep=",")
    _bundled_dict = _tablizer.bundle_by_marker(
        marker="MARKER_NEW", include_marker_line=False, sep=",", as_dict=_as_dict
    )
    assert isinstance(_bundled, list) and len(_bundled) > 0
    assert isinstance(_bundled_dict, dict) and len(_bundled) > 0
