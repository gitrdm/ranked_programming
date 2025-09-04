import pytest

from ranked_programming.causal import (
    StructuralRankingModel,
    Variable,
    MinimalRepairSolver,
    RepairSearchConfig,
    root_cause_chain,
)
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


def noisy_bool():
    return Ranking.from_generator(nrm_exc, False, True, 1)


def test_minimal_repairs_chain():
    # A -> B -> C; desire C=True, candidates {A,B}
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: a)
    C = Variable("C", (False, True), ("B",), lambda b: b)
    srm = StructuralRankingModel([A, B, C])

    solver = MinimalRepairSolver()
    repairs = solver.repairs(srm, target="C", desired_value=True, candidates=["A", "B"])

    # Either A or B set to True should suffice minimally
    as_sets = [set(r) for r in repairs]
    assert {"A"} in as_sets or {"B"} in as_sets


def test_root_cause_chain_paths():
    # A -> B -> C; repair {A}
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: a)
    C = Variable("C", (False, True), ("B",), lambda b: b)
    srm = StructuralRankingModel([A, B, C])

    chains = root_cause_chain(srm, ["A"], "C")
    assert ["A", "B", "C"] in chains
