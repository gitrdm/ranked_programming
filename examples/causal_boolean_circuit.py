#!/usr/bin/env python3
"""
Causal analysis of a small boolean circuit using production APIs.

What this shows
- How to build a ranked model of a simple circuit with independent faults.
- How to ask causal questions with the production `CausalReasoner`:
    - Direct cause checks
    - Counterfactual queries
    - Conditional effects (screening-off)
    - Structure discovery (PC algorithm) over user-defined propositions

Why two scenarios?
- Screened scenario (c=True): the final OR input is True, so the last gate
    "shields" the output from upstream faults. Only the last OR gate fault (O2) can
    cause failure. This demonstrates screening-off and absence of spurious causes.
- Unshielded scenario (c=False): output depends on upstream logic; NOT (N) and the
    first OR gate (O1) can now also cause failure. This demonstrates multiple genuine
    causes and intuitive upstream influence.

How to interpret outputs
- Ranks: lower is more plausible (0 is typical). A unit of fault adds 1 rank.
- "Causes output failure" is True when the intervention changes the output from OK
    to FAIL in at least one sufficiently plausible world, per the library's causal
    semantics. The reported strength is a rank-based measure from the reasoner.
- PC discovery lists directed relationships between propositions; for this example
    we include both faults and derived internal wires (l1, l2) to visualize flow.

Production dependencies used (no changes made)
- ranked_programming.Ranking, nrm_exc, rlet
- ranked_programming.causal_reasoning.CausalReasoner

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming import Ranking, nrm_exc, rlet
from ranked_programming.causal_reasoning import CausalReasoner
from typing import Callable, Dict, Tuple, List


def create_boolean_circuit_ranking(i1: bool, i2: bool, i3: bool) -> Ranking:
    """
    Build a ranked model of the circuit (i1, i2) pass through NOT and OR, then OR with i3.

    Fault variables are modeled as typically-working booleans with a rank-1 exception:
    True = working, False = faulty. A faulty gate forces its output to False.

    Args:
        i1: First input (feeds NOT gate)
        i2: Second input (feeds first OR gate)
        i3: Third input (feeds final OR gate)

    Returns:
        Ranking over tuples (N_working, O1_working, O2_working, out)
    """
    # Fault variables - normally working (True), exceptionally faulty (False)
    N = Ranking(lambda: nrm_exc(True, False, 1))   # NOT gate working?
    O1 = Ranking(lambda: nrm_exc(True, False, 1))  # First OR working?
    O2 = Ranking(lambda: nrm_exc(True, False, 1))  # Final OR working?

    def circuit(N, O1, O2):
        # Circuit logic with fault handling
        l1 = (not i1) if N else False           # NOT gate output
        l2 = (l1 or i2) if O1 else False        # First OR output
        out = (l2 or i3) if O2 else False       # Final OR output
        return (N, O1, O2, out)

    return Ranking(lambda: rlet([
        ('N', N),
        ('O1', O1),
        ('O2', O2)
    ], circuit))


def make_propositions(i1: bool, i2: bool, i3: bool) -> Dict[str, Callable[[Tuple[bool, bool, bool, bool]], bool]]:
    """
    Create named propositional functions over worlds (N, O1, O2, out).

    We also expose derived internal wires (l1, l2) computed from (i1, i2, i3)
    and gate status in the world; this lets PC discovery visualize signal flow.
    """
    def n_fault(x):
        return x[0] is False

    def o1_fault(x):
        return x[1] is False

    def o2_fault(x):
        return x[2] is False

    def output_failure(x):
        return x[3] is False

    # Derived wires
    def l1_true(x):
        N = x[0]
        return (not i1) if N else False

    def l2_true(x):
        N, O1 = x[0], x[1]
        l1 = (not i1) if N else False
        return (l1 or i2) if O1 else False

    return {
        'n_fault': n_fault,
        'o1_fault': o1_fault,
        'o2_fault': o2_fault,
        'output_failure': output_failure,
        'l1_true': l1_true,
        'l2_true': l2_true,
    }


def analyze_fault_causality(i1: bool, i2: bool, i3: bool, title: str):
    """
    Analyze direct causes, conditional effects, and counterfactuals for a given input setting.
    """
    print(f"=== {title} ===")
    print(f"Inputs: a={i1}, b={i2}, c={i3}")
    print()

    ranking = create_boolean_circuit_ranking(i1, i2, i3)
    reasoner = CausalReasoner()

    P = make_propositions(i1, i2, i3)
    n_fault = P['n_fault']
    o1_fault = P['o1_fault']
    o2_fault = P['o2_fault']
    output_failure = P['output_failure']

    # Individual fault causation
    faults = [
        ("NOT gate fault (N)", n_fault),
        ("First OR gate fault (O1)", o1_fault),
        ("Second OR gate fault (O2)", o2_fault),
    ]

    print("Individual fault → output failure:")
    print("-" * 42)
    for name, prop in faults:
        is_cause, strength = reasoner.is_direct_cause(prop, output_failure, [], ranking)
        print(f"{name}: causes? {is_cause}; strength={strength}")
    print()

    # Screening-off example: effect of N fault when O2 is known working
    o2_working = lambda x: x[2] is True
    cond = reasoner.conditional_causal_analysis(n_fault, output_failure, o2_working, ranking)
    print("Effect of NOT fault when final OR is known working (screening-off):")
    print(f"  unconditional={cond['unconditional_effect']} conditional={cond['conditional_true_effect']} Δ={cond['conditional_difference']}")
    print()

    # Counterfactual: if a gate were working instead of faulty, would output still fail?
    factual, counterf = reasoner.counterfactual_reasoning(
        ranking,
        {n_fault: False},  # Intervene to make NOT gate work
        output_failure,
    )
    print("Counterfactual: if NOT gate were working")
    print(f"  factual_fail={factual} counterfactual_fail={counterf} effect={factual - counterf}")
    print()


def analyze_fault_patterns(i1: bool, i2: bool, i3: bool, title: str):
    """
    Show most plausible worlds and quick takeaways for a given input setting.
    """
    print(f"=== {title} — plausible worlds ===")
    ranking = create_boolean_circuit_ranking(i1, i2, i3)
    top = list(ranking)[:6]
    for i, (world, k) in enumerate(top, 1):
        N, O1, O2, out = world
        faults = [name for ok, name in [(N, 'N'), (O1, 'O1'), (O2, 'O2')] if not ok]
        print(f"{i}. k={k:>2} faults={','.join(faults) or 'none'} out={'FAIL' if not out else 'OK'}")
    print("Notes: rank k equals number of faults here; lower k is more plausible.")
    print()


def demonstrate_causal_discovery(i1: bool, i2: bool, i3: bool, title: str):
    """
    Run PC discovery over faults plus derived wires l1, l2 and output failure.
    """
    print(f"=== {title} — PC causal discovery ===")
    ranking = create_boolean_circuit_ranking(i1, i2, i3)
    reasoner = CausalReasoner()

    P = make_propositions(i1, i2, i3)
    variables: List[Callable] = [
        P['n_fault'], P['o1_fault'], P['o2_fault'], P['l1_true'], P['l2_true'], P['output_failure']
    ]
    names = ["N_fault", "O1_fault", "O2_fault", "l1_true", "l2_true", "Output_fail"]

    cm = reasoner.pc_algorithm(variables, ranking)
    for (i, j), strength in cm.items():
        if strength > 0:
            print(f"{names[i]} → {names[j]} (strength={strength})")
    print("(Edges reflect influence under ranked plausibility, not logic sign.)")
    print()


def main():
    """Run the demo in two scenarios to highlight screening vs upstream influence."""
    print("Causal Analysis of Boolean Circuit Faults")
    print("=" * 50)
    print()

    # Scenario 1: Screened (c=True) — only O2 fault can fail the output
    analyze_fault_causality(False, False, True, "Screened scenario (c=True): only final gate matters")
    analyze_fault_patterns(False, False, True, "Screened scenario")
    demonstrate_causal_discovery(False, False, True, "Screened scenario")

    # Scenario 2: Unshielded (c=False) — upstream faults can cause failure
    analyze_fault_causality(False, False, False, "Unshielded scenario (c=False): upstream gates matter too")
    analyze_fault_patterns(False, False, False, "Unshielded scenario")
    demonstrate_causal_discovery(False, False, False, "Unshielded scenario")

    print("Done.")


if __name__ == "__main__":
    main()
