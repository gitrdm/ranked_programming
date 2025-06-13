"""
Literate Example: Recursion (Python)

This example demonstrates ranked programming with recursion and ranked choices.

- The recur function: normally returns x, exceptionally recurses on x*2 (until x > 500), using nrm_exc and Ranking.
- The observe combinator is used to filter for values greater than 500.
- The output is a ranking of all possible values > 500, ranked by plausibility (number of recursions).

Note: All combinators yield only (value, rank) pairs as expected; no manual flattening is needed.

Run this file to see the ranked output for the recursive scenario.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, observe

def pr_all(lr, limit=10):
    """Pretty-print all (value, rank) pairs from a Ranking."""
    items = list(lr)
    if not items:
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in items[:limit]:
        print(f"{rank:>5} {v}")
    print("...")

def recur(x):
    # Normally return x, exceptionally recur on x*2 (as Ranking)
    def gen():
        yield (x, 0)
        if x <= 10000:  # Limit recursion to avoid RecursionError
            for v, r in recur(x * 2):
                yield (v, r + 1)
    return Ranking(gen)

def recursion_example():
    # Print the full ranking for recur(1) (no observation)
    print("Full recursion ranking (recur(1)):")
    pr_all(recur(1))
    # Print the observed ranking for values > 100
    print("\nObserved recursion ranking (values > 100):")
    ranking = Ranking(lambda: observe(lambda v: v > 100, recur(1)))
    pr_all(ranking)

if __name__ == "__main__":
    recursion_example()
