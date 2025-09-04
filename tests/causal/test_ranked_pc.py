import pytest

from ranked_programming.causal import StructuralRankingModel, Variable
from ranked_programming.causal.ranked_pc import ranked_ci, pc_skeleton
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


def noisy_bool():
    return Ranking.from_generator(nrm_exc, False, True, 1)

def copy_noisy(x: bool, ex_rank: int = 2):
    # Prefer the input value at rank 0, the opposite at rank ex_rank
    return Ranking.from_generator(nrm_exc, x, (not x), ex_rank)


def test_ranked_ci_chain():
    # X -> Z -> Y; expect CI(X, Y | Z)
    X = Variable("X", (False, True), (), lambda: noisy_bool())
    Z = Variable("Z", (False, True), ("X",), lambda x: copy_noisy(x, 2))
    Y = Variable("Y", (False, True), ("Z",), lambda z: copy_noisy(z, 2))
    srm = StructuralRankingModel([X, Z, Y])

    assert ranked_ci("X", "Y", ["Z"], srm, epsilon=0.0, max_contexts=64)
    assert not ranked_ci("X", "Y", [], srm, epsilon=0.0, max_contexts=64)


def test_ranked_ci_fork():
    # X -> Y and X -> Z; Y and Z dependent unconditionally, independent given X
    X = Variable("X", (False, True), (), lambda: noisy_bool())
    Y = Variable("Y", (False, True), ("X",), lambda x: copy_noisy(x, 2))
    Z = Variable("Z", (False, True), ("X",), lambda x: copy_noisy(x, 2))
    srm = StructuralRankingModel([X, Y, Z])

    assert not ranked_ci("Y", "Z", [], srm)
    assert ranked_ci("Y", "Z", ["X"], srm)


def test_pc_skeleton_chain_and_v_struct():
    # Chain: A -> B -> C. Expect edges: A-B, B-C; no A-C. No v-structure here.
    A = Variable("A", (False, True), (), lambda: noisy_bool())
    B = Variable("B", (False, True), ("A",), lambda a: copy_noisy(a, 2))
    C = Variable("C", (False, True), ("B",), lambda b: copy_noisy(b, 2))
    srm = StructuralRankingModel([A, B, C])

    res = pc_skeleton(["A", "B", "C"], srm, k_max=2)
    assert ("A", "B") in res.edges or ("B", "A") in res.edges
    assert ("B", "C") in res.edges or ("C", "B") in res.edges
    assert ("A", "C") not in res.edges and ("C", "A") not in res.edges

    # Collider: A -> C <- B should orient A->C and B->C
    A2 = Variable("A2", (False, True), (), lambda: noisy_bool())
    B2 = Variable("B2", (False, True), (), lambda: noisy_bool())
    C2 = Variable("C2", (False, True), ("A2", "B2"), lambda a, b: a and b)
    srm2 = StructuralRankingModel([A2, B2, C2])

    res2 = pc_skeleton(["A2", "B2", "C2"], srm2, k_max=2)
    assert ("A2", "C2") in res2.oriented
    assert ("B2", "C2") in res2.oriented
