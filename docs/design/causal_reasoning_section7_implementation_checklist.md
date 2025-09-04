# Section 7 Causal Framework — Implementation Checklist

Status: living checklist (keep updated as work progresses)

Owner: ranked_programming maintainers

Date: 2025-09-04

Purpose: Companion to the design doc. Provides an ordered, actionable plan with clear artifacts, tests, and definitions of done (DoD) so both humans and LLM agents can stay in sync as context windows shift.

Conventions
- Branch naming: `feature/causal-v2/<phase>-<short>` (e.g., `feature/causal-v2/m0-srm`)
- Feature flags (env or settings): `CR_USE_SURGERY`, `CR_SOLVER_BACKEND`, `CR_MAX_K`, `CR_Z_REASON`, `CR_EPS_CI`, `CR_TIMEOUT_MS`
- Extras: `causal[cp-sat]`, `causal[maxsat]`, `causal[asp]`, `causal[z3]`
- Graph lib: `networkx`

## M0 — Structural Ranking Model (SRM) + Surgery

Steps
1) Implement `StructuralRankingModel`
   - Types: Variable(name, domain, parents, mechanism)
   - Build topological order (networkx) and validate DAG
   - `to_ranking()`: compose mechanisms via `rlet` to joint Ranking
2) Implement surgery `do(interventions)`
   - Override mechanisms for intervened vars (constant ranking)
   - Ignore parents for intervened vars during composition
3) Keep `_intervene` in legacy API but mark as deprecated in docstrings

Artifacts
- `src/ranked_programming/causal/srm.py`
- `src/ranked_programming/causal/__init__.py` (exports)
- Unit tests: `tests/causal/test_srm.py`

Tests
- DAG validation, topo order stable
- `to_ranking()` equals hand-built Ranking for small models
- `do(X=v)`: parents of X ignored; downstream changes as expected

DoD
- SRM produces correct joint Ranking; surgery semantics verified on toy graphs
- Lint/type pass; tests green

## M1 — Causation: Stable Reason-Relations + Effects

Steps
1) Implement `CausalReasonerV2.is_cause(A,B,srm,z)`
   - Enumerate/sampling of admissible contexts (non-descendants of A)
   - Compare τ(B|A,C) vs τ(B|¬A,C); record minimal margin
   - Early exit on violation
2) Effects utilities
   - `effect_under_surgery(A,B,a,a',srm)` compare τ under `do`
   - `conditional_effect(A,B|Z=z)` using filter/conditioning compatibly
3) Config thresholds via settings/env

Artifacts
- `src/ranked_programming/causal/causal_v2.py`
- Tests: `tests/causal/test_causation_v2.py`

Tests
- Synthetic cases where cause holds/fails; enumerate contexts on small graphs
- Screened vs unshielded boolean circuit; margins consistent

DoD
- Boolean causation judgments match expectations across scenarios; tests green

## M2 — Ranked CI + PC/FCI Skeleton

Steps
1) Ranked CI predicate `ci(A,B|Z)` with ε tolerance
2) PC skeleton
   - Adjacency pruning by CI up to k
   - Store separating sets; orient v-structures; Meek rules
3) FCI optional partial orientation

Artifacts
- `src/ranked_programming/causal/ranked_pc.py`
- Tests: `tests/causal/test_ranked_pc.py`

Tests
- Recover chain, fork, collider on canonical 3–5 node graphs
- Sensitivity to ε and k_max documented

DoD
- PC recovers correct skeleton/orientation on toys; API stable

## M3 — Explanations: Minimal Repair + Root-Cause Chains

Steps
1) `MinimalRepairSolver` (strategy pattern)
   - Strategies: `ucs` (incremental search), `cp-sat`, `maxsat`, `asp`
   - Return all minimal sets up to size bound; de-dup supersets
2) `root_cause_chain(world, target, graph, srm)`
   - Trace from repairs to target through oriented graph
   - Optional inclusion of internal nodes (user-provided)
3) Per-world counterfactual proof (apply `do` and verify target flips)

Artifacts
- `src/ranked_programming/causal/explanations.py`
- Tests: `tests/causal/test_explanations.py`

Tests
- Boolean circuit failing cases: minimal repairs {O2} for c=True; {N} or {O1} or {O2} for c=False
- Chains narrate via provided l1/l2 when present; counterfactual checks pass

DoD
- Explanations produce minimal repairs and valid chain proofs

## M4 — Identification: Backdoor/Frontdoor (Rank Analogues)

Steps
1) Backdoor admissibility checker on oriented graph
2) Effect estimation under adjustment sets with surgery
3) Frontdoor helper for simple mediators

Artifacts
- `src/ranked_programming/causal/identification.py`
- Tests: `tests/causal/test_identification.py`

Tests
- Backdoor examples where Z blocks confounding; effect matches direct surgery in acyclic simple models

DoD
- Utilities usable on discovered/assumed graphs; documented behavior

## M5 — Pluggable Solver Backends

Steps
1) Interfaces: `SeparatingSetFinder`, `MinimalRepairSolver`, `CounterexampleFinder`
2) Backends: greedy (default), CP-SAT, MaxSAT, SMT, ASP
3) Extras, detection, timeouts, and graceful fallback

Artifacts
- `src/ranked_programming/causal/constraints.py`
- Tests: `tests/causal/test_constraints.py`

Tests
- Backend parity on small instances; fallback path exercised

DoD
- Backends configurable; defaults work without optional deps

## M6 — Docs, Tutorials, Examples

Steps
1) Update design + checklist (this file) as features land
2) Author tutorial: SRM modeling, surgery, causation, PC, explanations
3) Two domain examples beyond boolean circuits (e.g., HMM causal slice; small planning/diagnosis)

Artifacts
- `docs/causal_reasoning_tutorial.md`
- Examples under `examples/causal/`

DoD
- Tutorial runnable; examples produce expected outputs

## M7 — Performance, CI, Telemetry

Steps
1) Micro-bench SRM/to_ranking and surgery on medium graphs; ensure no regressions vs legacy
2) Add CI jobs for tests/lint/type; optional slow suite behind flag
3) Add simple logging around solver fallback/escalation and timing

Artifacts
- CI config updates; logging hooks

DoD
- CI green; logging aids backend selection tuning

---

Working notes
- Keep both this checklist and the design doc updated per PR.
- When a phase lands, tag the repo `causal-v2-M<phase>` and add a summary block at the top of both docs.
- Prefer small PRs per step with tests. If a step must span PRs, keep a stub feature flag and docs updated.
