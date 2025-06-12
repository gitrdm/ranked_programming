"""
Core ranking data structure and basic combinators for ranked programming.

Literate documentation and type hints included.
"""
from typing import Any, List, Tuple, Optional, Callable, Dict, Union, Generator

# --- LazyRanking: lazy ranked programming abstraction ---

from typing import Callable, Generator, Iterable, Tuple, Any

class LazyRanking:
    """
    LazyRanking: A lazy abstraction for ranked programming.

    This class wraps a generator of (value, rank) pairs, allowing for lazy
    combinators and efficient exploration of large or infinite search spaces.

    Example usage:
        def lazy_nrm_exc(v1, v2, rank2):
            yield (v1, 0)
            yield (v2, rank2)

        ranking = LazyRanking(lambda: lazy_nrm_exc('A', 'B', 1))
        for value, rank in ranking:
            print(value, rank)

    Methods:
        - __iter__: Iterate over (value, rank) pairs lazily.
        - to_eager: Materialize all pairs as a list.
        - map: Lazily map a function over values.
        - filter: Lazily filter values.
    """
    def __init__(self, generator_fn: Callable[[], Iterable[Tuple[Any, int]]]):
        self._generator_fn = generator_fn

    def __iter__(self):
        return iter(self._generator_fn())

    def to_eager(self) -> list:
        """Materialize all (value, rank) pairs as a list."""
        return list(self)

    def map(self, func: Callable[[Any], Any]) -> 'LazyRanking':
        """Return a new LazyRanking with func applied to each value."""
        def mapped():
            for v, r in self:
                yield (func(v), r)
        return LazyRanking(mapped)

    def filter(self, pred: Callable[[Any], bool]) -> 'LazyRanking':
        """Return a new LazyRanking with only values where pred(value) is True."""
        def filtered():
            for v, r in self:
                if pred(v):
                    yield (v, r)
        return LazyRanking(filtered)

def lazy_nrm_exc(v1, v2, rank2):
    """
    Lazy version of nrm_exc: yields (v1, 0) and all (value, rank) pairs from v2 at rank2 (flattened).

    If v2 is a LazyRanking or generator, yields all its (value, rank) pairs with rank incremented by rank2.
    If v2 is a single value, yields (v2, rank2).
    This ensures that nested LazyRanking or generator values are always flattened, never yielded as values.

    If both v1 and v2 are empty (generators that yield nothing), yields nothing.
    """
    from collections.abc import Iterable
    # Helper to check if a generator/iterable is empty without consuming it
    def is_empty_iterable(obj):
        try:
            it = iter(obj)
            first = next(it)
            # Not empty, re-yield first
            def new_gen():
                yield first
                yield from it
            return False, new_gen()
        except StopIteration:
            return True, None
        except TypeError:
            return False, obj
    # Handle v1
    v1_is_empty = False
    if isinstance(v1, LazyRanking):
        v1_iter = iter(v1)
        try:
            v1_first = next(v1_iter)
            def v1_gen():
                yield v1_first
                yield from v1_iter
            v1 = v1_gen()
        except StopIteration:
            v1_is_empty = True
    elif isinstance(v1, Iterable) and not isinstance(v1, (str, bytes, dict)):
        v1_is_empty, v1 = is_empty_iterable(v1)
    # Handle v2
    v2_is_empty = False
    if isinstance(v2, LazyRanking):
        v2_iter = iter(v2)
        try:
            v2_first = next(v2_iter)
            def v2_gen():
                yield v2_first
                yield from v2_iter
            v2 = v2_gen()
        except StopIteration:
            v2_is_empty = True
    elif isinstance(v2, Iterable) and not isinstance(v2, (str, bytes, dict)):
        v2_is_empty, v2 = is_empty_iterable(v2)
    # If both are empty, yield nothing
    if v1_is_empty and v2_is_empty:
        return
    # Yield v1 if not empty
    if not v1_is_empty:
        if isinstance(v1, Iterable) and not isinstance(v1, (str, bytes, dict)):
            for v, r in v1:
                yield (v, r)
        else:
            yield (v1, 0)
    # Yield v2 if not empty
    if not v2_is_empty:
        if isinstance(v2, Iterable) and not isinstance(v2, (str, bytes, dict)):
            for v, r in v2:
                yield (v, r + rank2)
        else:
            yield (v2, rank2)

