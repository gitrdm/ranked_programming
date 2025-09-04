# Changelog

All notable changes to this project for the `code-doc-cleanup` branch are documented in this file.

## [Unreleased] - 2025-06-14

### Added
- Input normalization for all combinators: all now accept values, iterables of (value, rank) pairs, or `Ranking` objects, and are normalized consistently.
- Centralized binding validation for `rlet` and `rlet_star`.
- Edge case validation for all major combinators and utilities (e.g., empty input, invalid types, sorted ranks).
- Fine-grained debug logging to all core combinators, guarded by logger level.
- Minimal usage examples for all major combinators and utility functions in docstrings.
- Documentation of logging facilities and deduplication policy in both code and reference docs.

### Changed
- Refactored all combinators to use `as_ranking` and lazy deduplication.
- Improved and clarified type annotations and error handling throughout the codebase.
- Updated and expanded docstrings for all combinators and utilities, including edge case documentation.
- Improved Sphinx documentation: all public API functions now have clear, example-rich docstrings.

### Fixed
- Bug in `either_of` and `either_or` with unhashable values and atomic/iterable distinction.
- Recursion/eager evaluation issues in deduplication by switching to lazy `itertools.chain`.
- Type checking for `rank2` in `nrm_exc`.
- Ensured all tests pass after each logic change and documentation update.

### Removed
- User-configurable deduplication (now always-on and lazy for all combinators).

---

## [2.1.0] - 2025-09-04

### Added
- Causal reasoning v2 aligned with Section 7: Structural Ranking Models (SRM) with surgery (`do()`), stable reasons (causation), and total effects in rank space.
- Ranked conditional independence tests and PC-style discovery with v-structures and Meek R1/R2 orientation.
- Identification utilities: backdoor/frontdoor admissibility and effect estimation in ranks.
- Explanations: minimal repairs (enumeration; optional CP-SAT backend) and root-cause chain export (DOT).
- New examples: `examples/causal_boolean_circuit_srm.py`, `examples/causal_srm_identification_demo.py`.
- Optional extras in `pyproject.toml` for solver backends: `cp-sat`, `maxsat`, `asp`, `z3`.

### Changed
- Documentation: new Section 7 design doc and checklist; expanded causal tutorial; examples README updates.
- Belief propagation and conditionalization docs clarified; README expanded substantially.

### Notes
- Remaining gaps: Meek R3/R4, FCI/PAG, c-representations/SMT, measurement/IC axioms. These are non-breaking and planned for future minor releases.

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) principles.
