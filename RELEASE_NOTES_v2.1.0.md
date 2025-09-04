# v2.1.0

## Added
- Causal reasoning v2 (Section 7): Structural Ranking Models (SRM) with surgery (`do()`), stable reasons (causation), and total effects in rank space.
- Ranked CI + PC discovery with v-structures and Meek R1/R2 orientation.
- Identification utilities: backdoor/frontdoor admissibility and τ-based effect estimation.
- Explanations: minimal repairs (enumeration; optional CP-SAT) and root-cause DOT export.
- New examples: `examples/causal_boolean_circuit_srm.py`, `examples/causal_srm_identification_demo.py`.
- Optional extras (`pyproject.toml`) for solver backends: `cp-sat`, `maxsat`, `asp`, `z3`.

## Changed
- Expanded documentation: Section 7 design + checklist; updated causal tutorial; enriched README.
- Clarified belief propagation and Spohn conditionalization notes.

## Notes
- Remaining gaps planned for future minors: Meek R3/R4, FCI/PAG, c-representations/SMT, measurement/IC axioms.
