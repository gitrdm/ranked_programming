"""
Tests for the core ranking data structure and basic constructors.
"""
import pytest
from ranked_programming.rp_core import Ranking, failure, construct_ranking

def test_failure_is_empty():
    r = failure()
    assert isinstance(r, Ranking)
    assert r.is_empty()
    assert r.to_assoc() == []

def test_construct_ranking_no_args_is_empty():
    r = construct_ranking()
    assert isinstance(r, Ranking)
    assert r.is_empty()
    assert r.to_assoc() == []

def test_construct_ranking_with_values():
    r = construct_ranking((1, 0), (2, 1))
    assert isinstance(r, Ranking)
    assert not r.is_empty()
    assert r.to_assoc() == [(1, 0), (2, 1)]

# Test that order is by rank, not insertion

def test_construct_ranking_sorts_by_rank():
    r = construct_ranking((2, 5), (1, 0), (3, 2))
    assert r.to_assoc() == [(1, 0), (3, 2), (2, 5)]

def test_ranking_equality():
    r1 = construct_ranking((1, 0), (2, 1))
    r2 = construct_ranking((1, 0), (2, 1))
    r3 = construct_ranking((2, 1), (1, 0))  # order should not matter
    r4 = construct_ranking((1, 0), (2, 2))
    r5 = failure()
    r6 = construct_ranking()
    assert r1 == r2
    assert r1 == r3
    assert r1 != r4
    assert r5 == r6
    assert r1 != r5
    assert r4 != r5

def test_ranking_repr():
    r = construct_ranking((1, 0), (2, 1))
    assert "Ranking" in repr(r)
    assert "(1, 0)" in repr(r)
    assert "(2, 1)" in repr(r)

def test_to_assoc_and_empty():
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    assert r.to_assoc() == [(1, 0), (2, 1), (3, 2)]
    assert failure().to_assoc() == []
    assert construct_ranking().to_assoc() == []

def test_ranking_with_duplicate_values():
    r = construct_ranking((1, 0), (1, 1), (2, 2))
    # By default, all entries are kept; deduplication is a separate concern
    assert r.to_assoc() == [(1, 0), (1, 1), (2, 2)]

def test_rf_to_hash_equivalent():
    # Simulate rf->hash: last occurrence of value wins
    r = construct_ranking((1, 0), (2, 1), (2, 2))
    # In Racket, rf->hash returns {1: 0, 2: 1} (first occurrence wins)
    # We'll match that behavior
    def rf_to_hash(ranking):
        d = {}
        for v, rank in ranking.to_assoc():
            if v not in d:
                d[v] = rank
        return d
    h = rf_to_hash(r)
    assert h == {1: 0, 2: 1}
    assert len(h) == 2
    assert h[1] == 0
    assert h[2] == 1
    # Empty ranking
    assert rf_to_hash(failure()) == {}

def test_rf_to_hash():
    """
    Test the rf_to_hash utility, which converts a ranking to a dict mapping value to rank (first occurrence wins, as in Racket).
    """
    from ranked_programming.rp_core import rf_to_hash, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (2, 2))
    h = rf_to_hash(r)
    assert h == {1: 0, 2: 1}
    assert len(h) == 2
    assert h[1] == 0
    assert h[2] == 1
    # Empty ranking
    assert rf_to_hash(failure()) == {}
    # Ranking with duplicate values
    r2 = construct_ranking((1, 0), (1, 1), (2, 2))
    assert rf_to_hash(r2) == {1: 0, 2: 2}

def test_normalise():
    # Normalise should shift all ranks so the minimum is 0
    from ranked_programming.rp_core import normalise
    r = construct_ranking((1, 2), (2, 4), (3, 7))
    normed = normalise(r)
    assert normed.to_assoc() == [(1, 0), (2, 2), (3, 5)]
    # Already normalised
    r2 = construct_ranking((1, 0), (2, 2), (3, 5))
    assert normalise(r2).to_assoc() == [(1, 0), (2, 2), (3, 5)]
    # Empty ranking stays empty
    assert normalise(failure()).is_empty()

