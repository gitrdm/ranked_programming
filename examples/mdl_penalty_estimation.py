"""
MDL Penalty Estimation: Five Practical Approaches
=================================================

This example demonstrates five ways to estimate the MDL (Minimum Description Length) penalty for evidence in ranked programming, when the set of possible worlds is too large or expensive to enumerate.

Each approach is illustrated with a simple k-bit boolean circuit, where the predicate is that the output is True. The approaches are:

1. Sampling
2. Symbolic/Analytic Counting
3. Upper/Lower Bounds
4. Approximate/Heuristic Penalties
5. Incremental/Adaptive Estimation

All code is written in a literate, Sphinx-compatible style and can be used as a reference for practical MDL estimation.
"""
import random
import math
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, TERMINATE_RANK

def circuit_output(inputs):
    # Example: AND of all bits
    return all(inputs)

def all_k_bit_inputs(k):
    """Generate all k-bit tuples."""
    return [tuple((i >> j) & 1 for j in reversed(range(k))) for i in range(2**k)]

def random_k_bit_input(k):
    """Generate a random k-bit tuple."""
    return tuple(random.randint(0, 1) for _ in range(k))

k = 10  # Large enough to make full enumeration expensive (2^10 = 1024)
pred = lambda x: circuit_output(x)

# 1. Sampling
"""
Sampling: Estimate N and M by randomly sampling possible worlds.
"""
sample_size = 200
sample = [random_k_bit_input(k) for _ in range(sample_size)]
M_sample = sum(1 for x in sample if pred(x))
N_est = 2 ** k
M_est = int(M_sample * (N_est / sample_size)) if sample_size > 0 else 0
penalty_sampling = math.ceil(math.log2(N_est / M_est)) if M_est > 0 else TERMINATE_RANK

# 2. Symbolic/Analytic Counting
"""
Symbolic/Analytic Counting: Use combinatorics or logic to count N and M.
For AND, only (1,1,...,1) satisfies, so M=1, N=2^k.
"""
M_analytic = 1
penalty_analytic = math.ceil(math.log2(N_est / M_analytic))

# 3. Upper/Lower Bounds
"""
Upper/Lower Bounds: Use known bounds for N and M.
Suppose we know at least 1 and at most 10 inputs satisfy the predicate.
"""
M_lower, M_upper = 1, 10
penalty_lower = math.ceil(math.log2(N_est / M_upper))
penalty_upper = math.ceil(math.log2(N_est / M_lower))

# 4. Approximate/Heuristic Penalties
"""
Approximate/Heuristic: Use domain knowledge to set a penalty.
Suppose we know the evidence is rare, so we set penalty = k (number of bits).
"""
penalty_heuristic = k

# 5. Incremental/Adaptive Estimation
"""
Incremental/Adaptive: Start with a small sample, refine as more computation is feasible.
"""
small_sample_size = 10
small_sample = [random_k_bit_input(k) for _ in range(small_sample_size)]
M_small = sum(1 for x in small_sample if pred(x))
M_small_est = int(M_small * (N_est / small_sample_size)) if small_sample_size > 0 else 0
penalty_adaptive = math.ceil(math.log2(N_est / M_small_est)) if M_small_est > 0 else TERMINATE_RANK

# Print results
print("MDL Penalty Estimation for k =", k)
print("1. Sampling:", penalty_sampling)
print("2. Symbolic/Analytic:", penalty_analytic)
print(f"3. Bounds: lower={penalty_lower}, upper={penalty_upper}")
print("4. Heuristic:", penalty_heuristic)
print("5. Incremental/Adaptive:", penalty_adaptive)

# Example: Apply one of the penalties to a sampled ranking
ranking_sample = [(x, 0) for x in sample]
observed = list(observe_e(penalty_sampling, pred, ranking_sample))
print(f"\nObserved ranking (sampling penalty): {len(observed)} values, first 5:")
for v, r in observed[:5]:
    print(f"  {v}: rank {r}")
