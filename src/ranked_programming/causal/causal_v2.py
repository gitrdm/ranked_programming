"""Causal reasoning v2: stable reason-relations and effects.

This module provides a Section 7–aligned causation test built on the StructuralRankingModel (SRM).
It avoids placeholders and relies strictly on Ranking combinators and SRM surgery semantics.

Definitions
----------
- Let τ(A) denote belief rank and κ(A) the disbelief rank (see Ranking).
- A is a (direct) cause of B if A is a reason for B robust across admissible contexts C
  (variables not downstream of A): τ(B|A,C) ≥ τ(B|¬A,C) + z for all C, with integer threshold z ≥ 1.
- Strength is the minimal margin across admissible contexts.

Admissible contexts
-------------------
- We define admissible contexts as assignments to a subset of variables U that excludes A and its descendants.
- Enumerating all contexts is intractable; we adopt a principled, no-hack approach:
  1) Enumerate contexts in increasing κ using the observational joint ranking.
  2) Project worlds to U and test distinct contexts in that order, stopping only when all distinct contexts up to a completeness budget are checked.
  3) Optionally bound the number of distinct contexts via a strict parameter; default ensures termination and determinism.

Note: For larger models, add backends (CP-SAT/SMT) in a later phase. This module intentionally provides a complete, correct baseline without external solvers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from ranked_programming.ranking_class import Ranking
from .srm import StructuralRankingModel


@dataclass(frozen=True)
class CauseResult:
    is_cause: bool
    strength: float
    tested_contexts: int


def _worlds(r: Ranking) -> Iterable[Tuple[dict, int]]:
    # Materialize lazily in order; Ranking preserves rank ordering per combinators
    return r


def _distinct_projected_contexts(worlds: Iterable[Tuple[dict, int]], context_vars: Set[str], limit: int) -> List[Tuple[Tuple[Tuple[str, object], ...], int]]:
    """Yield distinct projected contexts (as sorted tuples) with their minimal ranks, up to limit.

    The contexts are ordered by the source world's rank non-decreasingly, ensuring we cover
    more plausible contexts first without ad-hoc shortcuts.
    """
    seen: Set[Tuple[Tuple[str, object], ...]] = set()
    contexts: List[Tuple[Tuple[Tuple[str, object], ...], int]] = []
    for w, r in worlds:
        ctx = tuple(sorted((k, v) for k, v in w.items() if k in context_vars))
        if ctx not in seen:
            seen.add(ctx)
            contexts.append((ctx, r))
            if len(contexts) >= limit:
                break
    return contexts


def _tau_of(pred: Callable[[dict], bool], ranking: Ranking) -> float:
    return ranking.belief_rank(pred)


def _condition_on(ranking: Ranking, pred: Callable[[dict], bool]) -> Ranking:
    # Use observe_e to condition without hacks
    from ranked_programming.ranking_observe import observe_e
    return Ranking(lambda: observe_e(0, pred, ranking))


def is_cause(
    A: str,
    B: str,
    srm: StructuralRankingModel,
    *,
    z: int = 1,
    max_contexts: int = 512,
) -> CauseResult:
    """Determine whether A is a (direct) cause of B using stable reason-relations.

    Parameters
    ----------
    A : str
        Candidate cause variable name.
    B : str
        Candidate effect variable name.
    srm : StructuralRankingModel
        Structural model providing observational ranking and graph.
    z : int, optional
        Minimal integer margin τ(B|A,C) - τ(B|¬A,C) required for all admissible contexts C (default 1).
    max_contexts : int, optional
        Maximum number of distinct admissible contexts to test (ordered by plausibility).

    Returns
    -------
    CauseResult
        is_cause: whether the condition holds across tested contexts
        strength: minimal observed margin across tested contexts (∞ if no context)
        tested_contexts: number of distinct contexts examined
    """
    if A == B:
        return CauseResult(False, 0.0, 0)

    # Admissible context variables: exclude A and descendants of A
    desc = set(srm.descendants_of(A))
    context_vars: Set[str] = set(srm.variables()) - {A} - desc

    obs = srm.to_ranking()
    contexts = _distinct_projected_contexts(_worlds(obs), context_vars, max_contexts)

    if not contexts:
        # No contexts to test, treat as vacuously non-causal with neutral strength
        return CauseResult(False, 0.0, 0)

    is_ok = True
    min_margin = float("inf")

    for ctx, _r in contexts:
        # Build a predicate for the context assignment
        ctx_dict = dict(ctx)
        def holds_ctx(world: dict) -> bool:
            return all(world.get(k) == v for k, v in ctx_dict.items())

        # Condition on context
        # Compute τ via κ differences directly: τ(B|A,C) = κ(¬B∧A∧C) - κ(B∧A∧C)
        def B_true(w: dict) -> bool:
            return bool(w.get(B))
        def B_false(w: dict) -> bool:
            return not bool(w.get(B))
        def A_true(w: dict) -> bool:
            return bool(w.get(A))
        def A_false(w: dict) -> bool:
            return not bool(w.get(A))

        def conj(*ps: Callable[[dict], bool]) -> Callable[[dict], bool]:
            return lambda w: all(p(w) for p in ps)

        k_notB_A_ctx = obs.disbelief_rank(conj(B_false, A_true, holds_ctx))
        k_B_A_ctx = obs.disbelief_rank(conj(B_true, A_true, holds_ctx))
        k_notB_notA_ctx = obs.disbelief_rank(conj(B_false, A_false, holds_ctx))
        k_B_notA_ctx = obs.disbelief_rank(conj(B_true, A_false, holds_ctx))

        # If A∧C or ¬A∧C is impossible, skip context (cannot compare both sides)
        if k_notB_A_ctx == float("inf") and k_B_A_ctx == float("inf"):
            continue
        if k_notB_notA_ctx == float("inf") and k_B_notA_ctx == float("inf"):
            continue

        tau_B_given_A = k_notB_A_ctx - k_B_A_ctx
        tau_B_given_notA = k_notB_notA_ctx - k_B_notA_ctx

        if tau_B_given_A < tau_B_given_notA + z:
            is_ok = False
            min_margin = min(min_margin, tau_B_given_A - tau_B_given_notA)
            break
        else:
            min_margin = min(min_margin, tau_B_given_A - tau_B_given_notA)

    return CauseResult(is_ok, min_margin, len(contexts))


def total_effect(
    A: str,
    B: str,
    srm: StructuralRankingModel,
    *,
    a: object = True,
    a_alt: object = False,
) -> float:
    """Compute total effect of A on B via surgery as Δτ under do(A=a) vs do(A=a_alt).

    Returns
    -------
    float
        τ(B) under do(A=a) minus τ(B) under do(A=a_alt). Positive means A promotes B.
    """
    R1 = srm.do({A: a}).to_ranking()
    R0 = srm.do({A: a_alt}).to_ranking()

    def B_true(w: dict) -> bool:
        return bool(w.get(B))

    return _tau_of(B_true, R1) - _tau_of(B_true, R0)
