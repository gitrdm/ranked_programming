# Ranked Programming Python Library

This is the documentation for the Python port of the ranked programming library.

## API Overview

**All combinators and abstractions are now lazy by default.**
- All previous `lazy_`-prefixed combinators are now the default and only API.
- The eager API and all eager combinators have been removed.
- All combinators automatically flatten nested Ranking/generator values.

### Core Data Structure

- `Ranking`: Represents a lazy ranking, a generator of (value, rank) pairs, sorted by rank as you iterate.

### Core Combinators (all lazy by default)
- `nrm_exc(v1, v2, rank=1) -> Ranking`: Normal/exceptional value or ranking (lazy, flattens nested values).
- `rlet(bindings: list, body: Callable) -> Ranking`: Ranked let (independent uncertainty, lazy cartesian product).
- `rlet_star(bindings: list, body: Callable) -> Ranking`: Ranked let* (dependent uncertainty, lazy sequential binding).
- `either_of(*rankings: Ranking) -> Ranking`: Normalized union, lowest rank wins (lazy, deduplicates).
- `ranked_apply(f: Callable, *args) -> Ranking`: Ranked function application (lazy, flattens nested results).
- `observe(pred, r: Ranking) -> Ranking`: Filter and normalize by predicate (lazy, normalizes ranks).
- `observe_e(evidence: int, pred, r: Ranking) -> Ranking`: Evidence-oriented conditionalization (lazy).
- `observe_all(r: Ranking, predicates: list) -> Ranking`: Filter by all predicates (lazy, normalizes).
- `limit(n: int, r: Ranking) -> Ranking`: Restrict to n lowest-ranked values (lazy, generator order).
- `cut(threshold: int, r: Ranking) -> Ranking`: Restrict to values with rank <= threshold (lazy).

### Pretty-Print Utilities
- `pr_all(r: Ranking)`: Print all (value, rank) pairs (works with lazy Ranking).
- `pr_first(r: Ranking)`: Print first (lowest-ranked) value and rank (works with lazy Ranking).

### Migration Note
- All eager combinators and the eager Ranking class have been removed.
- Use the new lazy `Ranking` and combinators (no `lazy_` prefix) for all code.
- All combinators are generator-based and flatten nested values automatically.

---

(Other sections such as utilities, predicates, and examples can be updated similarly if needed.)
