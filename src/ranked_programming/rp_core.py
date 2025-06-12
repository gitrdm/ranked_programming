"""
Core ranking data structure and basic combinators for ranked programming.

Literate documentation and type hints included.
"""
from typing import Any, List, Tuple, Optional, Callable, Dict, Union, Generator

class Ranking:
    """
    Represents a ranking: a list of (value, rank) pairs, sorted by rank.
    An empty ranking represents failure.
    """
    def __init__(self, items: Optional[List[Tuple[Any, int]]] = None):
        self.items = [] if items is None else [ (v, int(r)) for v, r in items ]
        self.items.sort(key=lambda x: x[1])

    def is_empty(self) -> bool:
        """Return True if the ranking is empty (failure)."""
        return len(self.items) == 0

    def to_assoc(self) -> List[Tuple[Any, int]]:
        """Return the ranking as a list of (value, rank) pairs."""
        return list(self.items)

    def __eq__(self, other):
        if not isinstance(other, Ranking):
            return False
        return self.items == other.items

    def __repr__(self):
        return f"Ranking({self.items})"

    def filter(self, pred: Callable[[Any], bool]) -> 'Ranking':
        """
        Return a new Ranking containing only values for which pred(value) is True, keeping ranks unchanged.
        """
        return Ranking([(v, r) for v, r in self.items if pred(v)])

    def normalize(self) -> 'Ranking':
        """
        Return a new Ranking with ranks shifted so the minimum is 0. If empty, returns empty.
        """
        if self.is_empty():
            return Ranking([])
        min_rank = min(r for _, r in self.items)
        return Ranking([(v, r - min_rank) for v, r in self.items])

def failure() -> Ranking:
    """
    Return an empty ranking (failure).
    Equivalent to the Racket (failure) constructor.
    """
    return Ranking([])

def construct_ranking(*args: Tuple[Any, int]) -> Ranking:
    """
    Construct a ranking from (value, rank) pairs.
    If no arguments, returns an empty ranking (failure).
    Example: construct_ranking((1, 0), (2, 1))
    """
    return Ranking(list(args))

# --- New combinator: normalise ---
def normalise(r: Ranking) -> Ranking:
    """
    Shift all ranks so the minimum is 0. If empty, returns empty.
    Equivalent to Racket's normalise.
    """
    if r.is_empty():
        return failure()
    min_rank = min(rank for _, rank in r.items)
    return Ranking([(v, rank - min_rank) for v, rank in r.items])

def map_value(f, r: Ranking) -> Ranking:
    """
    Apply function f to each value in the ranking, keeping ranks unchanged.
    Equivalent to Racket's map-value.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    return Ranking([(f(v), rank) for v, rank in r.items])

def shift(amount: int, r: Ranking) -> Ranking:
    """
    Shift all ranks in the ranking by a constant amount.
    Equivalent to Racket's shift.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    return Ranking([(v, rank + amount) for v, rank in r.items])

def filter_ranking(pred, r: Ranking) -> Ranking:
    """
    Filter the ranking by a predicate on values, keeping ranks unchanged.
    Equivalent to Racket's filter-ranking.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if pred(v)]
    return Ranking(filtered)

def filter_after(pred, r: Ranking) -> Ranking:
    """
    Keep only the entries after the first one where pred(value) is True (inclusive).
    Equivalent to Racket's filter-after.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    found = False
    filtered = []
    for v, rank in r.items:
        if not found and pred(v):
            found = True
        if found:
            filtered.append((v, rank))
    return Ranking(filtered)

def up_to_rank(max_rank: int, r: Ranking) -> Ranking:
    """
    Keep only entries with rank <= max_rank.
    Equivalent to Racket's up-to-rank.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if rank <= max_rank]
    return Ranking(filtered)

def dedup(r: Ranking) -> Ranking:
    """
    Remove duplicate values, keeping the first occurrence (lowest rank).
    Equivalent to Racket's dedup.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    seen = set()
    deduped = []
    for v, rank in r.items:
        if v not in seen:
            seen.add(v)
            deduped.append((v, rank))
    return Ranking(deduped)

def do_with(f, r: Ranking) -> int:
    """
    Apply function f to each (value, rank) pair in the ranking and sum the results.
    Equivalent to Racket's do-with.
    Returns the sum, or 0 for empty ranking.
    """
    if r.is_empty():
        return 0
    return sum(f(v, rank) for v, rank in r.items)

