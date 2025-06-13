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
    # Fault variables (as in Racket)
    N = Ranking(lambda: nrm_exc(True, False, 1))
    O1 = Ranking(lambda: nrm_exc(True, False, 1))
    O2 = Ranking(lambda: nrm_exc(True, False, 1))
    def circuit(N, O1, O2):
        # Inputs are fixed as in the Racket example: i1 = False, i2 = False, i3 = True
        i1, i2, i3 = False, False, True
        l1 = (not i1) if N else False
        l2 = (l1 or i2) if O1 else False
        out = (l2 or i3) if O2 else False
        return (N, O1, O2, out)
    ranking = Ranking(lambda: rlet([
        ('N', N),
        ('O1', O1),
        ('O2', O2)
    ], circuit))
    print("Boolean circuit output ranking (faults and output):")
    print("Rank  (N, O1, O2, output)")
    print("------------------------")
    debug_results = list(ranking)
    for (tup, rank) in debug_results:
        N, O1, O2, output = tup
        print(f"{rank:>4} ({N!r}, {O1!r}, {O2!r}, {output!r})")
    print("Done")

if __name__ == "__main__":
    boolean_circuit()
"""
Boolean circuit output ranking (faults and output):
Rank  (N, O1, O2, output)
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