def test_map_value():
    from ranked_programming.rp_core import map_value
    r = construct_ranking((1, 2), (2, 4), (3, 7))
    mapped = map_value(lambda x: x * 10, r)
    assert mapped.to_assoc() == [(10, 2), (20, 4), (30, 7)]
    # Mapping over empty ranking returns empty
    assert map_value(lambda x: x + 1, failure()).is_empty()

def test_shift():
    from ranked_programming.rp_core import shift
    r = construct_ranking((1, 0), (2, 2), (3, 5))
    shifted = shift(10, r)
    assert shifted.to_assoc() == [(1, 10), (2, 12), (3, 15)]
    # Shifting an empty ranking returns empty
    assert shift(5, failure()).is_empty()

def test_filter_ranking():
    from ranked_programming.rp_core import filter_ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    filtered = filter_ranking(lambda x: x % 2 == 0, r)
    assert filtered.to_assoc() == [(2, 1), (4, 3)]
    # Filtering an empty ranking returns empty
    assert filter_ranking(lambda x: True, failure()).is_empty()

def test_filter_after():
    from ranked_programming.rp_core import filter_after
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    filtered = filter_after(lambda x: x > 2, r)
    assert filtered.to_assoc() == [(3, 2), (4, 3)]
    # Filtering after on empty ranking returns empty
    assert filter_after(lambda x: True, failure()).is_empty()

def test_up_to_rank():
    from ranked_programming.rp_core import up_to_rank
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3))
    upto = up_to_rank(2, r)
    assert upto.to_assoc() == [(1, 0), (2, 1), (3, 2)]
    # up_to_rank on empty ranking returns empty
    assert up_to_rank(2, failure()).is_empty()

def test_dedup():
    from ranked_programming.rp_core import dedup
    r = construct_ranking((1, 0), (1, 1), (2, 2), (2, 3))
    deduped = dedup(r)
    assert deduped.to_assoc() == [(1, 0), (2, 2)]
    # dedup on empty ranking returns empty
    assert dedup(failure()).is_empty()

def test_do_with():
    from ranked_programming.rp_core import do_with
    r = construct_ranking((1, 0), (2, 1))
    result = do_with(lambda x, y: x + y, r)
    # For this test, do_with should sum the values and ranks: (1+0)+(2+1)=1+0+2+1=4, but likely just sum x+r for each, then sum: (1+0)+(2+1)=1+3=4
    # But in Racket, do-with applies f to each (value, rank) and returns the sum
    assert result == (1 + 0) + (2 + 1)
    # do_with on empty ranking returns 0 (or a neutral value)
    assert do_with(lambda x, y: x + y, failure()) == 0

def test_either_of():
    """
    Test the either_of combinator, which unions multiple rankings and normalizes the result.
    """
    from ranked_programming.rp_core import either_of, construct_ranking, normalise
    r1 = construct_ranking((1, 2), (2, 3))
    r2 = construct_ranking((3, 1), (4, 4))
    r3 = construct_ranking((5, 0))
    # Union of all, then normalize so min rank is 0
    result = either_of(r1, r2, r3)
    # All entries, min rank is 0 (from r3), so subtract 0 from all
    expected = [(5, 0), (3, 1), (1, 2), (2, 3), (4, 4)]
    assert result.to_assoc() == expected
    # either_of with empty returns empty
    assert either_of(failure(), failure()).is_empty()
    # either_of with one ranking returns normalized version
    r4 = construct_ranking((10, 5), (20, 7))
    assert either_of(r4).to_assoc() == [(10, 0), (20, 2)]

def test_either_of_behavior():
    """
    Test the either_of combinator, which returns the normalized union of two rankings.
    Duplicate values keep the lower rank.
    """
    from ranked_programming.rp_core import either_of, construct_ranking, normalise
    r1 = construct_ranking((1, 0), (2, 2))
    r2 = construct_ranking((2, 1), (3, 3))
    result = either_of(r1, r2)
    # Union: (1,0), (2,1), (3,3) -- 2 appears in both, keep lower rank (1)
    assert result.to_assoc() == [(1, 0), (2, 1), (3, 3)]
    # Should be normalized (min rank is 0)
    assert min(rank for _, rank in result.to_assoc()) == 0
    # Either with empty returns the normalized other
    empty = construct_ranking()
    assert either_of(r1, empty).to_assoc() == normalise(r1).to_assoc()
    assert either_of(empty, r2).to_assoc() == normalise(r2).to_assoc()
    # Both empty returns empty
    assert either_of(empty, empty).is_empty()