def lazy_rlet_star(bindings, body):
    """
    lazy_rlet_star: Lazy version of rlet_star for sequential dependent bindings.

    Each binding can be a value, a LazyRanking, or a function of previous variables returning a generator or LazyRanking.
    The body can return a value, a LazyRanking, or a generator; all are automatically flattened so only (value, rank) pairs are yielded.
    Binding functions are called with as many arguments as they accept (from the environment), supporting both zero-argument and multi-argument functions.

    Example:
        def b1():
            yield (1, 0)
            yield (2, 1)
        def b2(x):
            yield (x + 10, 0)
            yield (x + 20, 2)
        def body(x, y):
            def gen():
                yield (x + y, 0)
                yield (x * y, 1)
            return gen()
        ranking = LazyRanking(lambda: lazy_rlet_star([
            ('x', b1),
            ('y', b2)
        ], body))
        # yields all (value, rank) pairs from the body, flattened
    """
    from collections.abc import Iterable
    import types
    import inspect
    def to_lazyranking(val, env):
        if isinstance(val, LazyRanking):
            return val
        elif callable(val):
            # Call with as many env args as the function accepts
            sig = inspect.signature(val)
            n_args = len(sig.parameters)
            result = val(*env[:n_args])
            if isinstance(result, LazyRanking):
                return result
            elif isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict, tuple)):
                return LazyRanking(lambda: result)
            else:
                return LazyRanking(lambda: ((result, 0),))
        else:
            return LazyRanking(lambda: ((val, 0),))
    def helper(idx, env, acc_rank):
        if idx == len(bindings):
            result = body(*env)
            if isinstance(result, LazyRanking):
                for v, r in result:
                    yield (v, acc_rank + r)
            elif isinstance(result, types.GeneratorType):
                for v, r in result:
                    yield (v, acc_rank + r)
            else:
                yield (result, acc_rank)
            return
        name, val = bindings[idx]
        ranking = to_lazyranking(val, env)
        for v, r in ranking:
            yield from helper(idx + 1, env + (v,), acc_rank + r)
    return helper(0, tuple(), 0)

def lazy_rlet(bindings, body):
    """
    lazy_rlet: Lazy version of rlet for parallel (cartesian product) bindings.

    Each binding can be a value, a LazyRanking, or a function of no arguments returning a generator or LazyRanking.
    Yields (body(*values), total_rank) lazily for each combination (cartesian product of all bindings).
    If the body returns a LazyRanking or generator, it is automatically flattened so only (value, rank) pairs are yielded.

    Example:
        def b1():
            yield (1, 0)
            yield (2, 1)
        def b2():
            yield (10, 0)
            yield (20, 2)
        def body(x, y):
            def gen():
                yield (x + y, 0)
                yield (x * y, 1)
            return gen()
        ranking = LazyRanking(lambda: lazy_rlet([
            ('x', b1),
            ('y', b2)
        ], body))
        # yields all (value, rank) pairs from the body, flattened
    """
    from collections.abc import Iterable
    import types
    def to_lazyranking(val):
        if isinstance(val, LazyRanking):
            return val
        elif callable(val):
            result = val()
            if isinstance(result, LazyRanking):
                return result
            elif isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
                return LazyRanking(lambda: result)
            else:
                return LazyRanking(lambda: ((result, 0),))
        else:
            return LazyRanking(lambda: ((val, 0),))
    rankings = [to_lazyranking(val) for _, val in bindings]
    from itertools import product
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = body(*values)
        # Flatten if result is LazyRanking or generator
        if isinstance(result, LazyRanking):
            for v, r in result:
                yield (v, total_rank + r)
        elif isinstance(result, types.GeneratorType):
            for v, r in result:
                yield (v, total_rank + r)
        else:
            yield (result, total_rank)

def lazy_either_of(*rankings):
    """
    lazy_either_of: Lazy union of any number of LazyRanking objects.
    For duplicate values, keep the lowest rank (first occurrence wins, as in Racket).
    Always yields values in the order they are encountered, with minimal rank.
    Example:
        r1 = LazyRanking(lambda: lazy_nrm_exc('A', 'B', 1))
        r2 = LazyRanking(lambda: lazy_nrm_exc('B', 'C', 2))
        ranking = LazyRanking(lambda: lazy_either_of(r1, r2))
        for value, rank in ranking:
            print(value, rank)
    """
    seen = {}
    for ranking in rankings:
        for v, r in ranking:
            if v not in seen or r < seen[v]:
                seen[v] = r
    # Yield in the order of first occurrence in any ranking
    yielded = set()
    for ranking in rankings:
        for v, r in ranking:
            if v in seen and v not in yielded and r == seen[v]:
                yield (v, r)
                yielded.add(v)
    # If no values, yield nothing (empty generator)

