"""
Ranking class and private helpers for ranked programming.

This module defines the core `Ranking` abstraction for lazy ranked programming, along with
internal helpers for flattening and normalizing ranking-like objects. All combinators and
utilities in the library are built on this class.

- `Ranking`: A lazy, generator-based abstraction for ranked search spaces.
- `_flatten_ranking_like`: Internal utility to flatten nested rankings, generators, or atomic values.
- `_normalize_ranking`: Internal utility to filter and normalize rankings by predicates and evidence.
- `deduplicate_hashable`: Lazily deduplicate (value, rank) pairs by value, always enabled for all combinators. Hashable values are yielded only once (with minimal rank); unhashable values are always yielded, even if repeated. See the docstring for details.

**Deduplication is always enabled and not user-configurable in this implementation.**

See the main API in `rp_api.py` for user-facing usage. See the Python reference and Sphinx docs for more on deduplication and ranking semantics.
"""
from typing import Any, Callable, Iterable, Tuple, Generator, Optional
from collections.abc import Iterable as ABCIterable, Iterator
import logging

# Set up a module-level logger
logger = logging.getLogger("ranked_programming.ranking_class")
logger.addHandler(logging.NullHandler())

def _flatten_ranking_like(obj: object, rank_offset: int = 0):
    """
    Flatten a Ranking, generator, or iterable into (value, rank) pairs, applying a rank offset.

    Args:
        obj: Ranking, generator, iterable, callable, or atomic value.
        rank_offset: Integer to add to all yielded ranks.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    import types
    # logger.debug(f"Flattening object: {repr(obj)} with rank_offset={rank_offset}")
    # Handle Ranking first to avoid treating it as a generic callable
    if isinstance(obj, Ranking):
        for v, r in obj:
            # logger.debug(f"Yield from Ranking: value={v}, rank={r} (offset={rank_offset})")
            yield (v, int(r) + rank_offset)
    # Lazily evaluate only zero-argument callables (thunks), not all callables
    elif callable(obj) and not isinstance(obj, (str, bytes)):
        import inspect
        sig = inspect.signature(obj)
        if len(sig.parameters) == 0:
            # logger.debug(f"Calling lazy zero-arg callable: {repr(obj)}")
            yield from _flatten_ranking_like(obj(), rank_offset)
        else:
            # logger.debug(f"Yield atomic non-thunk callable: {repr(obj)}")
            yield (obj, rank_offset)
    elif isinstance(obj, types.GeneratorType):
        try:
            it = iter(obj)
            first = next(it)
        except StopIteration:
            # logger.debug("Generator is empty.")
            return
        if (
            isinstance(first, tuple)
            and len(first) == 2
            and isinstance(first[1], (int, float))
        ):
            # logger.debug(f"Yield from generator (tuple): {first}")
            yield (first[0], int(first[1]) + rank_offset)
            for item in it:
                if (
                    isinstance(item, tuple)
                    and len(item) == 2
                    and isinstance(item[1], (int, float))
                ):
                    # logger.debug(f"Yield from generator (tuple): {item}")
                    yield (item[0], int(item[1]) + rank_offset)
                else:
                    # logger.debug(f"Yield from generator (non-tuple): {item}")
                    yield (item, rank_offset)
        else:
            # logger.debug(f"Yield from generator (first): {first}")
            yield (first, rank_offset)
            for v in it:
                # logger.debug(f"Yield from generator (rest): {v}")
                yield (v, rank_offset)
    elif isinstance(obj, (list, set, tuple)):
        # logger.debug(f"Yield atomic collection: {repr(obj)}")
        yield (obj, rank_offset)
    else:
        # logger.debug(f"Yield atomic value: {repr(obj)}")
        yield (obj, rank_offset)

def _normalize_ranking(
    ranking: Iterable[Tuple[Any, int]],
    pred: Optional[Callable[[Any], bool]] = None,
    evidence: Optional[int] = None,
    predicates: Optional[list[Callable[[Any], bool]]] = None
) -> list[Tuple[Any, int]]:
    # logger.debug(f"Normalizing ranking: {list(ranking)} pred={pred} evidence={evidence} predicates={predicates}")
    """
    Filter and normalize a ranking by predicates and evidence.

    Args:
        ranking: Iterable of (value, rank) pairs.
        pred: Optional predicate to filter values.
        evidence: Optional; add to rank if pred fails.
        predicates: Optional list of predicates; all must pass.

    Returns:
        List[Tuple[Any, int]]: Filtered and normalized (value, rank) pairs.
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

