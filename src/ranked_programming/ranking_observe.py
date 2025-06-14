"""
Observation and normalization combinators for ranked programming.

This module provides functions for filtering and normalizing ranked search spaces
using predicates and evidence. All functions operate lazily and are compatible with
Ranking and generator-based combinators.

- `observe`: Filter a ranking by a predicate and normalize ranks.
- `observe_e`: Add evidence to ranks for values failing a predicate, then normalize.
- `observe_all`: Filter by a list of predicates, keeping only values that satisfy all.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
from .ranking_class import _normalize_ranking

def observe(
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Filter a Ranking by a predicate and normalize ranks so the lowest is 0.

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
    """
    For each (value, rank) in ranking, add evidence to rank if pred fails, then normalize.

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
    """
    Filter a Ranking by a list of predicates, keeping only values that satisfy all, and normalize.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
        predicates: List of predicates.

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.
    """
    for v, r in _normalize_ranking(ranking, predicates=predicates):
        yield (v, r)

def observe_r(
    result_strength: int,
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Result-oriented conditionalization.

    Like :func:`observe`, but increases the rank of values failing ``pred`` by ``result_strength``, then normalizes.

    :param result_strength: Extra posterior belief strength (rank penalty) for values failing ``pred``.
    :type result_strength: int
    :param pred: Predicate to filter values.
    :type pred: Callable[[Any], bool]
    :param ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
    :type ranking: Iterable[Tuple[Any, int]]
    :yields: (value, rank) pairs, normalized.
    :rtype: Generator[Tuple[Any, int], None, None]
    """
    for v, r in _normalize_ranking(
        ((v, r + result_strength) if not pred(v) else (v, r) for v, r in ranking)
    ):
        yield (v, r)

def observe_e_x(
    evidence_strength: int,
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Evidence-oriented conditionalization.

    Like :func:`observe_e`, but increases the rank of values failing ``pred`` by ``evidence_strength``, then normalizes.

    :param evidence_strength: Extra evidence strength (rank penalty) for values failing ``pred``.
    :type evidence_strength: int
    :param pred: Predicate to filter values.
    :type pred: Callable[[Any], bool]
    :param ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
    :type ranking: Iterable[Tuple[Any, int]]
    :yields: (value, rank) pairs, normalized.
    :rtype: Generator[Tuple[Any, int], None, None]
    """
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence_strength):
        yield (v, r)
