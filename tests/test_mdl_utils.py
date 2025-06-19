import pytest
from ranked_programming.mdl_utils import mdl_evidence_penalty

def test_mdl_evidence_penalty_basic():
    ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
    # Predicate matches half
    assert mdl_evidence_penalty(ranking, lambda x: x % 2 == 0) == 1  # log2(4/2) = 1
    # Predicate matches one
    assert mdl_evidence_penalty(ranking, lambda x: x == 1) == 2  # log2(4/1) = 2
    # Predicate matches all
    assert mdl_evidence_penalty(ranking, lambda x: True) == 0  # log2(4/4) = 0
    # Predicate matches none
    assert mdl_evidence_penalty(ranking, lambda x: False) == float('inf')
    # Empty ranking
    assert mdl_evidence_penalty([], lambda x: True) == float('inf')
