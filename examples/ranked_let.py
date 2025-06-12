"""
Example: Ranked Let (Python port)

This example demonstrates the use of rlet and rlet_star for modeling independent and dependent uncertainty.

- Independent uncertainty: beer and peanuts are chosen independently, each with their own ranking.
- Dependent uncertainty: peanut consumption depends on whether beer is consumed, modeled with rlet_star.
- The output shows how uncertainty propagates through both independent and dependent choices.

Run this file to see the ranked outputs for both independent and dependent uncertainty scenarios.
"""
from ranked_programming.rp_api import nrm_exc, rlet, rlet_star, pr_all

def ranked_let_example():
    # Independent uncertainty: beer and peanuts
    def beer_and_peanuts(b, p):
        return f"{'beer' if b else 'no beer'} and {'peanuts' if p else 'no peanuts'}"
    b = nrm_exc(False, True, 1)  # Normally don't drink beer
    p = nrm_exc(True, False, 1)  # Normally eat peanuts
    print("Independent uncertainty (rlet):")
    pr_all(rlet({'b': b, 'p': p}, beer_and_peanuts))

    # Dependent uncertainty: peanut consumption depends on beer
    def peanuts_depends_on_beer(b):
        return nrm_exc(True, False, 1) if b else nrm_exc(False, True, 1)
    print("\nDependent uncertainty (rlet_star):")
    pr_all(rlet_star([
        ('b', b),
        ('p', peanuts_depends_on_beer)
    ], beer_and_peanuts))

if __name__ == "__main__":
    ranked_let_example()
