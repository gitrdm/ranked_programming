"""
Unit tests for performance enhancements: limit laziness, __bool__ efficiency, and documentation.
"""
from ranked_programming.rp_core import Ranking, limit

def test_limit_lazy():
    """Test that limit is lazy and does not exhaust the generator."""
    def gen():
        for i in range(1000000):
            yield (i, i)
    r = Ranking(gen)
    # Only the first 3 should be produced
    result = list(limit(3, r))
    assert result == [(0,0), (1,1), (2,2)]

def test_bool_short_circuit():
    """Test that bool(ranking) does not exhaust the generator and is efficient."""
    called = []
    def gen():
        called.append(True)
        yield (1, 0)
    r = Ranking(gen)
    assert bool(r) is True
    assert called == [True]
    r_empty = Ranking(lambda: iter([]))
    assert bool(r_empty) is False
