"""
Tests for nrm_exc combinator to match Racket semantics and examples.
"""
from ranked_programming.rp_core import Ranking, nrm_exc
import itertools

def test_nrm_exc_default_rank():
    r = Ranking(lambda: nrm_exc("foo", "bar"))
    result = sorted(r.to_eager(), key=lambda x: x[1])
    assert result == [("foo", 0), ("bar", 1)]

def test_nrm_exc_custom_rank():
    r = Ranking(lambda: nrm_exc("foo", "bar", 2))
    result = sorted(r.to_eager(), key=lambda x: x[1])
    assert result == [("foo", 0), ("bar", 2)]

def test_nrm_exc_nested():
    r = Ranking(lambda: nrm_exc("foo", nrm_exc("bar", "baz")))
    result = sorted(r.to_eager(), key=lambda x: x[1])
    assert result == [("foo", 0), ("bar", 1), ("baz", 2)]

def test_nrm_exc_deeply_nested():
    # nrm_exc("a", nrm_exc("b", nrm_exc("c", "d")))
    r = Ranking(lambda: nrm_exc("a", nrm_exc("b", nrm_exc("c", "d"))))
    result = sorted(r.to_eager(), key=lambda x: x[1])
    assert result == [("a", 0), ("b", 1), ("c", 2), ("d", 3)]

def test_nrm_exc_recursive_doubling():
    """
    Racket example:
        (define (recur x) (nrm/exc x (recur (* x 2))))
        (pr (recur 1))
    Should yield:
        Rank  Value
        0     1
        1     2
        2     4
        3     8
        4     16
        ...
    """
    def recur(x):
        return nrm_exc(x, lambda: recur(x * 2))
    r = Ranking(lambda: recur(1))
    # Only take the first 10 results to avoid infinite recursion
    result = list(itertools.islice(r, 10))
    # Check the first 10 results
    expected = [(2**i, i) for i in range(10)]
    for (val, rank), (exp_val, exp_rank) in zip(result, expected):
        assert val == exp_val
        assert rank == exp_rank
