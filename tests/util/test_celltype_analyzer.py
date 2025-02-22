"""testing celltype_analyzer.py"""

from util.celltype_analyzer import CellTypeAnalyzer, CellTypeMetaDictType


def test_celltype_analyzer_smoketest():
    """testing basics of celltype analyzer"""
    _analyzer = CellTypeAnalyzer()
    assert True


def test_celltype_analyzer_testdict(fixture_celltype_dict):
    """testing dict celltype"""
    _analyzer = CellTypeAnalyzer()
    for _key, _info in fixture_celltype_dict.items():
        _analyzer.analyze(_info, _key)
    _stats = _analyzer.get_stats()
    stats_parent_id = _stats["parent_id"]
    stats_value = _stats["value"]
    stats_object = _stats["object"]
    assert stats_parent_id["num"] == 3
    assert stats_parent_id["min_value"] == 1
    assert stats_parent_id["max_value"] == 2
    assert stats_parent_id["total"] == 3
    assert stats_value["total"] == 4.0
    assert stats_object["num_str"] == 3

    # _analyzer.analyze()
    assert True


def test_celltype_analyzer_testbasemodel(fixture_celltype_basemodel):
    """testing dict celltype"""
    _analyzer = CellTypeAnalyzer()
    for _key, _info in fixture_celltype_basemodel.items():
        _analyzer.analyze(_info, _key)
    _stats = _analyzer.get_stats()
    stats_parent_id = _stats["parent_id"]
    stats_value = _stats["value"]
    stats_object = _stats["obj"]
    assert stats_parent_id["num"] == 3
    assert stats_parent_id["min_value"] == 1
    assert stats_parent_id["max_value"] == 2
    assert stats_parent_id["total"] == 3
    assert stats_value["total"] == 4.0
    assert stats_object["num_str"] == 3
    # _analyzer.analyze()
    assert True


def test_celltype_analyzer_testrootmodel(fixture_celltype_rootmodel):
    """testing dict celltype"""
    _analyzer = CellTypeAnalyzer()
    for _key, _info in fixture_celltype_rootmodel.items():
        _analyzer.analyze(_info, _key)
    _stats = _analyzer.get_stats()
    stats_parent_id = _stats["parent_id"]
    stats_value = _stats["value"]
    stats_object = _stats["object"]
    assert stats_parent_id["num"] == 3
    assert stats_parent_id["min_value"] == 1
    assert stats_parent_id["max_value"] == 2
    assert stats_parent_id["total"] == 3
    assert stats_value["total"] == 4.0
    assert stats_object["num_str"] == 3
    # _analyzer.analyze()
    assert True


def test_celltype_analyzer_primitive():
    """testing dict celltype"""
    test_list = [None, "a", 2, "b", None, 8]
    _analyzer = CellTypeAnalyzer()
    for _value in test_list:
        _analyzer.analyze(_value)
    stats = _analyzer.get_stats(as_dict=False)["primitive"]
    # check for correct stats
    assert stats.total == 10
    assert stats.num_number == 2
    assert stats.num == 6
