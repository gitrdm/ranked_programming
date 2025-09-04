#!/usr/bin/env python3
"""
Demo: SMT-Only Constraint Solving

This demo showcases the general constraint solving capabilities of the
ConstraintRankingNetwork without using c-representation features.

It demonstrates:
- Causal constraints (A → B)
- Mutual exclusion constraints (A ⊕ B)
- Evidence propagation
- Optimal assignment finding
"""

from ranked_programming.constraint_reasoning import ConstraintRankingNetwork
from ranked_programming import Ranking


def demo_basic_constraint_solving():
    """Demonstrate basic constraint solving with evidence."""
    print("=== Basic Constraint Solving Demo ===")

    # Create a network with causal and exclusion constraints
    variables = ['A', 'B', 'C']
    constraints = [
        ('A', 'B', 1),  # A causes B
        ('B', 'C', 1),  # B causes C
        ('A', 'C', 2),  # A and C are mutually exclusive
    ]

    network = ConstraintRankingNetwork(variables, constraints)
    print(f"Network variables: {network.variables}")
    print(f"Network constraints: {network.constraints}")

    # Solve without evidence
    print("\n--- Solving without evidence ---")
    solution = network.solve_constraints()
    for var, ranking in solution.items():
        print(f"{var} ranking: {list(ranking)}")

    # Solve with evidence
    print("\n--- Solving with evidence A='A_normal' ---")
    evidence = {'A': 'A_normal'}
    solution_with_evidence = network.solve_constraints(evidence)
    for var, ranking in solution_with_evidence.items():
        print(f"{var} ranking: {list(ranking)}")

    # Find optimal assignment
    print("\n--- Finding optimal assignment ---")
    optimal = network.find_optimal_assignment()
    print(f"Optimal assignment: {optimal}")
    score = network.get_constraint_satisfaction_score(optimal)
    print(f"Constraint satisfaction score: {score}")


def demo_diagnostic_reasoning():
    """Demonstrate diagnostic reasoning with multiple constraints."""
    print("\n=== Diagnostic Reasoning Demo ===")

    # Medical diagnosis scenario
    variables = ['Fever', 'Infection', 'Medication', 'Recovery']
    constraints = [
        ('Infection', 'Fever', 1),        # Infection causes fever
        ('Medication', 'Infection', 1),   # Medication treats infection
        ('Infection', 'Recovery', 2),     # Infection prevents recovery
        ('Medication', 'Recovery', 1),    # Medication promotes recovery
    ]

    network = ConstraintRankingNetwork(variables, constraints)

    # Scenario 1: Patient has fever, no medication
    print("\n--- Scenario 1: Fever present, no medication ---")
    evidence1 = {'Fever': 'Fever_present', 'Medication': 'Medication_absent'}
    solution1 = network.solve_constraints(evidence1)

    print("Variable rankings:")
    for var, ranking in solution1.items():
        ranking_list = list(ranking)
        top_value = ranking_list[0][0] if ranking_list else "unknown"
        print(f"  {var}: {top_value} (rank {ranking_list[0][1] if ranking_list else 'inf'})")

    # Scenario 2: Patient has fever, taking medication
    print("\n--- Scenario 2: Fever present, taking medication ---")
    evidence2 = {'Fever': 'Fever_present', 'Medication': 'Medication_present'}
    solution2 = network.solve_constraints(evidence2)

    print("Variable rankings:")
    for var, ranking in solution2.items():
        ranking_list = list(ranking)
        top_value = ranking_list[0][0] if ranking_list else "unknown"
        print(f"  {var}: {top_value} (rank {ranking_list[0][1] if ranking_list else 'inf'})")


def demo_complex_network():
    """Demonstrate solving a more complex constraint network."""
    print("\n=== Complex Network Demo ===")

    # Create a larger network
    variables = [f'X{i}' for i in range(8)]
    network = ConstraintRankingNetwork(variables)

    # Add causal chain
    for i in range(len(variables) - 1):
        network.add_constraint(variables[i], variables[i + 1], 1)

    # Add some mutual exclusions
    network.add_constraint('X0', 'X3', 2)
    network.add_constraint('X2', 'X5', 2)
    network.add_constraint('X4', 'X7', 2)

    print(f"Complex network with {len(variables)} variables and {len(network.constraints)} constraints")

    # Solve with partial evidence
    evidence = {'X0': 'X0_normal', 'X7': 'X7_abnormal'}
    solution = network.solve_constraints(evidence)

    print("\nSolution with evidence X0=normal, X7=abnormal:")
    for var, ranking in solution.items():
        ranking_list = list(ranking)
        if ranking_list:
            top_value = ranking_list[0][0]
            top_rank = ranking_list[0][1]
            print(f"  {var}: {top_value} (rank {top_rank})")


if __name__ == "__main__":
    print("SMT-Only Constraint Solving Demo")
    print("=" * 50)

    demo_basic_constraint_solving()
    demo_diagnostic_reasoning()
    demo_complex_network()

    print("\n" + "=" * 50)
    print("Demo completed successfully!")
