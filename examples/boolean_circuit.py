"""
Literate Example: Lazy Boolean Circuit (Python, fully lazy)

This example demonstrates lazy ranked programming for a simple boolean circuit.

- Each input (a, b, c) is a lazy ranked boolean: normally True, exceptionally False (rank 1).
- The circuit computes (a and b) or c, propagating uncertainty through the logic.
- Uses lazy_rlet to combine uncertainty across all variables.
- The output is a lazy ranking of all possible circuit outputs, ranked by plausibility.

**Note:** This version relies on the API's idiomatic flattening. No local flattening or manual unwrapping is performed; all combinators yield only (value, rank) pairs as expected.

Run this file to see the ranked output for the boolean circuit, using the lazy API.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet

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

def boolean_circuit():
    a = Ranking(lambda: nrm_exc(True, False, 1))
    b = Ranking(lambda: nrm_exc(True, False, 1))
    c = Ranking(lambda: nrm_exc(True, False, 1))
    def circuit(a, b, c):
        return (a and b) or c
    ranking = Ranking(lambda: rlet([
        ('a', a),
        ('b', b),
        ('c', c)
    ], circuit))
    print("Boolean circuit output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    boolean_circuit()
