"""
MDL Example: Ranked Let with MDL-based evidence penalty.

This example demonstrates how to use mdl_evidence_penalty to set the evidence penalty for a predicate on ranked let output.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, rlet_star
from ranked_programming.mdl_utils import mdl_evidence_penalty
from ranked_programming.ranking_observe import observe_e

def pred(result):
    # Example: require both beer and peanuts
    return result == 'beer and peanuts'

# Independent uncertainty: beer and peanuts (lazy)
b = Ranking(lambda: nrm_exc(False, True, 1))
p = Ranking(lambda: nrm_exc(True, False, 1))
ranking = Ranking(lambda: rlet([
    ('b', b),
    ('p', p)
], lambda b, p: f"{'beer' if b else 'no beer'} and {'peanuts' if p else 'no peanuts'}"))
ranking_list = list(ranking)
penalty = mdl_evidence_penalty(ranking_list, pred)
print(f"MDL penalty for evidence: {penalty}")
observed = list(observe_e(penalty, pred, ranking_list))
print("Observed ranking (MDL penalty):")
for v, r in observed:
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_e(1, pred, ranking_list))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed:
    print(f"  {v}: rank {r}")
