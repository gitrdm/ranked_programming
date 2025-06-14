import pytest
from ranked_programming.ranking_utils import is_rank, is_ranking

def test_is_rank():
    assert is_rank(0)
    assert is_rank(5)
    assert is_rank(999999)
    assert is_rank(float('inf'))
    assert not is_rank(-1)
    assert not is_rank(-100)
    assert not is_rank(3.5)
    assert not is_rank('a')
    assert not is_rank(None)
    assert not is_rank(float('-inf'))

def test_is_ranking():
    assert is_ranking([(1, 0), (2, 1), (3, 2)])
    assert is_ranking([('a', 0), ('b', 5), ('c', float('inf'))])
    assert is_ranking([])
    assert not is_ranking([(1, -1), (2, 0)])  # negative rank
    assert not is_ranking([(1, 0), (2, 'a')])  # non-integer rank
    assert not is_ranking([(1, 0, 1)])  # tuple of wrong length
    assert not is_ranking([1, 2, 3])  # not tuples
    assert not is_ranking('not a ranking')
    assert not is_ranking(None)
    assert not is_ranking([(1, 0), (2,)])
