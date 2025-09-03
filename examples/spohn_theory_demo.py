#!/usr/bin/env python3
"""
Spohn's Ranking Theory Demonstration

This example demonstrates the core concepts of Wolfgang Spohn's Ranking Theory
as implemented in the ranked_programming library. It shows how the theoretical
constructs (κ, τ, conditional ranks) map to practical programming constructs.

Key Concepts Demonstrated:
- κ (kappa): Negative ranking function - degree of disbelief
- τ (tau): Belief function - τ(A) = κ(∼A) - κ(A)
- Conditional ranks: κ(B|A) - disbelief in B given A
- Law of disjunction: κ(A∪B) = min(κ(A), κ(B))

Author: Ranked Programming Library
Date: September 2025
"""

from ranked_programming import nrm_exc, Ranking


def demonstrate_negative_ranking():
    """
    Demonstrate the negative ranking function κ (kappa).

    κ represents degrees of disbelief:
    - κ(A) = 0: A is not disbelieved (normal/certain)
    - κ(A) = n > 0: A is disbelieved to degree n (exceptional/surprising)
    - κ(A) = ∞: A is impossible
    """
    print("=== Negative Ranking Function (κ) Demonstration ===")

    # Create a simple ranking: normal case A, exceptional case B
    ranking = Ranking(lambda: nrm_exc('normal_operation', 'failure', 2))

    print("Ranking: normal_operation (rank 0), failure (rank 2)")
    print(f"κ(normal_operation) = {ranking.disbelief_rank(lambda x: x == 'normal_operation')}")
    print(f"κ(failure) = {ranking.disbelief_rank(lambda x: x == 'failure')}")
    print(f"κ(impossible_event) = {ranking.disbelief_rank(lambda x: x == 'impossible')}")
    print()


def demonstrate_belief_function():
    """
    Demonstrate the belief function τ (tau).

    τ represents belief strength:
    - τ(A) > 0: Belief in A (∼A is more disbelieved than A)
    - τ(A) < 0: Disbelief in A (A is more disbelieved than ∼A)
    - τ(A) = 0: Suspension of judgment (equal disbelief in A and ∼A)
    """
    print("=== Belief Function (τ) Demonstration ===")

    # Strong belief case: A is normal, B is very exceptional
    strong_belief = Ranking(lambda: nrm_exc('healthy', 'sick', 3))
    print("Case 1 - Strong belief: healthy (rank 0), sick (rank 3)")
    print(f"τ(healthy) = {strong_belief.belief_rank(lambda x: x == 'healthy')} (strong belief)")
    print(f"τ(sick) = {strong_belief.belief_rank(lambda x: x == 'sick')} (strong disbelief)")
    print()

    # Suspension of judgment: equal disbelief
    suspension = Ranking(lambda: [('A', 1), ('B', 1)])
    print("Case 2 - Suspension of judgment: A (rank 1), B (rank 1)")
    print(f"τ(A) = {suspension.belief_rank(lambda x: x == 'A')} (suspension of judgment)")
    print()


def demonstrate_law_of_disjunction():
    """
    Demonstrate the law of disjunction: κ(A∪B) = min(κ(A), κ(B))

    This is a fundamental law of ranking theory that enables efficient
    computation of disjunctive possibilities.
    """
    print("=== Law of Disjunction Demonstration ===")
    print("κ(A∪B) = min(κ(A), κ(B))")
    print()

    # Create ranking with A, B, and A∪B represented as tuples
    ranking = Ranking(lambda: nrm_exc(('A',), ('B',), 1))

    # κ(A) - disbelief in proposition A
    kappa_A = ranking.disbelief_rank(lambda x: isinstance(x, tuple) and 'A' in x)
    print(f"κ(A) = {kappa_A}")

    # κ(B) - disbelief in proposition B
    kappa_B = ranking.disbelief_rank(lambda x: isinstance(x, tuple) and 'B' in x)
    print(f"κ(B) = {kappa_B}")

    # κ(A∪B) - disbelief in either A or B
    kappa_A_or_B = ranking.disbelief_rank(lambda x: isinstance(x, tuple) and ('A' in x or 'B' in x))
    print(f"κ(A∪B) = {kappa_A_or_B}")

    print(f"min(κ(A), κ(B)) = {min(kappa_A, kappa_B)}")
    print(f"Law holds: {kappa_A_or_B == min(kappa_A, kappa_B)}")
    print()


