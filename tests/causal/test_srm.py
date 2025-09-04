import pytest

from ranked_programming.causal import StructuralRankingModel, Variable
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_class import Ranking


def bool_noise():
    # Simple boolean with False at rank 0, True at rank 1
    return nrm_exc(False, True, 1)


def test_srm_topo_and_joint_ranking_deterministic_child():
    # A ~ nrm_exc(False@0, True@1)
    A = Variable(
        name="A",
        domain=(False, True),
        parents=(),
        mechanism=lambda: Ranking.from_generator(nrm_exc, False, True, 1),
    )
    # B := A deterministically
    B = Variable(
        name="B",
        domain=(False, True),
        parents=("A",),
        mechanism=lambda a: a,
    )

    srm = StructuralRankingModel([A, B])
    assert srm.variables() in (["A", "B"], ["B", "A"])  # topo order valid either way

    joint = srm.to_ranking()
    items = sorted(joint.to_eager(), key=lambda x: x[1])
    # Expect two assignments: {A: False, B: False} at rank 0; {A: True, B: True} at rank 1
    values = [v for v, _ in items]
    ranks = [r for _, r in items]
    assert {"A": False, "B": False} in values
    assert {"A": True, "B": True} in values
    # Minimal ranks should be 0 and 1 respectively
    d = {tuple(sorted(val.items())): r for val, r in items}
    assert d[tuple(sorted({"A": False, "B": False}.items()))] == 0
    assert d[tuple(sorted({"A": True, "B": True}.items()))] == 1


def test_srm_do_surgery_on_root():
    # A is noisy boolean
    A = Variable(
        name="A",
        domain=(False, True),
        parents=(),
        mechanism=lambda: Ranking.from_generator(nrm_exc, False, True, 1),
    )
    # B := A deterministically
    B = Variable(
        name="B",
        domain=(False, True),
        parents=("A",),
        mechanism=lambda a: a,
    )

    srm = StructuralRankingModel([A, B])

    # Intervene do(A=True): A becomes constant True@0, B follows deterministically
    do_model = srm.do({"A": True})
    items = list(do_model.to_ranking())
    assert items == [({"A": True, "B": True}, 0)]


def test_srm_do_surgery_on_child_ignores_parents():
    # A is noisy
    A = Variable(
        name="A",
        domain=(False, True),
        parents=(),
        mechanism=lambda: Ranking.from_generator(nrm_exc, False, True, 1),
    )
    # B := A deterministically
    B = Variable(
        name="B",
        domain=(False, True),
        parents=("A",),
        mechanism=lambda a: a,
    )

    srm = StructuralRankingModel([A, B])

    # Intervene do(B=False): B becomes constant False@0 regardless of A
    do_model = srm.do({"B": False})
    items = sorted(do_model.to_ranking().to_eager(), key=lambda x: x[1])
    assert items[0] == ({"A": False, "B": False}, 0)
    assert items[1] == ({"A": True, "B": False}, 1)


def test_srm_cycle_detection():
    # Create a simple cycle A <- B <- A
    A = Variable(
        name="A",
        domain=(0, 1),
        parents=("B",),
        mechanism=lambda b: b,
    )
    B = Variable(
        name="B",
        domain=(0, 1),
        parents=("A",),
        mechanism=lambda a: a,
    )
    with pytest.raises(ValueError):
        StructuralRankingModel([A, B])
