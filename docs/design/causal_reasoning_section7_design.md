# Section 7–Compliant Causal Reasoning (Design Doc)

Status: draft for review (M0 implemented)

Owner: ranked_programming maintainers

Date: 2025-09-04

## Motivation

Section 7 (Ranking-Theoretic Causal Inference) sets expectations for a projectivist causal framework grounded in ranking theory: causes are stable reason-relations encoded in a ranking function, interventions should reflect a “surgery-like” semantics, and one should be able to recover causal structure and provide root-cause style explanations. The current `causal_reasoning.py` offers useful building blocks (intervene, counterfactuals, pairwise checks), but it is not yet aligned with the full Section 7 program nor with SCM/do-calculus ergonomics.

This document proposes a concrete, incremental design to deliver a Section 7–compliant causal layer built on existing Ranking combinators (no ad-hoc alternative engines), with optional use of SMT/Prolog for robustness.

## Goals

- Structural ranking model (SRM): declaratively describe variables, parents, and ranked mechanisms using existing combinators.
- Intervention as surgery: `do(X=v)` ignores X’s parents (cuts incoming influences) and uses a mechanism override, not just filtering worlds.
- Stable reason-relations: formal, rank-based criterion for A causing B that quantifies stability “across non-effects contexts,” with thresholds and tractable approximations.
- Ranking-based conditional independence (CI): a defensible CI predicate in ranks to support real PC/FCI-style discovery and edge orientation.
- Discovery: implement a ranked-PC variant (and optionally FCI) operating over propositions/variables; support internal/derived nodes.
- Explanations: minimal repair sets and root-cause chains for failing outcomes, with per-world counterfactual proofs.
- Identification: rank analogs of backdoor/frontdoor adjustment once surgery semantics exist.
- Built on Ranking: use `Ranking`, `rlet`, `nrm_exc`, `observe_e`, Shenoy-style BP, and existing APIs—no separate ad-hoc modeling engine.

## Non-goals (initially)

- Full do-calculus rule system (sound/complete proofs). We target practical backdoor/frontdoor and PC/FCI first.
- Probabilistic estimators. All semantics are rank-based; probabilistic mapping is out-of-scope.

## Section 7 requirements distilled

- Causation as reasons: A is a cause of B if τ(B|A) > τ(B|¬A) robust across admissible contexts (variables not downstream of A).
- Intervention semantics: manipulate variables by breaking incoming influences (surgery), not merely reweighting.
- Discovery: extract causal structure from stable reason-relations; internal nodes (e.g., l1, l2) must be representable as propositions/variables.

## Current status (2025-09-04)

- Implemented M0 (SRM + surgery):
  - `StructuralRankingModel` with internal DAG validation and Kahn topological order.
  - `to_ranking()` composes mechanisms via `rlet_star` to produce a joint Ranking over assignments.
  - `do(interventions)` performs surgery by overriding mechanisms with constants and clearing parents for intervened variables.
  - Exports available from `ranked_programming.causal`.
  - Tests cover topo order, composition, surgery, and cycle detection.

+- Implemented M1 baseline (causation and effects):
  - Stable reason-relations `is_cause(A,B,srm,z,max_contexts)` with context enumeration by plausibility and τ via κ differences.
  - `total_effect(A,B,srm,a,a_alt)` via surgery do-operator.
  - Added graph query helpers to SRM for admissible context definition.

+- Implemented M2 (ranked CI + PC skeleton):
  - Ranked CI predicate with symmetric τ checks under hard conditioning.
  - PC skeleton discovery using CI up to k, storing separating sets, and v-structure orientation.
  - Tests cover chain, fork, collider using noisy link mechanisms to ensure faithfulness.

- Implemented M3 baseline (explanations):
  - Minimal repair sets via exact enumeration baseline; SRM surgery to verify fixes.
  - Root-cause chains traced along SRM DAG.
  - Tests cover chain graph minimal repairs and path narration.

- Test suite passing: 202 tests.

Next milestones: M1 (stable reason-relations), M2 (ranked CI + PC skeleton), as outlined below.

