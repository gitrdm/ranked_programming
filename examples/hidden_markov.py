"""
Example: Hidden Markov Model (Python port)

This example demonstrates ranked programming for a simple Hidden Markov Model (HMM) with two states.

- States: S0 (normal), S1 (exceptional).
- Transitions: normally stay in the same state, exceptionally switch (using nrm_exc).
- Emissions: each state emits a symbol, with normal and exceptional outcomes.
- rlet_star is used to model the sequence of states and emissions, propagating uncertainty through time.
- The output is a ranking of all possible (s0, s1, e0, e1) tuples, ranked by plausibility.

Run this file to see the ranked output for the HMM scenario.
"""
from ranked_programming.rp_api import nrm_exc, rlet_star, pr_all

def hmm_example():
    # States: S0 (normal), S1 (exceptional)
    def transition(prev):
        return nrm_exc('S0', 'S1', 1) if prev == 'S0' else nrm_exc('S1', 'S0', 1)
    def emission(state):
        return nrm_exc('A', 'B', 1) if state == 'S0' else nrm_exc('B', 'A', 1)
    # Initial state
    s0 = nrm_exc('S0', 'S1', 1)
    # rlet_star for sequence: s0, s1, e0, e1
    ranking = rlet_star([
        ('s0', s0),
        ('s1', lambda s0: transition(s0)),
        ('e0', lambda s0, s1: emission(s0)),
        ('e1', lambda s0, s1, e0: emission(s1)),  # FIX: accept s0, s1, e0
    ], lambda s0, s1, e0, e1: (s0, s1, e0, e1))
    print("Hidden Markov Model output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    hmm_example()