def either_of(*rankings: Ranking) -> Ranking:
    """
    Return the normalized union of any number of rankings.
    For duplicate values, keep the lowest rank.
    Always normalizes the result, even for a single ranking.
    Equivalent to the Racket either_of combinator.
    """
    non_empty = [r for r in rankings if not r.is_empty()]
    if not non_empty:
        return failure()
    combined = {}
    for r in non_empty:
        for v, rank in r.items:
            if v in combined:
                combined[v] = min(combined[v], rank)
            else:
                combined[v] = rank
    result = Ranking(list(combined.items()))
    return normalise(result)

def either_or(*rankings: Ranking) -> Ranking:
    """
    Return a ranking where all unique values from the input rankings are assigned rank 0.
    Duplicates are removed. If all rankings are empty, returns failure().
    Equivalent to the Racket either/or macro/combinator.
    """
    values = set()
    for r in rankings:
        for v, _ in r.items:
            values.add(v)
    if not values:
        return failure()
    return Ranking([(v, 0) for v in values])

def nrm_exc(v1: Any, v2: Any, rank: int = 1) -> Ranking:
    """
    Construct a ranking with a normal and exceptional value (or ranking).
    - If v1 and v2 are not rankings, treat them as singleton rankings.
    - v1 is always at rank 0.
    - v2 is at rank `rank` (default 1).
    - If v1 or v2 is empty, return the other (shifted as needed).
    - If both are empty, return failure().
    Equivalent to the Racket nrm/exc macro/combinator.
    """
    from .rp_core import Ranking, failure
    def to_ranking(x):
        if isinstance(x, Ranking):
            return x
        return Ranking([(x, 0)])
    r1 = to_ranking(v1)
    r2 = to_ranking(v2)
    if r1.is_empty() and r2.is_empty():
        return failure()
    if r1.is_empty():
        # Only exceptional part
        return Ranking([(v, rank) for v, _ in r2.items])
    if r2.is_empty():
        return r1
    # Merge: r1 at 0, r2 shifted by rank
    merged = r1.items + [(v, r + rank) for v, r in r2.items]
    return Ranking(merged)

def rlet(bindings: Dict[str, Ranking], body: Callable) -> Ranking:
    """
    Ranked let: produce a joint ranking over variables.
    - bindings: dict mapping variable names to Ranking or value
    - body: function taking variables in order and returning a value
    The rank of each result is the sum of the ranks of the chosen values.
    If any input ranking is empty, the result is empty.
    Equivalent to the Racket rlet macro/combinator.
    """
    # Convert all values to rankings if needed
    var_names = list(bindings.keys())
    rankings = []
    for v in var_names:
        val = bindings[v]
        if isinstance(val, Ranking):
            rankings.append(val)
        else:
            rankings.append(Ranking([(val, 0)]))
    if any(r.is_empty() for r in rankings):
        return failure()
    # Build joint ranking: cartesian product, sum ranks
    from itertools import product
    results = []
    for combo in product(*[r.items for r in rankings]):
        values = [v for v, _ in combo]
        total_rank = sum(rank for _, rank in combo)
        result = body(*values)
        results.append((result, total_rank))
    return Ranking(results)

def ranked_apply(f: Callable, *args: Any) -> Ranking:
    """
    Ranked application: applies function f to all combinations of ranked arguments.
    Each argument can be a Ranking or a value (treated as rank 0).
    The rank of each result is the sum of the input ranks.
    If any argument is empty, the result is empty.
    Equivalent to the Racket $ macro/combinator.
    """
    def to_ranking(x):
        if isinstance(x, Ranking):
            return x
        return Ranking([(x, 0)])
    rankings = [to_ranking(arg) for arg in args]
    if any(r.is_empty() for r in rankings):
        return failure()
    from itertools import product
    results = []
    for combo in product(*[r.items for r in rankings]):
        values = [v for v, _ in combo]
        total_rank = sum(rank for _, rank in combo)
        result = f(*values)
        results.append((result, total_rank))
    return Ranking(results)

