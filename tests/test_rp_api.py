# test_rp_api.py
import pytest
from ranked_programming.rp_api import construct_from_assoc, truth, ranking
from ranked_programming.rp_core import Ranking

# Only test the currently implemented API functions

def test_construct_from_assoc():
    assoc = [("a", 0), ("b", 1), ("c", 2)]
    r = construct_from_assoc(assoc)
    assert isinstance(r, Ranking)
    assert r.to_assoc() == assoc

def test_truth():
    r = truth(5)
    assert isinstance(r, Ranking)
    assert r.to_assoc() == [(5, 0)]

def test_ranking_predicate():
    r = truth(42)
    assert ranking(r)
    assert not ranking(42)
    assert not ranking([1, 2, 3])

def test_api_failure():
    from ranked_programming.rp_api import failure
    r = failure()
    assert isinstance(r, Ranking)
    assert r.is_empty()
    assert r.to_assoc() == []

def test_api_construct_ranking():
    from ranked_programming.rp_api import construct_ranking
    r = construct_ranking((1, 0), (2, 1))
    assert isinstance(r, Ranking)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    r_empty = construct_ranking()
    assert r_empty.is_empty()

def test_api_normalise():
    from ranked_programming.rp_api import normalise
    from ranked_programming.rp_api import construct_ranking
    r = construct_ranking((1, 2), (2, 4), (3, 7))
    normed = normalise(r)
    assert normed.to_assoc() == [(1, 0), (2, 2), (3, 5)]
    # Already normalised
    r2 = construct_ranking((1, 0), (2, 2), (3, 5))
    assert normalise(r2).to_assoc() == [(1, 0), (2, 2), (3, 5)]
    # Empty ranking stays empty
    from ranked_programming.rp_api import failure
    assert normalise(failure()).is_empty()

def test_api_map_value():
    from ranked_programming.rp_api import map_value, construct_ranking, failure
    r = construct_ranking((1, 2), (2, 4), (3, 7))
    mapped = map_value(lambda x: x * 10, r)
    assert mapped.to_assoc() == [(10, 2), (20, 4), (30, 7)]
    # Mapping over empty ranking returns empty
    assert map_value(lambda x: x + 1, failure()).is_empty()

def test_api_shift():
    from ranked_programming.rp_api import shift, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 2), (3, 5))
    shifted = shift(10, r)
    assert shifted.to_assoc() == [(1, 10), (2, 12), (3, 15)]
    # Shifting an empty ranking returns empty
    assert shift(5, failure()).is_empty()

def test_api_filter_ranking():
    from ranked_programming.rp_api import filter_ranking, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    filtered = filter_ranking(lambda x: x % 2 == 0, r)
    assert filtered.to_assoc() == [(2, 1), (4, 3)]
    # Filtering an empty ranking returns empty
    assert filter_ranking(lambda x: True, failure()).is_empty()

def test_api_filter_after():
    from ranked_programming.rp_api import filter_after, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    filtered = filter_after(lambda x: x > 2, r)
    assert filtered.to_assoc() == [(3, 2), (4, 3)]
    # Filtering after on empty ranking returns empty
    assert filter_after(lambda x: True, failure()).is_empty()

def test_api_up_to_rank():
    from ranked_programming.rp_api import up_to_rank, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    upto = up_to_rank(2, r)
    assert upto.to_assoc() == [(1, 0), (2, 1), (3, 2)]
    # up_to_rank on empty ranking returns empty
    assert up_to_rank(2, failure()).is_empty()

def test_api_dedup():
    from ranked_programming.rp_api import dedup, construct_ranking, failure
    r = construct_ranking((1, 0), (1, 1), (2, 2), (2, 3))
    deduped = dedup(r)
    assert deduped.to_assoc() == [(1, 0), (2, 2)]
    # dedup on empty ranking returns empty
    assert dedup(failure()).is_empty()

def test_api_do_with():
    from ranked_programming.rp_api import do_with, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1))
    result = do_with(lambda x, y: x + y, r)
    assert result == (1 + 0) + (2 + 1)
    # do_with on empty ranking returns 0
    assert do_with(lambda x, y: x + y, failure()) == 0

