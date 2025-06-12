"""
Literate Example: Lazy Ranked Procedure Call (Python, fully lazy)

This example demonstrates lazy ranked function application using lazy_rlet_star.

- The operation (op) is uncertain: normally addition, exceptionally multiplication (using lazy_nrm_exc).
- The argument (arg) is uncertain: normally 10, exceptionally 20 (using lazy_nrm_exc).
- lazy_rlet_star is used to apply the uncertain operation to the uncertain argument.
- The output is a lazy ranking of all possible results, ranked by plausibility.

**Note:** This version relies on the API's idiomatic flattening. No local flattening or manual unwrapping is performed; all combinators yield only (value, rank) pairs as expected.

Run this file to see the ranked output for the uncertain procedure call, using the lazy API.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star

def pr_all(lr):
    items = list(lr)
    if not items:
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in items:
        print(f"{rank:>5} {v}")
    print("Done")

def ranked_procedure_call_example():
    # Uncertain operation: normally add, exceptionally multiply (lazy)
    op = Ranking(lambda: nrm_exc(lambda x, y: x + y, lambda x, y: x * y, 1))
    # Uncertain argument: normally 10, exceptionally 20 (lazy)
    arg = Ranking(lambda: nrm_exc(10, 20, 1))
    # Apply uncertain operation to uncertain argument using lazy_rlet_star (no flattening needed)
    ranking = Ranking(lambda: rlet_star([
        ('op', op),
        ('arg', arg)
    ], lambda op, arg: op(5, arg)))
    print("Ranked procedure call output (lazy):")
    pr_all(ranking)

if __name__ == "__main__":
    ranked_procedure_call_example()
