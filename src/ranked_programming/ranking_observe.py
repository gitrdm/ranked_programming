"""
Observation and normalization combinators for ranked programming.

This module provides a suite of combinators for filtering and normalizing ranked search spaces using predicates and evidence. These tools are essential for conditioning ranked models on observations, analogous to Bayesian conditioning in probabilistic programming, but using ranks (degrees of surprise) instead of probabilities.

**Motivation and Use Cases**

- In ranked programming, we often want to restrict a search space to only those outcomes that satisfy certain conditions (observations), or to penalize outcomes that fail to meet evidence.
- These combinators allow you to express observations, evidence, and normalization in a lazy, compositional way, supporting both hard and soft conditioning.
- Typical use cases include diagnosis (filtering for healthy/faulty states), spelling correction (observing correct spellings), and any scenario where you want to update beliefs based on new information.

**Design Philosophy**

- All functions operate lazily and are compatible with the `Ranking` abstraction and generator-based combinators.
- All combinators normalize ranks so that the lowest rank is always 0, ensuring consistent semantics for further computation.
- Functions are designed for composability and can be chained or nested as needed.
- Deduplication is always enforced for hashable values (see library policy).

**Combinators Provided**

- ``observe``: Filter a ranking by a predicate and normalize ranks.
- ``observe_e``: Add evidence to ranks for values failing a predicate, then normalize.
- ``observe_all``: Filter by a list of predicates, keeping only values that satisfy all.
- ``observe_r``: Result-oriented conditionalization (penalize failing values by a fixed amount).
- ``observe_e_x``: Evidence-oriented conditionalization (penalize failing values by evidence strength).

**Best Practices**

- Use ``observe`` for hard conditioning (keep only values that satisfy a predicate).
- Use ``observe_e`` or ``observe_e_x`` for soft conditioning (penalize but do not eliminate values).
- Use ``observe_all`` to combine multiple observations.
- All combinators are lazy and can be used with infinite/lazy search spaces.
- Logging and tracing can be enabled for debugging (see library reference).

**Examples**

.. code-block:: python

    from ranked_programming.ranking_observe import observe, observe_e
    from ranked_programming.ranking_combinators import nrm_exc

    # Hard conditioning: keep only even numbers
    r = nrm_exc(2, 3, 1)
    list(observe(lambda x: x % 2 == 0, r))  # [(2, 0)]

    # Soft conditioning: penalize odd numbers by 2
    r = nrm_exc(2, 3, 1)
    list(observe_e(2, lambda x: x % 2 == 0, r))  # [(2, 0), (3, 3)]

**Testing and Contract**

- All combinators are tested for edge cases (empty rankings, all values fail, all values pass, etc.).
- All functions are designed for TDD and are covered by regression tests.
- See ``tests/test_observe.py`` for test cases and usage patterns.

See the Python reference and Sphinx documentation for further details and advanced usage.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
from .ranking_class import _normalize_ranking

def observe(
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Filter a ranking by a predicate and normalize ranks so the lowest is 0.

    This is the primary combinator for hard conditioning: only values for which ``pred(value)`` is True are kept. Ranks are normalized so the lowest is 0. If no values satisfy the predicate, yields nothing.

    Args:
        pred: Predicate to filter values (``Callable[[Any], bool]``).
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.

    Example::

        >>> from ranked_programming.ranking_combinators import nrm_exc
        >>> r = nrm_exc(2, 3, 1)
        >>> list(observe(lambda x: x % 2 == 0, r))
        [(2, 0)]

    Edge cases::

        >>> list(observe(lambda x: False, r))
        []
        >>> list(observe(lambda x: True, r))
        [(2, 0), (3, 1)]
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

    This is the primary combinator for soft conditioning: values failing ``pred`` are not eliminated, but their rank is increased by ``evidence``. All ranks are then normalized so the lowest is 0.

    Args:
        evidence: Amount to add to rank if pred fails (``int``).
        pred: Predicate to filter values (``Callable[[Any], bool]``).
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.

    Example::

        >>> from ranked_programming.ranking_combinators import nrm_exc
        >>> r = nrm_exc(2, 3, 1)
        >>> list(observe_e(2, lambda x: x % 2 == 0, r))
        [(2, 0), (3, 3)]

    Edge cases::

        >>> list(observe_e(2, lambda x: False, r))
        [(3, 0)]
        >>> list(observe_e(2, lambda x: True, r))
        [(2, 0), (3, 1)]
    """
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence):
        yield (v, r)

def observe_all(
    ranking: Iterable[Tuple[Any, int]],
    predicates: list[Callable[[Any], bool]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Filter a ranking by a list of predicates, keeping only values that satisfy all, and normalize.

    This combinator is useful for chaining multiple observations. Only values that satisfy all predicates are kept. Ranks are normalized so the lowest is 0.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
        predicates: List of predicates (``list[Callable[[Any], bool]]``).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.

    Example::

        >>> from ranked_programming.ranking_combinators import nrm_exc
        >>> r = nrm_exc(2, 3, 1)
        >>> list(observe_all(r, [lambda x: x > 1, lambda x: x % 2 == 0]))
        [(2, 0)]
    """
    for v, r in _normalize_ranking(ranking, predicates=predicates):
        yield (v, r)

def observe_r(
    result_strength: int,
    pred: Callable[[Any], bool],
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Result-oriented conditionalization: penalize values failing ``pred`` by ``result_strength``, then normalize.

    Like :func:`observe`, but increases the rank of values failing ``pred`` by ``result_strength``, then normalizes. This is useful for modeling soft constraints or partial evidence.

    Args:
        result_strength: Extra posterior belief strength (rank penalty) for values failing ``pred`` (``int``).
        pred: Predicate to filter values (``Callable[[Any], bool]``).
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.

    Example::

        >>> from ranked_programming.ranking_combinators import nrm_exc
        >>> r = nrm_exc(2, 3, 1)
        >>> list(observe_r(2, lambda x: x % 2 == 0, r))
        [(2, 0), (3, 3)]
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
    Evidence-oriented conditionalization: penalize values failing ``pred`` by ``evidence_strength``, then normalize.

    Like :func:`observe_e`, but increases the rank of values failing ``pred`` by ``evidence_strength``, then normalizes. This is useful for modeling graded or partial evidence.

    Args:
        evidence_strength: Extra evidence strength (rank penalty) for values failing ``pred`` (``int``).
        pred: Predicate to filter values (``Callable[[Any], bool]``).
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).

    Yields:
        Tuple[Any, int]: (value, rank) pairs, normalized.

    Example::

        >>> from ranked_programming.ranking_combinators import nrm_exc
        >>> r = nrm_exc(2, 3, 1)
        >>> list(observe_e_x(2, lambda x: x % 2 == 0, r))
        [(2, 0), (3, 3)]
    """
    for v, r in _normalize_ranking(ranking, pred=pred, evidence=evidence_strength):
        yield (v, r)
