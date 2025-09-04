"""Ranked PC: conditional independence testing and PC skeleton for ranks.

This module provides a ranked conditional independence predicate and a PC-style
skeleton discovery algorithm using the Ranking/SRM semantics.

CI predicate (ranked)
---------------------
We define CI(X, Y | Z) to hold if for all admissible contexts over Z (assignments
projected from the observational joint ranking), both of the following are within
an absolute tolerance epsilon::

    |τ(Y | X, Z=z) - τ(Y | Z=z)| ≤ ε
    |τ(X | Y, Z=z) - τ(X | Z=z)| ≤ ε

Contexts are enumerated in non-decreasing κ (plausibility) order and deduplicated
by projection to Z; up to ``max_contexts`` distinct contexts are checked.

PC skeleton
-----------
The PC algorithm starts with a complete undirected graph and removes an edge X—Y
if CI(X, Y | S) holds for some S subset of adjacents(X)\\{Y} of size k, iterating k
from 0 up to k_max. Separating sets are recorded for potential orientation.

Orientation is limited here to v-structures (X -> Z <- Y) based on separating sets.
Additional Meek rules can be added later.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ranked_programming.ranking_class import Ranking
from .srm import StructuralRankingModel


def _worlds(r: Ranking) -> Iterable[Tuple[dict, int]]:
    return r


def _projected_contexts(r: Ranking, vars: Sequence[str], limit: int) -> List[Tuple[Tuple[Tuple[str, object], ...], int]]:
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


def _tau(pred: Callable[[dict], bool], r: Ranking) -> float:
    return r.belief_rank(pred)


def _condition(r: Ranking, pred: Callable[[dict], bool]) -> Ranking:
    # Hard conditioning: keep only worlds satisfying pred
    from ranked_programming.ranking_observe import observe
    return Ranking(lambda: observe(pred, r))


def ranked_ci(
    X: str,
    Y: str,
    Z: Sequence[str],
    srm: StructuralRankingModel,
    *,
    epsilon: float = 0.0,
    max_contexts: int = 256,
) -> bool:
    """Ranked conditional independence test CI(X, Y | Z) with symmetry and ε tolerance.

    Parameters
    ----------
    X, Y : str
        Variable names under test.
    Z : Sequence[str]
        Conditioning set variable names.
    srm : StructuralRankingModel
        Source model to produce observational ranking.
    epsilon : float, optional
        Tolerance threshold for τ deviations (default 0.0).
    max_contexts : int, optional
        Maximum number of distinct Z-contexts to test, ordered by plausibility.

    Returns
    -------
    bool
        True if CI holds across tested contexts, False on first violation.
    """
    obs = srm.to_ranking()
    contexts = _projected_contexts(obs, Z, max_contexts)

    def is_true(var: str):
        return lambda w: bool(w.get(var))

    iter_contexts = contexts if contexts else [(tuple(), 0)]
    for ctx, _ in iter_contexts:
        C = dict(ctx)
        def holds_ctx(w: dict) -> bool:
            return all(w.get(k) == v for k, v in C.items())

        R_ctx = _condition(obs, holds_ctx) if ctx else obs
        if not R_ctx:
            continue

        R_ctx_X = _condition(R_ctx, is_true(X))
        R_ctx_notX = _condition(R_ctx, lambda w: not bool(w.get(X)))
        R_ctx_Y = _condition(R_ctx, is_true(Y))
        R_ctx_notY = _condition(R_ctx, lambda w: not bool(w.get(Y)))

        # Skip contexts where X or Y is impossible under C
        if not R_ctx_X or not R_ctx_notX or not R_ctx_Y or not R_ctx_notY:
            continue

        dY = abs(_tau(is_true(Y), R_ctx_X) - _tau(is_true(Y), R_ctx))
        dX = abs(_tau(is_true(X), R_ctx_Y) - _tau(is_true(X), R_ctx))

        if dX > epsilon or dY > epsilon:
            return False

    return True


@dataclass
class PCResult:
    nodes: List[str]
    edges: Set[Tuple[str, str]]  # undirected edges as sorted pairs
    sepsets: Dict[Tuple[str, str], Set[str]]
    oriented: Set[Tuple[str, str]]  # directed edges X->Y


def pc_skeleton(
    vars: Sequence[str],
    srm: StructuralRankingModel,
    *,
    k_max: int = 2,
    epsilon: float = 0.0,
    max_contexts: int = 128,
) -> PCResult:
    """Discover PC skeleton using ranked CI.

    Parameters
    ----------
    vars : Sequence[str]
        Variable names to include.
    srm : StructuralRankingModel
        Model for CI queries.
    k_max : int, optional
        Maximum conditioning set size (default 2).
    epsilon : float, optional
        CI tolerance (default 0.0).
    max_contexts : int, optional
        Context limit per CI test.

    Returns
    -------
    PCResult
        Undirected skeleton, separating sets, and oriented v-structures.
    """
    nodes = list(vars)
    edges: Set[Tuple[str, str]] = set()
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            key: Tuple[str, str] = (a, b) if a < b else (b, a)
            edges.add(key)
    sepsets: Dict[Tuple[str, str], Set[str]] = {}

    # adjacency as dynamic neighbors
    def neighbors(x: str) -> Set[str]:
        return {v for (u, v) in edges if u == x} | {u for (u, v) in edges if v == x}

    # Remove edges based on CI
    k = 0
    while k <= k_max:
        removed_any = False
        for a, b in list(edges):
            # Consider separating sets from neighbors of a (excluding b), then b (excluding a)
            adja = list(neighbors(a) - {b})
            adjb = list(neighbors(b) - {a})
            if len(adja) >= k:
                for S in combinations(adja, k):
                    if ranked_ci(a, b, list(S), srm, epsilon=epsilon, max_contexts=max_contexts):
                        key: Tuple[str, str] = (a, b) if a < b else (b, a)
                        edges.remove(key)
                        sepsets[key] = set(S)
                        removed_any = True
                        break
                if removed_any:
                    continue
            if len(adjb) >= k:
                for S in combinations(adjb, k):
                    if ranked_ci(a, b, list(S), srm, epsilon=epsilon, max_contexts=max_contexts):
                        key = (a, b) if a < b else (b, a)
                        edges.remove(key)
                        sepsets[key] = set(S)
                        removed_any = True
                        break
            # no need to try more S once removed
        if not removed_any:
            k += 1

    # Orient v-structures: a - z - b with a and b non-adjacent and z not in sepset(a,b)
    oriented: Set[Tuple[str, str]] = set()
    for z in nodes:
        nbrs = [n for n in neighbors(z)]
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                a, b = nbrs[i], nbrs[j]
                key: Tuple[str, str] = (a, b) if a < b else (b, a)
                if key in edges:
                    continue  # still adjacent; not a v-structure
                sep = sepsets.get(key, set())
                if z not in sep:
                    oriented.add((a, z))
                    oriented.add((b, z))

    return PCResult(nodes, edges, sepsets, oriented)
