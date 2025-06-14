from ranked_programming.rp_core import bang, Ranking

def test_bang_singleton():
    # (! 5) should yield only (5, 0)
    result = list(bang(5))
    assert result == [(5, 0)]

    # Should work with strings too
    result = list(bang("foo"))
    assert result == [("foo", 0)]

    # Should work with None
    result = list(bang(None))
    assert result == [(None, 0)]

    # Should work with Ranking wrapper
    r = Ranking(lambda: bang(42))
    assert list(r) == [(42, 0)]
