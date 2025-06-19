"""
Example: Boolean circuit with MDL-based result penalty in observe_r.

This example demonstrates how to use the mdl_evidence_penalty utility to set the result_strength penalty in observe_r, and compares it to a fixed penalty. This is analogous to using MDL for evidence, but applies the penalty to the result predicate. The output is for illustration and is not part of regression tests.
"""
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_observe import observe_r
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

# Compute MDL penalty for result (using the same utility as for evidence)
result_penalty = mdl_evidence_penalty(ranking, pred)
if result_penalty >= 10**9:
    print("MDL penalty for result: impossible (no satisfying assignments)")
else:
    print(f"MDL penalty for result: {result_penalty}")
# Apply result penalty with MDL
observed_ranking = list(observe_r(result_penalty, pred, ranking))

print("Observed ranking (MDL result penalty):")
for v, r in observed_ranking:
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_r(1, pred, ranking))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed:
    print(f"  {v}: rank {r}")
