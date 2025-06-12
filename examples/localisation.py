"""
Literate Example: Robot Localisation (Python)

This example demonstrates ranked programming for a simple robot localisation problem.

- The robot can be in one of three locations: A, B, or C.
- Initial belief: normally at A, exceptionally at B or C (using nested nrm_exc).
- The robot moves: normally stays, exceptionally moves to the next location.
- The sensor: normally correct, exceptionally reports 'unknown'.
- rlet_star is used to model the sequence of states and observations, propagating uncertainty.
- The output is a ranking of all possible (l0, l1, s1) tuples, ranked by plausibility.

Note: All combinators yield only (value, rank) pairs as expected; no manual flattening is needed.

Run this file to see the ranked output for the robot localisation scenario.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star, pr_all

def localisation_example():
    # Locations: A, B, C
    # Initial belief: normally at A, exceptionally at B or C (fully lazy, flat)
    def initial():
        yield ('A', 0)
        yield ('B', 1)
        yield ('C', 2)
    initial_lr = Ranking(initial)
    # Move: normally stays, exceptionally moves to next
    def move(loc):
        if loc == 'A':
            return Ranking(lambda: nrm_exc('A', 'B', 1))
        elif loc == 'B':
            return Ranking(lambda: nrm_exc('B', 'C', 1))
        else:
            return Ranking(lambda: nrm_exc('C', 'A', 1))
    # Sensor: normally correct, exceptionally wrong
    def sense(loc):
        return Ranking(lambda: nrm_exc(loc, 'unknown', 1))
    # No flattening needed: all combinators yield (value, rank) pairs
    ranking = Ranking(lambda: rlet_star([
        ('l0', initial_lr),
        ('l1', move),
        ('s1', lambda l0, l1: sense(l1))
    ], lambda l0, l1, s1: (l0, l1, s1)))
    print("Robot localisation output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    localisation_example()
