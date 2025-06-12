"""
Literate Example: Lazy Spelling Correction (Python, fully lazy)

This example demonstrates lazy ranked programming for spelling correction using lazy ranked choices.

- The goal is to correct the word 'hte' (intended: 'the').
- Possible corrections: 'the' (normal), 'hat', 'hit', 'hot', 'hoe' (exceptional, grouped).
- lazy_nrm_exc and lazy_either_of are used to model the ranking of corrections.
- The output is a lazy ranking of possible corrections, ranked by plausibility.

**Note:** This version relies on the API's idiomatic flattening. No local flattening or manual unwrapping is performed; all combinators yield only (value, rank) pairs as expected.

Run this file to see the ranked output for the spelling correction scenario, using the lazy API.
"""
from ranked_programming.rp_core import LazyRanking, lazy_nrm_exc, lazy_either_of

def pr_all_lazy(lr):
    """Pretty-print all (value, rank) pairs from a LazyRanking."""
    # No local flattening needed: lr is guaranteed to yield (value, rank) pairs
    items = list(lr)
    if not items:
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in items:
        print(f"{rank:>5} {v}")
    print("Done")

def spelling_correction_example():
    # Suppose we want to correct the word 'hte' (intended: 'the')
    # Possible corrections: 'the', 'hat', 'hit', 'hot', 'hoe'
    # Normally 'the', exceptionally others (all lazy)
    # No flattening needed: all combinators yield (value, rank) pairs
    ranking = LazyRanking(lambda: lazy_nrm_exc(
        'the',
        lazy_either_of(
            LazyRanking(lambda: lazy_nrm_exc('hat', 'hit', 1)),
            LazyRanking(lambda: lazy_nrm_exc('hot', 'hoe', 1))
        ),
        1
    ))
    print("Spelling correction output ranking (lazy):")
    pr_all_lazy(ranking)

if __name__ == "__main__":
    spelling_correction_example()
