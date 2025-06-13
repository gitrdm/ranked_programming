"""
Unit tests for Ranking class enhancements: __len__, __bool__, __repr__.
"""
from ranked_programming.rp_core import Ranking

def test_ranking_len():
    """Test that len(ranking) returns the number of (value, rank) pairs."""
    r = Ranking(lambda: [(1, 0), (2, 1), (3, 2)])
    assert len(r) == 3
    r_empty = Ranking(lambda: [])
    assert len(r_empty) == 0

def test_ranking_bool():
    """Test that bool(ranking) is True if not empty, False if empty."""
    r = Ranking(lambda: [(1, 0)])
    assert bool(r) is True
    r_empty = Ranking(lambda: [])
    assert bool(r_empty) is False

def test_ranking_repr():
    """Test that repr(ranking) returns a readable summary."""
    r = Ranking(lambda: [(1, 0), (2, 1), (3, 2)])
    s = repr(r)
    assert s.startswith('<Ranking:')
    assert '3 items' in s or '[(1, 0),' in s
    r_empty = Ranking(lambda: [])
    assert '0 items' in repr(r_empty)
