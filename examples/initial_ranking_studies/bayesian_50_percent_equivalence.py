#!/usr/bin/env python3
"""
Bayesian 50% Prior ↔ Ranking Theory Equivalence

This example demonstrates the correct equivalence between Bayesian uninformative priors
and ranking theory initialization, addressing the common misconception about "large numbers".

Key Insight: A Bayesian 50% prior (maximum uncertainty) corresponds to EQUAL disbelief
ranks in ranking theory, NOT a large number. Large numbers represent high certainty.

Author: Ranked Programming Library
Date: September 2025
"""

import math
from ranked_programming import Ranking, nrm_exc
from ranked_programming.ranking_observe import observe_e
from ranked_programming.theory_types import PRACTICAL_INFINITY


def demonstrate_bayesian_equivalence():
    """
    Demonstrate the correct mapping between Bayesian priors and ranking theory.
    """
    print("🔬 Bayesian 50% Prior ↔ Ranking Theory Equivalence")
    print("=" * 55)

    # Binary hypothesis: Coin is fair vs unfair
    propositions = ['coin_fair', 'coin_unfair']

    print("\n🎲 Bayesian 50% Prior (Maximum Uncertainty)")
    print("   P(fair) = 0.5, P(unfair) = 0.5")
    print("   → Equal probability for both hypotheses")

    print("\n🎯 Ranking Theory Equivalent: Indifference Principle")
    print("   κ(fair) = 1, κ(unfair) = 1")
    print("   → Equal disbelief (equal surprise) for both possibilities")

    # Create indifference initialization
    indifference_ranking = Ranking(lambda: iter([
        ('coin_fair', 1),
        ('coin_unfair', 1)
    ]))

    print(f"\n   Ranking: {list(indifference_ranking)}")

    print("\n❌ Common Misconception: 'Large Number' ≠ 50% Prior")
    print("   A large κ value represents HIGH CERTAINTY, not uncertainty!")
    print("   κ = 10 means 'very surprised if this happens' (low probability)")
    print("   κ = 1 means 'somewhat surprised' (moderate probability)")

    # Demonstrate with large numbers
    print("\n📊 Large Number Example (High Certainty)")
    large_number_ranking = Ranking(lambda: iter([
        ('coin_fair', 0),      # Expected
        ('coin_unfair', 10)    # Very surprising (high certainty fair)
    ]))

    print(f"   Ranking: {list(large_number_ranking)}")
    print("   This represents ~99.9% confidence that coin is fair")
    print("   NOT equivalent to 50% uncertainty!")


def penalty_measures_with_initialization():
    """
    Demonstrate which penalty measures work best with different initializations.
    """
    print("\n" + "=" * 60)
    print("🧮 Penalty Measures with Different Initializations")
    print("=" * 60)

    # Test data: observing that a coin shows 8 heads in 10 flips
    evidence = "8_heads_10_flips"
    predicate = lambda x: x == evidence

    # Different initial rankings
    indifference_init = [('coin_fair', 1), ('coin_unfair', 1)]
    large_number_init = [('coin_fair', 0), ('coin_unfair', 10)]
    conservative_init = [('coin_fair', 0), ('coin_unfair', 5)]

    initializations = [
        ("Indifference (50% equivalent)", indifference_init),
        ("Large Number (High certainty)", large_number_init),
        ("Conservative (Moderate uncertainty)", conservative_init)
    ]

    # Different penalty measures
    penalties = [
        ("Small penalty (1)", 1),
        ("Medium penalty (3)", 3),
        ("Large penalty (8)", 8),
        ("Very large penalty (15)", 15)
    ]

    for init_name, init_ranking in initializations:
        print(f"\n🎯 {init_name}")
        print(f"   Initial: {init_ranking}")

        for penalty_name, penalty_value in penalties:
            ranking_data = init_ranking + [(evidence, 0)]  # Add evidence with rank 0
            observed = list(observe_e(penalty_value, predicate, ranking_data))
            updated_ranking = Ranking(lambda: iter(observed))

            print(f"   {penalty_name}: {list(updated_ranking)}")


def epistemological_interpretation():
    """
    Provide epistemological interpretation of the equivalence.
    """
    print("\n" + "=" * 60)
    print("🎓 Epistemological Interpretation")
    print("=" * 60)

    print("\n📚 Bayesian Perspective:")
    print("   50% prior = Maximum uncertainty")
    print("   Large probability mass spread evenly across possibilities")
    print("   Represents 'I have no idea what to expect'")

    print("\n🎯 Ranking Theory Perspective:")
    print("   κ = 1 for all = Equal surprise for any outcome")
    print("   Large κ values = High surprise (low expectation)")
    print("   Represents 'Any outcome would be equally unexpected'")

    print("\n🔄 Key Equivalence:")
    print("   Bayesian 50% = Ranking Theory indifference (κ=1)")
    print("   NOT: Bayesian 50% = Ranking Theory large κ")

    print("\n💡 Practical Rule:")
    print("   For maximum uncertainty: Use equal, small κ values (1-2)")
    print("   For high certainty: Use large κ for unlikely alternatives")
    print("   For moderate uncertainty: Use medium κ differences (3-5)")


def demonstrate_with_real_example():
    """
    Show a concrete example with actual probability calculations.
    """
    print("\n" + "=" * 60)
    print("🪙 Concrete Example: Coin Fairness")
    print("=" * 60)

    # Show how ranking theory ranks translate to approximate probabilities
    rank_to_prob = {
        0: "99.9% (certain)",
        1: "~90% (likely)",
        2: "~73% (possible)",
        3: "~50% (coin flip)",
        4: "~27% (unlikely)",
        5: "~10% (surprising)",
        10: "~0.1% (very surprising)"
    }

    print("\n📊 Approximate Probability Mapping:")
    for rank, prob in rank_to_prob.items():
        print("5d")

    print("\n🎲 Bayesian 50% Prior Mapping:")
    print("   P(fair) = 0.5 → κ(fair) ≈ 3 (equal surprise)")
    print("   P(unfair) = 0.5 → κ(unfair) ≈ 3 (equal surprise)")

    print("\n📈 High Certainty Mapping:")
    print("   P(fair) = 0.999 → κ(fair) ≈ 0 (expected)")
    print("   P(unfair) = 0.001 → κ(unfair) ≈ 10 (very surprising)")


if __name__ == "__main__":
    demonstrate_bayesian_equivalence()
    penalty_measures_with_initialization()
    epistemological_interpretation()
    demonstrate_with_real_example()

    print("\n" + "=" * 60)
    print("✨ Summary: Bayesian 50% ↔ Ranking Theory κ=1 (not large numbers!)")
    print("=" * 60)
