"""
Core ranking data structure and basic combinators for ranked programming (lazy by default).

All combinators and the main abstraction (`Ranking`) are lazy, generator-based, and automatically flatten nested values. The API is fully lazy and idiomatic, mirroring the original Racket code's laziness.

Literate documentation and type hints included.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
from collections.abc import Iterable as ABCIterable, Iterator

# --- Ranking: lazy ranked programming abstraction ---

class Ranking(ABCIterable):
    """
    Ranking: A lazy abstraction for ranked programming.

    This class wraps a generator of (value, rank) pairs, allowing for lazy
    combinators and efficient exploration of large or infinite search spaces.

    Example usage:
        def nrm_exc(v1, v2, rank2):
            yield (v1, 0)
            yield (v2, rank2)

        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))
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

    def __iter__(self) -> Iterator[Tuple[Any, int]]:
        return iter(self._generator_fn())

    def to_eager(self) -> list[Tuple[Any, int]]:
        """Materialize all (value, rank) pairs as a list."""
        return list(self)

    def map(self, func: Callable[[Any], Any]) -> 'Ranking':
        """Return a new Ranking with func applied to each value."""
        def mapped():
            for v, r in self:
                yield (func(v), r)
        return Ranking(mapped)

    def filter(self, pred: Callable[[Any], bool]) -> 'Ranking':
        """Return a new Ranking with only values where pred(value) is True."""
        def filtered():
            for v, r in self:
                if pred(v):
                    yield (v, r)
        return Ranking(filtered)

# --- Lazy combinators (now default, no prefix) ---

def _flatten_ranking_like(obj, rank_offset=0):
    """
    Helper: Yield (value, rank) pairs from a Ranking, generator, or iterable, with optional rank offset.
    If obj is a Ranking, generator, or iterable of (value, rank), yields all pairs with rank incremented by rank_offset.
    If obj is a single value, yields (obj, rank_offset).
    """
    from collections.abc import Iterable
    import types
    if isinstance(obj, Ranking):
        for v, r in obj:
            yield (v, r + rank_offset)
    elif isinstance(obj, types.GeneratorType) or (isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, dict))):
        try:
            it = iter(obj)
            first = next(it)
            if isinstance(first, tuple) and len(first) == 2:
                yield (first[0], first[1] + rank_offset)
                for v, r in it:
                    yield (v, r + rank_offset)
            else:
                yield (first, rank_offset)
                for v in it:
                    yield (v, rank_offset)
        except StopIteration:
            return
    else:
        yield (obj, rank_offset)

def nrm_exc(v1, v2, rank2):
    """
    nrm_exc: yields (v1, 0) and all (value, rank) pairs from v2 at rank2 (flattened).

    If v2 is a Ranking or generator, yields all its (value, rank) pairs with rank incremented by rank2.
    If v2 is a single value, yields (v2, rank2).
    This ensures that nested Ranking or generator values are always flattened, never yielded as values.

    If both v1 and v2 are empty (generators that yield nothing), yields nothing.
    """
    yielded = False
    for pair in _flatten_ranking_like(v1, 0):
        yield pair
        yielded = True
    for pair in _flatten_ranking_like(v2, rank2):
        yield pair
        yielded = True
    if not yielded:
        return

def rlet_star(bindings, body):
    """
    rlet_star: Sequential dependent bindings (lazy, default).

    Each binding can be a value, a Ranking, or a function of previous variables returning a generator or Ranking.
    The body can return a value, a Ranking, or a generator; all are automatically flattened so only (value, rank) pairs are yielded.
    Binding functions are called with as many arguments as they accept (from the environment), supporting both zero-argument and multi-argument functions.
    """
    from collections.abc import Iterable
    import inspect
    def to_ranking(val, env):
        if isinstance(val, Ranking):
            return val
        elif callable(val):
            sig = inspect.signature(val)
            n_args = len(sig.parameters)
            result = val(*env[:n_args])
            return Ranking(lambda: _flatten_ranking_like(result, 0))
        else:
            return Ranking(lambda: _flatten_ranking_like(val, 0))
    def helper(idx, env, acc_rank):
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

def rlet(bindings, body):
    """
    rlet: Parallel (cartesian product) bindings (lazy, default).

    Each binding can be a value, a Ranking, or a function of no arguments returning a generator or Ranking.
    Yields (body(*values), total_rank) lazily for each combination (cartesian product of all bindings).
    If the body returns a Ranking or generator, it is automatically flattened so only (value, rank) pairs are yielded.
    """
    from collections.abc import Iterable
    def to_ranking(val):
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

