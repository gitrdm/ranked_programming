"""
API layer for ranked programming (Python port).
Literate documentation and type hints included.
"""
from typing import Any, Callable, List, Tuple, Optional, Union, Generator, Dict
from .rp_core import Ranking, failure, construct_ranking, normalise, map_value, shift, filter_ranking, filter_after, up_to_rank, dedup, do_with, observe_all, limit, cut, rank_of

def construct_from_assoc(assoc: List[Tuple[Any, int]]) -> Ranking:
    """
    Construct a ranking from an association list (list of (value, rank) pairs).
    Equivalent to Racket's construct-from-assoc.
    """
    return Ranking(list(assoc))

# Truth function: !
def truth(value: Any) -> Ranking:
    """
    Return a ranking with a single value at rank 0.
    Equivalent to Racket's ! macro.
    """
    return Ranking([(value, 0)])

# Ranking predicate
def ranking(obj: Any) -> bool:
    """
    Return True if obj is a Ranking instance.
    Equivalent to Racket's ranking? predicate.
    """
    return isinstance(obj, Ranking)

def failure() -> Ranking:
    """
    Return an empty ranking (failure).
    Equivalent to the Racket (failure) constructor.
    """
    from .rp_core import failure as core_failure
    return core_failure()

def construct_ranking(*args: tuple) -> Ranking:
    """
    Construct a ranking from (value, rank) pairs.
    Equivalent to the Racket construct-ranking API.
    Raises TypeError if arguments are not (value, rank) tuples with int or float('inf') rank.
    """
    for pair in args:
        if not (isinstance(pair, tuple) and len(pair) == 2):
            raise TypeError("Each argument must be a (value, rank) tuple.")
        v, r = pair
        if not ((isinstance(r, int) and r >= 0) or (isinstance(r, float) and r == float('inf'))):
            raise TypeError("Rank must be a non-negative integer or float('inf').")
    from .rp_core import construct_ranking as core_construct_ranking
    return core_construct_ranking(*args)

def normalise(r: Ranking) -> Ranking:
    """
    Shift all ranks so the minimum is 0. If empty, returns empty.
    Equivalent to Racket's normalise API.
    """
    from .rp_core import normalise as core_normalise
    return core_normalise(r)

def map_value(f, r: Ranking) -> Ranking:
    """
    Apply function f to each value in the ranking, keeping ranks unchanged.
    Equivalent to Racket's map-value API.
    Returns a new Ranking.
    """
    from .rp_core import map_value as core_map_value
    return core_map_value(f, r)

def shift(amount: int, r: Ranking) -> Ranking:
    """
    Shift all ranks in the ranking by a constant amount.
    Equivalent to Racket's shift API.
    Returns a new Ranking.
    """
    from .rp_core import shift as core_shift
    return core_shift(amount, r)

def filter_ranking(pred, r: Ranking) -> Ranking:
    """
    Filter the ranking by a predicate on values, keeping ranks unchanged.
    Equivalent to Racket's filter-ranking API.
    Returns a new Ranking.
    """
    from .rp_core import filter_ranking as core_filter_ranking
    return core_filter_ranking(pred, r)

def filter_after(pred, r: Ranking) -> Ranking:
    """
    Keep only the entries after the first one where pred(value) is True (inclusive).
    Equivalent to Racket's filter-after API.
    Returns a new Ranking.
    """
    from .rp_core import filter_after as core_filter_after
    return core_filter_after(pred, r)

def up_to_rank(max_rank: int, r: Ranking) -> Ranking:
    """
    Keep only entries with rank <= max_rank.
    Equivalent to Racket's up-to-rank API.
    Returns a new Ranking.
    """
    from .rp_core import up_to_rank as core_up_to_rank
    return core_up_to_rank(max_rank, r)

# Global deduplication toggle
_global_dedup_enabled = True

def set_global_dedup(enabled: bool) -> None:
    """
    Set the global deduplication setting. If enabled, duplicate higher-ranked values are filtered out of any ranking.
    If disabled, duplicates may occur. Equivalent to Racket's set-global-dedup.
    """
    global _global_dedup_enabled
    _global_dedup_enabled = bool(enabled)

