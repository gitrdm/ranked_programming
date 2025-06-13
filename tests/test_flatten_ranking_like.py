"""
Unit tests for _flatten_ranking_like in rp_core.py.

Covers all expected behaviors for flattening Ranking, generators, iterables, and atomic values.
"""
import types
import pytest
from ranked_programming.rp_core import _flatten_ranking_like, Ranking

def test_flatten_ranking_with_ranking():
    """Test flattening a Ranking object with rank offset."""
    r = Ranking(lambda: [(1, 0), (2, 1)])
    result = list(_flatten_ranking_like(r, 2))
    assert result == [(1, 2), (2, 3)]

def test_flatten_ranking_with_generator_of_pairs():
    """Test flattening a generator of (value, rank) pairs with rank offset."""
    def gen():
        yield (10, 0)
        yield (20, 5)
    g = gen()
    result = list(_flatten_ranking_like(g, 3))
    assert result == [(10, 3), (20, 8)]

def test_flatten_ranking_with_generator_of_values():
    """Test flattening a generator of values (not pairs) with rank offset."""
    def gen():
        yield 'a'
        yield 'b'
    g = gen()
    result = list(_flatten_ranking_like(g, 7))
    assert result == [('a', 7), ('b', 7)]

def test_flatten_ranking_with_list():
    """Test flattening a list (should treat as atomic value)."""
    result = list(_flatten_ranking_like([1, 2, 3], 4))
    assert result == [([1, 2, 3], 4)]

def test_flatten_ranking_with_atomic():
    """Test flattening an atomic value (should yield (value, rank_offset))."""
    result = list(_flatten_ranking_like(42, 5))
    assert result == [(42, 5)]
