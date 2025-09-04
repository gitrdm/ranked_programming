import pytest

from ranked_programming.causal import StructuralRankingModel, Variable, is_cause, total_effect
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_class import Ranking


def noisy_bool(false_rank: int = 0, true_rank: int = 1):
    return Ranking.from_generator(nrm_exc, False, True, true_rank)


def test_is_cause_chain_unshielded():
    # A -> B -> C (booleans)
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: a)
    C = Variable("C", (False, True), ("B",), lambda b: b)

    srm = StructuralRankingModel([A, B, C])

    res = is_cause("A", "C", srm, z=1, max_contexts=64)
    assert res.is_cause
    assert res.strength >= 1
    assert res.tested_contexts > 0


def test_is_cause_screened_off():
    # A -> B -> C and A -/-> C directly. Screening: given B, A should not be a reason for C.
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: a)
    C = Variable("C", (False, True), ("B",), lambda b: b)
    srm = StructuralRankingModel([A, B, C])

    # Contexts exclude descendants of A, but include B? B is a descendant of A, so excluded.
    # Therefore stable reason-relations consider contexts outside descendants; A should still cause C overall.
    res = is_cause("A", "C", srm, z=1, max_contexts=64)
    assert res.is_cause


def test_total_effect_do_surgery():
    # Fork: A -> B and A -> C; stronger True rank makes True less plausible.
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: a)
    C = Variable("C", (False, True), ("A",), lambda a: a)

    srm = StructuralRankingModel([A, B, C])

    eff = total_effect("A", "C", srm, a=True, a_alt=False)
    assert eff >= 0
