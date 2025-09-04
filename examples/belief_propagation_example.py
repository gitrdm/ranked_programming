"""
Belief Propagation Example for Ranked Programming

This example demonstrates the belief propagation capabilities added in Phase 4
of the ranked programming library. It shows how to:

1. Create belief propagation networks
2. Perform inference on ranking-based graphical models
3. Handle evidence propagation
4. Work with different network topologies

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.belief_propagation import BeliefPropagationNetwork, create_chain_network


def example_simple_chain():
    """
    Example 1: Simple Chain Network

    This example creates a simple chain A -> B -> C and demonstrates
    belief propagation for computing marginal rankings.
    """
    print("=== Example 1: Simple Chain Network ===")
    print()

    # Create a simple chain: A -> B -> C
    # A influences B, B influences C
    factors = {
        ('A',): Ranking(lambda: nrm_exc('A_healthy', 'A_faulty', 2)),
        ('A', 'B'): Ranking(lambda: nrm_exc(
            ('A_healthy', 'B_good'),
            ('A_healthy', 'B_bad'),
            1
        )),
        ('B', 'C'): Ranking(lambda: nrm_exc(
            ('B_good', 'C_working'),
            ('B_good', 'C_broken'),
            1
        ))
    }

    network = BeliefPropagationNetwork(factors)

    print("Network structure:")
    print("- Variables: A, B, C")
    print("- Factors: P(A), P(B|A), P(C|B)")
    print("- Topology: A -> B -> C")
    print()

    # Compute marginals without evidence
    print("Marginal rankings (no evidence):")
    marginals = network.propagate_beliefs()

    for var, ranking in marginals.items():
        print(f"  {var}: ", end="")
        values = list(ranking)
        for value, rank in values[:3]:  # Show first 3 values
            print(f"{value}→{rank}", end=" ")
        if len(values) > 3:
            print("...")
        else:
            print()

    print()

    # Add evidence that A is healthy
    print("With evidence: A is healthy")
    evidence = {'A': lambda x: x == 'A_healthy'}
    marginals_with_evidence = network.propagate_beliefs(evidence)

    print("Updated marginals:")
    for var, ranking in marginals_with_evidence.items():
        print(f"  {var}: ", end="")
        values = list(ranking)
        for value, rank in values[:3]:
            print(f"{value}→{rank}", end=" ")
        if len(values) > 3:
            print("...")
        else:
            print()

    print()


def example_diagnostic_network():
    """
    Example 2: Diagnostic Network

    This example models a diagnostic scenario where multiple symptoms
    help diagnose a disease, with some confounding factors.
    """
    print("=== Example 2: Diagnostic Network ===")
    print()

    # Model: Disease -> Symptoms, with some confounding
    factors = {
        ('Disease',): Ranking(lambda: nrm_exc('healthy', 'infected', 3)),
        ('Disease', 'Fever'): Ranking(lambda: nrm_exc(
            ('healthy', 'no_fever'),
            ('healthy', 'fever'),
            2
        )),
        ('Disease', 'Cough'): Ranking(lambda: nrm_exc(
            ('healthy', 'no_cough'),
            ('healthy', 'cough'),
            2
        )),
        ('Fever', 'Cough'): Ranking(lambda: nrm_exc(
            ('no_fever', 'no_cough'),
            ('fever', 'cough'),
            1  # Confounding: fever often causes cough
        ))
    }

    network = BeliefPropagationNetwork(factors)

    print("Diagnostic network:")
    print("- Variables: Disease, Fever, Cough")
    print("- Disease influences both symptoms")
    print("- Fever and Cough are correlated (confounding)")
    print()

    # Scenario 1: No symptoms observed
    print("Scenario 1: No evidence")
    marginals = network.propagate_beliefs()
    disease_marginal = marginals['Disease']
    values = list(disease_marginal)
    healthy_rank = next(rank for value, rank in values if value == 'healthy')
    infected_rank = next(rank for value, rank in values if value == 'infected')
    print(f"  Disease belief: healthy→{healthy_rank}, infected→{infected_rank}")
    print()

    # Scenario 2: Patient has fever
    print("Scenario 2: Patient has fever")
    evidence = {'Fever': lambda x: x == 'fever'}
    marginals = network.propagate_beliefs(evidence)
    disease_marginal = marginals['Disease']
    values = list(disease_marginal)
    healthy_rank = next(rank for value, rank in values if value == 'healthy')
    infected_rank = next(rank for value, rank in values if value == 'infected')
    print(f"  Disease belief: healthy→{healthy_rank}, infected→{infected_rank}")
    print()

    # Scenario 3: Patient has both fever and cough
    print("Scenario 3: Patient has fever and cough")
    evidence = {
        'Fever': lambda x: x == 'fever',
        'Cough': lambda x: x == 'cough'
    }
    marginals = network.propagate_beliefs(evidence)
    disease_marginal = marginals['Disease']
    values = list(disease_marginal)
    healthy_rank = next(rank for value, rank in values if value == 'healthy')
    infected_rank = next(rank for value, rank in values if value == 'infected')
    print(f"  Disease belief: healthy→{healthy_rank}, infected→{infected_rank}")
    print()


def example_chain_network_utility():
    """
    Example 3: Using the Chain Network Utility

    This example demonstrates the create_chain_network utility function
    for quickly creating chain topologies.
    """
    print("=== Example 3: Chain Network Utility ===")
    print()

    # Create a chain of 5 variables
    network = create_chain_network(5)

    print("Created chain network with 5 variables: X0 -> X1 -> X2 -> X3 -> X4")
    print(f"Variables: {sorted(network.variables)}")
    print(f"Number of factors: {len(network.factors)}")
    print()

    # Run belief propagation
    marginals = network.propagate_beliefs()

    print("Marginal rankings for each variable:")
    for var in sorted(network.variables):
        ranking = marginals[var]
        values = list(ranking)
        print(f"  {var}: {len(values)} possible values")

    print()


def example_performance_comparison():
    """
    Example 4: Performance Characteristics

    This example demonstrates the performance characteristics of belief
    propagation on networks of different sizes.
    """
    print("=== Example 4: Performance Characteristics ===")
    print()

    import time

    sizes = [3, 5, 8, 10]

    for size in sizes:
        network = create_chain_network(size)

        start_time = time.time()
        marginals = network.propagate_beliefs(max_iterations=5)
        end_time = time.time()

        elapsed = end_time - start_time
        print(".4f"
              f"({len(marginals)} marginals computed)")

    print()


def example_evidence_propagation():
    """
    Example 5: Evidence Propagation

    This example shows how evidence propagates through the network
    and affects beliefs about other variables.
    """
    print("=== Example 5: Evidence Propagation ===")
    print()

    # Create a more complex network
    factors = {
        ('A',): Ranking(lambda: nrm_exc('A_low', 'A_high', 1)),
        ('B',): Ranking(lambda: nrm_exc('B_low', 'B_high', 1)),
        ('C',): Ranking(lambda: nrm_exc('C_low', 'C_high', 1)),
        ('A', 'B'): Ranking(lambda: nrm_exc(('A_low', 'B_low'), ('A_high', 'B_high'), 1)),
        ('B', 'C'): Ranking(lambda: nrm_exc(('B_low', 'C_low'), ('B_high', 'C_high'), 1)),
        ('A', 'C'): Ranking(lambda: nrm_exc(('A_low', 'C_high'), ('A_high', 'C_low'), 1))
    }

    network = BeliefPropagationNetwork(factors)

    print("Network: A - B - C with A-C correlation")
    print()

    # Test different evidence scenarios
    scenarios = [
        ("No evidence", {}),
        ("A is high", {'A': lambda x: x == 'A_high'}),
        ("C is low", {'C': lambda x: x == 'C_low'}),
        ("Both A high and C low", {'A': lambda x: x == 'A_high', 'C': lambda x: x == 'C_low'})
    ]

    for scenario_name, evidence in scenarios:
        print(f"{scenario_name}:")
        marginals = network.propagate_beliefs(evidence)

        for var in ['A', 'B', 'C']:
            ranking = marginals[var]
            values = list(ranking)
            high_rank = next((rank for value, rank in values if f'{var}_high' in str(value)), float('inf'))
            low_rank = next((rank for value, rank in values if f'{var}_low' in str(value)), float('inf'))
            print(f"  {var}: high→{high_rank}, low→{low_rank}")

        print()


def main():
    """Run all belief propagation examples."""
    print("Belief Propagation Examples for Ranked Programming")
    print("=" * 55)
    print()

    try:
        example_simple_chain()
        example_diagnostic_network()
        example_chain_network_utility()
        example_performance_comparison()
        example_evidence_propagation()

        print("All examples completed successfully! 🎉")
        print()
        print("Key takeaways:")
        print("- Belief propagation enables efficient inference in ranking networks")
        print("- Evidence propagates through the network affecting all variables")
        print("- Chain networks scale well with the implemented algorithm")
        print("- Complex diagnostic scenarios can be modeled effectively")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