def lazy_ranked_apply(f, *args):
    """
    lazy_ranked_apply: Lazy version of ranked_apply.
    Applies function f to all combinations of lazy ranked arguments.
    Each argument can be a LazyRanking or a value (treated as rank 0).
    Yields (f(*values), total_rank) lazily for each combination.
    If f(*values) returns a LazyRanking or generator, it is automatically flattened so only (value, rank) pairs are yielded.
    Example:
        r1 = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
        r2 = LazyRanking(lambda: lazy_nrm_exc(10, 20, 2))
        def f(x, y):
            def gen():
                yield (x + y, 0)
                yield (x * y, 1)
            return gen()
        ranking = LazyRanking(lambda: lazy_ranked_apply(f, r1, r2))
        # yields all (value, rank) pairs from f, flattened
    """
    from collections.abc import Iterable
    import types
    def to_lazyranking(x):
        if isinstance(x, LazyRanking):
            return x
        else:
            return LazyRanking(lambda: ((x, 0),))
    rankings = [to_lazyranking(arg) for arg in args]
    from itertools import product
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = f(*values)
        # Flatten if result is LazyRanking or generator
        if isinstance(result, LazyRanking):
            for v, r in result:
                yield (v, total_rank + r)
        elif isinstance(result, types.GeneratorType):
            for v, r in result:
                yield (v, total_rank + r)
        else:
            yield (result, total_rank)

def lazy_observe(pred, ranking):
    """
    lazy_observe: Lazy version of observe.
    Filters a LazyRanking by a predicate, yields only values for which pred(value) is True, and normalizes ranks so the lowest is 0.
    If no values pass, yields nothing (empty generator).
    Example:
        r = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
        filtered = LazyRanking(lambda: lazy_observe(lambda x: x == 2, r))
        for value, rank in filtered:
            print(value, rank)
    """
    # Materialize to find the minimum rank among passing values
    filtered = [(v, r) for v, r in ranking if pred(v)]
    if not filtered:
        return
    min_rank = min(r for _, r in filtered)
    for v, r in filtered:
        yield (v, r - min_rank)

def lazy_observe_e(evidence, pred, ranking):
    """
    lazy_observe_e: Lazy version of observe_e.
    For each (value, rank) in ranking:
      - If pred(value) is True, keep rank.
      - Else, add evidence to rank.
    Yields all such pairs, normalized so the lowest rank is 0.
    Example:
        r = LazyRanking(lambda: lazy_nrm_exc(1, 2, 1))
        filtered = LazyRanking(lambda: lazy_observe_e(5, lambda x: x == 2, r))
        for value, rank in filtered:
            print(value, rank)
    """
    adjusted = [(v, r if pred(v) else r + evidence) for v, r in ranking]
    if not adjusted:
        return
    min_rank = min(r for _, r in adjusted)
    for v, r in adjusted:
        yield (v, r - min_rank)

def lazy_observe_all(ranking, predicates):
    """
    lazy_observe_all: Lazy version of observe_all.
    Filters a LazyRanking by a list of predicates, keeping only values that satisfy all predicates, and normalizes the result.
    If predicates is empty, all values are kept and normalized.
    Example:
        r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
        filtered = LazyRanking(lambda: lazy_observe_all(r, [lambda x: x > 10, lambda x: x < 30]))
        for value, rank in filtered:
            print(value, rank)
    """
    if not predicates:
        # Just normalize all values
        filtered = [(v, r) for v, r in ranking]
    else:
        def all_preds(x):
            return all(pred(x) for pred in predicates)
        filtered = [(v, r) for v, r in ranking if all_preds(v)]
    if not filtered:
        return
    min_rank = min(r for _, r in filtered)
    for v, r in filtered:
        yield (v, r - min_rank)

def lazy_limit(n, ranking):
    """
    lazy_limit: Lazy version of limit.
    Restricts a LazyRanking to the n lowest-ranked values (in generator order).
    If n <= 0, yields nothing. If n >= number of values, yields all.
    Example:
        r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
        limited = LazyRanking(lambda: lazy_limit(2, r))
        for value, rank in limited:
            print(value, rank)
    """
    if n <= 0:
        return
    count = 0
    for v, r in ranking:
        if count >= n:
            break
        yield (v, r)
        count += 1

def lazy_cut(threshold, ranking):
    """
    lazy_cut: Lazy version of cut.
    Restricts a LazyRanking to values with rank <= threshold.
    Example:
        r = LazyRanking(lambda: ((10, 5), (20, 7), (30, 6)))
        cut_r = LazyRanking(lambda: lazy_cut(6, r))
        for value, rank in cut_r:
            print(value, rank)
    """
    for v, r in ranking:
        if r <= threshold:
            yield (v, r)

__all__ = [
    'LazyRanking',
    'lazy_nrm_exc',
    'lazy_rlet_star',
    'lazy_either_of',
    'lazy_rlet',
    'lazy_ranked_apply',
    'lazy_observe',
    'lazy_observe_e',
    'lazy_observe_all',
    'lazy_limit',
    'lazy_cut',
]