def get_global_dedup() -> bool:
    """
    Get the current global deduplication setting.
    """
    return _global_dedup_enabled

def dedup(r: Ranking) -> Ranking:
    """
    Remove duplicate values, keeping the first occurrence (lowest rank), unless deduplication is globally disabled.
    Equivalent to Racket's dedup API.
    Returns a new Ranking.
    """
    from .rp_core import dedup as core_dedup
    if not _global_dedup_enabled:
        return r
    return core_dedup(r)

def do_with(f, r: Ranking) -> int:
    """
    Apply function f to each (value, rank) pair in the ranking and sum the results.
    Equivalent to Racket's do-with API.
    Returns the sum, or 0 for empty ranking.
    """
    from .rp_core import do_with as core_do_with
    return core_do_with(f, r)

def rf_to_hash(r: Ranking) -> Dict[Any, int]:
    """
    API wrapper for the rf_to_hash utility.
    Converts a ranking to a dict mapping value to rank (first occurrence wins).
    Equivalent to Racket's rf->hash utility.
    """
    from .rp_core import rf_to_hash as core_rf_to_hash
    return core_rf_to_hash(r)

def rf_to_assoc(r: Ranking) -> List[Tuple[Any, int]]:
    """
    API wrapper for the rf_to_assoc utility.
    Converts a ranking to a list of (value, rank) pairs in order.
    Equivalent to Racket's rf->assoc utility.
    """
    from .rp_core import rf_to_assoc as core_rf_to_assoc
    return core_rf_to_assoc(r)

def either_of(*rankings: Ranking) -> Ranking:
    """
    API wrapper for the either_of combinator.
    Returns the normalized union of any number of rankings.
    For duplicate values, keeps the lowest rank.
    Equivalent to Racket's either_of API.
    """
    from .rp_core import either_of as core_either_of
    return core_either_of(*rankings)

def either_or(*rankings: Ranking) -> Ranking:
    """
    API wrapper for the either_or macro/combinator.
    Returns a ranking where all unique values from the input rankings are assigned rank 0.
    Duplicates are removed. If all rankings are empty, returns failure().
    Equivalent to Racket's either/or API.
    """
    from .rp_core import either_or as core_either_or
    return core_either_or(*rankings)

def nrm_exc(v1: Any, v2: Any, rank: int = 1) -> Ranking:
    """
    API wrapper for the nrm_exc macro/combinator.
    Constructs a ranking with a normal and exceptional value (or ranking).
    - If v1 and v2 are not rankings, treat them as singleton rankings.
    - v1 is always at rank 0.
    - v2 is at rank `rank` (default 1).
    - If v1 or v2 is empty, return the other (shifted as needed).
    - If both are empty, return failure().
    Equivalent to Racket's nrm/exc macro/combinator.
    """
    from .rp_core import nrm_exc as core_nrm_exc
    return core_nrm_exc(v1, v2, rank)

def rlet(bindings: dict, body: Callable) -> Ranking:
    """
    API wrapper for the rlet macro/combinator.
    Produces a joint ranking over variables, with rank as the sum of the ranks of the chosen values.
    Equivalent to Racket's rlet macro/combinator.
    """
    from .rp_core import rlet as core_rlet
    return core_rlet(bindings, body)

def rlet_star(bindings: List[Tuple[str, Union[Ranking, Callable]]], body: Callable) -> Ranking:
    """
    API wrapper for the rlet_star macro/combinator.
    Produces a joint ranking over variables, binding sequentially.
    Equivalent to Racket's rlet* macro/combinator.
    """
    from .rp_core import rlet_star as core_rlet_star
    return core_rlet_star(bindings, body)

def ranked_apply(f: Callable, *args: Any) -> Ranking:
    """
    API wrapper for the ranked_apply combinator.
    Applies function f to all combinations of ranked arguments, summing ranks.
    Equivalent to Racket's $ macro/combinator.
    """
    from .rp_core import ranked_apply as core_ranked_apply
    return core_ranked_apply(f, *args)

