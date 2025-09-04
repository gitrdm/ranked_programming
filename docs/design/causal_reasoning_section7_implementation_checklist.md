# Section 7 Causal Framework — Implementation Checklist

Status: living checklist (keep updated as work progresses)

Owner: ranked_programming maintainers

Date: 2025-09-04

Purpose: Companion to the design doc. Provides an ordered, actionable plan with clear artifacts, tests, and definitions of done (DoD) so both humans and LLM agents can stay in sync as context windows shift.

Conventions
- Branch naming: `feature/causal-v2/<phase>-<short>` (e.g., `feature/causal-v2/m0-srm`)
- Feature flags (env or settings): `CR_USE_SURGERY`, `CR_SOLVER_BACKEND`, `CR_MAX_K`, `CR_Z_REASON`, `CR_EPS_CI`, `CR_TIMEOUT_MS`
- Extras: `causal[cp-sat]`, `causal[maxsat]`, `causal[asp]`, `causal[z3]`
- Graph lib: `networkx` (optional). SRM uses internal Kahn topo sort; external graph libs may be used later for PC/FCI and orientation.

Progress summary (2025-09-04)
- M0 implemented: `StructuralRankingModel` with surgery-based `do()`; internal DAG validation + topological order (no external deps).
- Graph queries added: parents/children/ancestors/descendants with Sphinx-friendly docstrings.
- M1 baseline implemented: stable reason-relations (`is_cause`) and `total_effect` under surgery.
- M2 implemented: ranked CI (`ranked_ci`) and PC skeleton (`pc_skeleton`) with v-structure orientation.
- M3 baseline implemented: minimal repairs (`MinimalRepairSolver`) and root-cause chains (`root_cause_chain`).
- M4 implemented: identification (`is_backdoor_admissible`, `backdoor_adjusted_effect`, `is_frontdoor_applicable`, `frontdoor_effect`).
- Exports added under `ranked_programming.causal`.
- Unit tests added: `tests/causal/test_srm.py`, `tests/causal/test_causation_v2.py`, `tests/causal/test_ranked_pc.py`, `tests/causal/test_explanations.py`, `tests/causal/test_identification.py`.
- Full suite passing: 206 tests.

## M0 — Structural Ranking Model (SRM) + Surgery

Steps
1) Implement `StructuralRankingModel`
   - Types: Variable(name, domain, parents, mechanism)
   - Build topological order (internal Kahn algorithm) and validate DAG
   - `to_ranking()`: compose mechanisms via `rlet_star` into a joint Ranking
2) Implement surgery `do(interventions)`
   - Override mechanisms for intervened vars (constant Ranking)
   - Ignore parents for intervened vars (cut incoming edges) during composition
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

Status: Completed 2025-09-04
- Code: `src/ranked_programming/causal/srm.py`, `src/ranked_programming/causal/__init__.py`
- Tests: `tests/causal/test_srm.py` (PASS); full suite 194 PASS

## M1 — Causation: Stable Reason-Relations + Effects

Steps
1) Implement `is_cause(A,B,srm,z)`
   - Contexts: assignments over variables excluding A and its descendants; ordered by plausibility (κ) from observational joint ranking
   - Compute τ via κ differences on observational ranking; record minimal margin; early exit on violation
2) Effects utilities
   - `total_effect(A,B,a,a')` compare τ(B) under `do(A=a)` vs `do(A=a')`
   - `conditional_effect(A,B|Z=z)` using filtering/conditioning (planned)
3) Config thresholds via settings/env (planned)

Artifacts
- `src/ranked_programming/causal/causal_v2.py`
- Tests: `tests/causal/test_causation_v2.py`

Tests
- Unshielded chain A→B→C shows A causes C; minimal strength recorded
- Fork and screening notes; additional conditioning tests planned

DoD
- Baseline stable reason-relations and total effect implemented; tests green

Status: In progress (baseline landed 2025-09-04)
- Code: `src/ranked_programming/causal/causal_v2.py`
- Tests: `tests/causal/test_causation_v2.py` (PASS); full suite 197 PASS

## M2 — Ranked CI + PC/FCI Skeleton

Steps
1) Ranked CI predicate `ranked_ci(A,B|Z)` with ε tolerance (hard conditioning)
2) PC skeleton
   - Adjacency pruning by CI up to k
   - Store separating sets; orient v-structures; Meek rules (planned)
3) FCI optional partial orientation (planned)

Artifacts
- `src/ranked_programming/causal/ranked_pc.py`
- Tests: `tests/causal/test_ranked_pc.py`

Tests
- Recover chain, fork, collider on canonical 3–5 node graphs with noisy links
- Sensitivity to ε and k_max documented (planned)

DoD
- PC recovers correct skeleton/orientation on toys; API stable

Status: Completed 2025-09-04 (skeleton + v-structures)
- Code: `src/ranked_programming/causal/ranked_pc.py`
- Tests: `tests/causal/test_ranked_pc.py` (PASS); full suite 200 PASS

## M3 — Explanations: Minimal Repair + Root-Cause Chains

Steps
1) `MinimalRepairSolver` (baseline exact enumeration)
   - Return all minimal sets up to size bound; de-dup supersets
   - Solver backends (ucs/cp-sat/maxsat/asp) planned in M5
2) `root_cause_chain(srm, repair_set, target)`
   - Trace from repairs to target through SRM DAG
   - Optional internal nodes (planned)
3) Per-world counterfactual proof (planned)

Artifacts
- `src/ranked_programming/causal/explanations.py`
- Tests: `tests/causal/test_explanations.py`

Tests
- Boolean circuit failing cases: minimal repairs {O2} for c=True; {N} or {O1} or {O2} for c=False
- Chains narrate via provided l1/l2 when present; counterfactual checks pass

DoD
- Baseline: minimal repairs and DAG chains produced; tests green

Status: Completed baseline 2025-09-04
- Code: `src/ranked_programming/causal/explanations.py`
- Tests: `tests/causal/test_explanations.py` (PASS); full suite 202 PASS

## M4 — Identification: Backdoor/Frontdoor (Rank Analogues)

Steps
1) Backdoor admissibility checker on oriented graph
2) Effect estimation under adjustment sets with surgery
3) Frontdoor helper for simple mediators

Artifacts
- `src/ranked_programming/causal/identification.py`
- Tests: `tests/causal/test_identification.py`

Tests
- Backdoor: Confounded A→B with common cause U; Z={U} admissible, ∅ not. Adjusted effect computed via min-plus aggregation.
- Frontdoor: A→M→B with confounding U→{A,B}; applicability holds; mediator aggregation returns finite τ.

DoD
- Utilities usable on discovered/assumed graphs; documented behavior; Sphinx docstrings in code.

Status: Completed 2025-09-04
- Code: `src/ranked_programming/causal/identification.py` (PASS)
- Tests: `tests/causal/test_identification.py` (PASS); suite 206 PASS

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
