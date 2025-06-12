"""
Literate Example: Lazy Hidden Markov Model (Python, fully lazy)

This example demonstrates lazy ranked programming for a simple Hidden Markov Model (HMM) with two states.

- States: S0 (normal), S1 (exceptional).
- Transitions: normally stay in the same state, exceptionally switch (using lazy_nrm_exc).
- Emissions: each state emits a symbol, with normal and exceptional outcomes.
- lazy_rlet_star is used to model the sequence of states and emissions, propagating uncertainty through time.
- The output is a lazy ranking of all possible (s0, s1, e0, e1) tuples, ranked by plausibility.

**Note:** This version relies on the API's idiomatic flattening. No local flattening or manual unwrapping is performed; all combinators yield only (value, rank) pairs as expected.

Run this file to see the ranked output for the HMM scenario, using the lazy API.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star, pr_all

def hmm_example():
    # States: S0 (normal), S1 (exceptional)
    def transition(prev):
        return Ranking(lambda: nrm_exc('S0', 'S1', 1)) if prev == 'S0' else Ranking(lambda: nrm_exc('S1', 'S0', 1))
    def emission(state):
        return Ranking(lambda: nrm_exc('A', 'B', 1)) if state == 'S0' else Ranking(lambda: nrm_exc('B', 'A', 1))
    # Initial state
    s0 = Ranking(lambda: nrm_exc('S0', 'S1', 1))
    # lazy_rlet_star for sequence: s0, s1, e0, e1 (no flattening needed)
    ranking = Ranking(lambda: rlet_star([
        ('s0', s0),
        ('s1', transition),
        ('e0', lambda s0, s1: emission(s0)),
        ('e1', lambda s0, s1, e0: emission(s1)),
    ], lambda s0, s1, e0, e1: (s0, s1, e0, e1)))
    print("Hidden Markov Model output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    hmm_example()
