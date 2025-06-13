"""
Core ranking data structure and basic combinators for ranked programming (lazy by default).

All combinators and the main abstraction (`Ranking`) are lazy, generator-based, and automatically flatten nested values. The API is fully lazy and idiomatic, mirroring the original Racket code's laziness.

Literate documentation and type hints included.
"""
from typing import Any, Callable, Iterable, Tuple, Generator, Optional
from collections.abc import Iterable as ABCIterable, Iterator
import heapq
from itertools import islice

# --- Private helpers (flattening, normalization) ---

def _flatten_ranking_like(obj: object, rank_offset: int = 0):
    """Yield (value, rank) pairs from a Ranking, generator, or iterable, with optional rank offset.

    This function flattens nested Ranking objects and generators of (value, rank) pairs,
    assigning a rank offset to all yielded pairs. Lists, sets, and tuples are treated as atomic values.
    Any malformed input is treated as an atomic value.

    Args:
        obj: Ranking, generator, iterable, or single value.
        rank_offset: Amount to add to all yielded ranks.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    import types
    if isinstance(obj, Ranking):
        for v, r in obj:
            yield (v, int(r) + rank_offset)
    elif isinstance(obj, types.GeneratorType):
        try:
            it = iter(obj)
            first = next(it)
        except StopIteration:
            return
        if (
            isinstance(first, tuple)
            and len(first) == 2
            and isinstance(first[1], (int, float))
        ):
            yield (first[0], int(first[1]) + rank_offset)
            for item in it:
                if (
                    isinstance(item, tuple)
                    and len(item) == 2
                    and isinstance(item[1], (int, float))
                ):
                    yield (item[0], int(item[1]) + rank_offset)
                else:
                    yield (item, rank_offset)
        else:
            yield (first, rank_offset)
            for v in it:
                yield (v, rank_offset)
    elif isinstance(obj, (list, set, tuple)):
        yield (obj, rank_offset)
    else:
        yield (obj, rank_offset)

def _normalize_ranking(
    ranking: Iterable[Tuple[Any, int]],
    pred: Optional[Callable[[Any], bool]] = None,
    evidence: Optional[int] = None,
    predicates: Optional[list[Callable[[Any], bool]]] = None
) -> list[Tuple[Any, int]]:
    """Filter and normalize a ranking by predicates and evidence.

    Args:
        ranking: An iterable of (value, rank) pairs.
        pred: Optional; a predicate to filter values.
        evidence: Optional; if provided, add this to the rank of values failing pred.
        predicates: Optional; a list of predicates, all of which must pass for a value to be kept.

    Returns:
        List[Tuple[Any, int]]: Filtered and normalized (value, rank) pairs, with minimum rank set to 0.
    """
    if predicates is not None:
        def all_preds(x: Any) -> bool:
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

# --- Ranking: lazy ranked programming abstraction ---

class Ranking(Iterable):
    """
    Ranking: A lazy abstraction for ranked programming.

    This class wraps a generator of (value, rank) pairs, allowing for lazy
    combinators and efficient exploration of large or infinite search spaces.

    Args:
        generator_fn: Callable[[], Iterable[Tuple[Any, int]]]
            A function returning an iterable of (value, rank) pairs.
    """
    def __init__(self, generator_fn: Callable[[], Iterable[Tuple[Any, int]]]):
        self._generator_fn = generator_fn

    def __iter__(self) -> Iterator[Tuple[Any, int]]:
        """
        Iterate over (value, rank) pairs lazily.

        Returns:
            Iterator[Tuple[Any, int]]: An iterator over (value, rank) pairs.
        """
        return iter(self._generator_fn())

    def to_eager(self) -> list[Tuple[Any, int]]:
        """
        Materialize all (value, rank) pairs as a list.

        Returns:
            list[Tuple[Any, int]]: All (value, rank) pairs in the ranking.
        """
        return list(self._generator_fn())

    def map(self, func: Callable[[Any], Any]) -> 'Ranking':
        """
        Lazily map a function over values.

        Args:
            func: Callable[[Any], Any]
                Function to apply to each value.

        Returns:
            Ranking: A new Ranking with func applied to each value.
        """
        def mapped() -> Generator[Tuple[Any, int], None, None]:
            for v, r in self:
                yield (func(v), r)
        return Ranking(mapped)

    def filter(self, pred: Callable[[Any], bool]) -> 'Ranking':
        """
        Lazily filter values by a predicate.

        Args:
            pred: Callable[[Any], bool]
                Predicate to filter values.

        Returns:
            Ranking: A new Ranking with only values where pred(value) is True.
        """
        def filtered() -> Generator[Tuple[Any, int], None, None]:
            for v, r in self:
                if pred(v):
                    yield (v, r)
        return Ranking(filtered)

    def __len__(self) -> int:
        """
        Return the number of (value, rank) pairs in the ranking.

        Returns:
            int: The number of items in the ranking.
        """
        return len(list(self._generator_fn()))

    def __bool__(self) -> bool:
        """
        Return True if the ranking has at least one (value, rank) pair, False if empty.

        This method is efficient and does not exhaust the generator beyond the first item.
        For infinite or very large rankings, this is a constant-time check.

        Returns:
            bool: True if ranking is non-empty, False otherwise.
        """
        return next(iter(self._generator_fn()), None) is not None

    def __repr__(self) -> str:
        """
        Return a readable string representation of the Ranking object.

        Returns:
            str: A summary of the ranking, showing the number of items and a preview of the first few.
        """
        items = list(self._generator_fn())
        n = len(items)
        preview = items[:3]
        if n == 0:
            return f"<Ranking: 0 items>"
        elif n <= 3:
            return f"<Ranking: {n} items {preview}>"
        else:
            return f"<Ranking: {n} items {preview} ...>"

# --- Lazy combinators (now default, no prefix) ---

def nrm_exc(
    v1: object,
    v2: object,
    rank2: int
) -> Generator[Tuple[Any, int], None, None]:
    """Yield (v1, 0) and all (value, rank) pairs from v2 at rank2 (flattened).

    If v2 is a Ranking or generator, yields all its (value, rank) pairs with rank incremented by rank2.
    If v2 is a single value, yields (v2, rank2).
    This ensures that nested Ranking or generator values are always flattened, never yielded as values.

    If both v1 and v2 are empty (generators that yield nothing), yields nothing.

    Args:
        v1: First value or Ranking/generator/iterable.
        v2: Second value or Ranking/generator/iterable.
        rank2: Rank to assign to v2 (or its values).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
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

