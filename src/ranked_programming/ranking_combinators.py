"""
Combinators for ranked programming.
"""
from typing import Any, Callable, Iterable, Tuple, Generator
import heapq
from .ranking_class import Ranking, _flatten_ranking_like

def nrm_exc(
    v1: object,
    v2: object,
    rank2: int
) -> Generator[Tuple[Any, int], None, None]:
    if not isinstance(rank2, int):
        raise TypeError(f"rank2 must be int, got {type(rank2).__name__}")
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
    from itertools import product
    def to_ranking(x: object) -> Ranking:
        if isinstance(x, Ranking):
            return x
        else:
            return Ranking(lambda: _flatten_ranking_like(x, 0))
    rankings = [to_ranking(arg) for arg in args]
    for combo in product(*rankings):
        values = [v for v, _ in combo]
        total_rank = sum(r for _, r in combo)
        result = f(*values)
        for v, r in _flatten_ranking_like(result, total_rank):
            yield (v, r)
