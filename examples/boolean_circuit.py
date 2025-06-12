"""
Literate Example: Boolean Circuit (Python)

This example demonstrates ranked programming for a simple boolean circuit.

- Each input (a, b, c) is a ranked boolean: normally True, exceptionally False (rank 1).
- The circuit computes (a and b) or c, propagating uncertainty through the logic.
- Uses rlet to combine uncertainty across all variables.
- The output is a ranking of all possible circuit outputs, ranked by plausibility.

Note: All combinators yield only (value, rank) pairs as expected; no manual flattening is needed.

Run this file to see the ranked output for the boolean circuit.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, pr_all

def boolean_circuit():
    a = Ranking(lambda: nrm_exc(True, False, 1))
    b = Ranking(lambda: nrm_exc(True, False, 1))
    c = Ranking(lambda: nrm_exc(True, False, 1))
    def circuit(a, b, c):
        result = (a, b, c, (a and b) or c)
        return (result,)
    ranking = Ranking(lambda: rlet([
        ('a', a),
        ('b', b),
        ('c', c)
    ], circuit))
    print("Boolean circuit output ranking (inputs and output):")
    print("Rank  (a, b, c, output)")
    print("------------------------")
    debug_results = list(ranking)
    for (tup, rank) in debug_results:
        a, b, c, output = tup
        print(f"{rank:>4} ({a!r}, {b!r}, {c!r}, {output!r})")
    print("Done")

if __name__ == "__main__":
    boolean_circuit()
"""
Boolean circuit output ranking (inputs and output):
Rank  (a, b, c, output)
------------------------
    0 (True, True, True, True)
    1 (True, True, True, True)
    1 (True, True, True, True)
    2 (False, False, False, False)
    1 (True, True, True, True)
    2 (False, False, False, False)
    2 (True, True, True, True)
    3 (False, False, False, False)
Done
"""