def test_api_rf_to_hash_and_assoc():
    from ranked_programming.rp_api import rf_to_hash, rf_to_assoc, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (2, 2))
    h = rf_to_hash(r)
    assert h == {1: 0, 2: 1}
    assert len(h) == 2
    assert h[1] == 0
    assert h[2] == 1
    # Empty ranking
    assert rf_to_hash(failure()) == {}
    # Assoc
    assoc = rf_to_assoc(r)
    assert assoc == [(1, 0), (2, 1), (2, 2)]
    assert rf_to_assoc(failure()) == []

def test_api_either_of():
    from ranked_programming.rp_api import either_of, construct_ranking, failure, normalise
    r1 = construct_ranking((1, 2), (2, 3))
    r2 = construct_ranking((3, 1), (4, 4))
    r3 = construct_ranking((5, 0))
    # Union of all, then normalize so min rank is 0
    result = either_of(r1, r2, r3)
    expected = [(5, 0), (3, 1), (1, 2), (2, 3), (4, 4)]
    assert result.to_assoc() == expected
    # either_of with empty returns empty
    assert either_of(failure(), failure()).is_empty()
    # either_of with one ranking returns normalized version
    r4 = construct_ranking((10, 5), (20, 7))
    assert either_of(r4).to_assoc() == [(10, 0), (20, 2)]
    # either_of with empty and one ranking returns normalized version
    assert either_of(failure(), r4).to_assoc() == normalise(r4).to_assoc()
    assert either_of(r4, failure()).to_assoc() == normalise(r4).to_assoc()

def test_api_either_or():
    from ranked_programming.rp_api import either_or, construct_ranking, failure
    r1 = construct_ranking((1, 2), (2, 3))
    r2 = construct_ranking((3, 1), (4, 4))
    r3 = construct_ranking((2, 0), (5, 0))
    # All values from all rankings, deduplicated, all at rank 0
    result = either_or(r1, r2, r3)
    expected = set([(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)])
    assert set(result.to_assoc()) == expected
    # either_or with empty returns empty
    assert either_or(failure(), failure()).is_empty()
    # either_or with one ranking returns all values at rank 0, deduped
    r4 = construct_ranking((10, 5), (20, 7), (10, 8))
    assert set(either_or(r4).to_assoc()) == set([(10, 0), (20, 0)])

def test_api_nrm_exc():
    from ranked_programming.rp_api import nrm_exc, construct_ranking, failure
    # Two-argument form: v1 at 0, v2 at 1
    r = nrm_exc(1, 2)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    # Three-argument form: v1 at 0, v2 at given rank
    r2 = nrm_exc(1, 2, 5)
    assert r2.to_assoc() == [(1, 0), (2, 5)]
    # If v1 and v2 are rankings, merge and shift as needed
    r3 = nrm_exc(construct_ranking((1, 0), (2, 1)), construct_ranking((3, 0), (4, 2)), 2)
    assert r3.to_assoc() == [(1, 0), (2, 1), (3, 2), (4, 4)]
    # nrm_exc with empty returns just the non-empty part
    assert nrm_exc(failure(), 5).to_assoc() == [(5, 1)]
    assert nrm_exc(5, failure()).to_assoc() == [(5, 0)]
    # nrm_exc with both empty returns empty
    assert nrm_exc(failure(), failure()).is_empty()

def test_api_rlet():
    from ranked_programming.rp_api import rlet, construct_ranking, failure
    # Single binding: rlet(x=ranking) returns the same as the ranking, but as a tuple
    r = rlet({'x': construct_ranking((1, 0), (2, 1))}, lambda x: x)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    # Two bindings: joint ranking of tuples, rank is sum
    r2 = rlet(
        {'x': construct_ranking((1, 0), (2, 1)), 'y': construct_ranking((10, 0), (20, 2))},
        lambda x, y: (x, y)
    )
    expected = [((1, 10), 0), ((1, 20), 2), ((2, 10), 1), ((2, 20), 3)]
    assert sorted(r2.to_assoc()) == sorted(expected)
    # If any input is empty, result is empty
    r3 = rlet({'x': failure(), 'y': construct_ranking((1, 0))}, lambda x, y: (x, y))
    assert r3.is_empty()