def test_either_or():
    """
    Test the either_or macro/combinator, which unions any number of rankings and assigns all values rank 0 (deduplicated).
    """
    from ranked_programming.rp_core import either_or, construct_ranking, failure
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

def test_nrm_exc():
    """
    Test the nrm_exc macro/combinator, which constructs a ranking with a normal and exceptional value (or ranking).
    """
    from ranked_programming.rp_core import nrm_exc, construct_ranking, failure
    # Two-argument form: v1 at 0, v2 at 1
    r = nrm_exc(1, 2)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    # Three-argument form: v1 at 0, v2 at given rank
    r2 = nrm_exc(1, 2, 5)
    assert r2.to_assoc() == [(1, 0), (2, 5)]
    # If v1 and v2 are rankings, merge and shift as needed
    r3 = nrm_exc(construct_ranking((1, 0), (2, 1)), construct_ranking((3, 0), (4, 2)), 2)
    # r3 should be: (1,0),(2,1),(3,2),(4,4)
    assert r3.to_assoc() == [(1, 0), (2, 1), (3, 2), (4, 4)]
    # nrm_exc with empty returns just the non-empty part
    assert nrm_exc(failure(), 5).to_assoc() == [(5, 1)]
    assert nrm_exc(5, failure()).to_assoc() == [(5, 0)]
    # nrm_exc with both empty returns empty
    assert nrm_exc(failure(), failure()).is_empty()

def test_rlet():
    """
    Test the rlet macro/combinator, which produces a joint ranking over variables.
    The rank of each result is the sum of the ranks of the chosen values.
    """
    from ranked_programming.rp_core import rlet, construct_ranking, failure
    # Single binding: rlet(x=ranking) returns the same as the ranking, but as a tuple
    r = rlet({'x': construct_ranking((1, 0), (2, 1))}, lambda x: x)
    assert r.to_assoc() == [(1, 0), (2, 1)]
    # Two bindings: joint ranking of tuples, rank is sum
    r2 = rlet(
        {'x': construct_ranking((1, 0), (2, 1)), 'y': construct_ranking((10, 0), (20, 2))},
        lambda x, y: (x, y)
    )
    # All combinations, rank is sum
    expected = [((1, 10), 0), ((1, 20), 2), ((2, 10), 1), ((2, 20), 3)]
    assert sorted(r2.to_assoc()) == sorted(expected)
    # If any input is empty, result is empty
    r3 = rlet({'x': failure(), 'y': construct_ranking((1, 0))}, lambda x, y: (x, y))
    assert r3.is_empty()

def test_rlet_star():
    """
    Test the rlet_star macro/combinator, which produces a joint ranking over variables sequentially.
    Each binding can depend on the previous ones.
    """
    from ranked_programming.rp_core import rlet_star, construct_ranking, failure

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
    # For x=1: y in (11,0),(21,2) → (1,11,0+0),(1,21,0+2)
    # For x=2: y in (12,0),(22,2) → (2,12,1+0),(2,22,1+2)
    expected = [((1, 11), 0), ((1, 21), 2), ((2, 12), 1), ((2, 22), 3)]
    actual = [((x, y), r) for (x, y), r in r2.to_assoc()]
    for pair in expected:
        assert pair in actual

    # If any input is empty, result is empty
    r3 = rlet_star([('x', failure()), ('y', lambda x: construct_ranking((x + 1, 0)))], lambda x, y: (x, y))
    assert r3.is_empty()

