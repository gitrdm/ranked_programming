"""Identification utilities for ranked causal inference (M4).

This module implements rank-analog backdoor and frontdoor utilities on SRM DAGs.

Principles
----------
- Use SRM's directed edges (parents->child) for path logic; no external graph lib.
- Use exact d-separation rules to test backdoor admissibility (block all backdoor paths).
- Effects under adjustment use a min-plus aggregation consistent with ranking semantics:
  κ_adj(A) = min_{z in Z} [ κ(A ∧ z) + κ_obs(z) ] - min_{z in Z} κ_obs(z)
  and τ_adj(B) = κ_adj(¬B) - κ_adj(B).
- Frontdoor estimate uses mediator aggregation:
  κ_fd(B | do(A=a)) = min_m [ κ(B | do(M=m)) + κ(M=m | do(A=a)) ] - min_m κ(M=m | do(A=a)).

These combine interventional components via surgery and weigh contexts by observational/interventional plausibility using rank addition, avoiding placeholders.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ranked_programming.ranking_class import Ranking
from .srm import StructuralRankingModel


def _parents(srm: StructuralRankingModel, x: str) -> Tuple[str, ...]:
    return srm.parents_of(x)


def _children(srm: StructuralRankingModel, x: str) -> Tuple[str, ...]:
    return srm.children_of(x)


def _descendants(srm: StructuralRankingModel, x: str) -> Set[str]:
    return set(srm.descendants_of(x))


def _is_collider_on_path(srm: StructuralRankingModel, prev: str, node: str, nxt: str) -> bool:
    # node is a collider if both edges point into node: prev -> node <- nxt
    return (prev in _parents(srm, node)) and (nxt in _parents(srm, node))


def _is_non_collider_on_path(srm: StructuralRankingModel, prev: str, node: str, nxt: str) -> bool:
    return not _is_collider_on_path(srm, prev, node, nxt)


def _simple_paths(srm: StructuralRankingModel, src: str, dst: str, limit: int = 1000) -> List[List[str]]:
    paths: List[List[str]] = []
    from collections import deque
    dq = deque([[src]])
    visited_on_path: Set[Tuple[str, ...]] = set()
    while dq and len(paths) < limit:
        p = dq.popleft()
        last = p[-1]
        if last == dst:
            paths.append(p)
            continue
        # neighbors in undirected sense: parents ∪ children
        neighbors = set(_parents(srm, last)) | set(_children(srm, last))
        for nb in neighbors:
            if nb in p:
                continue
            np = p + [nb]
            key = tuple(np)
            if key in visited_on_path:
                continue
            visited_on_path.add(key)
            dq.append(np)
    return paths


def _path_is_backdoor(srm: StructuralRankingModel, A: str, path: List[str]) -> bool:
    # Backdoor path must start with an arrow into A.
    if len(path) < 2 or path[0] != A:
        return False
    first = path[1]
    return A in _children(srm, first)  # first -> A


def _active_given_Z(srm: StructuralRankingModel, path: List[str], Z: Set[str]) -> bool:
    # d-separation: path active iff for every non-collider node, it is not in Z;
    # and for every collider node, collider or a descendant of it is in Z.
    for i in range(1, len(path) - 1):
        prev, node, nxt = path[i - 1], path[i], path[i + 1]
        if _is_collider_on_path(srm, prev, node, nxt):
            # require collider or a descendant in Z to activate
            if node not in Z:
                desc = _descendants(srm, node)
                if not (desc & Z):
                    return False
        else:
            # non-collider must not be in Z
            if node in Z:
                return False
    return True


def is_backdoor_admissible(
    A: str,
    B: str,
    Z: Sequence[str],
    srm: StructuralRankingModel,
) -> bool:
    """Check the backdoor criterion for Z between A and B on the SRM DAG.

    Conditions
    ----------
    - No member of Z is a descendant of A.
    - Z blocks every backdoor path from A to B (paths that start with an arrow into A) under d-separation.
    """
    Zs = set(Z)
    if _descendants(srm, A) & Zs:
        return False
    for p in _simple_paths(srm, A, B):
        if _path_is_backdoor(srm, A, p) and _active_given_Z(srm, p, Zs):
            return False
    return True


def _projected_contexts(r: Ranking, vars: Sequence[str], limit: int = 512) -> List[Tuple[Tuple[Tuple[str, object], ...], int]]:
    seen: Set[Tuple[Tuple[str, object], ...]] = set()
    contexts: List[Tuple[Tuple[Tuple[str, object], ...], int]] = []
    for w, rk in r:
        ctx = tuple(sorted((k, w[k]) for k in vars if k in w))
        if ctx not in seen:
            seen.add(ctx)
            contexts.append((ctx, rk))
            if len(contexts) >= limit:
                break
    return contexts


def _kappa_of(pred: Callable[[dict], bool], r: Ranking) -> float:
    return r.disbelief_rank(pred)


def _conj(*ps: Callable[[dict], bool]) -> Callable[[dict], bool]:
    return lambda w: all(p(w) for p in ps)


def _is_true(var: str) -> Callable[[dict], bool]:
    return lambda w: bool(w.get(var))


def _is_false(var: str) -> Callable[[dict], bool]:
    return lambda w: not bool(w.get(var))


def _holds(assign: Dict[str, object]) -> Callable[[dict], bool]:
    return lambda w: all(w.get(k) == v for k, v in assign.items())


def _min_plus_marginal(
    r: Ranking,
    contexts: List[Tuple[Tuple[Tuple[str, object], ...], int]],
    pred: Callable[[dict], bool],
) -> float:
    # κ*(pred) = min_z [ κ(pred ∧ z) + κ(z) ] - min_z κ(z)
    if not contexts:
        return r.disbelief_rank(pred)
    ks_z = []
    ks_pred_z = []
    for ctx, _rk in contexts:
        ctxd = dict(ctx)
        z_pred = _holds(ctxd)
        ks_z.append(r.disbelief_rank(z_pred))
        ks_pred_z.append(r.disbelief_rank(_conj(pred, z_pred)))
    base = min(ks_z)
    agg = min(kp + kz for kp, kz in zip(ks_pred_z, ks_z))
    return agg - base


def backdoor_adjusted_effect(
    A: str,
    B: str,
    Z: Sequence[str],
    srm: StructuralRankingModel,
    *,
    a: object = True,
    a_alt: object = False,
) -> float:
    """Backdoor-adjusted total effect using rank min-plus aggregation.

    Computes τ_adj(B) under do(A=a) and do(A=a_alt) by aggregating over Z contexts
    weighted by observational plausibility κ_obs(Z=z).
    Returns τ_adj(B|do(a)) - τ_adj(B|do(a_alt)).
    """
    obs = srm.to_ranking()
    Z_ctxs = _projected_contexts(obs, Z)

    def tau_adj_for(a_val: object) -> float:
        R_do = srm.do({A: a_val}).to_ranking()
        k_B = _min_plus_marginal(R_do, Z_ctxs, _is_true(B))
        k_notB = _min_plus_marginal(R_do, Z_ctxs, _is_false(B))
        return k_notB - k_B

    return tau_adj_for(a) - tau_adj_for(a_alt)


def is_frontdoor_applicable(
    A: str,
    M: str,
    B: str,
    srm: StructuralRankingModel,
) -> bool:
    """Check simple frontdoor applicability conditions on SRM DAG.

    Checks (sufficient, not necessary):
    - All directed paths from A to B pass through M (no direct A->B or via other intermediates without M).
    - There is no unblocked backdoor path from A to M with Z = ∅.
    - All backdoor paths from M to B are blocked by Z = {A}.
    """
    # A->B without M?
    # If any child path from A reaches B without M, fail.
    def reaches_without_M(src: str, dst: str, forbid: str) -> bool:
        # DFS along directed edges only
        stack = [src]
        visited = set()
        while stack:
            u = stack.pop()
            if u == forbid:
                continue
            if u == dst and u != src:
                return True
            for c in _children(srm, u):
                if c not in visited:
                    visited.add(c)
                    stack.append(c)
        return False

    if reaches_without_M(A, B, M):
        return False

    # No unblocked backdoor path A~M with Z=∅
    if not is_backdoor_admissible(A, M, [], srm):
        return False

    # Backdoor paths from M to B blocked by {A}
    if not is_backdoor_admissible(M, B, [A], srm):
        return False

    return True


def frontdoor_effect(
    A: str,
    M: str,
    B: str,
    srm: StructuralRankingModel,
    *,
    a: object = True,
    a_alt: object = False,
) -> float:
    """Frontdoor effect estimate via mediator aggregation (rank analog).

    τ_fd(B|do(A=a)) := κ_fd(¬B|do(A=a)) - κ_fd(B|do(A=a)) with
        κ_fd(X|do(A=a)) = min_m [ κ_do(M=m)(X) + κ_do(A=a)(M=m) ] - min_m κ_do(A=a)(M=m)
    Returns τ_fd(B|do(a)) - τ_fd(B|do(a_alt)).
    """
    def tau_fd_for(a_val: object) -> float:
        R_doA = srm.do({A: a_val}).to_ranking()
        # enumerate mediator contexts from do(A=a)
        M_ctxs = _projected_contexts(R_doA, [M])
        def k_fd(pred: Callable[[dict], bool]) -> float:
            if not M_ctxs:
                return srm.do({A: a_val}).to_ranking().disbelief_rank(pred)
            ks_m = []
            ks_pred_m = []
            for ctx, _rk in M_ctxs:
                m_assign = dict(ctx)
                R_doM = srm.do(m_assign).to_ranking()
                ks_m.append(R_doA.disbelief_rank(_holds(m_assign)))
                ks_pred_m.append(R_doM.disbelief_rank(pred))
            base = min(ks_m)
            agg = min(kp + km for kp, km in zip(ks_pred_m, ks_m))
            return agg - base
        k_B = k_fd(_is_true(B))
        k_notB = k_fd(_is_false(B))
        return k_notB - k_B
    return tau_fd_for(a) - tau_fd_for(a_alt)
