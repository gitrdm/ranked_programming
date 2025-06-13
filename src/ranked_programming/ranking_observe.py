"""
Observation and normalization combinators for ranked programming.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
from .ranking_class import _normalize_ranking

def observe(
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    for v, r in _normalize_ranking(ranking, pred=pred):
        yield (v, r)

def observe_e(
    evidence: int,
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence):
        yield (v, r)

def observe_all(
    ranking: Iterable[Tuple[Any, int]],
    predicates: list[Callable[[Any], bool]]
) -> Generator[Tuple[Any, int], None, None]:
    for v, r in _normalize_ranking(ranking, predicates=predicates):
        yield (v, r)
