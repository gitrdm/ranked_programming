"""
Example: Robot Localisation (Python port)
Demonstrates ranked programming for a simple robot localisation problem.
"""
from ranked_programming.rp_api import nrm_exc, rlet_star, pr_all

def localisation_example():
    # Locations: A, B, C
    # Initial belief: normally at A, exceptionally at B or C
    initial = nrm_exc('A', nrm_exc('B', 'C', 1), 1)
    # Move: normally stays, exceptionally moves to next
    def move(loc):
        if loc == 'A':
            return nrm_exc('A', 'B', 1)
        elif loc == 'B':
            return nrm_exc('B', 'C', 1)
        else:
            return nrm_exc('C', 'A', 1)
    # Sensor: normally correct, exceptionally wrong
    def sense(loc):
        return nrm_exc(loc, 'unknown', 1)
    ranking = rlet_star([
        ('l0', initial),
        ('l1', lambda l0: move(l0)),
        ('s1', lambda l0, l1: sense(l1))
    ], lambda l0, l1, s1: (l0, l1, s1))
    print("Robot localisation output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    localisation_example()
