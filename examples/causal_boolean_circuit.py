#!/usr/bin/env python3
"""
Causal Analysis of Boolean Circuit Faults

This example demonstrates causal reasoning applied to the boolean circuit example.
It shows how to analyze the causal relationships between circuit faults and output
behavior using the ranked programming causal reasoning toolkit.

The circuit computes: (a and b) or c with fixed inputs a=False, b=False, c=True
Expected output: True (since c=True)

Faults can cause the output to be False:
- N fault: NOT gate fails, l1 becomes False instead of True
- O1 fault: OR gate fails, l2 becomes False instead of True
- O2 fault: OR gate fails, output becomes False instead of True

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming import Ranking, nrm_exc, rlet
from ranked_programming.causal_reasoning import CausalReasoner
from typing import List, Callable


def create_boolean_circuit_ranking():
    """
    Create a ranking function representing the boolean circuit with faults.

    Returns:
        Ranking: Complete ranking of all fault combinations and their outputs
    """
    # Fault variables - normally working (True), exceptionally faulty (False)
    N = Ranking(lambda: nrm_exc(True, False, 1))   # NOT gate fault
    O1 = Ranking(lambda: nrm_exc(True, False, 1))  # First OR gate fault
    O2 = Ranking(lambda: nrm_exc(True, False, 1))  # Second OR gate fault

    def circuit(N, O1, O2):
        # Fixed inputs: i1 = False, i2 = False, i3 = True
        i1, i2, i3 = False, False, True

        # Circuit logic with fault handling
        l1 = (not i1) if N else False           # NOT gate: ~i1 = True normally
        l2 = (l1 or i2) if O1 else False        # OR gate: True or False = True normally
        out = (l2 or i3) if O2 else False       # OR gate: True or True = True normally

        return (N, O1, O2, out)

    return Ranking(lambda: rlet([
        ('N', N),
        ('O1', O1),
        ('O2', O2)
    ], circuit))


def analyze_fault_causality():
    """
    Analyze the causal relationships between faults and circuit output.
    """
    print("=== Causal Analysis of Boolean Circuit Faults ===")
    print()

    ranking = create_boolean_circuit_ranking()
    reasoner = CausalReasoner()

    # Define propositions
    n_fault = lambda x: x[0] == False  # NOT gate is faulty
    o1_fault = lambda x: x[1] == False  # First OR gate is faulty
    o2_fault = lambda x: x[2] == False  # Second OR gate is faulty
    output_failure = lambda x: x[3] == False  # Circuit output is False

    print("Circuit Analysis:")
    print("- Fixed inputs: a=False, b=False, c=True")
    print("- Expected output: True")
    print("- Faults can cause output to be False")
    print()

    # Test individual fault causation
    faults = [
        ("NOT gate fault (N)", n_fault),
        ("First OR gate fault (O1)", o1_fault),
        ("Second OR gate fault (O2)", o2_fault)
    ]

    print("Individual Fault Causation Analysis:")
    print("-" * 50)

    for fault_name, fault_prop in faults:
        is_cause, strength = reasoner.is_direct_cause(
            fault_prop, output_failure, [], ranking
        )

        print(f"{fault_name}:")
        print(f"  Causes output failure: {is_cause}")
        print(f"  Causal strength: {strength}")
        print()

    # Analyze causal chains
    print("Causal Chain Analysis:")
    print("-" * 30)

    # N fault -> O1 fault -> output failure
    n_to_o1, strength1 = reasoner.is_direct_cause(n_fault, o1_fault, [], ranking)
    o1_to_output, strength2 = reasoner.is_direct_cause(o1_fault, output_failure, [], ranking)

    print("NOT fault → First OR fault:")
    print(f"  Direct causation: {n_to_o1}, Strength: {strength1}")
    print("First OR fault → Output failure:")
    print(f"  Direct causation: {o1_to_output}, Strength: {strength2}")
    print()

    # Conditional causal analysis
    print("Conditional Causal Analysis:")
    print("-" * 32)

    # How does N fault affect output when O2 is working?
    o2_working = lambda x: x[2] == True

    conditional_results = reasoner.conditional_causal_analysis(
        n_fault, output_failure, o2_working, ranking
    )

    print("Effect of NOT fault on output (when second OR gate works):")
    print(f"  Unconditional effect: {conditional_results['unconditional_effect']}")
    print(f"  Conditional effect: {conditional_results['conditional_true_effect']}")
    print(f"  Difference: {conditional_results['conditional_difference']}")
    print()

    # Counterfactual analysis
    print("Counterfactual Analysis:")
    print("-" * 25)

    # What would output be if N were working (counterfactual)?
    factual_value, counterfactual_value = reasoner.counterfactual_reasoning(
        ranking,
        {n_fault: False},  # Intervene: make N work
        output_failure     # Query: would output fail?
    )

    print("Counterfactual: What if NOT gate were working?")
    print(f"  Factual (N faulty): Output fails = {factual_value}")
    print(f"  Counterfactual (N working): Output fails = {counterfactual_value}")
    print(f"  Causal effect of N fault: {factual_value - counterfactual_value}")
    print()


def analyze_fault_patterns():
    """
    Analyze patterns in fault combinations and their causal effects.
    """
    print("=== Fault Pattern Analysis ===")
    print()

    ranking = create_boolean_circuit_ranking()

    print("Most likely fault scenarios:")
    print("-" * 35)

    # Show the most probable fault combinations
    top_scenarios = list(ranking)[:5]  # Top 5 most likely scenarios

    for i, (scenario, rank) in enumerate(top_scenarios, 1):
        N, O1, O2, output = scenario
        faults = []
        if not N: faults.append("NOT")
        if not O1: faults.append("OR1")
        if not O2: faults.append("OR2")

        fault_str = ", ".join(faults) if faults else "No faults"
        status = "FAIL" if not output else "OK"

        print(f"{i}. Rank {rank}: {fault_str} → Output {status}")

    print()
    print("Key Insights:")
    print("- Single faults have lower ranks (more likely)")
    print("- Multiple faults have higher ranks (less likely)")
    print("- NOT gate fault alone doesn't cause output failure")
    print("- OR gate faults directly affect output")
    print()


def demonstrate_causal_discovery():
    """
    Demonstrate causal discovery on the boolean circuit.
    """
    print("=== Causal Discovery on Boolean Circuit ===")
    print()

    ranking = create_boolean_circuit_ranking()
    reasoner = CausalReasoner()

    # Define variables for causal discovery
    variables = [
        lambda x: x[0] == False,  # N fault
        lambda x: x[1] == False,  # O1 fault
        lambda x: x[2] == False,  # O2 fault
        lambda x: x[3] == False   # Output failure
    ]

    var_names = ["N_fault", "O1_fault", "O2_fault", "Output_fail"]

    print("Discovering causal relationships using PC algorithm...")
    print()

    # Run PC algorithm for causal discovery
    causal_matrix = reasoner.pc_algorithm(variables, ranking)

    print("Discovered Causal Relationships:")
    print("-" * 35)

    for (i, j), strength in causal_matrix.items():
        if strength > 0:
            print(f"{var_names[i]} → {var_names[j]} (strength: {strength})")

    print()
    print("Expected causal structure:")
    print("- N_fault → O1_fault (NOT fault affects first OR)")
    print("- O1_fault → Output_fail (First OR fault affects output)")
    print("- O2_fault → Output_fail (Second OR fault affects output)")
    print()


def main():
    """
    Run all causal analyses of the boolean circuit.
    """
    print("Causal Analysis of Boolean Circuit Faults")
    print("=" * 50)
    print()

    analyze_fault_causality()
    analyze_fault_patterns()
    demonstrate_causal_discovery()

    print("Analysis complete! 🎯")
    print()
    print("This analysis demonstrates how causal reasoning can help")
    print("understand and diagnose faults in complex systems like")
    print("boolean circuits using ranking-theoretic methods.")


if __name__ == "__main__":
    main()