def test_ranked_apply():
    """
    Test the ranked_apply combinator, which applies a function to ranked arguments,
    producing a ranking of results with summed ranks.
    """
    from ranked_programming.rp_core import ranked_apply, construct_ranking, failure

    # Simple: add two ranked numbers
    r1 = construct_ranking((1, 0), (2, 1))
    r2 = construct_ranking((10, 0), (20, 2))
    result = ranked_apply(lambda x, y: x + y, r1, r2)
    expected = [(11, 0), (21, 2), (12, 1), (22, 3)]
    assert sorted(result.to_assoc()) == sorted(expected)

    # Mix of value and ranking
    result2 = ranked_apply(lambda x, y: x * y, 2, r2)
    expected2 = [(20, 0), (40, 2)]
    assert sorted(result2.to_assoc()) == sorted(expected2)

    # Ranking of functions
    rf = construct_ranking((lambda x: x + 1, 0), (lambda x: x * 10, 1))
    rarg = construct_ranking((3, 0), (4, 2))
    result3 = ranked_apply(lambda f, x: f(x), rf, rarg)
    # (3+1, 0+0), (4+1, 0+2), (3*10, 1+0), (4*10, 1+2)
    expected3 = [(4, 0), (5, 2), (30, 1), (40, 3)]
    assert sorted(result3.to_assoc()) == sorted(expected3)

    # Any empty argument yields empty
    assert ranked_apply(lambda x, y: x + y, failure(), r2).is_empty()
    assert ranked_apply(lambda x, y: x + y, r1, failure()).is_empty()

def test_observe():
    """
    Test the observe macro/combinator, which filters a ranking by a predicate and normalizes the result.
    """
    from ranked_programming.rp_core import observe, construct_ranking, failure

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
    Test the observe_all macro/combinator, which filters a ranking by multiple predicates and normalizes the result.
    Only values passing all predicates are kept.
    """
    from ranked_programming.rp_core import observe_all, construct_ranking, failure
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
    Test the limit utility, which restricts a ranking to the n lowest-ranked values.
    """
    from ranked_programming.rp_core import limit, construct_ranking, failure
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
    Test the cut utility, which restricts a ranking to values with rank <= threshold.
    """
    from ranked_programming.rp_core import cut, construct_ranking, failure
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
    Test the rank_of utility, which returns the lowest rank for which a predicate holds, or infinity if none.
    """
    from ranked_programming.rp_core import rank_of, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 2), (3, 4), (4, 6))
    # Find rank of value == 3
    assert rank_of(lambda x: x == 3, r) == 4
    # Find rank of even value
    assert rank_of(lambda x: x % 2 == 0, r) == 2
    # No match returns infinity
    assert rank_of(lambda x: x > 10, r) == float('inf')
    # Empty ranking returns infinity
    assert rank_of(lambda x: x > 10, failure()) == float('inf')
    # Multiple matches: should return lowest rank
    r2 = construct_ranking((1, 1), (2, 2), (3, 2), (4, 3))
    assert rank_of(lambda x: x > 1, r2) == 2

