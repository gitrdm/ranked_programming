"""
Structural Ranking Model (SRM) and surgery-based interventions.

Builds joint Rankings from variable mechanisms using existing Ranking combinators.
Implements do(X=v) by overriding mechanisms and ignoring parents (graph surgery).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, List, Sequence, Tuple

from ranked_programming import Ranking
from ranked_programming.ranking_combinators import rlet_star


@dataclass(frozen=True)
class Variable:
    name: str
    domain: Sequence[Any] | None  # optional; informational for now
    parents: Tuple[str, ...]
    # mechanism: takes parent values in the order of `parents`, returns Ranking-like over values
    mechanism: Callable[..., Any]


class StructuralRankingModel:
    def __init__(self, variables: Sequence[Variable]):
        self._vars: Dict[str, Variable] = {v.name: v for v in variables}
        # Build adjacency and validate parents
        self._adj: Dict[str, List[str]] = {n: [] for n in self._vars.keys()}
        indeg: Dict[str, int] = {n: 0 for n in self._vars.keys()}
        for v in variables:
            for p in v.parents:
                if p not in self._vars:
                    raise ValueError(f"Unknown parent '{p}' for variable '{v.name}'")
                self._adj[p].append(v.name)
                indeg[v.name] += 1
        # Kahn's algorithm for DAG check and topo order
        queue: List[str] = [n for n, d in indeg.items() if d == 0]
        order: List[str] = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for m in self._adj.get(n, []):
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
        if len(order) != len(self._vars):
            raise ValueError("StructuralRankingModel requires a DAG (found cycle)")
        self._order = order

    def variables(self) -> List[str]:
        """Return variable names in a valid topological order.

        Returns
        -------
        list[str]
            Variable names in topological order (parents before children).
        """
        return list(self._order)

    # --- Graph queries ---------------------------------------------------
    def parents_of(self, name: str) -> Tuple[str, ...]:
        """Return direct parents of a variable.

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        tuple[str, ...]
            Parent variable names.
        """
        return self._vars[name].parents

    def children_of(self, name: str) -> Tuple[str, ...]:
        """Return direct children of a variable.

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        tuple[str, ...]
            Children variable names.
        """
        return tuple(self._adj.get(name, ()))

    def ancestors_of(self, name: str) -> Tuple[str, ...]:
        """Return all ancestors of a variable (transitive closure of parents).

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        tuple[str, ...]
            All ancestor variable names (excluding `name`).
        """
        ancestors: set[str] = set()
        stack = list(self._vars[name].parents)
        while stack:
            p = stack.pop()
            if p in ancestors:
                continue
            ancestors.add(p)
            stack.extend(self._vars[p].parents)
        return tuple(sorted(ancestors))

    def descendants_of(self, name: str) -> Tuple[str, ...]:
        """Return all descendants of a variable (transitive closure of children).

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        tuple[str, ...]
            All descendant variable names (excluding `name`).
        """
        descendants: set[str] = set()
        stack = list(self._adj.get(name, ()))
        while stack:
            c = stack.pop()
            if c in descendants:
                continue
            descendants.add(c)
            stack.extend(self._adj.get(c, ()))
        return tuple(sorted(descendants))

    def to_ranking(self) -> Ranking:
        """Compose mechanisms in topological order into a joint Ranking over assignments (dict)."""
        name_to_idx = {n: i for i, n in enumerate(self._order)}

        bindings: List[Tuple[str, object]] = []
        for idx, name in enumerate(self._order):
            v = self._vars[name]
            parent_indices = tuple(name_to_idx[p] for p in v.parents)

            # Build a binding function with arity = idx (number of prior vars)
            def make_binding_fn(arity: int, parents_idx: Tuple[int, ...], mech: Callable[..., Any]):
                # arity matches number of previous bindings; as_ranking will pass a prefix of env of length=arity
                # We need access to all previous values; thus expect arity args and pick parent values by index.
                def binding_fn(*args):
                    # args correspond to values of vars in self._order[:arity] in order
                    parent_vals = tuple(args[i] for i in parents_idx)
                    return mech(*parent_vals)
                # Adjust signature arity by binding a tuple of positional args
                # Python doesn't expose arity directly; as_ranking inspects signature length
                # Using *args preserves flexible arity; however as_ranking infers 1 parameter for *args.
                # Workaround: wrap in a lambda with explicit positional args count equal to arity.
                if arity == 0:
                    return lambda: binding_fn()
                elif arity == 1:
                    return lambda a0: binding_fn(a0)
                elif arity == 2:
                    return lambda a0, a1: binding_fn(a0, a1)
                elif arity == 3:
                    return lambda a0, a1, a2: binding_fn(a0, a1, a2)
                elif arity == 4:
                    return lambda a0, a1, a2, a3: binding_fn(a0, a1, a2, a3)
                elif arity == 5:
                    return lambda a0, a1, a2, a3, a4: binding_fn(a0, a1, a2, a3, a4)
                elif arity == 6:
                    return lambda a0, a1, a2, a3, a4, a5: binding_fn(a0, a1, a2, a3, a4, a5)
                elif arity == 7:
                    return lambda a0, a1, a2, a3, a4, a5, a6: binding_fn(a0, a1, a2, a3, a4, a5, a6)
                elif arity == 8:
                    return lambda a0, a1, a2, a3, a4, a5, a6, a7: binding_fn(a0, a1, a2, a3, a4, a5, a6, a7)
                elif arity == 9:
                    return lambda a0, a1, a2, a3, a4, a5, a6, a7, a8: binding_fn(a0, a1, a2, a3, a4, a5, a6, a7, a8)
                elif arity == 10:
                    return lambda a0, a1, a2, a3, a4, a5, a6, a7, a8, a9: binding_fn(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9)
                elif arity == 11:
                    return lambda a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10: binding_fn(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10)
                elif arity == 12:
                    return lambda a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11: binding_fn(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11)
                else:
                    # Fallback: accept many args; as_ranking will pass only a prefix equal to parameter count.
                    # For large models, we can extend explicit cases as needed.
                    return lambda *aa: binding_fn(*aa)

            bindings.append((name, make_binding_fn(idx, parent_indices, v.mechanism)))

        def build_assignment(*values):
            return {name: values[i] for i, name in enumerate(self._order)}

        return Ranking(lambda: rlet_star(bindings, build_assignment))

    def do(self, interventions: Dict[str, Any]) -> "StructuralRankingModel":
        """Return a new SRM with interventions applied via surgery (override mechanisms)."""
        new_vars: List[Variable] = []
        for name in self._order:
            v = self._vars[name]
            if name in interventions:
                val = interventions[name]
                # Constant mechanism ignoring parents, yielding fixed value at rank 0
                const_mech = (lambda fixed=val: (lambda: Ranking(lambda: [(fixed, 0)])))()
                # Also remove all parents to reflect surgical cut
                new_vars.append(replace(v, parents=(), mechanism=const_mech))
            else:
                new_vars.append(v)
        return StructuralRankingModel(new_vars)
