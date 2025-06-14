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

Note: Use double backticks (``) for any asterisk or special character in docstrings to avoid Sphinx warnings.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
import heapq
from .ranking_class import Ranking, _flatten_ranking_like
import logging

# Set up a module-level logger
logger = logging.getLogger("ranked_programming.ranking_combinators")
logger.addHandler(logging.NullHandler())

def nrm_exc(
    v1: object,
    v2: object,
    rank2: int = 1
) -> Generator[Tuple[Any, int], None, None]:
    # Logging removed to avoid RecursionError in deep recursion
    """
    Normal/exceptional choice combinator (lazy version).

    Yields values from v1 at rank 0, then from v2 at rank2, deduplicating by minimal rank.
    Supports lazy recursion and infinite structures.
    """
    if not isinstance(rank2, int):
        logger.error(f"rank2 must be int, got {type(rank2).__name__}")
        raise TypeError(f"rank2 must be int, got {type(rank2).__name__}")
    import types
    atomic_types = (int, float, str, bool, type(None))
    if v1 is v2 and not isinstance(v1, (Ranking, types.GeneratorType, list, set, tuple)):
        logger.debug(f"Special case: v1 is v2 and atomic: {repr(v1)}")
        yield (v1, 0)
        yield (v1, rank2)
        return
    yielded_hashable = set()
    # First yield from v1 at rank 0
    for v, r in _flatten_ranking_like(v1, 0):
        # Do NOT call v if it's callable; let _flatten_ranking_like handle laziness
        if hasattr(v, '__hash__') and v not in yielded_hashable:
            logger.debug(f"Yield hashable from v1: {v} at rank={r}")
            yield (v, r)
            yielded_hashable.add(v)
        elif not hasattr(v, '__hash__'):
            logger.debug(f"Yield unhashable from v1: {v} at rank={r}")
            yield (v, r)
    # Then yield from v2 at rank2, skipping values already yielded
    for v, r in _flatten_ranking_like(v2, rank2):
        # Do NOT call v if it's callable; let _flatten_ranking_like handle laziness
        if hasattr(v, '__hash__') and v not in yielded_hashable:
            logger.debug(f"Yield hashable from v2: {v} at rank={r}")
            yield (v, r)
            yielded_hashable.add(v)
        elif not hasattr(v, '__hash__'):
            logger.debug(f"Yield unhashable from v2: {v} at rank={r}")
            yield (v, r)

