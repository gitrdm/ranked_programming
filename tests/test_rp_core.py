"""
Unit tests for error handling and type safety in Ranking combinators.
"""
import pytest
from ranked_programming.rp_core import Ranking, nrm_exc

def test_nrm_exc_type_error():
    """Test that nrm_exc raises TypeError for invalid rank2 type."""
    with pytest.raises(TypeError):
        list(nrm_exc(1, 2, 'not-an-int'))

def test_ranking_slots():
    """Test that Ranking uses __slots__ and disallows arbitrary attributes."""
    r = Ranking(lambda: [(1, 0)])
    with pytest.raises(AttributeError):
        r.foo = 42

def test_ranked_apply_racket_examples():
    from ranked_programming.rp_core import ranked_apply, nrm_exc, Ranking
    # 1. Deterministic: ($ + 5 10)
    result = list(ranked_apply(lambda x, y: x + y, 5, 10))
    assert result == [(15, 0)]

    # 2. Uncertain argument: ($ + 5 (nrm/exc 10 20))
    arg = Ranking(lambda: nrm_exc(10, 20))
    result = list(ranked_apply(lambda x, y: x + y, 5, arg))
    assert (15, 0) in result and (25, 1) in result and len(result) == 2

    # 3. Uncertain function and argument: ($ (nrm/exc + *) 5 (nrm/exc 10 20))
    import operator
    op = Ranking(lambda: nrm_exc(operator.add, operator.mul))
    arg = Ranking(lambda: nrm_exc(10, 20))
    result = list(ranked_apply(lambda f, x, y: f(x, y), op, 5, arg))
    # Possible (value, rank): (15,0), (25,1), (50,1), (100,2)
    expected = set([(15,0), (25,1), (50,1), (100,2)])
    assert set(result) == expected
