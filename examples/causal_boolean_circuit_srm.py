#!/usr/bin/env python3
"""
SRM-based causal analysis of a small boolean circuit.

What this shows (Section 7 framework)
- StructuralRankingModel (SRM) of a NOT → OR → OR circuit with independent gate faults
- Causation: is_cause(A, B) using stable reason-relations on an SRM
- Effects: total_effect via surgery do(A=a)
- Discovery: ranked_ci and PC skeleton orientation over faults and internal wires
- Explanations: minimal repair sets to ensure desired output

Scenarios
- Screened (i3=True): the final OR input is True and “shields” the output; only the last gate fault can cause failure
- Unshielded (i3=False): upstream faults can also cause failure

Author: Ranked Programming Library
Date: September 2025
"""
from __future__ import annotations

from typing import List

from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.causal import (
    StructuralRankingModel,
    Variable,
    is_cause,
    total_effect,
    ranked_ci,
    pc_skeleton,
    MinimalRepairSolver,
    RepairSearchConfig,
    GreedySeparatingSetFinder,
    SeparatingSetRequest,
    root_cause_chain,
)


def build_circuit_srm(i1: bool, i2: bool, i3: bool) -> StructuralRankingModel:
    """Build an SRM for a simple boolean circuit with gate faults.

    Variables
    ---------
    - N_fault, O1_fault, O2_fault: independent faults (False=normal, True=fault) with rank-1 exceptions
    - L1, L2: internal wires (deterministic)
    - Out: final output
    - Fail: derived failure indicator (¬Out)
    """
    Nf = Variable("N_fault", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    O1f = Variable("O1_fault", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    O2f = Variable("O2_fault", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))

    # Internal wires (deterministic mechanisms)
    L1 = Variable("L1", (False, True), ("N_fault",), lambda nf: (False if nf else (not i1)))
    L2 = Variable("L2", (False, True), ("L1", "O1_fault"), lambda l1, o1f: (False if o1f else (l1 or i2)))
    Out = Variable("Out", (False, True), ("L2", "O2_fault"), lambda l2, o2f: (False if o2f else (l2 or i3)))
    Fail = Variable("Fail", (False, True), ("Out",), lambda out: (not out))

    return StructuralRankingModel([Nf, O1f, O2f, L1, L2, Out, Fail])


def show_causation_and_effects(title: str, srm: StructuralRankingModel):
    print(f"=== {title}: causes and effects ===")
    for gate in ["N_fault", "O1_fault", "O2_fault"]:
        res = is_cause(gate, "Fail", srm, z=1)
        print(f"{gate} → Fail? {res.is_cause} (strength={res.strength}, tested={res.tested_contexts})")

    # Total effect: how much a fault promotes failure (positive ⇒ increases Fail)
    for gate in ["N_fault", "O1_fault", "O2_fault"]:
        tau = total_effect(gate, "Fail", srm, a=True, a_alt=False)
        print(f"Δτ(Fail) under do({gate}=True) vs False: {tau}")
    print()


def show_discovery(title: str, srm: StructuralRankingModel, screened: bool):
    print(f"=== {title}: ranked CI and PC discovery ===")
    # Simple CI: in screened scenario, N_fault ⟂ Fail | {O2_fault}
    ci = ranked_ci("N_fault", "Fail", ["O2_fault"], srm, epsilon=0.0)
    print(f"CI(N_fault, Fail | O2_fault) = {ci}")

    vars: List[str] = ["N_fault", "O1_fault", "O2_fault", "L1", "L2", "Out", "Fail"]
    res = pc_skeleton(vars, srm, k_max=2)
    # Print oriented v-structures only (X→Z←Y)
    if res.oriented:
        oriented_str = ", ".join([f"{a}->{b}" for (a, b) in sorted(res.oriented)])
        print(f"Oriented edges: {oriented_str}")
    else:
        print("No oriented edges (sparse orientation at this k_max).")
    print()


def show_repairs(title: str, srm: StructuralRankingModel):
    print(f"=== {title}: minimal repairs for Out=True ===")
    solver = MinimalRepairSolver()
    # Repairs act on fault variables; setting them to False (no fault) is a repair action
    repairs = solver.repairs(
        srm,
        target="Out",
        desired_value=True,
        candidates=["O2_fault", "O1_fault", "N_fault"],
        repair_values={"O2_fault": False, "O1_fault": False, "N_fault": False},
        config=RepairSearchConfig(max_size=3),
    )
    if repairs:
        print("Minimal repair sets:", [sorted(list(s)) for s in repairs])
    else:
        print("No repairs within size bound.")
    print()


def show_separating_set(title: str, srm: StructuralRankingModel):
    print(f"=== {title}: greedy separating set (toy) ===")
    finder = GreedySeparatingSetFinder()
    req = SeparatingSetRequest("N_fault", "Fail", ["O2_fault", "O1_fault", "L2", "Out"], k_max=2)
    Z = finder.find(req, srm, ranked_ci)
    print(f"Separating set for N_fault–Fail (k≤2): {Z}")
    print()


def show_cp_sat_backends(title: str, srm: StructuralRankingModel):
    print(f"=== {title}: CP-SAT backends (optional) ===")
    try:
        # Import inside to avoid import-time hard dependency
        from ranked_programming.causal import CPSATMinimalRepair, CPSATSeparatingSetFinder  # type: ignore
    except Exception:
        print("OR-Tools not installed; skipping CP-SAT demo.")
        print()
        return

    # CP-SAT minimal repairs
    try:
        expl = CPSATMinimalRepair()
        repairs = expl.repairs(
            srm,
            target="Out",
            desired_value=True,
            candidates=["O2_fault", "O1_fault", "N_fault"],
            repair_values={"O2_fault": False, "O1_fault": False, "N_fault": False},
            max_size=3,
        )
        print("CP-SAT minimal repair sets:", [sorted(list(s)) for s in repairs] or "none")
    except Exception as e:
        print(f"CP-SAT minimal repairs unavailable: {e}")

    # CP-SAT separating set
    try:
        sat_finder = CPSATSeparatingSetFinder()
        req = SeparatingSetRequest("N_fault", "Fail", ["O2_fault", "O1_fault", "L2", "Out"], k_max=2)
        Z = sat_finder.find(req, srm, ranked_ci)
        print(f"CP-SAT separating set for N_fault–Fail (k≤2): {Z}")
    except Exception as e:
        print(f"CP-SAT separating set unavailable: {e}")
    print()


def show_root_cause_graph(title: str, srm: StructuralRankingModel):
    print(f"=== {title}: root cause graph (paths to Fail) ===")
    causes = []
    for gate in ["N_fault", "O1_fault", "O2_fault"]:
        res = is_cause(gate, "Fail", srm, z=1)
        if res.is_cause:
            causes.append(gate)
    if not causes:
        print("No root causes detected under z=1.")
        print()
        return
    chains = root_cause_chain(srm, causes, target="Fail")
    edges = set()
    for path in chains:
        for u, v in zip(path, path[1:]):
            edges.add((u, v))
    print(f"Root causes: {sorted(causes)}")
    if edges:
        edge_list = ", ".join([f"{a}->{b}" for (a, b) in sorted(edges)])
        print(f"Edges: {edge_list}")
        # Optional DOT snippet for visualization
        print("DOT:")
        print("digraph RC {" )
        for a, b in sorted(edges):
            print(f"  {a} -> {b};")
        print("}")
    else:
        print("No edges (causes are the target or disconnected).")
    print()


def main():
    print("Causal Analysis of Boolean Circuit Faults — SRM Edition")
    print("=" * 60)
    print()

    # Screened scenario: i3=True shields output from upstream faults
    srm_screened = build_circuit_srm(i1=False, i2=False, i3=True)
    show_causation_and_effects("Screened (i3=True)", srm_screened)
    show_discovery("Screened", srm_screened, screened=True)
    show_repairs("Screened", srm_screened)
    show_separating_set("Screened", srm_screened)
    show_cp_sat_backends("Screened", srm_screened)
    show_root_cause_graph("Screened", srm_screened)

    # Unshielded scenario: i3=False exposes influence of upstream faults
    srm_unshielded = build_circuit_srm(i1=False, i2=False, i3=False)
    show_causation_and_effects("Unshielded (i3=False)", srm_unshielded)
    show_discovery("Unshielded", srm_unshielded, screened=False)
    show_repairs("Unshielded", srm_unshielded)
    show_separating_set("Unshielded", srm_unshielded)
    show_cp_sat_backends("Unshielded", srm_unshielded)
    show_root_cause_graph("Unshielded", srm_unshielded)

    print("Done.")


if __name__ == "__main__":
    main()