## High-level architecture

- Core module: `srm.py` (Structural Ranking Model)
  - Declarative model of variables, parents, mechanisms (as Ranking combinators).
  - Generate observational `Ranking` and intervened `Ranking` via composition (`rlet_star`) and Shenoy BP when needed.
- Causation module: `causal_do.py`
  - Stable reason-relations causation test; effect strengths; conditional/screened effects.
- Discovery module: `ranked_pc.py`
  - Ranked CI test; PC/FCI-like skeleton adapted to ranks; edge orientation rules.
- Explanations module: `explanations.py`
  - Minimal repair, root-cause chains, per-world proofs.
- Integration: optional `constraints.py` to leverage SMT and/or Prolog/kanren for repair-set minimality and CI counterexamples.

All modules depend on existing `Ranking` primitives and do not reimplement ranking engines.

## Core abstractions and API sketches

- Variable (structural):
  - name: str
  - domain: finite set (bool in first iteration)
  - parents: list[str]
  - mechanism: Callable[parent_values -> Ranking over variable values] or combinator-backed callable

- StructuralRankingModel
  - constructor(vars: List[Variable])
  - methods:
    - `to_ranking() -> Ranking`: compose mechanisms with `rlet` into a joint Ranking over assignments
    - `do(interventions: Dict[str, Any]) -> StructuralRankingModel`: return a copy where intervened variables ignore parents and use constant mechanisms (or provided mechanisms)
    - `observational() -> Ranking`: alias of `to_ranking()`
    - `interventional(interventions) -> Ranking`: `do(...).to_ranking()`

- CausalReasonerV2
  - `is_cause(A: str, B: str, srm: StructuralRankingModel, z: int=1) -> Tuple[bool, float]`
    - A cause of B iff for all admissible contexts C (sets of non-descendants of A), τ(B|A,C) ≥ τ(B|¬A,C)+z, computed on observational ranking.
    - Approximations for tractability (see below).
  - `effect(A, B, srm) -> float`: rank-difference effect under surgery and/or reason-based delta τ.
  - `conditional_effect(A,B | Z=z)`: via filtering and/or surgery + conditioning.

- RankedPC
  - `discover(vars: List[str], srm or ranking, ci_params) -> Graph`
  - Uses ranked CI predicate (see next section) to prune and orient edges.

- Explanations
  - `minimal_repair(world, targets: List[str], srm) -> List[Set[str]]`
  - `root_cause_chain(world, target: str, graph, srm) -> List[str]`

API usage is intentionally SCM-like but remains rank-native.

## Intervention semantics (surgery)

- Observational generation: compose variable mechanisms with `rlet_star` (and `nrm_exc`) into a joint `Ranking`.
- Surgery: for `do(X=v)`, replace X’s mechanism with a constant `Ranking(lambda: [ (v, 0) ])` (or a trivial `nrm_exc` with 0 penalty) and remove X from parents of its children during composition.
- Implementation detail: In `to_ranking()`, build the joint generator in topological order of the graph; for intervened variables, ignore parent values when invoking the mechanism. The rest of the graph composes normally.
- Backward-compatible path: retain legacy filter-style `_intervene` for simple demos; mark as deprecated once surgery is stable.

## Ranking-based conditional independence (CI)

We need a predicate CI(A, B | Z) over ranks. Proposed practical criterion:

- Define Δτ = |τ(B|A,Z) − τ(B|Z)| (and symmetrically |τ(A|B,Z) − τ(A|Z)|).
- CI(A,B|Z) holds if both deltas ≤ ε (tolerance), and all terms are finite (or clipped using PRACTICAL_INFINITY handling).
- For booleans, τ derived from κ via τ(B) = κ(¬B) − κ(B). Conditionals via κ(B∧Z) − κ(Z) using existing `Ranking` methods.
- Notes:
  - ε (and stability threshold z) are configuration knobs; defaults aligned to integer granularity (e.g., ε=0, z=1).
  - Use Shenoy BP to compute conditionals on large models efficiently.

## Discovery (PC/FCI variant over ranks)

