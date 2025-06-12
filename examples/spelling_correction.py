"""
Example: Spelling Correction (Python port)
Demonstrates ranked programming for spelling correction using ranked choices.
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