def demonstrate_conditional_ranks():
    """
    Demonstrate conditional ranking κ(B|A).

    Conditional ranks represent disbelief in B given that A is true.
    This is computed as κ(A∧B) - κ(A).
    """
    print("=== Conditional Ranks Demonstration ===")
    print("κ(B|A) = κ(A∧B) - κ(A)")
    print()

    # Create a ranking with joint possibilities
    ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

    # κ(A∧B) - disbelief in both A and B being true
    kappa_A_and_B = ranking.disbelief_rank(lambda x: isinstance(x, tuple) and 'A' in x and 'B' in x)
    print(f"κ(A∧B) = {kappa_A_and_B}")

    # κ(A) - disbelief in A being true (regardless of B)
    kappa_A = ranking.disbelief_rank(lambda x: isinstance(x, tuple) and 'A' in x)
    print(f"κ(A) = {kappa_A}")

    # κ(B|A) - conditional disbelief using the method
    kappa_B_given_A = ranking.conditional_disbelief(
        lambda x: isinstance(x, tuple) and 'A' in x,  # Condition: A is true
        lambda x: isinstance(x, tuple) and 'B' in x   # Consequent: B is true
    )
    print(f"κ(B|A) = {kappa_B_given_A}")

    # Manual calculation
    manual_conditional = kappa_A_and_B - kappa_A
    print(f"Manual calculation: κ(A∧B) - κ(A) = {manual_conditional}")
    print(f"Method matches manual: {kappa_B_given_A == manual_conditional}")
    print()


def demonstrate_theory_integration():
    """
    Demonstrate how all three theoretical constructs work together.
    """
    print("=== Theory Integration Demonstration ===")
    print("Combining κ, τ, and conditional ranks")
    print()

    # Complex scenario: medical diagnosis
    # Normal: healthy, Slightly surprising: mild symptoms, Very surprising: severe symptoms
    diagnosis = Ranking(lambda: nrm_exc(
        ('healthy', 'no_symptoms'),
        nrm_exc(
            ('mild_illness', 'mild_symptoms'),
            ('severe_illness', 'severe_symptoms'),
            2
        ),
        1
    ))

    print("Medical diagnosis scenario:")
    print("- Healthy with no symptoms (rank 0)")
    print("- Mild illness with symptoms (rank 1)")
    print("- Severe illness with symptoms (rank 3)")
    print()

    # Analyze different propositions
    propositions = [
        ("Patient is healthy", lambda x: x[0] == 'healthy'),
        ("Patient has symptoms", lambda x: x[1] in ['mild_symptoms', 'severe_symptoms']),
        ("Patient has severe symptoms", lambda x: x[1] == 'severe_symptoms'),
    ]

    for name, prop in propositions:
        kappa = diagnosis.disbelief_rank(prop)
        tau = diagnosis.belief_rank(prop)
        print(f"{name}:")
        print(f"  κ = {kappa} (disbelief rank)")
        print(f"  τ = {tau} (belief rank)")
        print()

    # Conditional analysis
    print("Conditional analysis:")
    kappa_severe_given_symptoms = diagnosis.conditional_disbelief(
        lambda x: x[1] in ['mild_symptoms', 'severe_symptoms'],  # Given symptoms
        lambda x: x[1] == 'severe_symptoms'                      # Severe symptoms
    )
    print(f"κ(severe symptoms | symptoms) = {kappa_severe_given_symptoms}")
    print()


def main():
    """
    Run all theory demonstrations.
    """
    print("🎯 Wolfgang Spohn's Ranking Theory Demonstration")
    print("=" * 50)
    print()

    demonstrate_negative_ranking()
    demonstrate_belief_function()
    demonstrate_law_of_disjunction()
    demonstrate_conditional_ranks()
    demonstrate_theory_integration()

    print("✅ All demonstrations completed!")
    print()
    print("Key Takeaways:")
    print("- κ (disbelief) measures surprise/exceptionalness")
    print("- τ (belief) measures belief strength: positive=belief, negative=disbelief, zero=suspension")
    print("- Conditional ranks κ(B|A) enable reasoning about dependencies")
    print("- Law of disjunction enables efficient computation of alternatives")
    print("- These theoretical constructs provide a foundation for uncertainty reasoning")


if __name__ == "__main__":
    main()
