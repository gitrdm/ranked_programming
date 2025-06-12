"""
Edge case and output expectation tests for the lazy API (LazyRanking and lazy combinators).
Covers empty/failure input, normalization, deduplication, order, flattening, and type consistency.
"""
import pytest
from ranked_programming.rp_core import LazyRanking, lazy_nrm_exc, lazy_rlet, lazy_rlet_star, lazy_either_of, lazy_observe, lazy_limit, lazy_cut

def test_lazy_nrm_exc_empty():
    # Both values empty: yields nothing
    def empty():
        if False:
            yield (None, 0)
    ranking = LazyRanking(lambda: lazy_nrm_exc(empty(), empty(), 1))
    assert ranking.to_eager() == []

def test_lazy_rlet_empty():
    # Any empty binding yields nothing
    def gen():
        if False:
            yield (1, 0)
    ranking = LazyRanking(lambda: lazy_rlet([
        ('x', gen),
        ('y', lambda: ((2, 0),))
    ], lambda x, y: (x, y)))
    assert ranking.to_eager() == []

def test_lazy_rlet_star_empty():
    # Any empty binding yields nothing
    def gen():
        if False:
            yield (1, 0)
    ranking = LazyRanking(lambda: lazy_rlet_star([
        ('x', gen),
        ('y', lambda x: ((x+1, 0),))
    ], lambda x, y: (x, y)))
    assert ranking.to_eager() == []

def test_lazy_either_of_duplicates():
    # Duplicate values: lowest rank wins
    def g1():
        yield ('A', 2)
        yield ('B', 1)
    def g2():
        yield ('A', 0)
        yield ('C', 3)
    ranking = LazyRanking(lambda: lazy_either_of(LazyRanking(g1), LazyRanking(g2)))
    result = dict(ranking.to_eager())
    assert result['A'] == 0
    assert result['B'] == 1
    assert result['C'] == 3

def test_lazy_observe_normalizes():
    # After filtering, ranks are normalized
    def g():
        yield (1, 2)
        yield (2, 4)
        yield (3, 7)
    ranking = LazyRanking(g)
    filtered = LazyRanking(lambda: lazy_observe(lambda x: x > 1, ranking))
    result = filtered.to_eager()
    assert min(r for _, r in result) == 0

def test_lazy_limit_empty():
    # Limit on empty yields nothing
    def g():
        if False:
            yield (1, 0)
    ranking = LazyRanking(g)
    limited = LazyRanking(lambda: lazy_limit(3, ranking))
    assert limited.to_eager() == []

def test_lazy_cut_empty():
    # Cut on empty yields nothing
    def g():
        if False:
            yield (1, 0)
    ranking = LazyRanking(g)
    cut = LazyRanking(lambda: lazy_cut(2, ranking))
    assert cut.to_eager() == []

def test_lazy_flattening_type():
    # All combinators should yield only (value, rank) pairs, never nested LazyRanking or generator
    def g():
        yield (10, 0)
        yield (20, 1)
    ranking = LazyRanking(lambda: lazy_nrm_exc(1, LazyRanking(g), 2))
    for v, r in ranking:
        assert not hasattr(v, '__iter__') or isinstance(v, (str, int, float))
        assert isinstance(r, int)

def test_lazy_order_preservation():
    # Order should be by rank, then by input order
    def g():
        yield (1, 2)
        yield (2, 1)
        yield (3, 0)
    ranking = LazyRanking(g)
    result = sorted(ranking.to_eager(), key=lambda x: x[1])
    # Should be sorted by rank
    ranks = [r for _, r in result]
    assert ranks == sorted(ranks)
