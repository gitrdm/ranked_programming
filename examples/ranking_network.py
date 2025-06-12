"""
Literate Example: Ranking Network (Python)

This example demonstrates ranked programming for a simple ranking network.

- Nodes x and y are uncertain, each with a normal and exceptional value (using nrm_exc).
- Node z depends on x and y: normally z = x + y, exceptionally z = x * y (using nrm_exc).
- rlet is used to combine uncertainty across the network.
- The output is a ranking of all possible z values, ranked by plausibility.

Note: All combinators yield only (value, rank) pairs as expected; no manual flattening is needed.

Run this file to see the ranked output for the ranking network.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, pr_all

def ranking_network_example():
    # Nodes: x, y, z (all lazy)
    x = Ranking(lambda: nrm_exc(1, 2, 1))
    y = Ranking(lambda: nrm_exc(2, 3, 1))
    def z(x, y):
        return Ranking(lambda: nrm_exc(x + y, x * y, 1))
    ranking = Ranking(lambda: rlet([
        ('x', x),
        ('y', y)
    ], lambda x, y: z(x, y)))
    print("Ranking network output ranking (lazy):")
    pr_all(ranking)

if __name__ == "__main__":
    ranking_network_example()