def observe(pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    API wrapper for the observe macro/combinator.
    Filters a ranking by a predicate and normalizes the result.
    Equivalent to Racket's observe macro/combinator.
    """
    from .rp_core import observe as core_observe
    return core_observe(pred, r)

def observe_all(r: Ranking, predicates: List[Callable[[Any], bool]]) -> Ranking:
    """
    API wrapper for the observe_all macro/combinator.
    Filters a ranking by a list of predicates, keeping only entries that satisfy all predicates, and normalizes the result.
    If predicates is empty, keeps all and normalizes.
    Equivalent to Racket's observe_all macro/combinator.
    """
    from .rp_core import observe_all as core_observe_all
    return core_observe_all(r, predicates)

def limit(n: int, r: Ranking) -> Ranking:
    """
    API wrapper for the limit utility.
    Restricts a ranking to the n lowest-ranked values.
    Equivalent to Racket's limit utility.
    """
    from .rp_core import limit as core_limit
    return core_limit(n, r)

def cut(threshold: int, r: Ranking) -> Ranking:
    """
    API wrapper for the cut utility.
    Restricts a ranking to values with rank <= threshold.
    Equivalent to Racket's cut utility.
    """
    from .rp_core import cut as core_cut
    return core_cut(threshold, r)

def rank_of(pred: Callable[[Any], bool], r: Ranking) -> float:
    """
    API wrapper for the rank_of utility.
    Returns the lowest rank for which pred(value) is True, or float('inf') if none.
    Equivalent to Racket's rank-of utility.
    """
    from .rp_core import rank_of as core_rank_of
    return core_rank_of(pred, r)

def argmin(r: Ranking) -> List[Any]:
    """
    API wrapper for the argmin utility.
    Returns all values with the minimal rank in the ranking.
    Equivalent to Racket's argmin utility.
    """
    from .rp_core import argmin as core_argmin
    return core_argmin(r)

def rf_to_stream(r: Ranking) -> Generator[Tuple[Any, int], None, None]:
    """
    API wrapper for the rf_to_stream utility.
    Converts a ranking to a generator of (value, rank) pairs in order.
    Equivalent to Racket's rf->stream utility.
    """
    from .rp_core import rf_to_stream as core_rf_to_stream
    return core_rf_to_stream(r)

def rf_equal(r1: Ranking, r2: Ranking) -> bool:
    """
    API wrapper for the rf_equal utility.
    Checks if two rankings are equal (same values and ranks, order irrelevant).
    Equivalent to Racket's rf-equal? utility.
    """
    from .rp_core import rf_equal as core_rf_equal
    return core_rf_equal(r1, r2)

def top_k(k: int, r: Ranking) -> List[Any]:
    """
    API wrapper for the top_k utility.
    Returns a list of the k lowest-ranked values from the ranking.
    Equivalent to Racket's top-k utility (if present).
    """
    from .rp_core import top_k as core_top_k
    return core_top_k(k, r)

def rank(obj: Any) -> bool:
    """
    Return True if obj is a valid rank (non-negative integer or infinity).
    Equivalent to Racket's rank? predicate.
    """
    return (isinstance(obj, int) and obj >= 0) or (isinstance(obj, float) and obj == float('inf'))

def observe_e(evidence: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    API wrapper for the observe_e utility.
    Evidence-oriented conditionalization: values for which pred(value) is True keep their rank, others are shifted by evidence, then normalized.
    Equivalent to Racket's observe-e.
    """
    from .rp_core import observe_e as core_observe_e
    return core_observe_e(evidence, pred, r)

def observe_r(rank: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    API wrapper for the observe_r utility.
    Rank-oriented conditionalization: values for which pred(value) is True keep their rank, others are set to the given rank, then normalized.
    Equivalent to Racket's observe-r.
    """
    from .rp_core import observe_r as core_observe_r
    return core_observe_r(rank, pred, r)

def pr_all(r: Ranking) -> None:
    """
    Pretty-print all (value, rank) pairs in order, or print a failure message if empty.
    This is the user-facing pretty-print utility for ranked programming.
    - If the ranking is empty, prints "Failure (empty ranking)".
    - Otherwise, prints a table of ranks and values, one per line.
    Example output:
        Rank  Value
        ------------
            0 foo
            1 bar
        Done
    Args:
        r (Ranking): The input ranking.
    Returns:
        None
    """
    from .rp_core import pr_all as core_pr_all
    return core_pr_all(r)
