"""
Unit tests for Ranking.from_generator classmethod.

Covers construction from generator-based combinators and argument passing.
"""
import pytest
from ranked_programming.rp_core import Ranking, nrm_exc, rlet

def test_from_generator_nrm_exc():
    """
    Test constructing a Ranking from nrm_exc using from_generator.
    """
    r = Ranking.from_generator(nrm_exc, 1, 2, 1)
    result = r.to_eager()
    assert (1, 0) in result
    assert (2, 1) in result
    assert len(result) == 2

def test_from_generator_rlet():
    """
    Test constructing a Ranking from rlet using from_generator.
    Each binding value should be a generator or Ranking, not a plain list.
    """
    def gen1():
        yield (1, 0)
        yield (2, 0)
    def gen2():
        yield (10, 0)
        yield (20, 0)
    r = Ranking.from_generator(rlet, [('x', Ranking(gen1)), ('y', Ranking(gen2))], lambda x, y: (x, y))
    result = r.to_eager()
    values = [v for v, _ in result]
    assert (1, 10) in values
    assert (2, 20) in values
    assert len(result) == 4

def test_from_generator_kwargs():
    """
    Test that from_generator passes keyword arguments correctly.
    """
    def gen(x, y=0):
        yield (x + y, 0)
    r = Ranking.from_generator(gen, 5, y=7)
    result = r.to_eager()
    assert result == [(12, 0)]