def test_argmin():
    """
    Test the argmin utility, which returns all values with the minimal rank.
    """
    from ranked_programming.rp_core import argmin, construct_ranking, failure
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
    Test the rf_to_stream utility, which converts a ranking to a generator of (value, rank) pairs in order.
    """
    from ranked_programming.rp_core import rf_to_stream, construct_ranking, failure
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
    Test the rf_equal utility, which checks if two rankings are equal (same values and ranks, order irrelevant).
    """
    from ranked_programming.rp_core import rf_equal, construct_ranking, failure
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
    Test the rf_to_assoc utility, which converts a ranking to a list of (value, rank) pairs in order.
    """
    from ranked_programming.rp_core import rf_to_assoc, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    assoc = rf_to_assoc(r)
    assert assoc == [(1, 0), (2, 1), (3, 2)]
    # Empty ranking yields empty list
    assert rf_to_assoc(failure()) == []
    # Ranking with duplicate values
    r2 = construct_ranking((1, 0), (1, 1), (2, 2))
    assert rf_to_assoc(r2) == [(1, 0), (1, 1), (2, 2)]

def test_pr_all(capsys):
    """
    Test the pr_all utility, which prints all (value, rank) pairs in order.
    """
    from ranked_programming.rp_core import pr_all, construct_ranking, failure
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    pr_all(r)
    captured = capsys.readouterr().out
    assert "Rank  Value" in captured
    # Check for correct output format: rank (right-aligned), then value
    assert "    0 1" in captured
    assert "    1 2" in captured
    assert "    2 3" in captured
    # Empty ranking prints failure message
    pr_all(failure())
    captured = capsys.readouterr().out
    assert "Failure" in captured

def test_top_k():
    """
    Test the top_k utility, which returns the k lowest-ranked values as a list.
    """
    from ranked_programming.rp_core import top_k, construct_ranking, failure
    # Normal ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2), (4, 3), (5, 4))
    assert top_k(3, r) == [1, 2, 3]
    # k = 0 returns empty list
    assert top_k(0, r) == []
    # k > number of values returns all values
    assert top_k(10, r) == [1, 2, 3, 4, 5]
    # Ties: all values with the same rank are included if within k
    r2 = construct_ranking((1, 0), (2, 0), (3, 1), (4, 1), (5, 2))
    assert set(top_k(2, r2)) == {1, 2}
    assert set(top_k(4, r2)) == {1, 2, 3, 4}
    # Empty ranking returns empty list
    assert top_k(3, failure()) == []
    # Ranking with only one value
    r3 = construct_ranking((42, 7))
    assert top_k(1, r3) == [42]

def test_pr_first(capsys):
    """
    Test the pr_first utility, which prints the first (lowest-ranked) value and its rank.
    """
    from ranked_programming.rp_core import pr_first, construct_ranking, failure
    r = construct_ranking((2, 1), (1, 0), (3, 2))
    pr_first(r)
    out = capsys.readouterr().out
    assert "0 1" in out or "1 0" in out  # Accept either order, but should print lowest rank and value
    # Test empty ranking
    pr_first(failure())
    out = capsys.readouterr().out
    assert "Failure" in out

def test_observe_e():
    """
    Test the observe_e utility, which implements evidence-oriented conditionalization.
    """
    from ranked_programming.rp_core import observe_e, construct_ranking
    r = construct_ranking((1, 0), (2, 1), (3, 2))
    # Evidence strength 2, predicate x == 2
    result = observe_e(2, lambda x: x == 2, r)
    # Only 2 should be at rank 0, others at +2, then normalized
    assert result.to_assoc() == [(2, 0), (1, 1), (3, 3)]
    # If no match, all at +evidence, then normalized (min is 2)
    result = observe_e(2, lambda x: x == 42, r)
    # All shifted by +2, then normalized (min is 2)
    assert result.to_assoc() == [(1, 0), (2, 1), (3, 2)]

# --- LazyRanking tests ---

def test_lazy_ranking_iter():
    from ranked_programming.rp_core import LazyRanking
    def gen():
        yield (1, 0)
        yield (2, 1)
        yield (3, 2)
    ranking = LazyRanking(gen)
    assert list(ranking) == [(1, 0), (2, 1), (3, 2)]

def test_lazy_ranking_to_eager():
    from ranked_programming.rp_core import LazyRanking
    def gen():
        yield ("a", 0)
        yield ("b", 1)
    ranking = LazyRanking(gen)
    assert ranking.to_eager() == [("a", 0), ("b", 1)]

def test_lazy_ranking_map():
    from ranked_programming.rp_core import LazyRanking
    def gen():
        yield (1, 0)
        yield (2, 1)
    ranking = LazyRanking(gen)
    mapped = ranking.map(lambda x: x * 10)
    assert mapped.to_eager() == [(10, 0), (20, 1)]

def test_lazy_ranking_filter():
    from ranked_programming.rp_core import LazyRanking
    def gen():
        yield (1, 0)
        yield (2, 1)
        yield (3, 2)
    ranking = LazyRanking(gen)
    filtered = ranking.filter(lambda x: x % 2 == 1)
    assert filtered.to_eager() == [(1, 0), (3, 2)]

def test_lazy_short_circuit():
    from ranked_programming.rp_core import LazyRanking
    def gen():
        for i in range(1000):
            yield (i, i)
    ranking = LazyRanking(gen)
    first = next(iter(ranking))
    assert first == (0, 0)

def test_lazy_nrm_exc():
    from ranked_programming.rp_core import LazyRanking, lazy_nrm_exc
    ranking = LazyRanking(lambda: lazy_nrm_exc('A', 'B', 1))
    # Should yield ('A', 0) and ('B', 1)
    assert ranking.to_eager() == [('A', 0), ('B', 1)]
    # Test laziness: only the first value is produced if we break early
    gen = lazy_nrm_exc('X', 'Y', 42)
    first = next(gen)
    assert first == ('X', 0)

def test_lazy_rlet_star():
    from ranked_programming.rp_core import LazyRanking, lazy_rlet_star
    # Simple case: two independent bindings
    def b1():
        yield (1, 0)
        yield (2, 1)
    def b2(x):
        yield (x + 10, 0)
        yield (x + 20, 2)
    ranking = LazyRanking(lambda: lazy_rlet_star([
        ('x', b1),
        ('y', b2)
    ], lambda x, y: (x, y)))
    result = ranking.to_eager()
    # Should yield all combinations
    expected = [((1, 11), 0), ((1, 21), 2), ((2, 12), 1), ((2, 22), 3)]
    actual = [((x, y), r) for (x, y), r in result]
    for pair in expected:
        assert pair in actual
    # Test laziness: only the first value is produced if we break early
    gen = lazy_rlet_star([
        ('x', b1),
        ('y', b2)
    ], lambda x, y: (x, y))
    first = next(gen)
    assert isinstance(first, tuple)

def test_lazy_observe_e_basic():
    """
    Test lazy_observe_e with a simple predicate and evidence.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_nrm_exc, lazy_observe_e
    r = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
    filtered = LazyRanking(lambda: lazy_observe_e(2, lambda x: x == 2, r))
    results = list(filtered)
    # 1: rank 0+2=2, 2: rank 1; normalized: min is 1, so (1,1), (2,0)
    assert (1, 1) in results
    assert (2, 0) in results

