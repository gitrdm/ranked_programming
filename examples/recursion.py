"""
Example: Recursion (Python port)

This example demonstrates ranked programming with recursion and ranked choices.

- The recur function: normally returns x, exceptionally recurses on x*2 (until x > 500).
- The observe combinator is used to filter for values greater than 500.
- The output is a ranking of all possible values > 500, ranked by plausibility (number of recursions).

Run this file to see the ranked output for the recursive scenario.
"""
from ranked_programming.rp_api import nrm_exc, observe, pr_all

def recur(x):
    # Normally return x, exceptionally recur on x*2
    return nrm_exc(x, recur(x * 2), 1) if x <= 500 else x

def recursion_example():
    # Observe: value > 500
    ranking = observe(lambda v: v > 500, recur(1))
    print("Recursion output ranking (values > 500):")
    pr_all(ranking)

if __name__ == "__main__":
    recursion_example()
