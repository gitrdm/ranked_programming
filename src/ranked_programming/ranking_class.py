"""
Ranking class and private helpers for ranked programming.
"""
from typing import Any, Callable, Iterable, Tuple, Generator, Optional
from collections.abc import Iterable as ABCIterable, Iterator

# --- Private helpers (flattening, normalization) ---
def _flatten_ranking_like(obj: object, rank_offset: int = 0):
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
    __slots__ = ("_generator_fn",)
    def __init__(self, generator_fn: Callable[[], Iterable[Tuple[Any, int]]]):
        self._generator_fn = generator_fn
    def __iter__(self) -> Iterator[Tuple[Any, int]]:
        return iter(self._generator_fn())
    def to_eager(self) -> list[Tuple[Any, int]]:
        return list(self._generator_fn())
    def map(self, func: Callable[[Any], Any]) -> 'Ranking':
        def mapped() -> Generator[Tuple[Any, int], None, None]:
            for v, r in self:
                yield (func(v), r)
        return Ranking(mapped)
    def filter(self, pred: Callable[[Any], bool]) -> 'Ranking':
        def filtered() -> Generator[Tuple[Any, int], None, None]:
            for v, r in self:
                if pred(v):
                    yield (v, r)
        return Ranking(filtered)
    def __len__(self) -> int:
        return len(list(self._generator_fn()))
    def __bool__(self) -> bool:
        return next(iter(self._generator_fn()), None) is not None
    def __repr__(self) -> str:
        items = list(self._generator_fn())
        n = len(items)
        preview = items[:3]
        if n == 0:
            return f"<Ranking: 0 items>"
        elif n <= 3:
            return f"<Ranking: {n} items {preview}>"
        else:
            return f"<Ranking: {n} items {preview} ...>"
