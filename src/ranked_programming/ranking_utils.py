"""
Utility and output functions for ranked programming.

This module provides utility functions for limiting, cutting, and pretty-printing ranked
search spaces. All functions operate lazily and are compatible with Ranking and generator-based combinators.

- `limit`: Restrict a ranking to the n lowest-ranked values.
- `cut`: Restrict a ranking to values with rank <= threshold.
- `pr_all`: Pretty-print all (value, rank) pairs in order.
- `pr_first`: Pretty-print the first (lowest-ranked) value and its rank.
"""
from typing import Any, Iterable, Tuple, Generator
from itertools import islice

def limit(
    n: int,
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    """
    Restrict a Ranking to the n lowest-ranked values (in generator order).

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
    """
    Restrict a Ranking to values with rank <= threshold.

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
    """
    Pretty-print all (value, rank) pairs in order, or print a failure message if empty.

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
    """
    Pretty-print the first (lowest-ranked) value and its rank, or print a failure message if empty.

    Args:
        ranking: Input ranking (Ranking or iterable of (value, rank) pairs).
    """
    items = list(ranking)
    if not items:
        print("Failure (empty ranking)")
        return
    v, rank = items[0]
    print(f"{rank} {v}")