def rlet_star(
    bindings: list[Tuple[str, object]],
    body: Callable[..., object]
) -> Generator[Tuple[Any, int], None, None]:
    """Sequential dependent bindings (lazy, default).

    Each binding can be a value, a Ranking, or a function of previous variables returning a generator or Ranking.
    The body can return a value, a Ranking, or a generator; all are automatically flattened so only (value, rank) pairs are yielded.
    Binding functions are called with as many arguments as they accept (from the environment), supporting both zero-argument and multi-argument functions.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    from collections.abc import Iterable
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
    """Parallel (cartesian product) bindings (lazy, default).

    Each binding can be a value, a Ranking, or a function of no arguments returning a generator or Ranking.
    Yields (body(values), total_rank) lazily for each combination (cartesian product of all bindings).
    If the body returns a Ranking or generator, it is automatically flattened so only (value, rank) pairs are yielded.

    Args:
        bindings: List of (name, value/function) pairs.
        body: Function returning the final value(s).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    from collections.abc import Iterable
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
    """Lazy union of any number of Ranking objects, yielding values in order of minimal rank.

    For duplicate values, keep the lowest rank (first occurrence wins, as in Racket).
    Always yields values in the order of minimal rank, deduplicating on the fly.

    Args:
        *rankings: One or more Ranking objects or iterables of (value, rank) pairs.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    # Prepare iterators and initial heap
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
    """Apply function f to all combinations of lazy ranked arguments.

    Each argument can be a Ranking or a value (treated as rank 0).
    Yields (f(values), total_rank) lazily for each combination.
    If f(values) returns a Ranking or generator, it is automatically flattened so only (value, rank) pairs are yielded.

    Args:
        f: Function to apply.
        *args: Ranking or value arguments.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    from collections.abc import Iterable
    def to_ranking(x: object) -> Ranking:
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

def observe(
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """Filter a Ranking by a predicate and normalize ranks so the lowest is 0.

    If no values pass, yields nothing (empty generator).

    Args:
        pred: Predicate to filter values.
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.
    """
    for v, r in _normalize_ranking(ranking, pred=pred):
        yield (v, r)

def observe_e(
    evidence: int,
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """For each (value, rank) in ranking, add evidence to rank if pred fails, then normalize.

    Args:
        evidence: Amount to add to rank if pred fails.
        pred: Predicate to filter values.
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.
    """
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence):
        yield (v, r)

def observe_all(
    ranking: Iterable[Tuple[Any, int]],
    predicates: list[Callable[[Any], bool]]
) -> Generator[Tuple[Any, int], None, None]:
    """Filter a Ranking by a list of predicates, keeping only values that satisfy all, and normalize.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
        predicates: List of predicates.

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.
    """
    for v, r in _normalize_ranking(ranking, predicates=predicates):
        yield (v, r)

def limit(
    n: int,
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """Restrict a Ranking to the n lowest-ranked values (in generator order).

    This function is lazy and uses itertools.islice for efficiency. For infinite or very large rankings,
    only the first n items are produced, and the generator is not exhausted beyond that.

    Args:
        n: Number of values to yield.
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    yield from islice(ranking, n)

def cut(
    threshold: int,
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """Restrict a Ranking to values with rank <= threshold.

    Args:
        threshold: Maximum rank to include.
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    for v, r in ranking:
        if r <= threshold:
            yield (v, r)

def pr_all(ranking: Iterable[Tuple[Any, int]]) -> None:
    """Pretty-print all (value, rank) pairs in order, or print a failure message if empty.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
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

def pr_first(ranking: Iterable[Tuple[Any, int]]) -> None:
    """Pretty-print the first (lowest-ranked) value and its rank, or print a failure message if empty.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
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
