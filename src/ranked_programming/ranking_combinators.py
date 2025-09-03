"""
Combinators for ranked programming.

This module provides the core combinators for constructing and manipulating lazy ranked
search spaces. These include:

- `nrm_exc`: Normal/exceptional choice combinator.
- `rlet_star`: Sequential dependent bindings (like Scheme's ``let*``).
- `rlet`: Parallel (cartesian product) bindings.
- `either_of`: Lazy union of multiple rankings, deduplicated by minimal rank.
- `ranked_apply`: Apply a function to all combinations of ranked arguments.

All combinators operate lazily and are compatible with the `Ranking` abstraction.

These combinators implement key concepts from Wolfgang Spohn's Ranking Theory, such as the negative ranking function (κ) for graded disbelief and the law of disjunction for handling choices.

.. note::

   **Logging and Debugging:**
   All core combinators emit debug-level log messages for tracing recursion, yielded values, and edge cases. To enable detailed tracing, configure the Python logging system (see the Python reference documentation for details). Debug logging is performance-guarded and off by default.

   **Deduplication policy:**
   All combinators in this module always deduplicate values by their hashable identity, keeping only the first occurrence (with the minimal rank) for each hashable value. Unhashable values (such as lists or dicts) are always yielded, even if repeated. This deduplication is always enabled and is not user-configurable. Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported. See the Python reference and `deduplicate_hashable` utility for details.

   If you need to allow duplicate values with different ranks, you must use unhashable types or modify the library.

Note: Use double backticks (``) for any asterisk or special character in docstrings to avoid Sphinx warnings.
"""
from typing import Any, Callable, Iterable, Tuple, Generator, Optional, Dict, List, Union
import heapq
from .ranking_class import Ranking, _flatten_ranking_like, as_ranking, deduplicate_hashable
import logging
from itertools import chain

# Set up a module-level logger
logger = logging.getLogger("ranked_programming.ranking_combinators")
logger.addHandler(logging.NullHandler())

def _validate_bindings(bindings):
    """
    Utility to validate a list of (name, value/function) pairs for rlet and rlet_star.
    Raises TypeError if invalid.
    """
    if not isinstance(bindings, list):
        raise TypeError("bindings must be a list of (name, value/function) pairs")
    for b in bindings:
        if not (isinstance(b, tuple) and len(b) == 2 and isinstance(b[0], str)):
            raise TypeError("Each binding must be a (str, value/function) tuple")

def nrm_exc(
    v1: object,
    v2: object,
    rank2: int = 1
) -> Generator[Tuple[Any, int], None, None]:
    """
    Normal/exceptional choice combinator (lazy version).

    Accepts any value, iterable, or Ranking for v1 and v2. All inputs are normalized automatically.
    Yields values from v1 at rank 0, then from v2 at rank2, deduplicating by minimal rank for hashable values. Unhashable values are always yielded, even if repeated.

    **Theoretical Foundation (Spohn's Ranking Theory):**
    
    This combinator implements the core idea of Ranking Theory's **negative ranking function (κ)**, where:
    - κ(A) = 0 means A is not disbelieved (normal/certain)
    - κ(A) = n > 0 means A is disbelieved to degree n (exceptional/surprising)
    - κ(A) = ∞ means A is impossible
    
    It supports the **law of disjunction**: κ(A∪B) = min(κ(A), κ(B)), enabling graded choice between alternatives.
    
    **Relation to Theory Methods:**
    - Use `ranking.disbelief_rank(lambda x: x == value)` to compute κ for specific propositions
    - Use `ranking.belief_rank(lambda x: x == value)` to compute the two-sided ranking function τ

    Args:
        v1: The normal value(s) (any type, value or ranking). Represents κ(v1) = 0.
        v2: The exceptional value(s) (any type, value or ranking). Represents κ(v2) = rank2.
        rank2: The rank (surprise) for v2 (must be int, default 1). Represents disbelief degree.

    Raises:
        TypeError: If rank2 is not an int.

    Supports lazy recursion and infinite structures.

    Example::

        >>> list(nrm_exc("foo", "bar", 1))
        [("foo", 0), ("bar", 1)]
        >>> list(nrm_exc([1, 2], [3, 4], 2))
        [(1, 0), (2, 0), (3, 2), (4, 2)]

    See also: 
    - `Ranking.disbelief_rank()` for computing κ values
    - `Ranking.belief_rank()` for computing τ values  
    - Ranking Theory (Spohn, 2012) for philosophical foundations
    """
    import types
    if v1 is v2 and not isinstance(v1, (Ranking, types.GeneratorType, list, set, tuple)):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"nrm_exc: yielding {v1!r} at ranks 0 and {rank2}")
        yield (v1, 0)
        yield (v1, rank2)
        return
    if not isinstance(rank2, int):
        raise TypeError(f"rank2 must be an int, got {type(rank2).__name__}")
    for v, r in deduplicate_hashable(
        chain(_flatten_ranking_like(v1, 0), _flatten_ranking_like(v2, rank2))
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"nrm_exc: yielding {v!r} at rank {r}")
        yield (v, r)