class Ranking(Iterable):
    """
    Ranking: A lazy abstraction for ranked programming.

    This class wraps a generator of (value, rank) pairs, allowing for lazy
    combinators and efficient exploration of large or infinite search spaces.

    **Theoretical Foundation (Spohn's Ranking Theory):**
    
    Each Ranking represents a **negative ranking function κ: Ω → ℕ ∪ {∞}** where:
    - κ(ω) = 0 means ω is not disbelieved (certain/normal)
    - κ(ω) = n > 0 means ω is disbelieved to degree n (surprising/exceptional)  
    - κ(ω) = ∞ means ω is impossible
    
    The class provides methods to compute:
    - κ(A): `disbelief_rank(lambda ω: proposition(ω))`
    - τ(A): `belief_rank(lambda ω: proposition(ω))` where τ(A) = κ(∼A) - κ(A)
    - κ(B|A): `conditional_disbelief(condition_pred, consequent_pred)`

    Args:
        generator_fn: Callable[[], Iterable[Tuple[Any, int]]]
            A function returning an iterable of (value, rank) pairs representing κ values.
    """
    __slots__ = ("_generator_fn",)
    def __init__(self, generator_fn: Callable[[], Iterable[Tuple[Any, int]]]):
        """
        Initialize a Ranking object.

        Args:
            generator_fn: Callable returning an iterable of (value, rank) pairs.
                         Each pair (ω, n) represents κ(ω) = n in Spohn's theory.
        """
        self._generator_fn = generator_fn
    @classmethod
    def from_generator(cls, gen_func: Callable, *args, **kwargs) -> 'Ranking':
        """
        Construct a Ranking from a generator function and its arguments.

        Args:
            gen_func: A generator function (e.g., ``nrm_exc``, ``rlet``, etc.).
            ``*args``: Positional arguments for the generator function.
            ``**kwargs``: Keyword arguments for the generator function.

        Returns:
            Ranking: A new Ranking instance wrapping the generator.

        Example::

            Ranking.from_generator(nrm_exc, "foo", "bar")
            # Equivalent to Ranking(lambda: nrm_exc("foo", "bar"))
        """
        return cls(lambda: gen_func(*args, **kwargs))
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
            func: Function to apply to each value.

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
            pred: Predicate to filter values.

        Returns:
            Ranking: A new Ranking with only values where pred(value) is True.
        """
        def filtered() -> Generator[Tuple[Any, int], None, None]:
            for v, r in self:
                if pred(v):
                    yield (v, r)
        return Ranking(filtered)
    def disbelief_rank(self, proposition: Callable[[Any], bool]) -> float:
        """
        κ(A): Compute disbelief rank for proposition A.
        
        This is the negative ranking function from Spohn's theory.
        Returns the minimum rank of worlds satisfying the proposition.
        
        **Theoretical Foundation:**
        κ: W → ℕ∪{∞} where W is the set of possible worlds.
        κ(A) represents the degree of disbelief in proposition A.
        
        Args:
            proposition: Predicate defining the proposition A.
                        Should return True for worlds where A holds.
            
        Returns:
            int: Disbelief rank κ(A), or ∞ if no worlds satisfy A.
            
        Examples:
            >>> ranking = nrm_exc('healthy', 'sick', 1)
            >>> ranking.disbelief_rank(lambda x: x == 'healthy')
            0
            >>> ranking.disbelief_rank(lambda x: x == 'sick')  
            1
        """
        satisfying_ranks = [rank for value, rank in self if proposition(value)]
        return min(satisfying_ranks) if satisfying_ranks else float('inf')
    
    def belief_rank(self, proposition: Callable[[Any], bool]) -> float:
        """
        τ(A): Compute belief rank for proposition A.
        
        This is the two-sided ranking function from Spohn's theory:
        τ(A) = κ(∼A) - κ(A)
        
        **Interpretation:**
        - τ(A) > 0: Belief in A (∼A is more disbelieved than A)
        - τ(A) < 0: Disbelief in A (A is more disbelieved than ∼A)  
        - τ(A) = 0: Suspension of judgment (equal disbelief in A and ∼A)
        
        Args:
            proposition: Predicate defining the proposition A.
            
        Returns:
            int: Belief rank τ(A).
            
        Examples:
            >>> ranking = nrm_exc('A', 'B', 1)  # κ(A)=0, κ(B)=1
            >>> ranking.belief_rank(lambda x: x == 'A')  # τ(A) = κ(B) - κ(A) = 1 - 0 = 1
            1
            >>> ranking.belief_rank(lambda x: x == 'B')  # τ(B) = κ(A) - κ(B) = 0 - 1 = -1
            -1
        """
        disbelief_A = self.disbelief_rank(proposition)
        disbelief_not_A = self.disbelief_rank(lambda x: not proposition(x))
        
        # Handle infinity cases to avoid NaN
        if disbelief_A == float('inf') and disbelief_not_A == float('inf'):
            return 0.0  # Suspension of judgment when both are impossible
        elif disbelief_A == float('inf'):
            return float('-inf')  # Strong disbelief when A is impossible but ∼A is possible
        elif disbelief_not_A == float('inf'):
            return float('inf')   # Strong belief when ∼A is impossible but A is possible
        else:
            return float(disbelief_not_A - disbelief_A)
    
    def conditional_disbelief(self, condition: Callable[[Any], bool],
                            consequent: Callable[[Any], bool]) -> float:
        """
        κ(B|A): Compute conditional disbelief rank.
        
        This implements Spohn's conditional ranks: κ(B|A) = κ(A∧B) - κ(A)
        
        **Theoretical Foundation:**
        Conditional disbelief represents how much more (or less) we disbelieve
        B given that A is true, compared to our disbelief in A alone.
        
        Args:
            condition: Predicate for condition A.
            consequent: Predicate for consequent B.
            
        Returns:
            float: Conditional disbelief rank κ(B|A), or ∞ if A is impossible.
            
        Examples:
            >>> ranking = nrm_exc(('A', 'B'), ('A', 'not_B'), 1)
            >>> # κ(A∧B) = 0, κ(A) = 0, so κ(B|A) = 0 - 0 = 0
            >>> ranking.conditional_disbelief(
            ...     lambda x: x[0] == 'A',      # A
            ...     lambda x: x[1] == 'B'       # B
            ... )
            0.0
        """
        disbelief_A = self.disbelief_rank(condition)
        if disbelief_A == float('inf'):
            return float('inf')  # Condition A is impossible
            
        # Create ranking conditioned on A using existing observe_e
        from .ranking_observe import observe_e
        conditioned_ranking = Ranking(lambda: observe_e(0, condition, self))
        disbelief_A_and_B = conditioned_ranking.disbelief_rank(consequent)
        
        return disbelief_A_and_B - disbelief_A
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
def as_ranking(val: object, env: tuple = ()) -> Ranking:
    """
    Convert a value, callable, or Ranking to a Ranking object.
    If val is callable, calls it with as many arguments as env provides.
    """
    import inspect
    if isinstance(val, Ranking):
        return val
    elif callable(val):
        sig = inspect.signature(val)
        n_args = len(sig.parameters)
        result = val(*env[:n_args])
        return Ranking(lambda: _flatten_ranking_like(result, 0))
    else:
        return Ranking(lambda: _flatten_ranking_like(val, 0))

def deduplicate_hashable(iterable):
    """
    Lazily deduplicate (value, rank) pairs by value, keeping only the first occurrence of each hashable value.

    - Hashable values are yielded only once (the first time they appear), regardless of rank.
    - Unhashable values (e.g., lists, dicts) are always yielded, even if repeated.
    - This function is used by all core combinators to ensure that rankings do not contain duplicate values with different ranks.
    - Deduplication is always enabled and not user-configurable in this implementation.
    - The function is fully lazy: it does not materialize the input, and works with infinite/lazy generators.

    Args:
        iterable: An iterable of (value, rank) pairs.

    Yields:
        (value, rank) pairs, with hashable values deduplicated by value.
    """
    seen = set()
    for v, r in iterable:
        try:
            hash(v)
        except TypeError:
            yield (v, r)
        else:
            if v not in seen:
                yield (v, r)
                seen.add(v)
