# Ranked Programming Python Library

This is the documentation for the Python port of the ranked programming library.

## API Overview

All functions are available from `ranked_programming.rp_api`.

### Core Data Structure

- `Ranking`: Represents a ranking, a list of (value, rank) pairs, sorted by rank.

### Constructors
- `construct_ranking(*args: tuple) -> Ranking`: Construct a ranking from (value, rank) pairs.
- `construct_from_assoc(assoc: List[Tuple[Any, int]]) -> Ranking`: From association list.
- `failure() -> Ranking`: Empty ranking (failure).
- `truth(value: Any) -> Ranking`: Singleton ranking at rank 0.

### Predicates
- `ranking(obj: Any) -> bool`: Is this a Ranking?
- `rank(obj: Any) -> bool`: Is this a valid rank (non-negative int or float('inf'))?

### Core Combinators
- `normalise(r: Ranking) -> Ranking`: Shift all ranks so minimum is 0.
- `map_value(f, r: Ranking) -> Ranking`: Map function over values.
- `shift(amount: int, r: Ranking) -> Ranking`: Shift all ranks by amount.
- `filter_ranking(pred, r: Ranking) -> Ranking`: Filter by value predicate.
- `filter_after(pred, r: Ranking) -> Ranking`: Keep entries after first match.
- `up_to_rank(max_rank: int, r: Ranking) -> Ranking`: Keep entries with rank <= max_rank.
- `dedup(r: Ranking) -> Ranking`: Remove duplicate values (unless dedup disabled).
- `do_with(f, r: Ranking) -> int`: Sum f(value, rank) over ranking.

### Choice and Observation
- `either_of(*rankings: Ranking) -> Ranking`: Normalized union, lowest rank wins.
- `either_or(*rankings: Ranking) -> Ranking`: All unique values at rank 0.
- `nrm_exc(v1, v2, rank=1) -> Ranking`: Normal/exceptional value or ranking.
- `rlet(bindings: dict, body: Callable) -> Ranking`: Ranked let (independent uncertainty).
- `rlet_star(bindings: List[Tuple[str, Union[Ranking, Callable]]], body: Callable) -> Ranking`: Ranked let* (dependent uncertainty).
- `ranked_apply(f: Callable, *args) -> Ranking`: Ranked function application.
- `observe(pred, r: Ranking) -> Ranking`: Filter and normalize by predicate.
- `observe_all(r: Ranking, predicates: List[Callable]) -> Ranking`: Filter by all predicates.
- `observe_e(evidence: int, pred, r: Ranking) -> Ranking`: Evidence-oriented conditionalization.
- `observe_r(rank: int, pred, r: Ranking) -> Ranking`: Rank-oriented conditionalization.

### Utilities
- `limit(n: int, r: Ranking) -> Ranking`: Restrict to n lowest-ranked values.
- `cut(threshold: int, r: Ranking) -> Ranking`: Restrict to values with rank <= threshold.
- `rank_of(pred, r: Ranking) -> float`: Lowest rank for which pred(value) is True.
- `argmin(r: Ranking) -> List[Any]`: All values with minimal rank.
- `rf_to_stream(r: Ranking) -> Generator`: Generator of (value, rank) pairs.
- `rf_equal(r1, r2) -> bool`: Ranking equality (order-insensitive).
- `rf_to_assoc(r: Ranking) -> List[Tuple[Any, int]]`: To association list.
- `rf_to_hash(r: Ranking) -> Dict[Any, int]`: To dict (first occurrence wins).
- `top_k(k: int, r: Ranking) -> List[Any]`: List of k lowest-ranked values.
- `set_global_dedup(enabled: bool)`: Enable/disable deduplication.
- `get_global_dedup() -> bool`: Get deduplication setting.

### Pretty-Print Utilities
- `pr_all(r: Ranking)`: Print all (value, rank) pairs.
- `pr_first(r: Ranking)`: Print first (lowest-ranked) value and rank.

## Examples

See the `python/examples/` directory for usage examples duplicating the Racket examples.

## Further Reading

- See the original Racket documentation for theoretical background.
- See the source code for literate docstrings and further details.
