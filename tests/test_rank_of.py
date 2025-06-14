from ranked_programming.rp_core import nrm_exc, rank_of

def recur(x):
    return nrm_exc(x, lambda: recur(x * 2), 1)

def test_rank_of_example():
    # Should return 9 for first value > 500 in recur(1)
    result = rank_of(lambda x: x > 500, recur(1))
    assert result == 9

    # Should return 0 for first value > 0
    result = rank_of(lambda x: x > 0, recur(1))
    assert result == 0

    # Should return 14 for first value > 10000
    result = rank_of(lambda x: x > 10000, recur(1))
    assert result == 14

    # The following would not terminate (infinite ranking, always-false predicate)
    # result = rank_of(lambda x: False, recur(1))
    # assert result is None
