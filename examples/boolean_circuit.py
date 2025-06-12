"""
Example: Boolean Circuit (Python port)
This example demonstrates ranked programming for a simple boolean circuit, analogous to the Racket example.
"""
from ranked_programming.rp_api import construct_ranking, nrm_exc, rlet, observe, pr_all

def boolean_circuit():
    # Define ranked booleans: normally True, exceptionally False (rank 1)
    a = nrm_exc(True, False, 1)
    b = nrm_exc(True, False, 1)
    c = nrm_exc(True, False, 1)
    # Circuit: (a and b) or c
    def circuit(a, b, c):
        return (a and b) or c
    # Use rlet to combine uncertainty
    ranking = rlet({'a': a, 'b': b, 'c': c}, circuit)
    print("Boolean circuit output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    boolean_circuit()
