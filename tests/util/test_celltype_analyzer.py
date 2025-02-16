"""testing celltype_analyzer.py"""

from util.celltype_analyzer import CellTypeAnalyzer


def test_celltype_analyzer_smoketest():
    """testing basics of celltype analyzer"""
    _analyzer = CellTypeAnalyzer()
    assert True


def test_celltype_analyzer_testdict(fixture_celltype_dict):
    """testing dict celltype"""
    _analyzer = CellTypeAnalyzer()
    for _key, _info in fixture_celltype_dict:
        _analyzer.analyze(_info, _key)

    # _analyzer.analyze()
    assert True


def test_celltype_analyzer_primitive():
    """testing dict celltype"""
    test_list = [None, "a", 2, "b", None, 8]
    _analyzer = CellTypeAnalyzer()
    for _value in test_list:
        _analyzer.analyze(_value)

    # _analyzer.analyze()
    assert True
