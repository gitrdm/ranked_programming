"""
Edge case and additional TDD tests for rp_core.py combinators and Ranking methods.
"""
import pytest
from ranked_programming.rp_core import Ranking, nrm_exc, either_of, limit, cut, observe, observe_e, observe_all, ranked_apply, pr_all, pr_first

def test_ranking_map_and_filter():
    r = Ranking(lambda: [(1, 0), (2, 1), (3, 2)])
    mapped = r.map(lambda x: x * 10)
    assert mapped.to_eager() == [(10, 0), (20, 1), (30, 2)]
    filtered = r.filter(lambda x: x > 1)
    assert filtered.to_eager() == [(2, 1), (3, 2)]
    # Empty ranking
    r_empty = Ranking(lambda: [])
    assert r_empty.map(lambda x: x).to_eager() == []
    assert r_empty.filter(lambda x: True).to_eager() == []

def test_either_of_all_empty():
    r = Ranking(lambda: either_of(Ranking(lambda: []), Ranking(lambda: [])))
    assert r.to_eager() == []

def test_either_of_single():
    r = Ranking(lambda: either_of([(1, 0), (2, 1)]))
    assert r.to_eager() == [(1, 0), (2, 1)]

def test_either_of_infinite():
    def inf():
        n = 0
        while n < 5:
            yield (n, n)
            n += 1
    r = Ranking(lambda: either_of(inf()))
    assert r.to_eager() == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

def test_limit_zero_and_cut_negative():
    r = Ranking(lambda: [(1, 0), (2, 1)])
    assert list(limit(0, r)) == []
    assert list(cut(-1, r)) == []

def test_limit_infinite():
    def inf():
        n = 0
        while True:
            yield (n, n)
            n += 1
    r = Ranking(lambda: inf())
    limited = Ranking(lambda: limit(3, r))
    assert limited.to_eager() == [(0, 0), (1, 1), (2, 2)]

def test_observe_all_fail_and_pass():
    r = Ranking(lambda: [(1, 0), (2, 1)])
    # All fail
    assert list(observe(lambda x: False, r)) == []
    # All pass: ranks are normalized so min is 0, but others may be >0
    result = list(observe(lambda x: True, r))
    assert (1, 0) in result
    assert any(rk == 0 for _, rk in result)

def test_observe_e_and_all_empty_predicates():
    r = Ranking(lambda: [(1, 0), (2, 1)])
    # All fail, evidence added: ranks are normalized so min is 0
    result = list(observe_e(5, lambda x: False, r))
    assert (1, 0) in result
    assert any(rk == 0 for _, rk in result)
    # Empty predicates list
    result = list(observe_all(r, []))
    assert set(result) == {(1, 0), (2, 1)}

def test_ranked_apply_no_args():
    called = []
    def f():
        called.append(1)
        return 42
    result = list(ranked_apply(f))
    assert result == [(42, 0)]
    assert called

def test_ranked_apply_mixed_args():
    r = Ranking(lambda: [(1, 0), (2, 1)])
    result = list(ranked_apply(lambda x, y: x + y, r, 10))
    assert result == [(11, 0), (12, 1)]

def test_pr_all_and_pr_first_single_and_nonstring(capsys):
    r = Ranking(lambda: [(42, 0)])
    pr_all(r)
    out = capsys.readouterr().out
    assert "42" in out
    pr_first(r)
    out = capsys.readouterr().out
    assert "42" in out
    # Non-string value
    r2 = Ranking(lambda: [((1, 2), 0)])
    pr_all(r2)
    out = capsys.readouterr().out
    assert "(1, 2)" in out
    pr_first(r2)
    out = capsys.readouterr().out
    assert "(1, 2)" in out
