"""
Example: Boolean circuit with MDL-based evidence penalty.

This example demonstrates how to use the mdl_evidence_penalty utility to set the evidence penalty in observe_e, and compares it to a fixed penalty. The output is for illustration and is not part of regression tests.
"""
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty

def circuit_output(inputs):
    # Simple AND circuit for illustration
    return inputs[0] and inputs[1] and inputs[2]

# All possible 3-bit inputs
inputs = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
# Assign rank 0 to all
ranking = [(inp, 0) for inp in inputs]

# Predicate: output must be True
pred = lambda x: circuit_output(x) == 1

# Compute MDL penalty
penalty = mdl_evidence_penalty(ranking, pred)

# Apply evidence with MDL penalty
observed_ranking = list(observe_e(penalty, pred, ranking))

print(f"MDL penalty for evidence: {penalty}")
print("Observed ranking (MDL penalty):")
for v, r in observed_ranking:
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_e(1, pred, ranking))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed:
    print(f"  {v}: rank {r}")
