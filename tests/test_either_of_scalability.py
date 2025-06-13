"""
Unit tests for either_of combinator, including large and streaming input cases.
"""
from ranked_programming.rp_core import Ranking, either_of

def test_either_of_small():
    """Test either_of with a few small rankings."""
    r1 = Ranking(lambda: [(1, 0), (2, 1)])
    r2 = Ranking(lambda: [(2, 0), (3, 2)])
    result = list(either_of(r1, r2))
    # Should yield (1,0), (2,0), (3,2) in some order
    assert set(result) == {(1,0), (2,0), (3,2)}
    # Each value should have its minimal rank
    assert dict(result)[2] == 0

def test_either_of_large():
    """Test either_of with many rankings (scalability)."""
    rankings = [Ranking(lambda i=i: [(i, i)]) for i in range(1000)]
    result = list(either_of(*rankings))
    assert len(result) == 1000
    for i in range(1000):
        assert (i, i) in result

def test_either_of_streaming():
    """Test either_of with generators that yield values lazily."""
    def gen(start):
        for i in range(start, start+5):
            yield (i, i-start)
    r1 = Ranking(lambda: gen(0))
    r2 = Ranking(lambda: gen(3))
    # r1: (0,0),(1,1),(2,2),(3,3),(4,4); r2: (3,0),(4,1),(5,2),(6,3),(7,4)
    result = list(either_of(r1, r2))
    # 0,1,2 from r1; 3,4 from r2 (lower rank); 5,6,7 from r2
    expected = {(0,0),(1,1),(2,2),(3,0),(4,1),(5,2),(6,3),(7,4)}
    assert set(result) == expected
    # 3 and 4 should have minimal ranks from r2
    assert dict(result)[3] == 0
    assert dict(result)[4] == 1
