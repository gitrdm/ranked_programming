"""
Core ranking data structure and basic combinators for ranked programming.

Literate documentation and type hints included.
"""
from typing import Any, List, Tuple, Optional, Callable, Dict, Union, Generator

class Ranking:
    """
    Represents a ranking: a list of (value, rank) pairs, sorted by rank.
    An empty ranking represents failure.
    """
    def __init__(self, items: Optional[List[Tuple[Any, int]]] = None):
        self.items = [] if items is None else [ (v, int(r)) for v, r in items ]
        self.items.sort(key=lambda x: x[1])

    def is_empty(self) -> bool:
        """Return True if the ranking is empty (failure)."""
        return len(self.items) == 0

    def to_assoc(self) -> List[Tuple[Any, int]]:
        """Return the ranking as a list of (value, rank) pairs."""
        return list(self.items)

    def __eq__(self, other):
        if not isinstance(other, Ranking):
            return False
        return self.items == other.items

    def __repr__(self):
        return f"Ranking({self.items})"

    def filter(self, pred: Callable[[Any], bool]) -> 'Ranking':
        """
        Return a new Ranking containing only values for which pred(value) is True, keeping ranks unchanged.
        """
        return Ranking([(v, r) for v, r in self.items if pred(v)])

    def normalize(self) -> 'Ranking':
        """
        Return a new Ranking with ranks shifted so the minimum is 0. If empty, returns empty.
        """
        if self.is_empty():
            return Ranking([])
        min_rank = min(r for _, r in self.items)
        return Ranking([(v, r - min_rank) for v, r in self.items])

def failure() -> Ranking:
    """
    Return an empty ranking (failure).
    Equivalent to the Racket (failure) constructor.
    """
    return Ranking([])

def construct_ranking(*args: Tuple[Any, int]) -> Ranking:
    """
    Construct a ranking from (value, rank) pairs.
    If no arguments, returns an empty ranking (failure).
    Example: construct_ranking((1, 0), (2, 1))
    """
    return Ranking(list(args))

# --- New combinator: normalise ---
def normalise(r: Ranking) -> Ranking:
    """
    Shift all ranks so the minimum is 0. If empty, returns empty.
    Equivalent to Racket's normalise.
    """
    if r.is_empty():
        return failure()
    min_rank = min(rank for _, rank in r.items)
    return Ranking([(v, rank - min_rank) for v, rank in r.items])

def map_value(f, r: Ranking) -> Ranking:
    """
    Apply function f to each value in the ranking, keeping ranks unchanged.
    Equivalent to Racket's map-value.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    return Ranking([(f(v), rank) for v, rank in r.items])

def shift(amount: int, r: Ranking) -> Ranking:
    """
    Shift all ranks in the ranking by a constant amount.
    Equivalent to Racket's shift.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    return Ranking([(v, rank + amount) for v, rank in r.items])

def filter_ranking(pred, r: Ranking) -> Ranking:
    """
    Filter the ranking by a predicate on values, keeping ranks unchanged.
    Equivalent to Racket's filter-ranking.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if pred(v)]
    return Ranking(filtered)

def filter_after(pred, r: Ranking) -> Ranking:
    """
    Keep only the entries after the first one where pred(value) is True (inclusive).
    Equivalent to Racket's filter-after.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    found = False
    filtered = []
    for v, rank in r.items:
        if not found and pred(v):
            found = True
        if found:
            filtered.append((v, rank))
    return Ranking(filtered)