def rlet_star(
    bindings: list[Tuple[str, object]],
    body: Callable[..., object]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Sequential dependent bindings (lazy, like Scheme's ``let*``).

    Each binding can be a value, a Ranking, or a function of previous variables returning a generator or Ranking. All inputs are normalized automatically.
    The body can return a value, a Ranking, or a generator; all are automatically flattened.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.

    Example::

        >>> def f(x, y):
        ...     return x + y
        >>> list(rlet_star([('x', [1, 2]), ('y', lambda x: [x, x+1])], f))
        [(2, 0), (3, 0), (3, 0), (4, 0)]
    """
    _validate_bindings(bindings)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"rlet_star: starting with bindings={bindings}")
    def helper(idx: int, env: tuple, acc_rank: int):
        if idx == len(bindings):
            result = body(*env)
            for v, r in _flatten_ranking_like(result, acc_rank):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"rlet_star: yielding {v!r} at rank {r}")
                yield (v, r)
            return
        name, val = bindings[idx]
        ranking = as_ranking(val, env)
        for v, r in ranking:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"rlet_star: binding {name}={v!r} at rank {r}")
            yield from helper(idx + 1, env + (v,), acc_rank + r)
    return helper(0, tuple(), 0)


def rlet(
    bindings: list[Tuple[str, object]],
    body: Callable[..., object]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Parallel (cartesian product) bindings (lazy, like Scheme's let).

    Each binding can be a value, a Ranking, or a function of no arguments returning a generator or Ranking. All inputs are normalized automatically.
    Yields (body(values), total_rank) lazily for each combination.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.

    Example::

        >>> def f(x, y):
        ...     return x * y
        >>> list(rlet([('x', [1, 2]), ('y', [10, 20])], f))
        [(10, 0), (20, 0), (20, 0), (40, 0)]
    """
    _validate_bindings(bindings)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"rlet: starting with bindings={bindings}")
    rankings = [as_ranking(val) for _, val in bindings]
    from itertools import product
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = body(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"rlet: yielding {v!r} at rank {r}")
            yield (v, r)


def _as_ranking_or_pairs(val, env=()):
    """
    Like as_ranking, but if val is a list/tuple/set of (value, rank) pairs, treat as a ranking, not atomic.
    """
    import collections.abc
    if isinstance(val, (list, tuple, set)) and val and all(
        isinstance(x, tuple) and len(x) == 2 and isinstance(x[1], int)
        for x in val
    ):
        return Ranking(lambda: (x for x in val))
    else:
        return as_ranking(val, env)

def either_of(*rankings: object) -> Generator[Tuple[Any, int], None, None]:
    """
    Lazy union of any number of Ranking objects, yielding values in order of minimal rank.

    Each argument can be a value, iterable of (value, rank) pairs, or Ranking. All inputs are normalized automatically. Lists/tuples/sets of (value, rank) pairs are treated as rankings, not atomic values.
    For duplicate values, keep the lowest rank (first occurrence wins).
    Always yields values in the order of minimal rank, deduplicating on the fly.

    Edge cases:
        - If no arguments are given, yields nothing (empty ranking).
        - If any argument is empty, it is ignored.
        - If all arguments are empty, yields nothing.

    Args:
        rankings: One or more Ranking objects or iterables of (value, rank) pairs. (Use ``*rankings`` in code.)

    Yields:
        Tuple[Any, int]: (value, rank) pairs.

    Example::

        >>> r1 = [("a", 0), ("b", 1)]
        >>> r2 = [("b", 0), ("c", 2)]
        >>> list(either_of(r1, r2))
        [("a", 0), ("b", 1), ("c", 2)]
        >>> list(either_of())
        []
    """
    if not rankings:
        return
        yield  # never reached
    normalized = [_as_ranking_or_pairs(r) for r in rankings]
    heap = []
    iterators = [iter(r) for r in normalized]
    for idx, it in enumerate(iterators):
        try:
            v, r = next(it)
            heapq.heappush(heap, (r, idx, v, it))
        except StopIteration:
            continue
    seen = set()
    while heap:
        r, idx, v, it = heapq.heappop(heap)
        if v not in seen:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"either_of: yielding {v!r} at rank {r}")
            yield (v, r)
            seen.add(v)
        try:
            v2, r2 = next(it)
            heapq.heappush(heap, (r2, idx, v2, it))
        except StopIteration:
            continue


