# Ranked Programming Python Library

This is the documentation for the Python port of the ranked programming library.

## Examples and Regression Testing

**All example files in the `examples/` directory are used as regression tests.**

- If you add or modify an example file, ensure its output remains consistent with the expected regression tests in `../tests/`.
- Regression tests will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or subdirectory, or coordinate with the test suite maintainers.

This policy ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.

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

## Evidence Penalty Types

The library provides three principled approaches to calculating evidence penalties for use with observation combinators:

- **MDL-based Penalties** (`mdl_evidence_penalty`): Information-theoretic approach using minimum description length
- **Adaptive Penalties** (`adaptive_evidence_penalty`): Learning-based approach that adapts to historical performance
- **Confidence-based Penalties** (`confidence_evidence_penalty`): Statistical approach using confidence intervals

## MDL Penalty Estimation Examples

See the following examples for practical usage of evidence penalties:

- `examples/boolean_circuit_mdl.py`: Demonstrates MDL penalty calculation for a small boolean circuit, including comparison to fixed and adaptive penalties.
- `examples/boolean_circuit_mdl_result.py`: Shows how to use MDL to set the result penalty in `observe_r`, providing a principled, adaptive alternative to fixed penalties.
- `examples/mdl_penalty_estimation.py`: Shows five practical approaches to estimating the MDL penalty when the set of possible worlds is too large to enumerate: sampling, analytic counting, bounds, heuristic, and adaptive estimation. Each approach is documented and illustrated in code.
- `examples/boolean_circuit_mdl_e_x.py`: Demonstrates MDL penalty calculation for use as the evidence penalty in `observe_e_x`, including comparison to fixed and confidence-based penalties.
- `examples/ranking_network_mdl.py`: MDL-based evidence penalty for a ranking network scenario.
- `examples/hidden_markov_mdl.py`: Comprehensive comparison of MDL, adaptive, and confidence-based evidence penalties for a hidden Markov model scenario.
- `examples/localisation_mdl.py`: MDL-based evidence penalty for a robot localisation scenario.
- `examples/ranked_procedure_call_mdl.py`: MDL-based evidence penalty for ranked procedure call outputs.
- `examples/recursion_mdl.py`: MDL-based evidence penalty for recursive search outputs.
- `examples/spelling_correction_mdl.py`: MDL-based evidence penalty for spelling correction outputs.
- `examples/ranked_let_mdl.py`: MDL-based evidence penalty for ranked let (independent/dependent uncertainty) outputs.

These examples provide guidance for principled, scalable evidence and result handling in ranked programming models.

---

(Other sections such as utilities, predicates, and examples can be updated similarly if needed.)