def test_api_rlet_star():
    from ranked_programming.rp_api import rlet_star, construct_ranking, failure
    # Single binding: rlet_star([(x, ranking)], lambda x: x) is just the ranking
    r = rlet_star([('x', construct_ranking((1, 0), (2, 1)))], lambda x: x)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    # Two bindings: second can depend on first
    r2 = rlet_star(
        [
            ('x', construct_ranking((1, 0), (2, 1))),
            ('y', lambda x: construct_ranking((x + 10, 0), (x + 20, 2)))
        ],
        lambda x, y: (x, y)
    )
    expected = [((1, 11), 0), ((1, 21), 2), ((2, 12), 1), ((2, 22), 3)]
    assert sorted(r2.to_assoc()) == sorted(expected)
    # If any input is empty, result is empty
    r3 = rlet_star([('x', failure()), ('y', lambda x: construct_ranking((x + 1, 0)))], lambda x, y: (x, y))
    assert r3.is_empty()

def test_api_observe():
    from ranked_programming.rp_api import observe, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    # Keep only even values, shift so lowest is 0
    result = observe(lambda x: x % 2 == 0, r)
    assert result.to_assoc() == [(2, 0), (4, 2)]
    # All pass: should just normalize
    result2 = observe(lambda x: True, r)
    assert result2.to_assoc() == [(1, 0), (2, 1), (3, 2), (4, 3)]
    # None pass: should be empty
    result3 = observe(lambda x: False, r)
    assert result3.is_empty()
    # Observe on empty ranking returns empty
    assert observe(lambda x: True, failure()).is_empty()

def test_observe_all():
    """
    Test the observe_all API wrapper, which filters a ranking by multiple predicates and normalizes the result.
    Only values passing all predicates are kept.
    """
    from ranked_programming.rp_api import observe_all, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3), (5, 4))
    # Keep only even values greater than 2
    result = observe_all(r, [lambda x: x % 2 == 0, lambda x: x > 2])
    assert result.to_assoc() == [(4, 0)]
    # All predicates true: should keep all
    result2 = observe_all(r, [lambda x: True, lambda x: True])
    assert result2.to_assoc() == [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)]
    # One predicate false: should remove all
    result3 = observe_all(r, [lambda x: False])
    assert result3.is_empty()
    # Empty ranking returns empty
    assert observe_all(failure(), [lambda x: True]).is_empty()
    # No predicates: should keep all, normalized
    r2 = construct_ranking((10, 5), (20, 7))
    assert observe_all(r2, []).to_assoc() == [(10, 0), (20, 2)]

def test_limit():
    """
    Test the limit API utility, which restricts a ranking to the n lowest-ranked values.
    """
    from ranked_programming.rp_api import limit, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3), (5, 4))
    # Limit to 3 lowest
    result = limit(3, r)
    assert result.to_assoc() == [(1, 0), (2, 1), (3, 2)]
    # Limit to 0 returns empty
    assert limit(0, r).is_empty()
    # Limit to more than available returns all
    assert limit(10, r).to_assoc() == [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)]
    # Limit on empty returns empty
    assert limit(3, failure()).is_empty()
    # Limit with ties: all values with same rank should be included if within n
    r2 = construct_ranking((1, 0), (2, 0), (3, 1), (4, 1), (5, 2))
    assert limit(2, r2).to_assoc() == [(1, 0), (2, 0)]
    assert limit(4, r2).to_assoc() == [(1, 0), (2, 0), (3, 1), (4, 1)]