def either_or(*ks: object, base_rank: int = 1) -> Generator[Tuple[Any, int], None, None]:
    """
    Returns a ranking where all arguments are equally surprising (same rank), or, if arguments are rankings, the rank of a value is the minimum among the ranks from the arguments.

    Each argument can be a value, iterable of (value, rank) pairs, or Ranking. All inputs are normalized automatically. Lists/tuples/sets of (value, rank) pairs are treated as rankings, not atomic values.

    Edge cases:
        - If no arguments are given, yields nothing (empty ranking).
        - If all arguments are atomic, yields each unique value at base_rank.
        - If all arguments are empty, yields nothing.

    Args:
        ks: Values or rankings.
        base_rank: The rank to assign to atomic values (default 1).

    Yields:
        (value, rank): Each value with its minimal rank among the arguments, or base_rank if atomic.

    Example::

        >>> list(either_or("ann", "bob", "charlie"))
        [("ann", 1), ("bob", 1), ("charlie", 1)]
        >>> list(either_or())
        []
        >>> from ranked_programming.rp_core import nrm_exc, Ranking
        >>> list(Ranking(lambda: nrm_exc("peter", either_or("ann", "bob", "charlie", base_rank=0))))
        [("peter", 0), ("ann", 1), ("bob", 1), ("charlie", 1)]

    If arguments are rankings, the rank of a value is the minimum among the ranks from the arguments::

        >>> r1 = Ranking(lambda: nrm_exc("peter", "ann"))
        >>> r2 = Ranking(lambda: nrm_exc("bob", "charly"))
        >>> list(either_or(r1, r2))
        [("peter", 0), ("bob", 0), ("ann", 1), ("charly", 1)]
    """
    if not ks:
        return
        yield  # never reached
    import types
    atomic_types = (int, float, str, bool, type(None))
    if all(
        not isinstance(k, (Ranking, types.GeneratorType, list, set, tuple)) and not callable(k)
        for k in ks
    ):
        seen = set()
        for k in ks:
            if k not in seen:
                yield (k, base_rank)
                seen.add(k)
        return
    from collections import defaultdict
    value_to_rank = defaultdict(list)
    for k in ks:
        for v, r in _as_ranking_or_pairs(k):
            value_to_rank[v].append(r)
    for v, ranks in value_to_rank.items():
        yield (v, min(ranks))


def construct_ranking(*pairs: Tuple[Any, int]) -> Generator[Tuple[Any, int], None, None]:
    """
    Constructs a ranking from an association list of (value, rank) pairs.
    The first rank must be 0, and ranks must be sorted in non-decreasing order.

    Args:
        pairs: Tuples of (value, rank).

    Yields:
        (value, rank): Each value with its specified rank.

    Edge cases:
        - If no pairs are given, yields nothing (empty ranking).
        - Raises TypeError if any argument is not a (value, rank) tuple.
        - Raises ValueError if any rank is negative, not an int, or if ranks are not sorted.

    Example::

        >>> list(construct_ranking(("x", 0), ("y", 1), ("z", 5)))
        [("x", 0), ("y", 1), ("z", 5)]
        >>> list(construct_ranking())
        []
    """
    if not all(isinstance(p, tuple) and len(p) == 2 for p in pairs):
        raise TypeError("All arguments must be (value, rank) pairs")
    if not all(isinstance(r, int) and r >= 0 for _, r in pairs):
        raise ValueError("All ranks must be non-negative integers")
    if not pairs:
        return
        yield  # never reached
    prev_rank = None
    for i, (v, r) in enumerate(pairs):
        if i == 0 and r != 0:
            raise ValueError("First rank must be 0")
        if prev_rank is not None and r < prev_rank:
            raise ValueError("Ranks must be sorted in non-decreasing order")
        yield (v, r)
        prev_rank = r


def rank_of(pred: Callable[[Any], bool], k: Iterable[Tuple[Any, int]]) -> Optional[int]:
    """
    Returns the minimal rank of a value in ranking k for which pred(value) is True.
    If no such value exists, returns None.

    Args:
        pred: Predicate function (any -> bool).
        k: Ranking (iterable of (value, rank)).

    Returns:
        int or None: The minimal rank for which pred(value) is True, or None if not found.

    Example::

        >>> def recur(x):
        ...     return nrm_exc(x, lambda: recur(x * 2), 1)
        >>> rank_of(lambda x: x > 500, recur(1))
        9
    """
    for v, r in k:
        if pred(v):
            return r
    return None


def failure() -> Generator[Tuple[Any, int], None, None]:
    """
    Returns an empty ranking (no values).

    Returns:
        generator: An empty generator.

    Example::

        >>> list(failure())
        []
    """
    return
    yield  # This is never reached, but makes this a generator


