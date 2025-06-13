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

def nrm_exc(
    v1: object,
    v2: object,
    rank2: int
) -> Generator[Tuple[Any, int], None, None]:
    """
    Yield (v1, 0) and all (value, rank) pairs from v2 at rank2 (flattened).

    Args:
        v1: First value or Ranking/generator/iterable.
        v2: Second value or Ranking/generator/iterable.
        rank2: Rank to assign to v2 (or its values).

    Raises:
        TypeError: If rank2 is not an int.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    if not isinstance(rank2, int):
        raise TypeError(f"rank2 must be int, got {type(rank2).__name__}")
    yielded = False
    for pair in _flatten_ranking_like(v1, 0):
        yield pair
        yielded = True
    for pair in _flatten_ranking_like(v2, rank2):
        yield pair
        yielded = True
    if not yielded:
        return

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
