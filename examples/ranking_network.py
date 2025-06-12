"""
Example: Ranking Network (Python port)
Demonstrates ranked programming for a simple ranking network.
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
