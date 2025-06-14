from ranked_programming.rp_core import failure, Ranking

def test_failure_empty():
    # Should yield nothing
    result = list(failure())
    assert result == []

    # Should work wrapped in Ranking
    r = Ranking(failure)
    assert list(r) == []
