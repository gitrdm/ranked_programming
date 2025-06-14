import pytest
from ranked_programming.rp_core import Ranking, nrm_exc, either_or

def test_either_or_atomic():
    # (either/or "ann" "bob" "charlie")
    result = list(either_or("ann", "bob", "charlie"))
    assert set(result) == {("ann", 1), ("bob", 1), ("charlie", 1)}
    assert len(result) == 3

def test_either_or_with_nrm_exc():
    # (pr (nrm/exc "peter" (either/or "ann" "bob" "charlie")))
    ranking = Ranking(lambda: nrm_exc("peter", either_or("ann", "bob", "charlie", base_rank=0)))
    result = list(ranking)
    assert ("peter", 0) in result
    assert ("ann", 1) in result
    assert ("bob", 1) in result
    assert ("charlie", 1) in result
    assert len(result) == 4

def test_either_or_of_rankings():
    # (either/or (nrm/exc "peter" "ann") (nrm/exc "bob" "charly"))
    r1 = Ranking(lambda: nrm_exc("peter", "ann"))
    r2 = Ranking(lambda: nrm_exc("bob", "charly"))
    result = list(either_or(r1, r2))
    assert ("peter", 0) in result
    assert ("bob", 0) in result
    assert ("ann", 1) in result
    assert ("charly", 1) in result
    assert len(result) == 4
