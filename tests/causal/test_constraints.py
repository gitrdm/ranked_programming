import unittest

from ranked_programming.causal.srm import StructuralRankingModel, Variable
from ranked_programming.causal.constraints import (
    GreedySeparatingSetFinder,
    SeparatingSetRequest,
    EnumerationMinimalRepair,
    Inequality,
    CounterexampleFinder,
)
from ranked_programming.causal.ranked_pc import ranked_ci
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


class TestConstraintsStrategies(unittest.TestCase):
    def setUp(self):
        # Simple chain X->Z->Y, where CI(X,Y|Z) should hold (with noisy links)
        X = Variable("X", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
        Z = Variable("Z", (False, True), ("X",), lambda x: x)
        Y = Variable("Y", (False, True), ("Z",), lambda z: z)
        self.srm = StructuralRankingModel([X, Z, Y])

    def test_greedy_separating_set(self):
        finder = GreedySeparatingSetFinder()
        req = SeparatingSetRequest(x="X", y="Y", candidates=["Z"], k_max=1)
        Zset = finder.find(req, self.srm, ranked_ci)
        self.assertEqual(Zset, {"Z"})

    def test_enumeration_minimal_repair(self):
        strat = EnumerationMinimalRepair()
        # Target Y True by repairing Z or X
        repairs = strat.repairs(self.srm, target="Y", desired_value=True, candidates=["Z", "X"], max_size=1)
        self.assertTrue(any({"Z"} == s or {"X"} == s for s in repairs))

    def test_counterexample_finder(self):
        # Inequality: world must satisfy Y==Z. This holds in this chain.
        ineq = Inequality(predicate=lambda w: (w.get("Y") == w.get("Z")))
        cf = CounterexampleFinder()
        w = cf.find_violation(self.srm, ineq, max_worlds=10)
        self.assertIsNone(w)


if __name__ == "__main__":
    unittest.main()
