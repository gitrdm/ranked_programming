# Ranked Programming (Python Port)

**Author:** Tjitze Rienstra (original Racket version)

## Introduction

This package implements ranked programming functionality for Python, ported from the original Racket library. For background and a general introduction to ranked programming, see [this paper (IJCAI 2019)](https://github.com/tjitze/ranked-programming/blob/master/documentation/ranked_programming.pdf).

A quick-start guide for the original package can be found [here](https://github.com/tjitze/ranked-programming/blob/master/README.md).

Before using this reference, you should be familiar with the paper above. There are a few minor differences between the language described in the paper and this Python implementation, as well as additional features. These are listed below:

---

### Ranked Choice

The syntax of the *ranked choice* expression in the paper is:

    (nrm K1 exc R K2)

In this library, the syntax is:

```python
nrm_exc(K1, K2, R)
```

---

### Either/Or

The syntax of the *either/or* expression in the paper is:

    (either K1 or K2)

In this library, the syntax is:

```python
either_or(K1, K2)
```

---

### Truth Expressions

The *truth expression* `!x` described in the paper is implemented as the function `bang(x)` in Python. Thus, you must write:

```python
nrm_exc(bang("foo"), bang("bar"), 1)
```

However, all combinators that accept rankings also accept values of any type, which are implicitly converted to rankings using `bang`. Therefore, you can simply write:

```python
nrm_exc("foo", "bar", 1)
```

where `"foo"` and `"bar"` are implicitly converted to `bang("foo")` and `bang("bar")`.

---

### Displaying Rankings

Rankings encode sets of possible return values, each associated with a degree of surprise (0 = not surprising, 1 = surprising, etc.). Rankings are represented by lazy generator-based data structures. To display a ranking, use one of the print functions:

```python
pr(nrm_exc("foo", "bar", 1))
```

Alternatives include `pr_all`, `pr_until`, and `pr_first` (see reference for details).

---

### Converting Rankings

You can convert a ranking to other data structures using:
- `rf_to_hash` (dict)
- `rf_to_assoc` (association list)
- `rf_to_stream` (generator/stream)

You may also use `cut` and `limit` to restrict rankings before conversion.

---

### Additional Functions and Expression Types

This library implements all functions and expression types discussed in the paper, including:
- `bang` (truth function)
- `nrm_exc` (ranked choice)
- `either_or` (either/or shortcut)
- `observe` (observation)
- `ranked_apply` (ranked procedure call)
- `rlet_star` (ranked let*)

Additional features include:
- `either_of`: Choose elements from a list (all equally surprising)
- `construct_ranking`: Construct ranking from an association list
- `rank_of`: Return rank of a predicate according to a ranking
- `failure`: Returns the empty ranking
- `rlet`: Generalizes let (parallel binding)
- `rf_equal`: Check if two rankings are equivalent
- `rf_to_hash`/`rf_to_assoc`/`rf_to_stream`: Convert ranking to other data structures
- `pr_all`/`pr_first`/`pr_until`/`pr`: Display a ranking
- `observe_r`/`observe_e_x`: Generalized observation variants
- `cut`: Restrict ranking up to a given rank
- `limit`: Restrict ranking up to a given number of values
- `is_rank`/`is_ranking`: Type checking for ranks and rankings

All are described in detail in the reference documentation and code docstrings.

---

### Deduplication of Values

All core combinators in this library automatically deduplicate values by their hashable identity, always keeping only the first occurrence (with the minimal rank) for each hashable value. This deduplication is always enabled and is not user-configurable. Unhashable values (such as lists or dicts) are always yielded, even if repeated.

- **Why?** This ensures that rankings represent sets of possible outcomes, not multisets, and that the minimal rank for each value is preserved.
- **How?** Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported.
- **Implication:** If you need to allow duplicate values with different ranks, you must use unhashable types or modify the library.

For more details, see the `deduplicate_hashable` utility in the code and the combinator docstrings.

---

### Logging and Debugging

All core combinators in this library include debug-level logging for tracing execution, recursion, and yielded values. By default, logging is disabled. To enable detailed tracing for debugging or development, configure the Python logging system in your application:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# To see only ranked_programming logs:
logging.getLogger("ranked_programming").setLevel(logging.DEBUG)
```

You will then see debug messages for key events in combinators such as `nrm_exc`, `rlet`, `rlet_star`, `either_of`, and `ranked_apply`. Debug logging is guarded for performance and will not impact normal usage.

For more details, see the module docstrings and code comments.

---

### Input Normalization and API Consistency

All core combinators in this library accept arguments that may be atomic values, iterables of (value, rank) pairs, or `Ranking` objects. All such inputs are automatically normalized to a standard ranking form using the `as_ranking` utility. This means you can freely mix values, lists, generators, or `Ranking` objects as arguments to any combinator, and the library will handle them consistently.

- **Values** (e.g., strings, numbers) are implicitly treated as `bang(value)` (rank 0).
- **Iterables** of (value, rank) pairs are treated as rankings.
- **Ranking objects** are used as-is.
- **Callables** (functions) are called with the appropriate environment (for `rlet_star` and `rlet`).

#### Special notes:
- For `rlet` and `rlet_star`, bindings must be a list of `(name, value/function)` pairs. Each value/function is normalized as above. For `rlet_star`, functions may take arguments corresponding to previous bindings.
- If a combinator has any special input handling or restrictions, this is documented in its docstring and below.

This normalization ensures API consistency and usability across all combinators. See the code docstrings for details and examples.

## Reference

See the Python docstrings and Sphinx documentation for detailed reference on each combinator and utility function.

- `nrm_exc(k1, k2, rank=1)`: Normally returns `k1`, exceptionally returns `k2` with surprise `rank`.
- `either_or(*ks, base_rank=1)`: All arguments are equally surprising; for rankings, uses minimal rank.
- `either_of(lst)`: All elements of the list are equally surprising.
- `bang(v)`: Ranking where `v` is ranked 0, all else infinity.
- `construct_ranking(*pairs)`: Build a ranking from (value, rank) pairs.
- `rank_of(pred, k)`: Returns the rank of the lowest-ranked value for which `pred` is true in ranking `k`.
- `failure()`: Returns an empty ranking.
- `observe(pred, k)`: Conditionalizes ranking `k` on `pred`.
- `ranked_apply(f, *args)`: Ranked procedure call.
- `rlet(bindings, body)`: Parallel ranked let.
- `rlet_star(bindings, body)`: Sequential ranked let*.
- `rf_equal(k1, k2, max_items=1000)`: Check if two rankings are equivalent.
- `rf_to_hash(k, max_items=1000)`: Convert ranking to dict.
- `rf_to_assoc(k, max_items=None)`: Convert ranking to association list.
- `rf_to_stream(k, max_items=None)`: Convert ranking to generator/stream.
- `pr_all(k)`, `pr_first(k)`, `pr_until(rank, k)`, `pr(k)`: Display rankings.
- `observe_r(result_strength, pred, k)`: Result-oriented conditionalization.
- `observe_e_x(evidence_strength, pred, k)`: Evidence-oriented conditionalization.
- `mdl_evidence_penalty(ranking, pred)`: Compute an MDL-based evidence penalty for use with observation combinators. See ``examples/boolean_circuit_mdl.py`` for a worked example.
- `cut(rank, k)`: Restrict ranking to values with rank <= `rank`.
- `limit(count, k)`: Restrict ranking to the `count` lowest-ranked values.
- `is_rank(x)`, `is_ranking(x)`: Type checking for ranks and rankings.

---

For more details, see the code docstrings and Sphinx-generated documentation.
