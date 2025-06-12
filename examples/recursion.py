"""
Example: Recursion (Python port)
Demonstrates ranked programming with recursion and ranked choices.
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
