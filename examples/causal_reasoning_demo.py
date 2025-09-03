#!/usr/bin/env python3
"""
Causal Reasoning Demo for Ranked Programming

This example demonstrates the causal reasoning capabilities of the ranked_programming library.
It shows how to use ranking theory for causal discovery, intervention analysis, and
conditional causal inference.

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming import Ranking, nrm_exc, observe_e
from ranked_programming.causal_reasoning import CausalReasoner, create_causal_model
from typing import List, Callable


def demonstrate_basic_causal_inference():
    """
    Demonstrate basic causal inference using intervention analysis.
    """
    print("=== Basic Causal Inference ===")
    print()

    # Create a ranking that represents a causal relationship: A -> B
    # Normal case: A=true, B=true (causal relationship holds)
    # Exceptional case: A=true, B=false (causal relationship violated)
    ranking = Ranking(lambda: nrm_exc(
        ('A_true', 'B_true'),      # Normal: A causes B
        ('A_true', 'B_false'),     # Exceptional: A doesn't cause B
        1
    ))

    print("Ranking function represents causal relationship A -> B")
    print("Normal case: A=true, B=true (rank 0)")
    print("Exceptional case: A=true, B=false (rank 1)")
    print()

    # Test for causation
    reasoner = CausalReasoner()

    cause_prop = lambda x: x[0] == 'A_true'
    effect_prop = lambda x: x[1] == 'B_true'

    is_cause, strength = reasoner.is_direct_cause(
        cause_prop, effect_prop, [], ranking
    )

    print(f"Causal test result:")
    print(f"  A causes B: {is_cause}")
    print(f"  Causal strength: {strength}")
    print()

    # Test causal effect strength
    effect_strength = reasoner.causal_effect_strength(cause_prop, effect_prop, ranking)
    print(f"Causal effect strength: {effect_strength}")
    print()


def demonstrate_conditional_causal_analysis():
    """
    Demonstrate conditional causal analysis using background conditions.
    """
    print("=== Conditional Causal Analysis ===")
    print()

    # Create a ranking with confounding: A -> B <- C
    # A and C are independent, both affect B
    ranking = Ranking(lambda: nrm_exc(
        ('A_true', 'B_true', 'C_false'),   # A causes B (no confounding)
        nrm_exc(('A_false', 'B_true', 'C_true'),   # C causes B (no confounding)
                ('A_true', 'B_true', 'C_true'), 1),  # Both A and C cause B
        1
    ))

    print("Ranking represents confounding scenario: A -> B <- C")
    print("Variables: A, B, C where both A and C influence B")
    print()

    reasoner = CausalReasoner()

    cause_prop = lambda x: x[0] == 'A_true'
    effect_prop = lambda x: x[1] == 'B_true'
    condition_prop = lambda x: x[2] == 'C_true'

    # Overall causal effect
    results = reasoner.conditional_causal_analysis(
        cause_prop, effect_prop, condition_prop, ranking
    )

    print("Conditional causal analysis results:")
    print(f"  Unconditional effect: {results['unconditional_effect']}")
    print(f"  Effect when C=true: {results['conditional_true_effect']}")
    print(f"  Effect when C=false: {results['conditional_false_effect']}")
    print(f"  Conditional difference: {results['conditional_difference']}")
    print()

    # Test conditional independence
    independence_results = reasoner.analyze_conditional_independence(
        cause_prop, effect_prop, condition_prop, ranking
    )

    print("Conditional independence analysis:")
    print(f"  Unconditional correlation: {independence_results['unconditional_correlation']}")
    print(f"  Correlation when C=true: {independence_results['conditional_true_correlation']}")
    print(f"  Correlation when C=false: {independence_results['conditional_false_correlation']}")
    print(f"  Conditionally independent: {independence_results['conditionally_independent']}")
    print()


def demonstrate_causal_discovery():
    """
    Demonstrate causal discovery using the PC algorithm.
    """
    print("=== Causal Discovery with PC Algorithm ===")
    print()

    # Create a ranking representing a known causal structure: X -> Y <- Z
    variables = [
        lambda w: w[0] == 'X_true',   # X
        lambda w: w[1] == 'Y_true',   # Y
        lambda w: w[2] == 'Z_true'    # Z
    ]

    ranking = Ranking(lambda: nrm_exc(
        ('X_true', 'Y_true', 'Z_false'),    # X -> Y
        nrm_exc(('X_false', 'Y_true', 'Z_true'),    # Z -> Y
                ('X_true', 'Y_true', 'Z_true'), 1),     # Both X and Z -> Y
        1
    ))

    print("Testing causal discovery on known structure: X -> Y <- Z")
    print("Variables: X, Y, Z with confounding between X and Z")
    print()

    reasoner = CausalReasoner()
    causal_matrix = reasoner.pc_algorithm(variables, ranking)

    print("Discovered causal relationships:")
    for (i, j), strength in causal_matrix.items():
        var_names = ['X', 'Y', 'Z']
        print(f"  {var_names[i]} -> {var_names[j]} (strength: {strength})")
    print()


def demonstrate_counterfactual_reasoning():
    """
    Demonstrate counterfactual reasoning capabilities.
    """
    print("=== Counterfactual Reasoning ===")
    print()

    # Create a ranking representing a causal chain: A -> B -> C
    ranking = Ranking(lambda: nrm_exc(
        ('A_true', 'B_true', 'C_true'),     # Normal causal chain
        nrm_exc(('A_true', 'B_true', 'C_false'),    # B doesn't cause C
                ('A_true', 'B_false', 'C_false'), 1),  # A doesn't cause B
        1
    ))

    print("Causal chain: A -> B -> C")
    print("Normal case: A=true, B=true, C=true")
    print("Counterfactual: What if A were false?")
    print()

    reasoner = CausalReasoner()

    # Define propositions
    a_prop = lambda x: x[0] == 'A_true'
    b_prop = lambda x: x[1] == 'B_true'
    c_prop = lambda x: x[2] == 'C_true'

    # Counterfactual: What would C be if A were false?
    factual_value, counterfactual_value = reasoner.counterfactual_reasoning(
        ranking,
        {a_prop: False},  # Intervene: set A to false
        c_prop           # Query: what is C?
    )

    print("Counterfactual analysis:")
    print(f"  Factual (A=true): C = {factual_value}")
    print(f"  Counterfactual (A=false): C = {counterfactual_value}")
    print(f"  Causal effect of A on C: {factual_value - counterfactual_value}")
    print()


def demonstrate_causal_model_creation():
    """
    Demonstrate creating and using declarative causal models.
    """
    print("=== Declarative Causal Model Creation ===")
    print()

    # Define variables
    variables = {
        'rain': lambda x: x.get('rain', False),
        'sprinkler': lambda x: x.get('sprinkler', False),
        'grass_wet': lambda x: x.get('grass_wet', False)
    }

    # Define causal relationships
    causal_relationships = [
        ('rain', 'grass_wet', 0.8),        # Rain causes wet grass
        ('sprinkler', 'grass_wet', 0.6),   # Sprinkler causes wet grass
    ]

    print("Creating causal model: Rain -> Wet Grass <- Sprinkler")
    print("Relationships:")
    for cause, effect, strength in causal_relationships:
        print(f"  {cause} -> {effect} (strength: {strength})")
    print()

    # Create the causal model
    reasoner = create_causal_model(variables, causal_relationships)

    print("Causal model created successfully!")
    print(f"Number of causal relationships: {len(reasoner.causal_strengths)}")
    print()


def demonstrate_integration_with_combinators():
    """
    Demonstrate integration with existing combinator framework.
    """
    print("=== Integration with Combinator Framework ===")
    print()

    # Create base ranking
    base_ranking = Ranking(lambda: nrm_exc(
        ('treatment_true', 'outcome_good'),     # Treatment helps
        ('treatment_true', 'outcome_bad'),      # Treatment doesn't help
        1
    ))

    print("Base ranking: Treatment -> Outcome")
    print("Using combinators to modify causal relationships")
    print()

    # Define combinators that modify the causal structure
    combinators = [
        lambda r: Ranking(lambda: observe_e(1, lambda x: x[0] == 'treatment_true', r)),
        lambda r: Ranking(lambda: observe_e(2, lambda x: x[1] == 'outcome_good', r))
    ]

    variables = [
        lambda x: x[0] == 'treatment_true',
        lambda x: x[1] == 'outcome_good'
    ]

    reasoner = CausalReasoner()
    causal_matrix = reasoner.learn_causal_structure_from_combinators(
        base_ranking, combinators, variables
    )

    print("Causal structure learned from combinators:")
    for (i, j), strength in causal_matrix.items():
        var_names = ['Treatment', 'Outcome']
        print(f"  {var_names[i]} -> {var_names[j]} (strength: {strength})")
    print()


def main():
    """
    Run all causal reasoning demonstrations.
    """
    print("Causal Reasoning Demo for Ranked Programming")
    print("=" * 50)
    print()

    demonstrate_basic_causal_inference()
    demonstrate_conditional_causal_analysis()
    demonstrate_causal_discovery()
    demonstrate_counterfactual_reasoning()
    demonstrate_causal_model_creation()
    demonstrate_integration_with_combinators()

    print("Demo completed! 🎉")
    print()
    print("This demo showcases the causal reasoning capabilities of")
    print("the ranked_programming library, including:")
    print("• Intervention analysis")
    print("• Conditional causal inference")
    print("• Causal discovery algorithms")
    print("• Counterfactual reasoning")
    print("• Integration with existing combinators")


if __name__ == "__main__":
    main()
