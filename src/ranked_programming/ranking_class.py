"""
Ranking class and private helpers for ranked programming.

This module defines the core `Ranking` abstraction for lazy ranked programming, along with
internal helpers for flattening and normalizing ranking-like objects. All combinators and
utilities in the library are built on this class.

- `Ranking`: A lazy, generator-based abstraction for ranked search spaces.
- `_flatten_ranking_like`: Internal utility to flatten nested rankings, generators, or atomic values.
- `_normalize_ranking`: Internal utility to filter and normalize rankings by predicates and evidence.

See the main API in `rp_api.py` for user-facing usage.
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
        obj: Ranking, generator, iterable, or atomic value.
        rank_offset: Integer to add to all yielded ranks.

    Yields:
        Tuple[Any, int]: (value, rank) pairs.
    """
    import types
    logger.debug(f"Flattening object: {repr(obj)} with rank_offset={rank_offset}")
    if isinstance(obj, Ranking):
        for v, r in obj:
            logger.debug(f"Yield from Ranking: value={v}, rank={r} (offset={rank_offset})")
            yield (v, int(r) + rank_offset)
    elif isinstance(obj, types.GeneratorType):
        try:
            it = iter(obj)
            first = next(it)
        except StopIteration:
            logger.debug("Generator is empty.")
            return
        if (
            isinstance(first, tuple)
            and len(first) == 2
            and isinstance(first[1], (int, float))
        ):
            logger.debug(f"Yield from generator (tuple): {first}")
            yield (first[0], int(first[1]) + rank_offset)
            for item in it:
                if (
                    isinstance(item, tuple)
                    and len(item) == 2
                    and isinstance(item[1], (int, float))
                ):
                    logger.debug(f"Yield from generator (tuple): {item}")
                    yield (item[0], int(item[1]) + rank_offset)
                else:
                    logger.debug(f"Yield from generator (non-tuple): {item}")
                    yield (item, rank_offset)
        else:
            logger.debug(f"Yield from generator (first): {first}")
            yield (first, rank_offset)
            for v in it:
                logger.debug(f"Yield from generator (rest): {v}")
                yield (v, rank_offset)
    elif isinstance(obj, (list, set, tuple)):
        logger.debug(f"Yield atomic collection: {repr(obj)}")
        yield (obj, rank_offset)
    else:
        logger.debug(f"Yield atomic value: {repr(obj)}")
        yield (obj, rank_offset)

def _normalize_ranking(
    ranking: Iterable[Tuple[Any, int]],
    pred: Optional[Callable[[Any], bool]] = None,
    evidence: Optional[int] = None,
    predicates: Optional[list[Callable[[Any], bool]]] = None
) -> list[Tuple[Any, int]]:
    logger.debug(f"Normalizing ranking: {list(ranking)} pred={pred} evidence={evidence} predicates={predicates}")
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

    Args:
        generator_fn: Callable[[], Iterable[Tuple[Any, int]]]
            A function returning an iterable of (value, rank) pairs.
    """
    __slots__ = ("_generator_fn",)
    def __init__(self, generator_fn: Callable[[], Iterable[Tuple[Any, int]]]):
        """
        Initialize a Ranking object.

        Args:
            generator_fn: Callable returning an iterable of (value, rank) pairs.
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
