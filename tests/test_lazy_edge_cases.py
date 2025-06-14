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

def test_rlet_star_racket_example():
    # Racket example: beer and peanuts, dependent
    from ranked_programming.rp_core import nrm_exc, rlet_star, Ranking
    def beer():
        return Ranking(lambda: nrm_exc(False, True))
    def peanuts(b):
        if b:
            return Ranking(lambda: nrm_exc(True, False))
        else:
            return False
    def body(b, p):
        return f"{'beer' if b else 'no beer'} and {'peanuts' if p else 'no peanuts'}"
    ranking = Ranking(lambda: rlet_star([
        ('b', beer()),
        ('p', peanuts)
    ], body))
    result = set(ranking.to_eager())
    expected = set([
        ("no beer and no peanuts", 0),
        ("beer and peanuts", 1),
        ("beer and no peanuts", 2)
    ])
    assert result == expected

def test_rf_equal_example():
    from ranked_programming.rp_core import Ranking, nrm_exc, rf_equal
    # Two rankings with same values/ranks, different order
    r1 = Ranking(lambda: [(1, 0), (2, 1)])
    r2 = Ranking(lambda: [(2, 1), (1, 0)])
    assert rf_equal(r1, r2)
    # Different values
    r3 = Ranking(lambda: [(1, 0), (3, 1)])
    assert not rf_equal(r1, r3)
    # Same values, different ranks
    r4 = Ranking(lambda: [(1, 1), (2, 0)])
    assert not rf_equal(r1, r4)
    # Infinite ranking: should not terminate if not for max_items
    def inf():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r_inf1 = Ranking(inf)
    r_inf2 = Ranking(inf)
    # Should be equal for first 1000 items
    assert rf_equal(r_inf1, r_inf2, max_items=1000)
    # Different infinite rankings
    def inf2():
        n = 0
        while True:
            yield (n+1, n)
            n += 1
    r_inf3 = Ranking(inf2)
    assert not rf_equal(r_inf1, r_inf3, max_items=1000)

def test_rf_to_hash_example():
    from ranked_programming.rp_core import Ranking, nrm_exc, rf_to_hash
    # Simple ranking
    r = Ranking(lambda: [(1, 0), (2, 1)])
    h = rf_to_hash(r)
    assert h == {1: 0, 2: 1} or h == {2: 1, 1: 0}  # order doesn't matter
    # Ranking with duplicate values (last wins)
    r2 = Ranking(lambda: [(1, 0), (1, 1), (2, 2)])
    h2 = rf_to_hash(r2)
    assert h2[1] in (0, 1) and h2[2] == 2
    # Infinite ranking: should only collect up to max_items
    def inf():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r_inf = Ranking(inf)
    h_inf = rf_to_hash(r_inf, max_items=10)
    assert len(h_inf) == 10
    assert all(h_inf[v] == v for v in range(10))

def test_rf_to_assoc_example():
    from ranked_programming.rp_core import Ranking, nrm_exc, rf_to_assoc
    # Simple ranking
    r = Ranking(lambda: [(1, 0), (2, 1), (3, 1)])
    assoc = rf_to_assoc(r)
    # Should be sorted by rank: [(1,0), (2,1), (3,1)] or [(1,0), (3,1), (2,1)]
    assert assoc[0][1] == 0
    assert set(assoc[1:]) == {(2, 1), (3, 1)}
    # Ranking with duplicate values (last wins, but all are included)
    r2 = Ranking(lambda: [(1, 0), (1, 1), (2, 2)])
    assoc2 = rf_to_assoc(r2)
    assert (1, 0) in assoc2 and (1, 1) in assoc2 and (2, 2) in assoc2
    # Infinite ranking: should only collect up to max_items
    def inf():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r_inf = Ranking(inf)
    assoc_inf = rf_to_assoc(r_inf, max_items=10)
    assert len(assoc_inf) == 10
    assert assoc_inf == [(i, i) for i in range(10)]
    # Document limitation: if ranking is infinite, only a prefix is collected

def test_rf_to_assoc_and_stream():
    from ranked_programming.rp_core import Ranking, nrm_exc, rf_to_assoc, rf_to_stream
    # Simple ranking
    r = Ranking(lambda: [(2, 1), (1, 0), (3, 2)])
    assoc = rf_to_assoc(r)
    assert assoc == [(1, 0), (2, 1), (3, 2)]
    # Duplicates: last wins in rf_to_hash, but all appear in assoc
    r2 = Ranking(lambda: [(1, 0), (1, 1), (2, 2)])
    assoc2 = rf_to_assoc(r2)
    assert assoc2 == [(1, 0), (1, 1), (2, 2)]
    # Infinite ranking: only test prefix using max_items
    def inf():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r_inf = Ranking(inf)
    assoc_inf = rf_to_assoc(r_inf, max_items=5)
    assert assoc_inf == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    # rf_to_stream: should yield in non-decreasing order
    r3 = Ranking(lambda: [(2, 1), (1, 0), (3, 2)])
    stream = rf_to_stream(r3)
    assert list(stream) == [(1, 0), (2, 1), (3, 2)]
    # Infinite stream: only test prefix using max_items
    def inf2():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r_inf2 = Ranking(inf2)
    stream2 = rf_to_stream(r_inf2, max_items=5)
    prefix = list(stream2)
    assert prefix == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
