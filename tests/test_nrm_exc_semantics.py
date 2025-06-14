"""
Tests for nrm_exc combinator to match Racket semantics and examples.
"""
from ranked_programming.rp_core import Ranking, nrm_exc

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
