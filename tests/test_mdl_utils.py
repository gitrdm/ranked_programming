import pytest
from ranked_programming.mdl_utils import mdl_evidence_penalty, TERMINATE_RANK
from ranked_programming.ranking_observe import observe_e_x

def test_mdl_evidence_penalty_basic():
    ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
    # Predicate matches half
    assert mdl_evidence_penalty(ranking, lambda x: x % 2 == 0) == 1  # log2(4/2) = 1
    # Predicate matches one
    assert mdl_evidence_penalty(ranking, lambda x: x == 1) == 2  # log2(4/1) = 2
    # Predicate matches all
    assert mdl_evidence_penalty(ranking, lambda x: True) == 0  # log2(4/4) = 0
    # Predicate matches none
    assert mdl_evidence_penalty(ranking, lambda x: False) == TERMINATE_RANK
    # Empty ranking
    assert mdl_evidence_penalty([], lambda x: True) == TERMINATE_RANK

def test_observe_e_x_with_mdl_penalty():
    # Simple ranking: 1 at 0, 2 at 1, 3 at 2, 4 at 3
    ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
    # Predicate matches half
    pred = lambda x: x % 2 == 0
    penalty = mdl_evidence_penalty(ranking, pred)
    result = list(observe_e_x(penalty, pred, ranking))
    # Should penalize odds by penalty, then normalize
    # odds: (1, penalty), (3, penalty+2); evens: (2,1), (4,3)
    # After normalization, lowest rank is 0
    min_rank = min(r for _, r in result)
    assert min_rank == 0
    # If predicate matches none, penalty is TERMINATE_RANK
    pred_none = lambda x: False
    penalty_none = mdl_evidence_penalty(ranking, pred_none)
    assert penalty_none == TERMINATE_RANK
    result_none = list(observe_e_x(penalty_none, pred_none, ranking))
    # All get TERMINATE_RANK, so normalized ranks should match original differences
    ranks = [r for _, r in result_none]
    assert ranks == [0, 1, 2, 3], f"Ranks after normalization: {ranks}"
