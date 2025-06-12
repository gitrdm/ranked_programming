"""
Literate Example: Ranked Procedure Call (Python)

This example demonstrates ranked function application using rlet_star.

- The operation (op) is uncertain: normally addition, exceptionally multiplication (using nrm_exc).
- The argument (arg) is uncertain: normally 10, exceptionally 20 (using nrm_exc).
- rlet_star is used to apply the uncertain operation to the uncertain argument.
- The output is a ranking of all possible results, ranked by plausibility.

Note: All combinators yield only (value, rank) pairs as expected; no manual flattening is needed.

Run this file to see the ranked output for the uncertain procedure call.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star, pr_all

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
