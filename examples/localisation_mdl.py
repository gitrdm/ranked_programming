"""
MDL Example: Localisation with MDL-based evidence penalty.

This example demonstrates how to use mdl_evidence_penalty to set the evidence penalty for a predicate on localisation output.
"""
from ranked_programming.rp_core import Ranking
from ranked_programming.mdl_utils import mdl_evidence_penalty
from ranked_programming.ranking_observe import observe_e
from localisation import hmm

def pred(path):
    # Example: require path to end at (1, 0)
    return path[-1] == (1, 0)

obs_seq = [
    (0, 3), (2, 3), (3, 3), (3, 2), (4, 1), (2, 1), (3, 0), (1, 0)
]
ranking = list(hmm(obs_seq, initial_state=(0, 3)))
penalty = mdl_evidence_penalty(ranking, pred)
print(f"MDL penalty for evidence: {penalty}")
observed = list(observe_e(penalty, pred, ranking))
print("Observed ranking (MDL penalty):")
for v, r in observed:
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_e(1, pred, ranking))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed:
    print(f"  {v}: rank {r}")
