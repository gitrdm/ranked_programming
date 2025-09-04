import unittest

from ranked_programming.causal.srm import StructuralRankingModel, Variable
from ranked_programming.causal.identification import (
    is_backdoor_admissible,
    backdoor_adjusted_effect,
    is_frontdoor_applicable,
    frontdoor_effect,
)
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


class TestIdentificationBackdoor(unittest.TestCase):
    def setUp(self):
        # DAG: U -> A -> B, and U -> B (confounding). Z blocks backdoor if Z={U}.
        U = Variable(
            name="U",
            domain=(False, True),
            parents=(),
            mechanism=lambda: Ranking.from_generator(nrm_exc, False, True, 1),
        )
        A = Variable(
            name="A",
            domain=(False, True),
            parents=("U",),
            mechanism=lambda u: u,  # A := U deterministically
        )
        B = Variable(
            name="B",
            domain=(False, True),
            parents=("A", "U"),
            mechanism=lambda a, u: (a or u),  # B := A ∨ U
        )
        self.srm = StructuralRankingModel([U, A, B])

    def test_backdoor_check(self):
        self.assertTrue(is_backdoor_admissible("A", "B", ["U"], self.srm))
        self.assertFalse(is_backdoor_admissible("A", "B", [], self.srm))

    def test_backdoor_adjusted_effect(self):
        tau = backdoor_adjusted_effect("A", "B", ["U"], self.srm, a=True, a_alt=False)
        self.assertIsInstance(tau, (int, float))


class TestIdentificationFrontdoor(unittest.TestCase):
    def setUp(self):
        # Frontdoor: A -> M -> B, with U -> A and U -> B (unobserved confounder simulated)
        U = Variable(
            name="U",
            domain=(False, True),
            parents=(),
            mechanism=lambda: Ranking.from_generator(nrm_exc, False, True, 1),
        )
        A = Variable(
            name="A",
            domain=(False, True),
            parents=("U",),
            mechanism=lambda u: u,  # A := U
        )
        M = Variable(
            name="M",
            domain=(False, True),
            parents=("A",),
            mechanism=lambda a: a,  # M := A
        )
        B = Variable(
            name="B",
            domain=(False, True),
            parents=("M", "U"),
            mechanism=lambda m, u: (m or u),  # B := M ∨ U
        )
        self.srm = StructuralRankingModel([U, A, M, B])

    def test_frontdoor_applicability(self):
        self.assertTrue(is_frontdoor_applicable("A", "M", "B", self.srm))

    def test_frontdoor_effect(self):
        tau = frontdoor_effect("A", "M", "B", self.srm, a=True, a_alt=False)
        self.assertIsInstance(tau, (int, float))


if __name__ == "__main__":
    unittest.main()