def test_lazy_observe_all_basic():
    """
    Test lazy_observe_all with two predicates.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_all
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    filtered = LazyRanking(lambda: lazy_observe_all(r, [lambda x: x > 10, lambda x: x < 30]))
    results = list(filtered)
    # Only 20 passes, original rank 7, normalized to 0
    assert results == [(20, 0)]

def test_lazy_observe_all_empty_predicates():
    """
    Test lazy_observe_all with empty predicates (should normalize all values).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_all
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    filtered = LazyRanking(lambda: lazy_observe_all(r, []))
    results = list(filtered)
    # All values, normalized: min is 5, so (10,0), (20,2), (30,1)
    assert (10, 0) in results
    assert (20, 2) in results
    assert (30, 1) in results

def test_lazy_observe_all_none_pass():
    """
    Test lazy_observe_all when no values pass (should yield nothing).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_all
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    filtered = LazyRanking(lambda: lazy_observe_all(r, [lambda x: x > 100]))
    results = list(filtered)
    assert results == []

def test_lazy_observe_all_short_circuit():
    """
    Test that lazy_observe_all is lazy (predicates are only called for values in the generator).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_all
    calls = []
    def pred1(x):
        calls.append(('pred1', x))
        return x > 10
    def pred2(x):
        calls.append(('pred2', x))
        return x < 30
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    filtered = LazyRanking(lambda: lazy_observe_all(r, [pred1, pred2]))
    it = iter(filtered)
    try:
        next(it)
    except StopIteration:
        pass
    # At least one predicate should have been called
    assert any(c[0] == 'pred1' for c in calls)
    assert any(c[0] == 'pred2' for c in calls)

def test_lazy_observe_e_basic():
    """
    Test lazy_observe_e with a simple predicate and evidence.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_nrm_exc, lazy_observe_e
    r = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
    filtered = LazyRanking(lambda: lazy_observe_e(2, lambda x: x == 2, r))
    results = list(filtered)
    # 1: rank 0+2=2, 2: rank 1; normalized: min is 1, so (1,1), (2,0)
    assert (1, 1) in results
    assert (2, 0) in results

def test_lazy_observe_e_all_fail():
    """
    Test lazy_observe_e when no values pass the predicate (all get evidence).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_nrm_exc, lazy_observe_e
    r = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
    filtered = LazyRanking(lambda: lazy_observe_e(3, lambda x: x == 99, r))
    results = list(filtered)
    # Both get evidence: (1,3), (2,4), normalized to (1,0), (2,1)
    assert (1, 0) in results
    assert (2, 1) in results