- Skeleton:
  1. Start with complete undirected graph over variables.
  2. For k=0..max, remove edge X—Y if ∃Z subset of adjacents with |Z|=k s.t. CI(X,Y|Z) holds. Store separating sets.
  3. Orient edges using standard PC rules (v-structures via separating sets, Meek rules), adapted to ranked CI.
- FCI extension: include possible latent confounding with partial orientation.
- Practicalities:
  - Limit k by budget.
  - Use SMT/Prolog to find separating sets efficiently when brute force is expensive.
  - Accept that “ranked CI” differs from probabilistic CI; behavior is stable in integer steps.

## Stable reason-relations causation test

- Section 7 notion: A directly causes B if A is a reason for B robust across non-effects contexts.
- Operationalization:
  - Compute set of admissible contexts C as configurations over variables not downstream of A (use discovered/assumed graph; if unknown, approximate with subsets of neighbors not pointing from A).
  - For each C, compare τ(B|A,C) vs τ(B|¬A,C). If τ(B|A,C) ≥ τ(B|¬A,C) + z for all C, accept causation. Record minimal Δ across C as strength.
  - Approximations:
    - Sample contexts C by (a) most plausible assignments (low κ), (b) small-cardinality subsets, (c) SMT search for counterexamples where inequality fails.
    - Early exit on violation.

## Effects and identification (backdoor/frontdoor analogs)

- With surgery semantics, define total effect of A on B via:
  - τ_do: compute τ(B) under `do(A=a)` and `do(A=a')` and compare.
  - Backdoor adjustment (rank analog): when Z blocks all backdoor paths A ← … → B, estimate effect via marginalization over Z in the intervened model.
- Provide utilities to test backdoor admissibility using the oriented graph (ranked PC output).

## Explanations: minimal repair and root-cause chains

- Minimal repair: Given a failing target T in world ω (from top plausible worlds), find smallest set S of components to set “working” such that in `do(S=working)` the target is OK.
  - Start with size-1 search, escalate; use SMT or Prolog/kanren to encode constraints; or greedy + verify.
  - Return all minimal S (not supersets).
- Root-cause chain: Given S and an oriented graph, trace paths from S to T. If internal nodes (e.g., l1, l2) are modeled, include them to narrate signal propagation. Validate with per-path counterfactual checks.

## Integration with Ranking combinators and BP

- Mechanisms: model default/exception behavior with `nrm_exc`, user-defined `Ranking` factories, and compose with `rlet`.
- Inference: use existing Shenoy-style message passing to compute marginals/conditionals in large SRMs.
- Evidence: integrate `observe_e` and standard combinators for updates before causation queries.

## SMT/Prolog integration points

- Separating set search: encode CI counterexample search as constraints; solver finds Z efficiently or proves none exist up to k.
- Minimal repair: encode as minimal hitting set / SAT on causal constraints.
- Stability counterexample: search for context C where τ(B|A,C) < τ(B|¬A,C)+z.

## Tooling and implementation choices

Core principle: keep Ranking Theory as the computational core (Ranking, rlet, nrm_exc, Shenoy/BP). Use external solvers only for combinatorial selection/optimization. Prefer robust, widely used libraries with Python bindings.

- Ranking and inference
  - Core: existing `ranked_programming` combinators and Shenoy-style belief propagation.
  - Numerics: no heavy numeric stack required; `numpy` optional for small vector ops if beneficial.

- Graph representation and algorithms
  - `networkx`: graph datastructures, topological order, Meek rules for PC/FCI orientation, reachability, ancestor/descendant queries.

- Conditional-independence search and separating sets
  - Default: greedy/heuristic search guided by plausibility (low κ) and adjacency constraints.
  - Escalation: Google OR-Tools CP-SAT (preferred), PySAT/MaxSAT, or Z3 SMT (LIA) to find Z with |Z|≤k satisfying CI predicates.
  - Rationale: CP-SAT/MaxSAT handle combinatorics and cardinality well; SMT is a fallback for mixed constraints.