def either_of(*rankings):
    """
    either_of: Lazy union of any number of Ranking objects.
    For duplicate values, keep the lowest rank (first occurrence wins, as in Racket).
    Always yields values in the order they are encountered, with minimal rank.
    """
    seen = {}
    for ranking in rankings:
        for v, r in ranking:
            if v not in seen or r < seen[v]:
                seen[v] = r
    yielded = set()
    for ranking in rankings:
        for v, r in ranking:
            if v in seen and v not in yielded and r == seen[v]:
                yield (v, r)
                yielded.add(v)

def ranked_apply(f, *args):
    """
    ranked_apply: Applies function f to all combinations of lazy ranked arguments.
    Each argument can be a Ranking or a value (treated as rank 0).
    Yields (f(*values), total_rank) lazily for each combination.
    If f(*values) returns a Ranking or generator, it is automatically flattened so only (value, rank) pairs are yielded.
    """
    from collections.abc import Iterable
    def to_ranking(x):
        if isinstance(x, Ranking):
            return x
        else:
            return Ranking(lambda: _flatten_ranking_like(x, 0))
    rankings = [to_ranking(arg) for arg in args]
    from itertools import product
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = f(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            yield (v, r)

def _normalize_ranking(ranking, pred=None, evidence=None, predicates=None):
    """
    Helper: Normalize and filter a Ranking by predicate(s), optionally adjusting ranks for evidence.
    - If pred is given, only values where pred(value) is True are kept.
    - If evidence is given, values not passing pred have evidence added to their rank.
    - If predicates is a list, all must pass.
    Returns a list of (value, rank) pairs with minimal rank normalized to 0.
    """
    if predicates is not None:
        def all_preds(x):
            return all(pred(x) for pred in predicates)
        filtered = [(v, r) for v, r in ranking if all_preds(v)]
    elif pred is not None and evidence is not None:
        filtered = [(v, r if pred(v) else r + evidence) for v, r in ranking]
    elif pred is not None:
        filtered = [(v, r) for v, r in ranking if pred(v)]
    else:
        filtered = [(v, r) for v, r in ranking]
    if not filtered:
        return []
    min_rank = min(r for _, r in filtered)
    return [(v, r - min_rank) for v, r in filtered]

def observe(pred, ranking):
    """
    observe: Filters a Ranking by a predicate, yields only values for which pred(value) is True, and normalizes ranks so the lowest is 0.
    If no values pass, yields nothing (empty generator).
    """
    for v, r in _normalize_ranking(ranking, pred=pred):
        yield (v, r)

def observe_e(evidence, pred, ranking):
    """
    observe_e: For each (value, rank) in ranking:
      - If pred(value) is True, keep rank.
      - Else, add evidence to rank.
    Yields all such pairs, normalized so the lowest rank is 0.
    """
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence):
        yield (v, r)

def observe_all(ranking, predicates):
    """
    observe_all: Filters a Ranking by a list of predicates, keeping only values that satisfy all predicates, and normalizes the result.
    If predicates is empty, all values are kept and normalized.
    """
    for v, r in _normalize_ranking(ranking, predicates=predicates):
        yield (v, r)

def limit(n, ranking):
    """
    limit: Restricts a Ranking to the n lowest-ranked values (in generator order).
    If n <= 0, yields nothing. If n >= number of values, yields all.
    """
    if n <= 0:
        return
    count = 0
    for v, r in ranking:
        if count >= n:
            break
        yield (v, r)
        count += 1

def cut(threshold, ranking):
    """
    cut: Restricts a Ranking to values with rank <= threshold.
    """
    for v, r in ranking:
        if r <= threshold:
            yield (v, r)

def pr_all(ranking) -> None:
    """
    Pretty-print all (value, rank) pairs in order, or print a failure message if empty.
    Works with Ranking.
    """
    items = list(ranking)
    if not items:
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in items:
        print(f"{rank:>5} {v}")
    print("Done")

def pr_first(ranking) -> None:
    """
    Pretty-print the first (lowest-ranked) value and its rank, or print a failure message if empty.
    Works with Ranking.
    """
    items = list(ranking)
    if not items:
        print("Failure (empty ranking)")
        return
    v, rank = items[0]
    print(f"{rank} {v}")

__all__ = [
    'Ranking',
    'nrm_exc',
    'rlet_star',
    'either_of',
    'rlet',
    'ranked_apply',
    'observe',
    'observe_e',
    'observe_all',
    'limit',
    'cut',
    'pr_all',
    'pr_first',
]
