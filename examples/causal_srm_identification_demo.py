"""End-to-end causal demo: SRM + identification + constraints (M6 example).

This script builds a small SRM, computes backdoor/frontdoor conditions and effects,
then uses greedy and optional CP-SAT strategies for explanations and separating sets.
"""
from ranked_programming.causal import (
    StructuralRankingModel,
    Variable,
    is_backdoor_admissible,
    backdoor_adjusted_effect,
    is_frontdoor_applicable,
    frontdoor_effect,
    GreedySeparatingSetFinder,
    SeparatingSetRequest,
    EnumerationMinimalRepair,
)
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc


def build_models():
    # Confounded fork: U -> A -> B, and U -> B
    U = Variable("U", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    A = Variable("A", (False, True), ("U",), lambda u: u)
    B = Variable("B", (False, True), ("A", "U"), lambda a, u: (a or u))
    srm_backdoor = StructuralRankingModel([U, A, B])

    # Frontdoor: U -> A, U -> B, A -> M -> B (no direct A->B)
    U2 = Variable("U", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    A2 = Variable("A", (False, True), ("U",), lambda u: u)
    M2 = Variable("M", (False, True), ("A",), lambda a: a)
    B2 = Variable("B", (False, True), ("M", "U"), lambda m, u: (m or u))
    srm_frontdoor = StructuralRankingModel([U2, A2, M2, B2])

    return srm_backdoor, srm_frontdoor


def main():
    srm_bd, srm_fd = build_models()

    print("-- Backdoor demo --")
    admissible = is_backdoor_admissible("A", "B", ["U"], srm_bd)
    print(f"Z={{U}} admissible for A->B: {admissible}")
    tau_bd = backdoor_adjusted_effect("A", "B", ["U"], srm_bd, a=True, a_alt=False)
    print(f"Backdoor-adjusted total effect τ: {tau_bd}")

    print("\n-- Frontdoor demo --")
    applicable = is_frontdoor_applicable("A", "M", "B", srm_fd)
    print(f"Frontdoor applicable via M: {applicable}")
    tau_fd = frontdoor_effect("A", "M", "B", srm_fd, a=True, a_alt=False)
    print(f"Frontdoor effect τ: {tau_fd}")

    print("\n-- Constraints demo (greedy) --")
    # Simple chain for separating set: X->Z->Y
    X = Variable("X", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    Z = Variable("Z", (False, True), ("X",), lambda x: x)
    Y = Variable("Y", (False, True), ("Z",), lambda z: z)
    srm_chain = StructuralRankingModel([X, Z, Y])

    from ranked_programming.causal import ranked_ci
    finder = GreedySeparatingSetFinder()
    Zset = finder.find(SeparatingSetRequest("X", "Y", ["Z"], k_max=1), srm_chain, ranked_ci)
    print(f"Separating set for X–Y: {Zset}")

    print("\n-- Explanation demo (minimal repair) --")
    expl = EnumerationMinimalRepair()
    repairs = expl.repairs(srm_chain, target="Y", desired_value=True, candidates=["Z", "X"], max_size=1)
    print(f"Minimal repairs to achieve Y=True: {repairs}")


if __name__ == "__main__":
    main()