def test_cut():
    """
    Test the cut API utility, which restricts a ranking to values with rank <= threshold.
    """
    from ranked_programming.rp_api import cut, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 2), (3, 4), (4, 6))
    # Cut at 2: keep 0,2
    result = cut(2, r)
    assert result.to_assoc() == [(1, 0), (2, 2)]
    # Cut at 0: only lowest
    assert cut(0, r).to_assoc() == [(1, 0)]
    # Cut at 4: up to 4
    assert cut(4, r).to_assoc() == [(1, 0), (2, 2), (3, 4)]
    # Cut above all: keep all
    assert cut(10, r).to_assoc() == [(1, 0), (2, 2), (3, 4), (4, 6)]
    # Cut below all: empty
    assert cut(-1, r).is_empty()
    # Cut on empty returns empty
    assert cut(2, failure()).is_empty()
    # Cut with exact match
    r2 = construct_ranking((1, 1), (2, 2), (3, 2), (4, 3))
    assert cut(2, r2).to_assoc() == [(1, 1), (2, 2), (3, 2)]

def test_rank_of():
    """
    Test the rank_of API utility, which returns the lowest rank for which a predicate holds, or infinity if none.
    """
    from ranked_programming.rp_api import rank_of, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 2), (3, 4), (4, 6))
    # Find rank of value == 3
    assert rank_of(lambda x: x == 3, r) == 4
    # Find rank of even value
    assert rank_of(lambda x: x % 2 == 0, r) == 2
    # No match returns infinity
    assert rank_of(lambda x: x > 10, r) == float('inf')
    # Empty ranking returns infinity
    assert rank_of(lambda x: True, failure()) == float('inf')
    # Multiple matches: should return lowest rank
    r2 = construct_ranking((1, 1), (2, 2), (3, 2), (4, 3))
    assert rank_of(lambda x: x > 1, r2) == 2

def test_argmin():
    """
    Test the argmin API utility, which returns all values with the minimal rank.
    """
    from ranked_programming.rp_api import argmin, construct_ranking, failure
    # Single minimum
    r = construct_ranking((1, 0), (2, 2), (3, 4))
    assert argmin(r) == [1]
    # Multiple minima (ties)
    r2 = construct_ranking((1, 0), (2, 0), (3, 2))
    assert set(argmin(r2)) == {1, 2}
    # All same rank
    r3 = construct_ranking((1, 1), (2, 1), (3, 1))
    assert set(argmin(r3)) == {1, 2, 3}
    # Empty ranking returns empty list
    assert argmin(failure()) == []
    # Ranking with only one value
    r4 = construct_ranking((42, 7))
    assert argmin(r4) == [42]

def test_rf_to_stream():
    """
    Test the rf_to_stream API utility, which converts a ranking to a generator of (value, rank) pairs in order.
    """
    from ranked_programming.rp_api import rf_to_stream, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    stream = list(rf_to_stream(r))
    assert stream == [(1, 0), (2, 1), (3, 2)]
    # Empty ranking yields empty stream
    assert list(rf_to_stream(failure())) == []
    # Ranking with duplicate values
    r2 = construct_ranking((1, 0), (1, 1), (2, 2))
    assert list(rf_to_stream(r2)) == [(1, 0), (1, 1), (2, 2)]

def test_rf_equal():
    """
    Test the rf_equal API utility, which checks if two rankings are equal (same values and ranks, order irrelevant).
    """
    from ranked_programming.rp_api import rf_equal, construct_ranking, failure
    r1 = construct_ranking((1, 0), (2, 1))
    r2 = construct_ranking((2, 1), (1, 0))
    r3 = construct_ranking((1, 0), (2, 2))
    r4 = failure()
    r5 = construct_ranking()
    assert rf_equal(r1, r2)
    assert not rf_equal(r1, r3)
    assert rf_equal(r4, r5)
    assert not rf_equal(r1, r4)

def test_rf_to_assoc():
    """
    Test the rf_to_assoc API utility, which converts a ranking to a list of (value, rank) pairs in order.
    """
    from ranked_programming.rp_api import rf_to_assoc, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    assoc = rf_to_assoc(r)
    assert assoc == [(1, 0), (2, 1), (3, 2)]
    # Empty ranking yields empty list
    assert rf_to_assoc(failure()) == []
    # Ranking with duplicate values
    r2 = construct_ranking((1, 0), (1, 1), (2, 2))
    assert rf_to_assoc(r2) == [(1, 0), (1, 1), (2, 2)]