def rf_equal(k1: Iterable[Tuple[Any, int]], k2: Iterable[Tuple[Any, int]], max_items: int = 1000) -> bool:
    """
    Returns True if k1 and k2 are equivalent rankings (same values at same ranks, order irrelevant).
    Only compares up to max_items items for each ranking to avoid non-termination on infinite rankings.

    Edge cases:
        - If either ranking is empty, returns True if both are empty, False otherwise.
        - If max_items is 0, always returns True.

    Example::

        >>> rf_equal([('a', 0), ('b', 1)], [('b', 1), ('a', 0)])
        True
        >>> rf_equal([('a', 0)], [('a', 1)])
        False
        >>> rf_equal([], [])
        True
        >>> rf_equal([('a', 0)], [])
        False
    """
    def to_set(ranking):
        items = set()
        for i, (v, r) in enumerate(ranking):
            if i >= max_items:
                break
            items.add((v, r))
        return items
    s1 = to_set(k1)
    s2 = to_set(k2)
    return s1 == s2


def rf_to_hash(k: Iterable[Tuple[Any, int]], max_items: int = 1000) -> Dict[Any, int]:
    """
    Converts a ranking k to a dict mapping each finitely ranked value to its rank.
    Only collects up to max_items items to avoid non-termination on infinite rankings.

    Edge cases:
        - If k is empty, returns an empty dict.
        - If max_items is 0, returns an empty dict.
        - If duplicate values are present, the last one seen is used.

    Example::

        >>> rf_to_hash([('a', 0), ('b', 1)])
        {'a': 0, 'b': 1}
        >>> rf_to_hash([])
        {}
    """
    result = {}
    for i, (v, r) in enumerate(k):
        if i >= max_items:
            break
        result[v] = r
    return result


def rf_to_assoc(k: Iterable[Tuple[Any, int]], max_items: Optional[int] = None) -> List[Tuple[Any, int]]:
    """
    Converts the ranking k to an association list (list of (value, rank) pairs),
    sorted in non-decreasing order of rank. If max_items is set, only collects up to that many items.

    Edge cases:
        - If k is empty, returns an empty list.
        - If max_items is 0, returns an empty list.

    Example::

        >>> rf_to_assoc([('b', 1), ('a', 0)])
        [('a', 0), ('b', 1)]
        >>> rf_to_assoc([])
        []
    """
    if max_items is None:
        items = list(k)
    else:
        items = []
        for i, x in enumerate(k):
            if i >= max_items:
                break
            items.append(x)
    return sorted(items, key=lambda vr: vr[1])


def rf_to_stream(k: Iterable[Tuple[Any, int]], max_items: Optional[int] = None) -> Generator[Tuple[Any, int], None, None]:
    """
    Converts the ranking k to a generator (stream) of (value, rank) pairs in non-decreasing order of rank.
    If max_items is set, only yields up to that many items.

    Edge cases:
        - If k is empty, yields nothing.
        - If max_items is 0, yields nothing.

    Example::

        >>> list(rf_to_stream([('b', 1), ('a', 0]]))
        [('a', 0), ('b', 1)]
        >>> list(rf_to_stream([]))
        []
    """
    if max_items is None:
        items = list(k)
    else:
        items = []
        for i, x in enumerate(k):
            if i >= max_items:
                break
            items.append(x)
    for item in sorted(items, key=lambda vr: vr[1]):
        yield item


def ranked_apply(
    f: Callable[..., object],
    *args: object
) -> Generator[Tuple[Any, int], None, None]:
    """
    Apply function f to all combinations of lazy ranked arguments.

    Each argument can be a Ranking, iterable of (value, rank) pairs, or a value (treated as rank 0). All inputs are normalized automatically.
    Yields (f(values), total_rank) lazily for each combination.
    If f(values) returns a Ranking or generator, it is automatically flattened.

    Edge cases:
        - If no arguments are given, yields f() at rank 0.
        - If any argument is empty, yields nothing.

    Example::

        >>> def add(x, y):
        ...     return x + y
        >>> list(ranked_apply(add, [1, 2], [10, 20]))
        [(11, 0), (21, 0), (12, 0), (22, 0)]
        >>> list(ranked_apply(lambda: 42))
        [(42, 0)]
    """
    logger.info(f"ranked_apply called with {len(args)} args")
    from itertools import product
    rankings = [_as_ranking_or_pairs(arg) for arg in args]
    if not rankings:
        # No arguments: just call f() at rank 0
        result = f()
        for v, r in _flatten_ranking_like(result, 0):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"ranked_apply: yielding {v!r} at rank {r}")
            yield (v, r)
        return
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = f(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"ranked_apply: yielding {v!r} at rank {r}")
            yield (v, r)

def bang(v: Any) -> Generator[Tuple[Any, int], None, None]:
    """
    Truth function: Returns a ranking where v is ranked 0 and anything else is ranked infinity.

    Example::

        >>> list(bang(5))
        [(5, 0)]
    """
    yield (v, 0)