def test_lazy_observe_e_normalization():
    """
    Test lazy_observe_e normalizes ranks so the lowest is 0.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_e
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    filtered = LazyRanking(lambda: lazy_observe_e(2, lambda x: x > 10, r))
    results = list(filtered)
    # 10: 5+2=7, 20: 7, 30: 6; normalized: (10,1), (20,1), (30,0)
    assert (10, 1) in results
    assert (20, 1) in results
    assert (30, 0) in results

def test_lazy_observe_e_short_circuit():
    """
    Test that lazy_observe_e is lazy (predicate is only called for values in the generator).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_observe_e
    calls = []
    def pred(x):
        calls.append(x)
        return x == 1
    r = LazyRanking(lambda: ((1, 0), (2, 1)))
    filtered = LazyRanking(lambda: lazy_observe_e(3, pred, r))
    it = iter(filtered)
    next(it)
    assert 1 in calls
    assert len(calls) <= 2

def test_lazy_limit_basic():
    """
    Test lazy_limit with a simple LazyRanking and n=2.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_limit
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    limited = LazyRanking(lambda: lazy_limit(2, r))
    results = list(limited)
    # Should yield first two in generator order: (10,5), (20,7)
    assert results == [(10, 5), (20, 7)]

def test_lazy_limit_zero():
    """
    Test lazy_limit with n=0 (should yield nothing).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_limit
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    limited = LazyRanking(lambda: lazy_limit(0, r))
    results = list(limited)
    assert results == []

def test_lazy_limit_more_than_length():
    """
    Test lazy_limit with n greater than the number of values (should yield all).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_limit
    r = LazyRanking(lambda: ((10, 5), (20, 7)))
    limited = LazyRanking(lambda: lazy_limit(5, r))
    results = list(limited)
    assert results == [(10, 5), (20, 7)]

def test_lazy_limit_short_circuit():
    """
    Test that lazy_limit is lazy (only yields up to n values, does not evaluate all).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_limit
    calls = []
    def gen():
        for i in range(100):
            calls.append(i)
            yield (i, i)
    r = LazyRanking(gen)
    limited = LazyRanking(lambda: lazy_limit(3, r))
    it = iter(limited)
    vals = [next(it) for _ in range(3)]
    assert vals == [(0, 0), (1, 1), (2, 2)]
    assert calls == [0, 1, 2]

def test_lazy_cut_basic():
    """
    Test lazy_cut with a simple LazyRanking and threshold=6.
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_cut
    r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
    cut_r = LazyRanking(lambda: lazy_cut(6, r))
    results = list(cut_r)
    # Should yield (10,5), (30,6)
    assert (10, 5) in results
    assert (30, 6) in results
    assert (20, 7) not in results

def test_lazy_cut_none_pass():
    """
    Test lazy_cut when no values pass (should yield nothing).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_cut
    r = LazyRanking(lambda: ((10, 8), (20, 9)))
    cut_r = LazyRanking(lambda: lazy_cut(6, r))
    results = list(cut_r)
    assert results == []

def test_lazy_cut_all_pass():
    """
    Test lazy_cut when all values pass (should yield all).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_cut
    r = LazyRanking(lambda: ((10, 5), (20, 6)))
    cut_r = LazyRanking(lambda: lazy_cut(6, r))
    results = list(cut_r)
    assert (10, 5) in results
    assert (20, 6) in results

def test_lazy_cut_short_circuit():
    """
    Test that lazy_cut is lazy (only yields values up to threshold, does not evaluate all).
    """
    from src.ranked_programming.rp_core import LazyRanking, lazy_cut
    calls = []
    def gen():
        for i in range(100):
            calls.append(i)
            yield (i, i)
    r = LazyRanking(gen)
    cut_r = LazyRanking(lambda: lazy_cut(2, r))
    it = iter(cut_r)
    vals = [next(it) for _ in range(3)]
    assert vals == [(0, 0), (1, 1), (2, 2)]
    assert calls == [0, 1, 2]
