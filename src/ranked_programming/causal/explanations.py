"""Explanations: minimal repair sets and root-cause chains (Section 7).

This module provides:
- MinimalRepairSolver: find minimal intervention sets that fix a target under surgery.
- root_cause_chain: trace a path from repair variables to the target along the SRM DAG.

Semantics
---------
- Repairs are applied via SRM surgery (``do``). For boolean domains, the default
  repair value is ``True`` (configurable per variable).
- A repair set S fixes target variable T to desired value v if, under ``do(S)``,
  the belief in T=v strictly dominates T!=v: τ(T=v) > 0, equivalently κ(T!=v) > κ(T=v).
- Minimality: enumerate subsets by increasing cardinality and return only those
  sets of minimal size that satisfy the repair condition (no supersets are included).

This baseline uses exact enumeration up to a provided bound; it is complete for
small candidate sets and serves as a correctness reference for later solver backends.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ranked_programming.ranking_class import Ranking
from .srm import StructuralRankingModel


@dataclass(frozen=True)
class RepairSearchConfig:
    max_size: Optional[int] = None  # None = search until first solution size


class MinimalRepairSolver:
    """Find minimal intervention sets that fix a target under surgery.

    Parameters
    ----------
    srm : StructuralRankingModel
        The structural model.
    target : str
        Target variable name to fix.
    desired_value : object
        Desired value for the target (e.g., True for booleans).
    candidates : Sequence[str]
        Variables that can be intervened on (repairs).
    repair_values : Optional[Dict[str, object]]
        Optional explicit values for each candidate; defaults to mapping each to desired_value
        when not provided.
    config : Optional[RepairSearchConfig]
        Search configuration; by default, searches until any solution size is found, then stops.

    Returns
    -------
    List[Set[str]]
        All minimal repair sets of the smallest size that achieve the target.
    """

    def repairs(
        self,
        srm: StructuralRankingModel,
        target: str,
        desired_value: object,
        candidates: Sequence[str],
        *,
        repair_values: Optional[Dict[str, object]] = None,
        config: Optional[RepairSearchConfig] = None,
    ) -> List[Set[str]]:
        cfg = config or RepairSearchConfig()
        cand = list(dict.fromkeys(candidates))  # de-dup, preserve order
        if len(cand) == 0:
            return []
        max_k = cfg.max_size if cfg.max_size is not None else len(cand)

        def is_fixed(model: StructuralRankingModel) -> bool:
            R = model.to_ranking()
            def t_is_v(w: dict) -> bool:
                return w.get(target) == desired_value
            def t_not_v(w: dict) -> bool:
                return w.get(target) != desired_value
            k_ok = R.disbelief_rank(t_is_v)
            k_bad = R.disbelief_rank(t_not_v)
            # Require strict improvement in favor of desired value
            return k_ok < k_bad

        found: List[Set[str]] = []
        for k in range(1, max_k + 1):
            level_solutions: List[Set[str]] = []
            for S in combinations(cand, k):
                # Build intervention map
                do_map: Dict[str, object] = {}
                for v in S:
                    do_map[v] = (repair_values[v] if repair_values and v in repair_values else desired_value)
                model_do = srm.do(do_map)
                if is_fixed(model_do):
                    level_solutions.append(set(S))
            if level_solutions:
                # Return only minimal-size solutions
                # Ensure no supersets within same level by construction; return distinct sets
                distinct = []
                seen = set()
                for s in level_solutions:
                    key = tuple(sorted(s))
                    if key not in seen:
                        seen.add(key)
                        distinct.append(s)
                found.extend(distinct)
                break
        return found


def root_cause_chain(
    srm: StructuralRankingModel,
    repair_set: Sequence[str],
    target: str,
) -> List[List[str]]:
    """Compute root-cause chains from each repair variable to target along SRM DAG.

    Parameters
    ----------
    srm : StructuralRankingModel
        The structural model.
    repair_set : Sequence[str]
        Variables included in the repair set.
    target : str
        The target variable name.

    Returns
    -------
    List[List[str]]
        A list of paths (as variable name lists) from each repair variable to target;
        empty if no path exists for a variable.
    """
    # BFS per repair variable on DAG adjacency
    paths: List[List[str]] = []
    for src in repair_set:
        if src == target:
            paths.append([src])
            continue
        # BFS
        from collections import deque
        q = deque([[src]])
        visited: Set[str] = set([src])
        found_path: Optional[List[str]] = None
        while q:
            p = q.popleft()
            last = p[-1]
            for child in srm.children_of(last):
                if child in visited:
                    continue
                np = p + [child]
                if child == target:
                    found_path = np
                    q.clear()
                    break
                visited.add(child)
                q.append(np)
        if found_path:
            paths.append(found_path)
        else:
            paths.append([])
    return paths
