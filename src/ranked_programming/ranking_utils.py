"""
Utility and output functions for ranked programming.
"""
from typing import Any, Iterable, Tuple, Generator
from itertools import islice

def limit(
    n: int,
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    yield from islice(ranking, n)

def cut(
    threshold: int,
    ranking: Iterable[Tuple[Any, int]]
) -> Generator[Tuple[Any, int], None, None]:
    for v, r in ranking:
        if r <= threshold:
            yield (v, r)

def pr_all(ranking: Iterable[Tuple[Any, int]]) -> None:
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
    items = list(ranking)
    if not items:
        print("Failure (empty ranking)")
        return
    v, rank = items[0]
    print(f"{rank} {v}")