def rlet_star(bindings: List[Tuple[str, Union[Ranking, Callable]]], body: Callable) -> Ranking:
    """
    Sequential ranked let: produce a joint ranking over variables, binding sequentially.
    - bindings: list of (name, Ranking/value or function) pairs
    - body: function taking variables in order and returning a value
    Each binding can depend on the previous ones.
    If any input ranking is empty, the result is empty.
    Equivalent to the Racket rlet* macro/combinator.
    """
    def helper(idx: int, env: tuple, acc_rank: int) -> List[Tuple[Any, int]]:
        if idx == len(bindings):
            return [(body(*env), acc_rank)]
        name, val = bindings[idx]
        # If val is a function, call with previous values
        if callable(val) and not isinstance(val, Ranking):
            ranking = val(*env)
        else:
            ranking = val if isinstance(val, Ranking) else Ranking([(val, 0)])
        if ranking.is_empty():
            return []
        results = []
        for v, r in ranking.items:
            results.extend(helper(idx + 1, env + (v,), acc_rank + r))
        return results
    items = helper(0, tuple(), 0)
    if not items:
        return failure()
    return Ranking(items)

def observe(pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Conditionalization: filter a ranking by a predicate and normalize the result.
    Only values for which pred(value) is True are kept, and ranks are shifted so the lowest is 0.
    If no values pass, returns empty ranking.
    Equivalent to the Racket observe macro/combinator.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if pred(v)]
    if not filtered:
        return failure()
    min_rank = min(rank for _, rank in filtered)
    return Ranking([(v, rank - min_rank) for v, rank in filtered])