- Minimal repair (root-cause fixes)
  - Preferred: CP-SAT (OR-Tools) or MaxSAT (PySAT) for min-cardinality intervention sets; returns all minimal sets or lexicographically minimal.
  - Alternative: ASP (clingo) for rich constraints/explanations; natural for minimality and enumeration.

- Counterexample finding for stability
  - Preferred: CP-SAT (bounded context size) or Z3; search for C that violates τ-inequalities. Start from most plausible contexts to prune.

- Logic/relational prototyping
  - Optional: Prolog (e.g., pyswip) or miniKanren/kanren for small relational searches; useful for explanation templates.

- Testing and verification
  - `pytest` for unit/integration tests; `hypothesis` for property-based checks (e.g., surgery invariants, CI symmetry).

- Packaging
  - Pin solver backends as extras: `causal[cp-sat]`, `causal[maxsat]`, `causal[asp]`, `causal[z3]`.
  - Provide runtime detection and graceful degradation to greedy heuristics when solvers are absent.

### Pluggable solver interface

Define thin strategy interfaces so higher-level code is backend-agnostic:

- `SeparatingSetFinder`
  - strategies: `"greedy" | "cp-sat" | "maxsat" | "smt"`
  - method: `find(x, y, candidates, k_max, ci_pred) -> Optional[Set[str]]`

- `MinimalRepairSolver`
  - strategies: `"ucs" | "cp-sat" | "maxsat" | "asp"`
  - method: `repairs(world, targets, srm, max_size=None) -> List[Set[str]]`

- `CounterexampleFinder`
  - strategies: `"enumerate" | "cp-sat" | "smt"`
  - method: `find_violation(ineq, vars, bound) -> Optional[Assignment]`

Backend selection can be configured via settings or environment; default to heuristics, escalate when installed and when problem size warrants.

## Edge cases and numerics

- PRACTICAL_INFINITY: use clipping for ∞; treat “decisive” changes as large constants, but report booleans prominently.
- Thresholds: expose `epsilon_ci` and `z_reason` with sane integer defaults; document sensitivity.
- Domains: start with booleans; keep APIs domain-agnostic for future finite domains.

## Migration and compatibility

- `causal_reasoning.py` becomes a thin wrapper delegating to SRM + V2 APIs; deprecate filter-style `_intervene` for surgery-based `do`.
- Update demos/tests to new APIs; add tutorial on SRM modeling and explanations.

## Testing plan

- Unit tests:
  - Surgery: verify parents ignored for intervened variable.
  - CI: known independences in toy graphs; check ε=0 exactness.
  - PC: recover structure on small canonical graphs (chains, forks, colliders).
  - Stable cause: synthetic cases where reason-relations hold/fail under enumerated contexts.
  - Minimal repair: small circuit; verify sets and per-world counterfactual recovery.
- Integration tests: boolean circuit scenarios (c=True screened vs c=False unshielded), hidden Markov examples.

## Milestones

- M0 (scaffolding): SRM + surgery; legacy `_intervene` deprecated; examples updated.
- M1 (causation): stable reason test with context sampling; conditional/screened effects.
- M2 (discovery): ranked CI + PC skeleton; graph orientation; hooks for SMT/Prolog.
- M3 (explanations): minimal repair and chain narration; per-world proofs.
- M4 (identification): backdoor/frontdoor utilities with surgery; docs and tutorials.

## Open questions

- Exact definition of ranked CI: is symmetric Δτ criterion sufficient, or should we use a τ-difference-of-differences test? Iterate based on empirical behavior.
- Context enumeration vs sampling: how to guarantee “for all contexts” practically; prioritize SMT counterexample search for robustness.
- Strength metrics: report boolean + minimal margin across contexts; avoid overinterpreting magnitudes near PRACTICAL_INFINITY.
- Backend selection policy: define size thresholds and timeouts for switching from heuristics to CP-SAT/MaxSAT/SMT/ASP; add telemetry/logging to inform defaults.

---

This design stays faithful to Section 7’s spirit—causation as stable reasons—while delivering practical, SCM-like ergonomics using the existing Ranking stack. It enables discovery, explanations, and identification without inventing a parallel modeling system.
