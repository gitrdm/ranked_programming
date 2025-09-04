# Future Idea: Soufflé Datalog Backend for Causal Discovery/Identification

Updated: 2025-09-04

## Why consider Datalog?
Soufflé excels at large-scale Horn-rule closures over relations and graph data. In our causal stack, several subproblems are closure-heavy and polynomial-time:
- Orientation rule propagation (Meek R1–R4) and FCI orientation rules.
- Graph reachability and ancestral closures (Anc/Desc), forbidden sets, moralization helpers.
- Precomputations for d-separation candidate pruning.

These are a good fit for Datalog’s bottom-up evaluation and can be much faster than pure Python for large graphs.

## Where it fits (and doesn’t)
- Good fit:
  - PC/FCI orientation propagation after v-structure detection.
  - Ancestor/descendant and reachability computations for pruning candidate conditioning sets.
  - Generating admissible adjustment candidate pools for backdoor/frontdoor checks.
- Poor fit:
  - Rank arithmetic (κ/τ), conditionalization, and Shenoy-style message passing.
  - Optimization/minimality (minimal repairs, minimal separators). Keep CP-SAT/ASP for those.

## Proposed scope
- Start with Meek R1–R4 as a Datalog ruleset over edges and arrowheads.
- Add ancestor/descendant relation derivation and basic reachability.
- Optional: FCI-lite orientation rules and PAG edges, as a second phase.

## Interface sketch
- Input facts (CSV):
  - `Undir(u,v)` for undirected adjacency.
  - `Arrow(u,v)` for oriented edges u->v from v-structures.
  - Optional: `Sep(x,y,z)` for known separating sets.
- Output relations:
  - `Arrow(u,v)` closed under Meek rules.
  - `Anc(u,v)` ancestor relation.
  - Optional: `Forbid(u,v)` or `Block(u,v,z)` helpers for pruning.

Python wrapper:
- Export current graph and constraints to CSV.
- Call `souffle -F facts -D out pc_orientation.dl`.
- Read back `Arrow.csv` and `Anc.csv`, update orientation state.

## Data model notes
- Keep vertices as strings; normalize to a stable set of IDs.
- Ensure symmetry on `Undir` inputs; Soufflé doesn’t enforce it.
- Meek rules expect no directed cycles; assert/validate acyclicity in Python.

## Performance expectations
- R1–R4 closure is linear-time per iteration; Soufflé’s bottom-up evaluation should converge in a handful of passes, efficiently handling thousands of nodes/edges.
- Ancestor closures can reuse standard transitive closure patterns and scale well.

## Risks and mitigations
- Tooling dependency: Gate behind optional extra `datalog` and skip if Soufflé not installed.
- Debuggability: Log generated facts and resulting relations; keep a dry-run flag.
- Semantics drift: Add unit tests mirroring Python Meek R1/R2; parity checks for new rules.

## Deliverables (if/when implemented)
- `souffle/pc_orientation.dl` with Meek R1–R4.
- `souffle/common.dl` with Anc/Desc closures and helpers.
- Python glue: `ranked_programming/causal/datalog_backend.py` (export, run, import).
- Flags: `use_backend="datalog"` in discovery APIs.
- Tests: orientation parity tests; reachability sanity; performance smoke.

## Decision
Defer implementation. Documenting potential; proceed if we target larger graphs or need full Meek/FCI orientation performance.
