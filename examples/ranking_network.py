"""
Example: Ranking Network (Python port)

This example demonstrates ranked programming for a simple ranking network.

- Nodes x and y are uncertain, each with a normal and exceptional value.
- Node z depends on x and y: normally z = x + y, exceptionally z = x * y.
- rlet is used to combine uncertainty across the network.
- The output is a ranking of all possible z values, ranked by plausibility.

Run this file to see the ranked output for the ranking network.
"""
from ranked_programming.rp_api import nrm_exc, rlet, pr_all

def ranking_network_example():
    # Nodes: x, y, z
    # x: normally 1, exceptionally 2
    # y: normally 2, exceptionally 3
    # z: normally x + y, exceptionally x * y
    x = nrm_exc(1, 2, 1)
    y = nrm_exc(2, 3, 1)
    def z(x, y):
        return nrm_exc(x + y, x * y, 1)
    ranking = rlet({'x': x, 'y': y}, lambda x, y: z(x, y))
    print("Ranking network output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    ranking_network_example()
