"""
Example: Spelling Correction (Python port)

This example demonstrates ranked programming for spelling correction using ranked choices.

- The goal is to correct the word 'hte' (intended: 'the').
- Possible corrections: 'the' (normal), 'hat', 'hit', 'hot', 'hoe' (exceptional, grouped).
- nrm_exc and either_of are used to model the ranking of corrections.
- The output is a ranking of possible corrections, ranked by plausibility.

Run this file to see the ranked output for the spelling correction scenario.
"""
from ranked_programming.rp_api import nrm_exc, either_of, pr_all

def spelling_correction_example():
    # Suppose we want to correct the word 'hte' (intended: 'the')
    # Possible corrections: 'the', 'hat', 'hit', 'hot', 'hoe'
    # Normally 'the', exceptionally others
    ranking = nrm_exc('the', either_of(
        nrm_exc('hat', 'hit', 1),
        nrm_exc('hot', 'hoe', 1)
    ), 1)
    print("Spelling correction output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    spelling_correction_example()