def up_to_rank(max_rank: int, r: Ranking) -> Ranking:
    """
    Keep only entries with rank <= max_rank.
    Equivalent to Racket's up-to-rank.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if rank <= max_rank]
    return Ranking(filtered)

def dedup(r: Ranking) -> Ranking:
    """
    Remove duplicate values, keeping the first occurrence (lowest rank).
    Equivalent to Racket's dedup.
    Returns a new Ranking.
    """
    if r.is_empty():
        return failure()
    seen = set()
    deduped = []
    for v, rank in r.items:
        if v not in seen:
            seen.add(v)
            deduped.append((v, rank))
    return Ranking(deduped)

def do_with(f, r: Ranking) -> int:
    """
    Apply function f to each (value, rank) pair in the ranking and sum the results.
    Equivalent to Racket's do-with.
    Returns the sum, or 0 for empty ranking.
    """
    if r.is_empty():
        return 0
    return sum(f(v, rank) for v, rank in r.items)

def either_of(*rankings: Ranking) -> Ranking:
    """
    Return the normalized union of any number of rankings.
    For duplicate values, keep the lowest rank.
    Always normalizes the result, even for a single ranking.
    Equivalent to the Racket either_of combinator.
    """
    non_empty = [r for r in rankings if not r.is_empty()]
    if not non_empty:
        return failure()
    combined = {}
    for r in non_empty:
        for v, rank in r.items:
            if v in combined:
                combined[v] = min(combined[v], rank)
            else:
                combined[v] = rank
    result = Ranking(list(combined.items()))
    return normalise(result)

def either_or(*rankings: Ranking) -> Ranking:
    """
    Return a ranking where all unique values from the input rankings are assigned rank 0.
    Duplicates are removed. If all rankings are empty, returns failure().
    Equivalent to the Racket either/or macro/combinator.
    """
    values = set()
    for r in rankings:
        for v, _ in r.items:
            values.add(v)
    if not values:
        return failure()
    return Ranking([(v, 0) for v in values])

def nrm_exc(v1: Any, v2: Any, rank: int = 1) -> Ranking:
    """
    Construct a ranking with a normal and exceptional value (or ranking).
    - If v1 and v2 are not rankings, treat them as singleton rankings.
    - v1 is always at rank 0.
    - v2 is at rank `rank` (default 1).
    - If v1 or v2 is empty, return the other (shifted as needed).
    - If both are empty, return failure().
    Equivalent to the Racket nrm/exc macro/combinator.
    """
    from .rp_core import Ranking, failure
    def to_ranking(x):
        if isinstance(x, Ranking):
            return x
        return Ranking([(x, 0)])
    r1 = to_ranking(v1)
    r2 = to_ranking(v2)
    if r1.is_empty() and r2.is_empty():
        return failure()
    if r1.is_empty():
        # Only exceptional part
        return Ranking([(v, rank) for v, _ in r2.items])
    if r2.is_empty():
        return r1
    # Merge: r1 at 0, r2 shifted by rank
    merged = r1.items + [(v, r + rank) for v, r in r2.items]
    return Ranking(merged)

def rlet(bindings: Dict[str, Ranking], body: Callable) -> Ranking:
    """
    Ranked let: produce a joint ranking over variables.
    - bindings: dict mapping variable names to Ranking or value
    - body: function taking variables in order and returning a value
    The rank of each result is the sum of the ranks of the chosen values.
    If any input ranking is empty, the result is empty.
    Equivalent to the Racket rlet macro/combinator.
    """
    # Convert all values to rankings if needed
    var_names = list(bindings.keys())
    rankings = []
    for v in var_names:
        val = bindings[v]
        if isinstance(val, Ranking):
            rankings.append(val)
        else:
            rankings.append(Ranking([(val, 0)]))
    if any(r.is_empty() for r in rankings):
        return failure()
    # Build joint ranking: cartesian product, sum ranks
    from itertools import product
    results = []
    for combo in product(*[r.items for r in rankings]):
        values = [v for v, _ in combo]
        total_rank = sum(rank for _, rank in combo)
        result = body(*values)
        results.append((result, total_rank))
    return Ranking(results)

def ranked_apply(f: Callable, *args: Any) -> Ranking:
    """
    Ranked application: applies function f to all combinations of ranked arguments.
    Each argument can be a Ranking or a value (treated as rank 0).
    The rank of each result is the sum of the input ranks.
    If any argument is empty, the result is empty.
    Equivalent to the Racket $ macro/combinator.
    """
    def to_ranking(x):
        if isinstance(x, Ranking):
            return x
        return Ranking([(x, 0)])
    rankings = [to_ranking(arg) for arg in args]
    if any(r.is_empty() for r in rankings):
        return failure()
    from itertools import product
    results = []
    for combo in product(*[r.items for r in rankings]):
        values = [v for v, _ in combo]
        total_rank = sum(rank for _, rank in combo)
        result = f(*values)
        results.append((result, total_rank))
    return Ranking(results)

def rlet_star(bindings: List[Tuple[str, Union[Ranking, Callable]]], body: Callable) -> Ranking:
    """
    Sequential ranked let: produce a joint ranking over variables, binding sequentially.
    - bindings: list of (name, Ranking/value or function) pairs
    - body: function taking variables in order and returning a value
    Each binding can depend on the previous ones.
    If any input ranking is empty, the result is empty.
    Equivalent to the Racket rlet* macro/combinator.
    """
    def helper(idx: int, env: tuple, acc_rank: int) -> List[Tuple[Any, int]]:
        if idx == len(bindings):
            return [(body(*env), acc_rank)]
        name, val = bindings[idx]
        # If val is a function, call with previous values
        if callable(val) and not isinstance(val, Ranking):
            ranking = val(*env)
        else:
            ranking = val if isinstance(val, Ranking) else Ranking([(val, 0)])
        if ranking.is_empty():
            return []
        results = []
        for v, r in ranking.items:
            results.extend(helper(idx + 1, env + (v,), acc_rank + r))
        return results
    items = helper(0, tuple(), 0)
    if not items:
        return failure()
    return Ranking(items)

def observe(pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Conditionalization: filter a ranking by a predicate and normalize the result.
    Only values for which pred(value) is True are kept, and ranks are shifted so the lowest is 0.
    If no values pass, returns empty ranking.
    Equivalent to the Racket observe macro/combinator.
    """
    if r.is_empty():
        return failure()
    filtered = [(v, rank) for v, rank in r.items if pred(v)]
    if not filtered:
        return failure()
    min_rank = min(rank for _, rank in filtered)
    return Ranking([(v, rank - min_rank) for v, rank in filtered])

