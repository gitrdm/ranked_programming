#!/usr/bin/env python3
"""
Causal Analysis of Ranking Network

This example demonstrates causal reasoning applied to the ranking network example.
It shows how interventions on network variables affect outcomes and reveals
the causal structure underlying the probabilistic relationships.

Network Structure:
- H (hypothesis) affects B (belief)
- B (belief) and F (fact) jointly affect S (conclusion)

This represents a classic causal model where we can analyze:
- Direct causal effects
- Indirect causal pathways
- Intervention effects
- Counterfactual reasoning

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming import Ranking, nrm_exc, rlet_star
from ranked_programming.causal_reasoning import CausalReasoner
from typing import List, Callable


def create_ranking_network():
    """
    Create the ranking network as defined in the original example.

    Returns:
        Ranking: Complete ranking of all variable combinations
    """
    def H():
        return Ranking(lambda: nrm_exc(False, True, 15))  # H normally False, exceptionally True

    def B(h):
        if h:
            return Ranking(lambda: nrm_exc(False, True, 4))   # If H=True, B normally False
        else:
            return Ranking(lambda: nrm_exc(True, False, 8))   # If H=False, B normally True

    def F():
        return Ranking(lambda: nrm_exc(True, False, 10))  # F normally True, exceptionally False

    def S(b, f):
        if b and f:
            return Ranking(lambda: nrm_exc(True, False, 3))   # If B and F both True, S normally True
        elif b and not f:
            return Ranking(lambda: nrm_exc(False, True, 13))  # If B=True, F=False, S normally False
        elif not b and f:
            return Ranking(lambda: nrm_exc(False, True, 11))  # If B=False, F=True, S normally False
        else:
            return Ranking(lambda: nrm_exc(False, True, 27))  # If B and F both False, S normally False

    network_generator = rlet_star([
        ('h', H()),
        ('b', lambda h: B(h)),
        ('f', F()),
        ('s', lambda b, f: S(b, f))
    ], lambda h, b, f, s: (h, b, f, s))

    return Ranking(lambda: network_generator)


def analyze_causal_structure():
    """
    Analyze the causal structure of the ranking network.
    """
    print("=== Causal Structure Analysis ===")
    print()

    network_ranking = create_ranking_network()
    reasoner = CausalReasoner()

    # Define propositions
    h_true = lambda x: x[0] == True   # Hypothesis is true
    b_true = lambda x: x[1] == True   # Belief is true
    f_true = lambda x: x[2] == True   # Fact is true
    s_true = lambda x: x[3] == True   # Conclusion is true

    print("Network Variables:")
    print("- H (Hypothesis): Affects belief formation")
    print("- B (Belief): Affected by H, affects conclusion with F")
    print("- F (Fact): Independent evidence, affects conclusion with B")
    print("- S (Conclusion): Jointly affected by B and F")
    print()

    # Test direct causal relationships
    causal_tests = [
        ("H → B", h_true, b_true),
        ("B → S", b_true, s_true),
        ("F → S", f_true, s_true),
        ("H → S", h_true, s_true),  # Indirect effect
    ]

    print("Direct Causal Relationships:")
    print("-" * 35)

    for name, cause, effect in causal_tests:
        is_cause, strength = reasoner.is_direct_cause(
            cause, effect, [], network_ranking
        )
        print(f"{name}: {is_cause} (strength: {strength})")

    print()

    # Analyze conditional causal effects
    print("Conditional Causal Analysis:")
    print("-" * 30)

    # How does H affect S when F is true vs false?
    conditional_results = reasoner.conditional_causal_analysis(
        h_true, s_true, f_true, network_ranking
    )

    print("Effect of H on S (conditional on F):")
    print(f"  Unconditional: {conditional_results['unconditional_effect']}")
    print(f"  When F=True: {conditional_results['conditional_true_effect']}")
    print(f"  When F=False: {conditional_results['conditional_false_effect']}")
    print(f"  Conditional difference: {conditional_results['conditional_difference']}")
    print()


def demonstrate_interventions():
    """
    Demonstrate intervention effects on the network.
    """
    print("=== Intervention Analysis ===")
    print()

    network_ranking = create_ranking_network()
    reasoner = CausalReasoner()

    # Define propositions
    h_true = lambda x: x[0] == True
    b_true = lambda x: x[1] == True
    f_true = lambda x: x[2] == True
    s_true = lambda x: x[3] == True

    interventions = [
        ("Force H=True", {h_true: True}, s_true, "What if hypothesis were true?"),
        ("Force H=False", {h_true: False}, s_true, "What if hypothesis were false?"),
        ("Force F=True", {f_true: True}, s_true, "What if fact were true?"),
        ("Force F=False", {f_true: False}, s_true, "What if fact were false?"),
        ("Force B=True", {b_true: True}, s_true, "What if belief were true?"),
    ]

    print("Intervention Effects on Conclusion (S):")
    print("-" * 45)

    for name, intervention, query, description in interventions:
        factual, counterfactual = reasoner.counterfactual_reasoning(
            network_ranking, intervention, query
        )

        effect = counterfactual - factual
        direction = "increases" if effect > 0 else "decreases" if effect < 0 else "no change"

        print(f"{name}:")
        print(f"  {description}")
        print(f"  Factual P(S=True): {factual}")
        print(f"  Counterfactual P(S=True): {counterfactual}")
        print(f"  Effect: {direction} by {abs(effect)}")
        print()

    # Multi-variable intervention
    print("Combined Intervention:")
    print("-" * 22)

    combined_intervention = {h_true: True, f_true: True}
    factual, counterfactual = reasoner.counterfactual_reasoning(
        network_ranking, combined_intervention, s_true
    )

    print("What if both H and F were true?")
    print(f"  Factual P(S=True): {factual}")
    print(f"  Counterfactual P(S=True): {counterfactual}")
    print(f"  Combined effect: {counterfactual - factual}")
    print()


def analyze_causal_pathways():
    """
    Analyze different causal pathways through the network.
    """
    print("=== Causal Pathway Analysis ===")
    print()

    network_ranking = create_ranking_network()
    reasoner = CausalReasoner()

    # Define propositions
    h_true = lambda x: x[0] == True
    b_true = lambda x: x[1] == True
    f_true = lambda x: x[2] == True
    s_true = lambda x: x[3] == True

    print("Causal Pathways from H to S:")
    print("-" * 30)

    # Direct pathway: H → B → S
    h_to_b, strength1 = reasoner.is_direct_cause(h_true, b_true, [], network_ranking)
    b_to_s, strength2 = reasoner.is_direct_cause(b_true, s_true, [], network_ranking)

    print("Direct pathway: H → B → S")
    print(f"  H → B: {h_to_b} (strength: {strength1})")
    print(f"  B → S: {b_to_s} (strength: {strength2})")
    print(f"  Pathway strength: {strength1 * strength2}")
    print()

    # Analyze mediation
    print("Mediation Analysis:")
    print("-" * 20)

    # Does B mediate the effect of H on S?
    # Compare total effect vs direct effect (controlling for B)

    # Total effect of H on S
    total_effect, _ = reasoner.is_direct_cause(h_true, s_true, [], network_ranking)

    # Direct effect of H on S controlling for B
    direct_effect, _ = reasoner.is_direct_cause(h_true, s_true, [b_true], network_ranking)

    mediation = total_effect - direct_effect

    print("Mediation through B:")
    print(f"  Total effect H → S: {total_effect}")
    print(f"  Direct effect H → S (controlling B): {direct_effect}")
    print(f"  Mediated effect through B: {mediation}")
    print()

    # Interaction effects
    print("Interaction Analysis:")
    print("-" * 22)

    # How do H and F interact in affecting S?
    # Test for synergistic effects

    h_only_intervention = {h_true: True, f_true: False}
    f_only_intervention = {h_true: False, f_true: True}
    both_intervention = {h_true: True, f_true: True}

    _, h_only_effect = reasoner.counterfactual_reasoning(network_ranking, h_only_intervention, s_true)
    _, f_only_effect = reasoner.counterfactual_reasoning(network_ranking, f_only_intervention, s_true)
    _, both_effect = reasoner.counterfactual_reasoning(network_ranking, both_intervention, s_true)

    expected_additive = h_only_effect + f_only_effect
    actual_interaction = both_effect
    synergy = actual_interaction - expected_additive

    print("Synergistic effects of H and F on S:")
    print(f"  H alone: {h_only_effect}")
    print(f"  F alone: {f_only_effect}")
    print(f"  Expected additive: {expected_additive}")
    print(f"  Actual combined: {actual_interaction}")
    print(f"  Synergy: {synergy} ({'positive' if synergy > 0 else 'negative'} interaction)")
    print()


def demonstrate_causal_discovery():
    """
    Demonstrate automated causal discovery on the network.
    """
    print("=== Automated Causal Discovery ===")
    print()

    network_ranking = create_ranking_network()
    reasoner = CausalReasoner()

    # Define variables for discovery
    variables = [
        lambda x: x[0] == True,  # H
        lambda x: x[1] == True,  # B
        lambda x: x[2] == True,  # F
        lambda x: x[3] == True   # S
    ]

    var_names = ["H", "B", "F", "S"]

    print("Running PC algorithm for causal discovery...")
    print()

    causal_matrix = reasoner.pc_algorithm(variables, network_ranking)

    print("Discovered Causal Graph:")
    print("-" * 25)

    edges_found = []
    for (i, j), strength in causal_matrix.items():
        if strength > 0:
            edges_found.append((var_names[i], var_names[j], strength))
            print(f"{var_names[i]} → {var_names[j]} (strength: {strength})")

    print()
    print("Expected vs Discovered:")
    print("-" * 25)
    print("Expected: H → B, H → S, B → S, F → S")
    print(f"Discovered: {', '.join([f'{a}→{b}' for a,b,_ in edges_found])}")

    if len(edges_found) >= 4:
        print("✓ All expected causal relationships discovered!")
    else:
        print("⚠ Some causal relationships may be weak or indirect")

    print()


def main():
    """
    Run all causal analyses of the ranking network.
    """
    print("Causal Analysis of Ranking Network")
    print("=" * 40)
    print()

    analyze_causal_structure()
    demonstrate_interventions()
    analyze_causal_pathways()
    demonstrate_causal_discovery()

    print("Analysis complete! 🧠")
    print()
    print("This analysis demonstrates how causal reasoning reveals")
    print("the underlying structure and dynamics of probabilistic")
    print("networks using ranking-theoretic methods.")


if __name__ == "__main__":
    main()