def rlet_star(
    bindings: list[Tuple[str, object]],
    body: Callable[..., object]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Sequential dependent bindings (lazy, like Scheme's ``let``).

    Each binding can be a value, a Ranking, or a function of previous variables returning a generator or Ranking.
    The body can return a value, a Ranking, or a generator; all are automatically flattened.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    logger.info(f"rlet_star called with bindings={bindings}")
    import inspect
    def to_ranking(val: object, env: tuple) -> Ranking:
        if isinstance(val, Ranking):
            return val
        elif callable(val):
            sig = inspect.signature(val)
            n_args = len(sig.parameters)
            result = val(*env[:n_args])
            return Ranking(lambda: _flatten_ranking_like(result, 0))
        else:
            return Ranking(lambda: _flatten_ranking_like(val, 0))
    def helper(idx: int, env: tuple, acc_rank: int):
        if idx == len(bindings):
            result = body(*env)
            for v, r in _flatten_ranking_like(result, acc_rank):
                yield (v, r)
            return
        name, val = bindings[idx]
        ranking = to_ranking(val, env)
        for v, r in ranking:
            yield from helper(idx + 1, env + (v,), acc_rank + r)
    return helper(0, tuple(), 0)

def rlet(
    bindings: list[Tuple[str, object]],
    body: Callable[..., object]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Parallel (cartesian product) bindings (lazy, like Scheme's let).

    Each binding can be a value, a Ranking, or a function of no arguments returning a generator or Ranking.
    Yields (body(values), total_rank) lazily for each combination.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    logger.info(f"rlet called with bindings={bindings}")
    def to_ranking(val: object) -> Ranking:
        if isinstance(val, Ranking):
            return val
        elif callable(val):
            result = val()
            return Ranking(lambda: _flatten_ranking_like(result, 0))
        else:
            return Ranking(lambda: _flatten_ranking_like(val, 0))
    rankings = [to_ranking(val) for _, val in bindings]
    from itertools import product
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = body(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            yield (v, r)

def either_of(*rankings: Iterable[Tuple[Any, int]]) -> Generator[Tuple[Any, int], None, None]:
    """
    Lazy union of any number of Ranking objects, yielding values in order of minimal rank.

    For duplicate values, keep the lowest rank (first occurrence wins).
    Always yields values in the order of minimal rank, deduplicating on the fly.

    Args:
        rankings: One or more Ranking objects or iterables of (value, rank) pairs. (Use ``*rankings`` in code.)

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    logger.info(f"either_of called with {len(rankings)} rankings")
    heap = []
    iterators = [iter(r) for r in rankings]
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
            yield (v, r)
            seen.add(v)
        try:
            v2, r2 = next(it)
            heapq.heappush(heap, (r2, idx, v2, it))
        except StopIteration:
            continue

def either_or(*ks, base_rank=1):
    """
    Returns a ranking where all arguments are equally surprising (same rank), or, if arguments are rankings, the rank of a value is the minimum among the ranks from the arguments.

    Args:
        ks: Values or rankings.
        base_rank: The rank to assign to atomic values (default 1).

    Yields:
        (value, rank): Each value with its minimal rank among the arguments, or base_rank if atomic.

    Example::

        >>> list(either_or("ann", "bob", "charlie"))
        [("ann", 1), ("bob", 1), ("charlie", 1)]
        >>> from ranked_programming.rp_core import nrm_exc, Ranking
        >>> list(Ranking(lambda: nrm_exc("peter", either_or("ann", "bob", "charlie", base_rank=0))))
        [("peter", 0), ("ann", 1), ("bob", 1), ("charlie", 1)]

    If arguments are rankings, the rank of a value is the minimum among the ranks from the arguments::

        >>> r1 = Ranking(lambda: nrm_exc("peter", "ann"))
        >>> r2 = Ranking(lambda: nrm_exc("bob", "charly"))
        >>> list(either_or(r1, r2))
        [("peter", 0), ("bob", 0), ("ann", 1), ("charly", 1)]
    """
    from .ranking_class import Ranking, _flatten_ranking_like
    import types
    # If all arguments are atomic (not Ranking, not generator, not callable), treat as equally surprising at base_rank
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
    # Otherwise, treat as rankings and yield values with minimal rank
    from collections import defaultdict
    value_to_rank = defaultdict(list)
    for k in ks:
        for v, r in _flatten_ranking_like(k, 0):
            value_to_rank[v].append(r)
    for v, ranks in value_to_rank.items():
        yield (v, min(ranks))

def ranked_apply(
    f: Callable[..., object],
    *args: object
) -> Generator[Tuple[Any, int], None, None]:
    """
    Apply function f to all combinations of lazy ranked arguments.

    Each argument can be a Ranking or a value (treated as rank 0).
    Yields (f(values), total_rank) lazily for each combination.
    If f(values) returns a Ranking or generator, it is automatically flattened.

    Args:
        f: Function to apply.
        args: Ranking or value arguments. (Use ``*args`` in code.)

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    logger.info(f"ranked_apply called with {len(args)} args")
    from itertools import product
    def to_ranking(x: object) -> Ranking:
        if isinstance(x, Ranking):
            return x
        else:
            return Ranking(lambda: _flatten_ranking_like(x, 0))
    rankings = [to_ranking(arg) for arg in args]
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = f(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            yield (v, r)

def bang(v):
    """
    Truth function: Returns a ranking where v is ranked 0 and anything else is ranked infinity.

    Args:
        v: The value to be ranked 0.

    Yields:
        (value, rank): (v, 0)

    Example::

        >>> list(bang(5))
        [(5, 0)]
    """
    yield (v, 0)

def construct_ranking(*pairs):
    """
    Constructs a ranking from an association list of (value, rank) pairs.
    The first rank must be 0, and ranks must be sorted in non-decreasing order.

    Args:
        pairs: Tuples of (value, rank).

    Yields:
        (value, rank): Each value with its specified rank.

    Example::

        >>> list(construct_ranking(("x", 0), ("y", 1), ("z", 5)))
        [("x", 0), ("y", 1), ("z", 5)]
    """
    if not pairs:
        return
    prev_rank = None
    for i, (v, r) in enumerate(pairs):
        if i == 0 and r != 0:
            raise ValueError("First rank must be 0")
        if prev_rank is not None and r < prev_rank:
            raise ValueError("Ranks must be sorted in non-decreasing order")
        yield (v, r)
        prev_rank = r

def rank_of(pred, k):
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

def failure():
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

def rf_equal(k1, k2, max_items=1000):
    """
    Returns True if k1 and k2 are equivalent rankings (same values at same ranks, order irrelevant).
    Only compares up to max_items items for each ranking to avoid non-termination on infinite rankings.
    """
    # Convert to (value, rank) pairs, up to max_items
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

def rf_to_hash(k, max_items=1000):
    """
    Converts a ranking k to a dict mapping each finitely ranked value to its rank.
    Only collects up to max_items items to avoid non-termination on infinite rankings.
    """
    result = {}
    for i, (v, r) in enumerate(k):
        if i >= max_items:
            break
        result[v] = r
    return result

def rf_to_assoc(k, max_items=1000):
    """
    Converts a ranking k to a list of (value, rank) pairs, sorted by non-decreasing rank.
    Only collects up to max_items items to avoid non-termination on infinite rankings.
    """
    items = []
    for i, (v, r) in enumerate(k):
        if i >= max_items:
            break
        items.append((v, r))
    items.sort(key=lambda x: x[1])
    return items
