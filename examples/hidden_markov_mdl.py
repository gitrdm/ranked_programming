"""
MDL Example: Hidden Markov Model with MDL-based evidence penalty.

This example demonstrates how to use mdl_evidence_penalty to set the evidence penalty for a predicate on HMM output.
"""
from ranked_programming.rp_core import Ranking
from ranked_programming.mdl_utils import mdl_evidence_penalty
from ranked_programming.ranking_observe import observe_e
from hidden_markov import hmm

def pred(result):
    emissions, states = result  # Fix: unpack directly
    return all(e == 'yes' for e in emissions)

obs = ['yes', 'yes', 'yes', 'yes', 'yes']
ranking = list(hmm(obs))
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
