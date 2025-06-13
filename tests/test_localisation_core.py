"""
TDD test for the observable and hmm internals in localisation.py
"""
from examples.localisation import observable, neighbouring

def test_observable_yields_pairs():
    s = (1, 2)
    obs = list(observable(s))
    # Should yield 1 normal and 8 exceptional values
    assert any(cell == s and rank == 0 for cell, rank in obs), "Normal value missing"
    assert sum(rank == 1 for cell, rank in obs) == 8, "Should have 8 exceptional values"
    assert all(isinstance(cell, tuple) and isinstance(rank, int) for cell, rank in obs), "All outputs should be (cell, rank) pairs"

def test_neighbouring():
    s = (1, 2)
    n = neighbouring(s)
    assert set(n) == {(0,2), (2,2), (1,1), (1,3)}, f"Unexpected neighbours: {n}"

if __name__ == "__main__":
    test_observable_yields_pairs()
    test_neighbouring()
    print("localisation core tests passed")