def observe_e(evidence: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Evidence-oriented conditionalization: values for which pred(value) is True keep their rank, others are shifted by evidence.
    Equivalent to Racket's observe-e.
    Args:
        evidence (int): Extra evidence strength (rank increment for non-matching values).
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The evidence-conditioned and normalized ranking.
    """
    if r.is_empty():
        return r
    assoc = r.to_assoc()
    result = []
    for v, rank in assoc:
        if pred(v):
            result.append((v, rank))
        else:
            result.append((v, rank + evidence))
    # Normalize so the lowest rank is 0
    min_rank = min(rk for _, rk in result)
    return Ranking([(v, rk - min_rank) for v, rk in result])

def observe_all(ranking, predicates):
    """
    Filter a ranking by a list of predicates, keeping only values that satisfy all predicates, and normalize the result.
    If predicates is empty, all values are kept and normalized.
    Args:
        ranking (Ranking): The input ranking.
        predicates (list[Callable[[Any], bool]]): List of predicates to apply.
    Returns:
        Ranking: The filtered and normalized ranking.
    """
    # If no predicates, keep all and normalize
    if not predicates:
        return ranking.normalize()
    def all_preds(x):
        return all(pred(x) for pred in predicates)
    return ranking.filter(all_preds).normalize()

def limit(n: int, r: 'Ranking') -> 'Ranking':
    """
    Restrict a ranking to the n lowest-ranked values. If n <= 0, returns empty. If n >= len(r), returns all.
    Ties are preserved: if the nth and (n+1)th values have the same rank, only the first n are kept.
    Args:
        n (int): Number of lowest-ranked values to keep.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The limited ranking.
    """
    if n <= 0 or r.is_empty():
        return Ranking([])
    return Ranking(r.to_assoc()[:n])

def cut(threshold: int, r: 'Ranking') -> 'Ranking':
    """
    Restrict a ranking to values with rank <= threshold.
    Args:
        threshold (int): Maximum allowed rank (inclusive).
        r (Ranking): The input ranking.
    Returns:
        Ranking: The cut ranking.
    """
    if r.is_empty():
        return Ranking([])
    return Ranking([(v, rank) for v, rank in r.to_assoc() if rank <= threshold])

def rank_of(pred: Callable[[Any], bool], r: 'Ranking') -> float:
    """
    Return the lowest rank for which pred(value) is True in the ranking.
    If no value matches, returns float('inf').
    Args:
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        float: The lowest rank for which pred(value) is True, or float('inf') if none.
    """
    for v, rank in r.to_assoc():
        if pred(v):
            return rank
    return float('inf')

def argmin(r: 'Ranking') -> List[Any]:
    """
    Return all values with the minimal rank in the ranking.
    If the ranking is empty, returns an empty list.
    Equivalent to the Racket argmin utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        List[Any]: List of all values with the minimal rank (ties included).
    """
    if r.is_empty():
        return []
    assoc = r.to_assoc()
    min_rank = min(rank for _, rank in assoc)
    return [v for v, rank in assoc if rank == min_rank]

def rf_to_stream(r: Ranking) -> Generator[Tuple[Any, int], None, None]:
    """
    Convert a ranking to a generator (stream) of (value, rank) pairs in order.
    Equivalent to the Racket rf->stream utility.
    Args:
        r (Ranking): The input ranking.
    Yields:
        Tuple[Any, int]: (value, rank) pairs in non-decreasing rank order.
    """
    for v, rank in r.to_assoc():
        yield (v, rank)

def rf_equal(r1: Ranking, r2: Ranking) -> bool:
    """
    Check if two rankings are equal: same values and ranks, order irrelevant.
    Equivalent to the Racket rf-equal? utility.
    Args:
        r1 (Ranking): First ranking.
        r2 (Ranking): Second ranking.
    Returns:
        bool: True if rankings are equal, False otherwise.
    """
    return sorted(r1.to_assoc()) == sorted(r2.to_assoc())

def rf_to_assoc(r: Ranking) -> List[Tuple[Any, int]]:
    """
    Convert a ranking to a list of (value, rank) pairs in order.
    Equivalent to the Racket rf->assoc utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        List[Tuple[Any, int]]: List of (value, rank) pairs in non-decreasing rank order.
    """
    return r.to_assoc()

def rf_to_hash(r: Ranking) -> Dict[Any, int]:
    """
    Convert a ranking to a dict mapping value to rank (first occurrence wins, as in Racket).
    Equivalent to the Racket rf->hash utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        Dict[Any, int]: Dictionary mapping value to rank.
    """
    d = {}
    for v, rank in r.to_assoc():
        if v not in d:
            d[v] = rank
    return d

def pr_all(r: Ranking) -> None:
    """
    Pretty-print all (value, rank) pairs in order, or print a failure message if empty.
    Equivalent to the Racket pr-all utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        None
    """
    if r.is_empty():
        print("Failure (empty ranking)")
        return
    print("Rank  Value")
    print("------------")
    for v, rank in r.to_assoc():
        print(f"{rank:>5} {v}")
    print("Done")

def pr_first(r: Ranking) -> None:
    """
    Pretty-print the first (lowest-ranked) value and its rank, or print a failure message if empty.
    Equivalent to the Racket pr-first utility.
    Args:
        r (Ranking): The input ranking.
    Returns:
        None
    """
    if r.is_empty():
        print("Failure (empty ranking)")
        return
    v, rank = r.to_assoc()[0]
    print(f"{rank} {v}")

def top_k(k: int, r: Ranking) -> List[Any]:
    """
    Return a list of the k lowest-ranked values from the ranking.
    If k <= 0, returns an empty list. If k >= number of values, returns all values.
    Ties are not split: only the first k values are included, even if the (k+1)th value has the same rank as the kth.
    Args:
        k (int): Number of lowest-ranked values to return.
        r (Ranking): The input ranking.
    Returns:
        List[Any]: List of the k lowest-ranked values (in order).
    """
    if k <= 0 or r.is_empty():
        return []
    return [v for v, _ in r.to_assoc()[:k]]

def observe_r(rank: int, pred: Callable[[Any], bool], r: Ranking) -> Ranking:
    """
    Rank-oriented conditionalization: values for which pred(value) is True keep their rank, others are set to the given rank.
    Equivalent to Racket's observe-r.
    Args:
        rank (int): The rank to assign to non-matching values.
        pred (Callable[[Any], bool]): Predicate to test values.
        r (Ranking): The input ranking.
    Returns:
        Ranking: The rank-conditioned and normalized ranking.
    """
    if r.is_empty():
        return r
    assoc = r.to_assoc()
    result = []
    for v, rk in assoc:
        if pred(v):
            result.append((v, rk))
        else:
            result.append((v, rank))
    # Normalize so the lowest rank is 0
    min_rank = min(rk for _, rk in result)
    return Ranking([(v, rk - min_rank) for v, rk in result])
