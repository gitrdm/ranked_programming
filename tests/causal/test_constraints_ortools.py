import unittest
import os

from ranked_programming.causal.srm import StructuralRankingModel, Variable
from ranked_programming.causal.constraints import (
    CPSATMinimalRepair,
    CPSATSeparatingSetFinder,
    SeparatingSetRequest,
)
from ranked_programming.causal.ranked_pc import ranked_ci
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


@unittest.skipUnless("ORTOOLS_AVAILABLE" in os.environ, "OR-Tools not installed or not enabled")
class TestCPSATBackends(unittest.TestCase):
    def setUp(self):
        X = Variable("X", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
        Z = Variable("Z", (False, True), ("X",), lambda x: x)
        Y = Variable("Y", (False, True), ("Z",), lambda z: z)
        self.srm = StructuralRankingModel([X, Z, Y])

    def test_cpsat_separating_set(self):
        finder = CPSATSeparatingSetFinder()
        req = SeparatingSetRequest(x="X", y="Y", candidates=["Z"], k_max=1)
        Zset = finder.find(req, self.srm, ranked_ci)
        self.assertEqual(Zset, {"Z"})

    def test_cpsat_minimal_repair(self):
        strat = CPSATMinimalRepair()
        repairs = strat.repairs(self.srm, target="Y", desired_value=True, candidates=["Z", "X"], max_size=1)
        self.assertTrue(any({"Z"} == s or {"X"} == s for s in repairs))


if __name__ == "__main__":
    unittest.main()
