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
