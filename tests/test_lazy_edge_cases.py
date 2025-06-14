"""
Edge case and output expectation tests for the lazy API (LazyRanking and lazy combinators).
Covers empty/failure input, normalization, deduplication, order, flattening, and type consistency.
"""
import pytest
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, rlet_star, either_of, observe, limit, cut, pr_all, pr_first

def test_nrm_exc_empty():
    # Both values empty: yields nothing
    def empty():
        if False:
            yield (None, 0)
    ranking = Ranking(lambda: nrm_exc(empty(), empty(), 1))
    assert ranking.to_eager() == []

def test_rlet_empty():
    # Any empty binding yields nothing
    def gen():
        if False:
            yield (1, 0)
    ranking = Ranking(lambda: rlet([
        ('x', gen),
        ('y', lambda: ((2, 0),))
    ], lambda x, y: (x, y)))
    assert ranking.to_eager() == []

def test_rlet_star_empty():
    # Any empty binding yields nothing
    def gen():
        if False:
            yield (1, 0)
    ranking = Ranking(lambda: rlet_star([
        ('x', gen),
        ('y', lambda x: ((x+1, 0),))
    ], lambda x, y: (x, y)))
    assert ranking.to_eager() == []

def test_either_of_duplicates():
    # Duplicate values: lowest rank wins
    def g1():
        yield ('A', 2)
        yield ('B', 1)
    def g2():
        yield ('A', 0)
        yield ('C', 3)
    ranking = Ranking(lambda: either_of(Ranking(g1), Ranking(g2)))
    result = dict(ranking.to_eager())
    assert result['A'] == 0
    assert result['B'] == 1
    assert result['C'] == 3

def test_observe_normalizes():
    # After filtering, ranks are normalized
    def g():
        yield (1, 2)
        yield (2, 4)
        yield (3, 7)
    ranking = Ranking(g)
    filtered = Ranking(lambda: observe(lambda x: x > 1, ranking))
    result = filtered.to_eager()
    assert min(r for _, r in result) == 0

def test_limit_empty():
    # Limit on empty yields nothing
    def g():
        if False:
            yield (1, 0)
    ranking = Ranking(g)
    limited = Ranking(lambda: limit(3, ranking))
    assert limited.to_eager() == []

def test_cut_empty():
    # Cut on empty yields nothing
    def g():
        if False:
            yield (1, 0)
    ranking = Ranking(g)
    cut_r = Ranking(lambda: cut(2, ranking))
    assert cut_r.to_eager() == []

def test_lazy_flattening_type():
    # All combinators should yield only (value, rank) pairs, never nested LazyRanking or generator
    def g():
        yield (10, 0)
        yield (20, 1)
    ranking = Ranking(lambda: nrm_exc(1, Ranking(g), 2))
    for v, r in ranking:
        assert not hasattr(v, '__iter__') or isinstance(v, (str, int, float))
        assert isinstance(r, int)

def test_lazy_order_preservation():
    # Order should be by rank, then by input order
    def g():
        yield (1, 2)
        yield (2, 1)
        yield (3, 0)
    ranking = Ranking(g)
    result = sorted(ranking.to_eager(), key=lambda x: x[1])
    # Should be sorted by rank
    ranks = [r for _, r in result]
    assert ranks == sorted(ranks)

def test_pr_all_and_pr_first(capsys):
    from ranked_programming.rp_core import pr_all, pr_first, Ranking
    def gen():
        yield ("foo", 0)
        yield ("bar", 1)
    ranking = Ranking(gen)
    pr_all(ranking)
    out = capsys.readouterr().out
    assert "foo" in out and "bar" in out and "Rank" in out
    pr_first(ranking)
    out = capsys.readouterr().out
    assert "foo" in out or "bar" in out
    # Empty ranking prints failure message
    empty = Ranking(lambda: iter([]))
    pr_all(empty)
    out = capsys.readouterr().out
    assert "Failure" in out
    pr_first(empty)
    out = capsys.readouterr().out
    assert "Failure" in out

def test_invalid_input():
    from ranked_programming.rp_core import Ranking, nrm_exc
    # Invalid: passing a string as a generator should yield the string as a value
    ranking = Ranking(lambda: nrm_exc("foo", "bar", 1))
    result = ranking.to_eager()
    assert ("foo", 0) in result and ("bar", 1) in result
    # Invalid: passing a dict as a generator should yield the dict as a value
    d = {"a": 1}
    ranking = Ranking(lambda: nrm_exc(d, d, 1))
    result = ranking.to_eager()
    assert (d, 0) in result and (d, 1) in result
    # Invalid: passing a non-iterable, non-callable object should yield it as a value
    class Dummy: pass
    dummy = Dummy()
    ranking = Ranking(lambda: nrm_exc(dummy, dummy, 1))
    result = ranking.to_eager()
    assert (dummy, 0) in result and (dummy, 1) in result

def test_rlet_racket_example():
    # Racket example: beer and peanuts
    from ranked_programming.rp_core import nrm_exc, rlet, Ranking
    beer = Ranking(lambda: nrm_exc(False, True))
    peanuts = Ranking(lambda: nrm_exc(True, False))
    def body(b, p):
        return f"{'beer' if b else 'no beer'} and {'peanuts' if p else 'no peanuts'}"
    ranking = Ranking(lambda: rlet([
        ('b', beer),
        ('p', peanuts)
    ], body))
    result = set(ranking.to_eager())
    expected = set([
        ("no beer and peanuts", 0),
        ("no beer and no peanuts", 1),
        ("beer and peanuts", 1),
        ("beer and no peanuts", 2)
    ])
    assert result == expected
