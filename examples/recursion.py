"""
Literate Example: Lazy Recursion (Python, fully lazy)

This example demonstrates lazy ranked programming with recursion and ranked choices.

- The recur function: normally returns x, exceptionally recurses on x*2 (until x > 500), using lazy_nrm_exc and LazyRanking.
- The lazy_observe combinator is used to filter for values greater than 500.
- The output is a lazy ranking of all possible values > 500, ranked by plausibility (number of recursions).

**Note:** This version relies on the API's idiomatic flattening. No local flattening or manual unwrapping is performed; all combinators yield only (value, rank) pairs as expected.

Run this file to see the ranked output for the recursive scenario, using the lazy API.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, observe

def pr_all(lr):
    """Pretty-print all (value, rank) pairs from a LazyRanking."""
    # No local flattening needed: lr is guaranteed to yield (value, rank) pairs
    items = list(lr)
    if not items:
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in items:
        print(f"{rank:>5} {v}")
    print("Done")

def recur(x):
    # Normally return x, exceptionally recur on x*2 (as LazyRanking)
    if x > 500:
        return Ranking(lambda: ((x, 0),))
    else:
        def gen():
            yield (x, 0)
            for v, r in recur(x * 2):
                yield (v, r + 1)
        return Ranking(gen)

def recursion_example():
    # Observe: value > 500 (lazy, no flattening needed)
    ranking = Ranking(lambda: observe(lambda v: v > 500, recur(1)))
    print("Recursion output ranking (values > 500, lazy):")
    pr_all(ranking)

if __name__ == "__main__":
    recursion_example()