def observe_e(evidence: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Evidence-oriented conditionalization: values for which pred(value) is True keep their rank, others are shifted by evidence.
    Equivalent to Racket's observe-e.
    Args:
        evidence (int): Extra evidence strength (rank increment for non-matching values).
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The evidence-conditioned and normalized ranking.
    """
    if r.is_empty():
        return r
    assoc = r.to_assoc()
    result = []
    for v, rank in assoc:
        if pred(v):
            result.append((v, rank))
        else:
            result.append((v, rank + evidence))
    # Normalize so the lowest rank is 0
    min_rank = min(rk for _, rk in result)
    return Ranking([(v, rk - min_rank) for v, rk in result])

def observe_all(ranking, predicates):
    """
    Filter a ranking by a list of predicates, keeping only values that satisfy all predicates, and normalize the result.
    If predicates is empty, all values are kept and normalized.
    Args:
        ranking (Ranking): The input ranking.
        predicates (list[Callable[[Any], bool]]): List of predicates to apply.
    Returns:
        Ranking: The filtered and normalized ranking.
    """
    # If no predicates, keep all and normalize
    if not predicates:
        return ranking.normalize()
    def all_preds(x):
        return all(pred(x) for pred in predicates)
    return ranking.filter(all_preds).normalize()

def limit(n: int, r: 'Ranking') -> 'Ranking':
    """
    Restrict a ranking to the n lowest-ranked values. If n <= 0, returns empty. If n >= len(r), returns all.
    Ties are preserved: if the nth and (n+1)th values have the same rank, only the first n are kept.
    Args:
        n (int): Number of lowest-ranked values to keep.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The limited ranking.
    """
    if n <= 0 or r.is_empty():
        return Ranking([])
    return Ranking(r.to_assoc()[:n])

def cut(threshold: int, r: 'Ranking') -> 'Ranking':
    """
    Restrict a ranking to values with rank <= threshold.
    Args:
        threshold (int): Maximum allowed rank (inclusive).
        r (Ranking): The input ranking.
    Returns:
        Ranking: The cut ranking.
    """
    if r.is_empty():
        return Ranking([])
    return Ranking([(v, rank) for v, rank in r.to_assoc() if rank <= threshold])

def rank_of(pred: Callable[[Any], bool], r: 'Ranking') -> float:
    """
    Return the lowest rank for which pred(value) is True in the ranking.
    If no value matches, returns float('inf').
    Args:
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        float: The lowest rank for which pred(value) is True, or float('inf') if none.
    """
    for v, rank in r.to_assoc():
        if pred(v):
            return rank
    return float('inf')

def argmin(r: 'Ranking') -> List[Any]:
    """
    Return all values with the minimal rank in the ranking.
    If the ranking is empty, returns an empty list.
    Equivalent to the Racket argmin utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        List[Any]: List of all values with the minimal rank (ties included).
    """
    if r.is_empty():
        return []
    assoc = r.to_assoc()
    min_rank = min(rank for _, rank in assoc)
    return [v for v, rank in assoc if rank == min_rank]

def rf_to_stream(r: Ranking) -> Generator[Tuple[Any, int], None, None]:
    """
    Convert a ranking to a generator (stream) of (value, rank) pairs in order.
    Equivalent to the Racket rf->stream utility.
    Args:
        r (Ranking): The input ranking.
    Yields:
        Tuple[Any, int]: (value, rank) pairs in non-decreasing rank order.
    """
    for v, rank in r.to_assoc():
        yield (v, rank)

def rf_equal(r1: Ranking, r2: Ranking) -> bool:
    """
    Check if two rankings are equal: same values and ranks, order irrelevant.
    Equivalent to the Racket rf-equal? utility.
    Args:
        r1 (Ranking): First ranking.
        r2 (Ranking): Second ranking.
    Returns:
        bool: True if rankings are equal, False otherwise.
    """
    return sorted(r1.to_assoc()) == sorted(r2.to_assoc())

def rf_to_assoc(r: Ranking) -> List[Tuple[Any, int]]:
    """
    Convert a ranking to a list of (value, rank) pairs in order.
    Equivalent to the Racket rf->assoc utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        List[Tuple[Any, int]]: List of (value, rank) pairs in non-decreasing rank order.
    """
    return r.to_assoc()

def rf_to_hash(r: Ranking) -> Dict[Any, int]:
    """
    Convert a ranking to a dict mapping value to rank (first occurrence wins, as in Racket).
    Equivalent to the Racket rf->hash utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        Dict[Any, int]: Dictionary mapping value to rank.
    """
    d = {}
    for v, rank in r.to_assoc():
        if v not in d:
            d[v] = rank
    return d

def pr_all(r: Ranking) -> None:
    """
    Pretty-print all (value, rank) pairs in order, or print a failure message if empty.
    Equivalent to the Racket pr-all utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        None
    """
    if r.is_empty():
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in r.to_assoc():
        print(f"{rank:>5} {v}")
    print("Done")

def pr_first(r: Ranking) -> None:
    """
    Pretty-print the first (lowest-ranked) value and its rank, or print a failure message if empty.
    Equivalent to the Racket pr-first utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        None
    """
    if r.is_empty():
        print("Failure (empty ranking)")
        return
    v, rank = r.to_assoc()[0]
    print(f"{rank} {v}")

def top_k(k: int, r: Ranking) -> List[Any]:
    """
    Return a list of the k lowest-ranked values from the ranking.
    If k <= 0, returns an empty list. If k >= number of values, returns all values.
    Ties are not split: only the first k values are included, even if the (k+1)th value has the same rank as the kth.
    Args:
        k (int): Number of lowest-ranked values to return.
        r (Ranking): The input ranking.
    Returns:
        List[Any]: List of the k lowest-ranked values (in order).
    """
    if k <= 0 or r.is_empty():
        return []
    return [v for v, _ in r.to_assoc()[:k]]

def observe_r(rank: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Rank-oriented conditionalization: values for which pred(value) is True keep their rank, others are set to the given rank.
    Equivalent to Racket's observe-r.
    Args:
        rank (int): The rank to assign to non-matching values.
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The rank-conditioned and normalized ranking.
    """
    if r.is_empty():
        return r
    assoc = r.to_assoc()
    result = []
    for v, rk in assoc:
        if pred(v):
            result.append((v, rk))
        else:
            result.append((v, rank))
    # Normalize so the lowest rank is 0
    min_rank = min(rk for _, rk in result)
    return Ranking([(v, rk - min_rank) for v, rk in result])

__all__ = [
    'Ranking',
    'failure',
    'construct_ranking',
    'normalise',
    'map_value',
    'shift',
    'filter_ranking',
    'filter_after',
    'up_to_rank',
    'dedup',
    'do_with',
    'either_of',
    'either_or',
    'nrm_exc',
    'rlet',
    'ranked_apply',
    'rlet_star',
    'observe',
    'observe_e',
    'observe_all',
    'limit',
    'cut',
    'rank_of',
    'argmin',
    'rf_to_stream',
    'rf_equal',
    'rf_to_assoc',
    'rf_to_hash',
    'pr_all',
    'pr_first',
    'top_k',
    'observe_r',
    'LazyRanking',
    'lazy_nrm_exc',
    'lazy_rlet_star',
    'lazy_either_of',
    'lazy_rlet',
]

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