def test_rf_to_hash():
    """
    Test the rf_to_hash API utility, which converts a ranking to a dict mapping value to rank (first occurrence wins).
    """
    from ranked_programming.rp_api import rf_to_hash, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (2, 2))
    h = rf_to_hash(r)
    assert h == {1: 0, 2: 1}
    assert len(h) == 2
    assert h[1] == 0
    assert h[2] == 1
    # Empty ranking
    assert rf_to_hash(failure()) == {}

def test_top_k_api():
    """
    Test the API wrapper for top_k.
    """
    from ranked_programming.rp_api import top_k, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3), (5, 4))
    assert top_k(3, r) == [1, 2, 3]
    assert top_k(0, r) == []
    assert top_k(10, r) == [1, 2, 3, 4, 5]
    r2 = construct_ranking((1, 0), (2, 0), (3, 1), (4, 1), (5, 2))
    assert set(top_k(2, r2)) == {1, 2}
    assert set(top_k(4, r2)) == {1, 2, 3, 4}
    assert top_k(3, failure()) == []
    r3 = construct_ranking((42, 7))
    assert top_k(1, r3) == [42]

def test_rank_predicate():
    """
    Test the rank predicate (rank?).
    """
    from ranked_programming.rp_api import rank
    assert rank(0)
    assert rank(5)
    assert rank(float('inf'))
    assert not rank(-1)
    assert not rank('foo')
    assert not rank(None)

def test_global_dedup():
    """
    Test the global deduplication toggle.
    """
    from ranked_programming.rp_api import set_global_dedup, dedup, construct_ranking
    # Enable deduplication (default)
    set_global_dedup(True)
    r = construct_ranking((1, 0), (1, 1), (2, 2))
    assert dedup(r).to_assoc() == [(1, 0), (2, 2)]
    # Disable deduplication: dedup should be a no-op
    set_global_dedup(False)
    r = construct_ranking((1, 0), (1, 1), (2, 2))
    assert dedup(r).to_assoc() == [(1, 0), (1, 1), (2, 2)]
    # Restore default
    set_global_dedup(True)

def test_observe_e_api():
    """
    Test the API wrapper for observe_e.
    """
    from ranked_programming.rp_api import observe_e, construct_ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    result = observe_e(2, lambda x: x == 2, r)
    assert result.to_assoc() == [(2, 0), (1, 1), (3, 3)]
    result = observe_e(2, lambda x: x == 42, r)
    assert result.to_assoc() == [(1, 0), (2, 1), (3, 2)]

def test_observe_r_api():
    """
    Test the API wrapper for observe_r.
    """
    from ranked_programming.rp_api import observe_r, construct_ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    result = observe_r(2, lambda x: x == 2, r)
    assert result.to_assoc() == [(2, 0), (1, 1), (3, 1)]
    result = observe_r(2, lambda x: x == 42, r)
    assert result.to_assoc() == [(1, 0), (2, 0), (3, 0)]

def test_construct_ranking_argument_error():
    """
    Test that construct_ranking raises TypeError for invalid arguments.
    """
    from ranked_programming.rp_api import construct_ranking
    # Not a tuple
    with pytest.raises(TypeError):
        construct_ranking(1)
    # Tuple of wrong length
    with pytest.raises(TypeError):
        construct_ranking((1,))
    # Tuple with non-integer rank
    with pytest.raises(TypeError):
        construct_ranking((1, 'a'))

def test_pr_all_api(capsys):
    """
    Test the API wrapper for pr_all.
    Ensures pr_all is callable from the API and prints the expected output for a simple ranking.
    """
    from ranked_programming.rp_api import construct_ranking, pr_all
    r = construct_ranking(("foo", 0), ("bar", 1))
    pr_all(r)
    out = capsys.readouterr().out
    assert "foo" in out and "bar" in out and "Rank" in out
    # Test empty ranking prints failure message
    from ranked_programming.rp_api import failure
    pr_all(failure())
    out = capsys.readouterr().out
    assert "Failure" in out
