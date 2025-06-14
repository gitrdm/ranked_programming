from ranked_programming.rp_core import construct_ranking, Ranking

def test_construct_ranking_basic():
    # (construct-ranking ("x" . 0) ("y" . 1) ("z" . 5))
    result = list(construct_ranking(("x", 0), ("y", 1), ("z", 5)))
    assert result == [("x", 0), ("y", 1), ("z", 5)]

    # Should work wrapped in Ranking
    r = Ranking(lambda: construct_ranking(("a", 0), ("b", 2)))
    assert list(r) == [("a", 0), ("b", 2)]

def test_construct_ranking_errors():
    # First rank not 0
    try:
        list(construct_ranking(("x", 1), ("y", 2)))
        assert False, "Should raise ValueError for first rank not 0"
    except ValueError:
        pass
    # Ranks not sorted
    try:
        list(construct_ranking(("x", 0), ("y", 2), ("z", 1)))
        assert False, "Should raise ValueError for unsorted ranks"
    except ValueError:
        pass
