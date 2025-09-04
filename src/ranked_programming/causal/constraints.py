"""Pluggable solver interfaces and greedy baselines (M5).

This module defines small strategy classes for combinatorial tasks used in causal routines,
with Sphinx-ready docstrings and concrete, dependency-free greedy implementations.

Strategies
----------
- SeparatingSetFinder: find a conditioning set Z ⊆ candidates (|Z| ≤ k_max) s.t. CI(X,Y|Z) holds.
- MinimalRepairStrategy: find minimal repair sets that fix a target under surgery.
- CounterexampleFinder: search for a context assignment violating a provided inequality.

The default implementations are exact enumeration (greedy) suitable for small problems and as a
correctness reference. Heavier backends (CP-SAT/MaxSAT/SMT/ASP) can be added later behind the same API.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .srm import StructuralRankingModel
from .explanations import MinimalRepairSolver, RepairSearchConfig


@dataclass(frozen=True)
class SeparatingSetRequest:
    """Request to find a separating set.

    Attributes
    ----------
    x : str
        Variable name X.
    y : str
        Variable name Y.
    candidates : Sequence[str]
        Candidate variables that may be included in Z.
    k_max : int
        Maximum conditioning set size.
    """
    x: str
    y: str
    candidates: Sequence[str]
    k_max: int = 3


class SeparatingSetFinder:
    """Abstract base for separating set searchers."""

    def find(
        self,
        req: SeparatingSetRequest,
        srm: StructuralRankingModel,
        ci_predicate: Callable[[str, str, Sequence[str], StructuralRankingModel], bool],
    ) -> Optional[Set[str]]:
        """Return a Z where CI(X,Y|Z) holds, or None if not found up to k_max.

        Parameters
        ----------
        req : SeparatingSetRequest
            Search request specifying (X, Y, candidates, k_max).
        srm : StructuralRankingModel
            The structural model (may be used by the predicate).
        ci_predicate : callable
            Function returning True if CI(X,Y|Z) holds under the given SRM.
        """
        raise NotImplementedError


class GreedySeparatingSetFinder(SeparatingSetFinder):
    """Brute-force search over subsets up to k_max in increasing size order."""

    def find(
        self,
        req: SeparatingSetRequest,
        srm: StructuralRankingModel,
        ci_predicate: Callable[[str, str, Sequence[str], StructuralRankingModel], bool],
    ) -> Optional[Set[str]]:
        cand = list(dict.fromkeys(req.candidates))
        for k in range(0, min(req.k_max, len(cand)) + 1):
            for Z in combinations(cand, k):
                if ci_predicate(req.x, req.y, list(Z), srm):
                    return set(Z)
        return None


class MinimalRepairStrategy:
    """Abstract strategy for minimal repair computation."""

    def repairs(
        self,
        srm: StructuralRankingModel,
        target: str,
        desired_value: object,
        candidates: Sequence[str],
        *,
        repair_values: Optional[Dict[str, object]] = None,
        max_size: Optional[int] = None,
    ) -> List[Set[str]]:
        """Return minimal repair sets of the smallest size achieving the target."""
        raise NotImplementedError


class EnumerationMinimalRepair(MinimalRepairStrategy):
    """Adapter using the existing MinimalRepairSolver (exact enumeration)."""

    def __init__(self) -> None:
        self._solver = MinimalRepairSolver()

    def repairs(
        self,
        srm: StructuralRankingModel,
        target: str,
        desired_value: object,
        candidates: Sequence[str],
        *,
        repair_values: Optional[Dict[str, object]] = None,
        max_size: Optional[int] = None,
    ) -> List[Set[str]]:
        cfg = RepairSearchConfig(max_size=max_size)
        return self._solver.repairs(
            srm,
            target,
            desired_value,
            candidates,
            repair_values=repair_values,
            config=cfg,
        )


@dataclass(frozen=True)
class Inequality:
    """Boolean-valued inequality over assignments from an SRM ranking.

    The predicate should return True when the inequality is satisfied, False when violated.
    Counterexample search aims to find an assignment where it returns False.
    """
    predicate: Callable[[dict], bool]


class CounterexampleFinder:
    """Search for a world assignment violating an inequality."""

    def find_violation(
        self,
        srm: StructuralRankingModel,
        ineq: Inequality,
        *,
        max_worlds: int = 512,
    ) -> Optional[dict]:
        """Return an assignment that violates the inequality, or None if none among top worlds.

        Parameters
        ----------
        srm : StructuralRankingModel
            The model generating observational worlds (by plausibility).
        ineq : Inequality
            Inequality predicate to test per-world.
        max_worlds : int
            Search budget across top-ranked worlds.
        """
        R = srm.to_ranking()
        count = 0
        for w, _k in R:
            if not ineq.predicate(w):
                return w
            count += 1
            if count >= max_worlds:
                break
        return None


# ----- Optional OR-Tools CP-SAT backends -----

def _has_ortools() -> bool:
    try:
        import ortools  # type: ignore
        return True
    except Exception:
        return False


class CPSATMinimalRepair(MinimalRepairStrategy):
    """CP-SAT-based minimal repair search with outer-loop validation and no-good cuts.

    Requires `ortools` to be installed. Minimizes repair set size and enumerates all
    minimal solutions of that cardinality that satisfy the repair predicate under surgery.
    """

    def __init__(self) -> None:
        if not _has_ortools():
            raise ImportError("ortools is required for CPSATMinimalRepair")
        from ortools.sat.python import cp_model  # type: ignore
        self._cp_model = cp_model

    def repairs(
        self,
        srm: StructuralRankingModel,
        target: str,
        desired_value: object,
        candidates: Sequence[str],
        *,
        repair_values: Optional[Dict[str, object]] = None,
        max_size: Optional[int] = None,
    ) -> List[Set[str]]:
        from ortools.sat.python import cp_model  # type: ignore
        cand = list(dict.fromkeys(candidates))
        n = len(cand)
        if n == 0:
            return []

        def is_fixed(subset: Set[str]) -> bool:
            do_map: Dict[str, object] = {}
            for v in subset:
                do_map[v] = (repair_values[v] if repair_values and v in repair_values else desired_value)
            R = srm.do(do_map).to_ranking()
            def t_is_v(w: dict) -> bool:
                return w.get(target) == desired_value
            def t_not_v(w: dict) -> bool:
                return w.get(target) != desired_value
            k_ok = R.disbelief_rank(t_is_v)
            k_bad = R.disbelief_rank(t_not_v)
            return k_ok < k_bad

        model = cp_model.CpModel()
        bvars = [model.NewBoolVar(f"b_{i}") for i in range(n)]
        # Enforce at least one repair (empty set rarely fixes anything)
        model.Add(sum(bvars) >= 1)
        if max_size is not None:
            model.Add(sum(bvars) <= int(max_size))
        # Objective: minimize cardinality
        model.Minimize(sum(bvars))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0

        found: List[Set[str]] = []
        current_k: Optional[int] = None
        # No-good cuts to exclude invalid subsets and to enumerate distinct solutions of same size
        while True:
            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break
            sel = {cand[i] for i in range(n) if solver.Value(bvars[i]) == 1}
            k = sum(1 for i in range(n) if solver.Value(bvars[i]) == 1)
            if current_k is None:
                current_k = k
            # If solver proposes larger than current_k (after blocking), stop if we already collected some
            if found and k > current_k:
                break
            if is_fixed(sel):
                found.append(set(sel))
                # Block this specific solution and continue to enumerate others of same cardinality
                model.Add(sum(bvars[i] for i in range(n) if cand[i] in sel) <= k - 1)
                continue
            # Not fixed: forbid this exact subset and continue
            pos = [i for i in range(n) if cand[i] in sel]
            neg = [i for i in range(n) if cand[i] not in sel]
            model.Add(sum(bvars[i] for i in pos) <= k - 1)
        return found


class CPSATSeparatingSetFinder(SeparatingSetFinder):
    """CP-SAT-guided search for separating sets with outer-loop CI validation.

    Minimizes the size of Z; uses no-good cuts to exclude Z where CI fails.
    Stops at the first valid minimal-cardinality separating set.
    """

    def __init__(self) -> None:
        if not _has_ortools():
            raise ImportError("ortools is required for CPSATSeparatingSetFinder")
        from ortools.sat.python import cp_model  # type: ignore
        self._cp_model = cp_model

    def find(
        self,
        req: SeparatingSetRequest,
        srm: StructuralRankingModel,
        ci_predicate: Callable[[str, str, Sequence[str], StructuralRankingModel], bool],
    ) -> Optional[Set[str]]:
        from ortools.sat.python import cp_model  # type: ignore
        cand = list(dict.fromkeys(req.candidates))
        n = len(cand)
        if n == 0:
            return set() if ci_predicate(req.x, req.y, [], srm) else None
        model = cp_model.CpModel()
        bvars = [model.NewBoolVar(f"z_{i}") for i in range(n)]
        # Cardinality bound
        model.Add(sum(bvars) >= 0)
        model.Add(sum(bvars) <= min(req.k_max, n))
        model.Minimize(sum(bvars))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0

        # No-good cuts loop
        while True:
            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                return None
            Z = {cand[i] for i in range(n) if solver.Value(bvars[i]) == 1}
            if ci_predicate(req.x, req.y, list(Z), srm):
                return Z
            # Forbid this Z and continue
            k = sum(1 for i in range(n) if solver.Value(bvars[i]) == 1)
            if k == 0:
                # Empty set failed; require at least one variable to be selected.
                model.Add(sum(bvars) >= 1)
            else:
                model.Add(sum(bvars[i] for i in range(n) if cand[i] in Z) <= k - 1)
