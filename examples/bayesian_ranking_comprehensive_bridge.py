#!/usr/bin/env python3
"""
Bayesian↔Ranking Bridge (Exploration Toolkit)
============================================

Purpose
-------
This standalone example helps users build intuition for how Bayesian probabilities
relate to Ranking Theory ranks (κ), and lets you explore different mapping
assumptions. It does not execute the library’s ranking combinators; instead it
provides small mathematical helpers and demos.

What you can do here
--------------------
- Use a recommended default mapping where one rank unit ≈ one bit of evidence
    (likelihood ratio ×2 per unit). This yields a compact, intuitive working range:
    0..10 covers 50% → ~99.9%.
- Switch to alternative mappings to see how choices affect the “feel” of ranks.
    For rare events, a κ≈−log_b(p) style approximation may be more intuitive.

Core helpers
------------
- Log-odds bit mapping (recommended default):
    k_bits(p) ≈ log_b(p/(1−p)), with b=2 by default.
    p(k_bits) = 1 / (1 + b^(−k_bits)).
- Kappa-style (rare-event) mapping:
    κ(p) ≈ round(−log_b(p)) when p is small (disbelief of event).
    p(κ) ≈ b^(−κ).

Use this file to experiment with ranges (e.g., 0..10 vs 0..12), evidence factors
(LR per unit), and table presentations so new users can get a “feel” for ranks.

Author: Ranked Programming examples
Date: September 2025
"""

import math
from typing import List, Tuple, Dict, Callable, Optional


def bayesian_update(prior: float, likelihood_ratio: float) -> float:
    """
    Perform Bayesian update using likelihood ratio.

    Args:
        prior: Prior probability P(H)
        likelihood_ratio: Likelihood ratio LR = P(E|H)/P(E|¬H)

    Returns:
        Posterior probability P(H|E)
    """
    return (prior * likelihood_ratio) / (prior * likelihood_ratio + (1 - prior))


def ranking_update(disbelief_rank: int, evidence_strength: int) -> int:
    """
    Perform ranking theory update using ordinal arithmetic.

    Args:
        disbelief_rank: Current disbelief rank κ
        evidence_strength: Evidence strength ε

    Returns:
        Updated disbelief rank κ' = max(0, κ - ε)
    """
    return max(0, disbelief_rank - evidence_strength)


def log_odds_bits_from_p(p: float, base: float = 2.0) -> float:
    """Return log-base odds bits: k_bits = log_b(p/(1-p)).

    Recommended default mapping unit: one bit (base=2).
    Monotone: higher p → higher k_bits; k_bits=0 at p=0.5.
    """
    if p <= 0.0:
        return float('-inf')
    if p >= 1.0:
        return float('inf')
    odds = p / (1.0 - p)
    return math.log(odds, base)


def p_from_log_odds_bits(k_bits: float, base: float = 2.0) -> float:
    """Inverse of log_odds_bits_from_p: p = 1 / (1 + b^(−k_bits))."""
    return 1.0 / (1.0 + (base ** (-k_bits)))


def kappa_from_p_rare_event(p: float, base: float = 2.0) -> float:
    """Approximate κ for rare event disbelief: κ ≈ −log_b(p).

    Useful when p is small and κ models disbelief in the event.
    Not ideal near 50% or high p.
    """
    if p <= 0.0:
        return float('inf')
    if p >= 1.0:
        return 0.0
    return -math.log(p, base)


def p_from_kappa_rare_event(kappa: float, base: float = 2.0) -> float:
    """Inverse of kappa_from_p_rare_event: p ≈ b^(−κ)."""
    if math.isinf(kappa):
        return 0.0
    return base ** (-kappa)


def generate_bridge_table(
    mapping: str = "log_odds_bits",
    base: float = 2.0,
    sample_probs: Optional[List[float]] = None,
    round_to: Optional[int] = 0,
) -> List[Dict]:
    """Generate a mapping table under a chosen assumption.

    Args:
        mapping: 'log_odds_bits' (default) or 'rare_event_kappa'.
        base: evidence base (2 → one bit per unit).
        sample_probs: probabilities to include; default uses canonical set.
        round_to: if not None, round displayed ranks to this many decimals
                  (0 for integers), otherwise show raw floats.

    Returns: list of rows for display or further processing.
    """
    print("\n🔄 GENERATING BAYESIAN↔RANKING BRIDGE TABLE")
    print("=" * 60)

    if sample_probs is None:
        sample_probs = [
            0.99, 0.95, 0.90, 0.80, 0.70,
            0.60, 0.50, 0.40, 0.30, 0.20,
            0.10, 0.05, 0.01,
        ]

    print(f"Mapping: {mapping} (base={base})")
    print("Bayesian Probability ↔ Rank-like Measure")
    print("-" * 50)

    rows: List[Dict] = []
    for p in sample_probs:
        if mapping == "log_odds_bits":
            k = log_odds_bits_from_p(p, base)
        elif mapping == "rare_event_kappa":
            k = kappa_from_p_rare_event(p, base)
        else:
            raise ValueError("Unknown mapping")

        k_disp = round(k, round_to) if round_to is not None and math.isfinite(k) else k
        print(f"{p:5.2%} → k={k_disp}")
        rows.append({
            'probability': p,
            'rank_like': k,
            'mapping': mapping,
            'base': base,
        })

    return rows
    print("🔄 GENERATING BAYESIAN-RANKING BRIDGE TABLE")
    print("=" * 60)

    # Define probability thresholds and their ranking equivalents
    probability_levels = [
        (0.99, "Complete Belief", 0),
        (0.95, "Very Strong", 1),
        (0.90, "Strong", 2),
        (0.80, "Moderate", 3),
        (0.70, "Weak", 4),
        (0.60, "Very Weak", 5),
        (0.50, "Complete Uncertainty", 6),
        (0.40, "Weak Disbelief", 7),
        (0.30, "Moderate Disbelief", 8),
        (0.20, "Strong Disbelief", 9),
        (0.10, "Very Strong Disbelief", 10),
        (0.05, "Extreme Disbelief", 11),
        (0.01, "Complete Disbelief", 12),
    ]

    bridge_data = []

    print("Bayesian Probability ↔ Ranking Disbelief Rank")
    print("-" * 50)
    print("Probability | Confidence Level | κ (Disbelief Rank)")
    print("-" * 50)

    for prob, level, rank in probability_levels:
        print(f"{prob:4.2f} | {level:<15} | {rank:2d}")
        bridge_data.append({
            'probability': prob,
            'confidence_level': level,
            'disbelief_rank': rank
        })

    print("-" * 50)
    return bridge_data


def demonstrate_evidence_accumulation():
    """
    Demonstrate how evidence accumulation works in both frameworks.
    Shows the transformation from 50% prior to high confidence with 5 evidence units.
    """
    print("\n📊 EVIDENCE ACCUMULATION DEMONSTRATION (LR×2 per unit)")
    print("=" * 60)

    # Starting conditions
    initial_prior = 0.5  # 50% uncertainty
    initial_rank = 6     # Complete uncertainty in ranking terms
    evidence_units = 5

    print("Starting from 50% prior probability (neutral log-odds = 0)")
    print("Recommended working range: 0..10 units spans 50% → ~99.9%")
    print()

    # Bayesian accumulation
    print("BAYESIAN ACCUMULATION (LR = 2^evidence_units):")
    print("Evidence | Likelihood Ratio | Posterior Probability")
    print("-" * 50)

    for i in range(evidence_units + 1):
        lr = 2 ** i
        posterior = bayesian_update(initial_prior, lr)
        status = "→" if i == evidence_units else "  "
        print(f"{i:2d}       | {lr:3.0f}              | {posterior:5.1%} {status}")

    print()
    print("RANKING ACCUMULATION (κ' = max(0, κ - ε)):")
    print("Evidence | Disbelief Rank | Confidence Level")
    print("-" * 50)

    # Log-odds bits view: units add linearly in bits
    print()
    print("LOG-ODDS BITS (k_bits) with base=2:")
    print("Evidence | k_bits | Implied P")
    print("-" * 40)
    for i in range(evidence_units + 1):
        p = bayesian_update(0.5, 2 ** i)
        k_bits = log_odds_bits_from_p(p, 2.0)
        status = "→" if i == evidence_units else "  "
        print(f"{i:2d}       | {int(round(k_bits)):6d} | {p:5.1%} {status}")

    print()
    print("🎯 RESULT: 5 evidence units transform 50% to ~97% (k_bits≈5).")


def explain_factor_of_two():
    """
    Comprehensive explanation of why the factor of 2 is used in Bayesian calculations.
    Shows that it's not arbitrary but grounded in multiple justifications.
    """
    print("\n🔢 WHY THE FACTOR OF 2? (Not a 'Magic' Number)")
    print("=" * 60)

    print("The likelihood ratio LR = 2^evidence_units is justified by:")
    print()

    # 1. Conceptual Origin
    print("🎯 1. CONCEPTUAL ORIGIN:")
    print("   • Represents a 'meaningful unit of evidence'")
    print("   • Answers: 'How much does one piece of evidence change belief?'")
    print("   • Intuitive: each evidence unit makes you 'twice as sure'")
    print()

    # 2. Information Theory
    print("📐 2. INFORMATION-THEORETIC GROUNDING:")
    print("   • 1 bit of information can distinguish between 2 possibilities")
    print("   • Likelihood ratio of 2 represents exactly 1 bit of evidence")
    print("   • Each evidence unit provides 1 bit of discriminatory information")
    print()

    # 3. Mathematical Properties
    print("🧮 3. MATHEMATICAL SIMPLICITY:")
    print("   • Powers of 2 are computationally efficient")
    print("   • Clear, predictable progression: 2^1=2, 2^2=4, 2^3=8, 2^4=16, 2^5=32")
    print("   • Easy to understand and communicate")
    print()

    # 4. Empirical Realism
    print("🌍 4. EMPIRICAL REALISM:")
    print("   • Medical diagnosis: Single symptom LR ≈ 2-3")
    print("   • Scientific evidence: Single study LR ≈ 2-5")
    print("   • Business decisions: Customer feedback LR ≈ 1.5-2")
    print("   • Legal evidence: Single witness LR ≈ 2-5")
    print()

    # 5. Alternative Factors Comparison
    print("📈 5. ALTERNATIVE FACTORS COMPARISON:")
    print("   Starting from P(H) = 0.5, different scaling factors:")
    print()
    print("   Factor | 1 unit | 2 units | 3 units | 4 units | 5 units")
    print("   ───────┼────────┼─────────┼─────────┼─────────┼─────────")

    factors = [1.5, 2.0, 3.0, 4.0, 10.0]
    for factor in factors:
        probs = []
        for units in range(1, 6):
            lr = factor ** units
            prob = bayesian_update(0.5, lr)
            probs.append(f"{prob:5.1%}")
        print(f"{factor:6.1f} | {' | '.join(probs)}")

    print()
    print("   💡 OBSERVATIONS:")
    print("   • Factor 1.5: Slow, gradual increase (conservative)")
    print("   • Factor 2.0: Balanced progression (moderate)")
    print("   • Factor 3.0: Faster convergence (aggressive)")
    print("   • Factor 4.0: Very fast convergence (optimistic)")
    print("   • Factor 10.0: Extremely fast (overly optimistic)")
    print()

    # 6. Bayesian Updating Properties
    print("🔄 6. BAYESIAN UPDATING PROPERTIES:")
    print("   • Preserves the mathematical structure of Bayesian inference")
    print("   • Maintains consistency with likelihood ratio interpretation")
    print("   • Allows meaningful comparison with ranking theory")
    print("   • Enables systematic evidence accumulation modeling")
    print()

    print("✅ CONCLUSION:")
    print("   The factor of 2 is a well-grounded modeling choice that balances")
    print("   mathematical tractability, conceptual intuitiveness, and empirical")
    print("   realism. It's not 'magic' but justified by information theory,")
    print("   real-world evidence patterns, and mathematical properties.")


def demonstrate_systematic_approaches():
    """
    Demonstrate different systematic approaches for choosing disbelief ranks
    without relying on logarithmic conversions.
    """
    print("\n🎯 SYSTEMATIC APPROACHES FOR CHOOSING DISBELIEF RANKS")
    print("=" * 60)

    print("Different methods to map probabilities to rank-like measures:")
    print()

    # Method 1: Threshold-based
    print("📊 METHOD 1: THRESHOLD-BASED MAPPING")
    thresholds = [  # pedagogical thresholds (optional)
        (0.99, 0, "Complete Belief"),
        (0.95, 1, "Very Strong"),
        (0.90, 2, "Strong"),
        (0.80, 3, "Moderate"),
        (0.70, 4, "Weak"),
        (0.60, 5, "Very Weak"),
        (0.50, 6, "Complete Uncertainty"),
        (0.40, 7, "Weak Disbelief"),
        (0.30, 8, "Moderate Disbelief"),
        (0.20, 9, "Strong Disbelief"),
        (0.10, 10, "Very Strong Disbelief"),
        (0.05, 11, "Extreme Disbelief"),
        (0.01, 12, "Complete Disbelief")
    ]

    for prob, rank, level in thresholds:
        print(f"{prob:5.2f} → κ = {rank:2d} ({level})")

    print()

    # Method 2: Evidence-based
    print("🔍 METHOD 2: EVIDENCE-BASED MAPPING")
    print("   Map based on how many evidence units needed to reach confidence:")
    print()
    print("   Target Probability | Evidence Units Needed | κ Rank")
    print("   ───────────────────┼───────────────────────┼────────")

    targets = [0.9, 0.95, 0.99]
    for target in targets:
        # Calculate how many evidence units needed
        units = 0
        prob = 0.5
        while prob < target and units < 10:
            units += 1
            prob = bayesian_update(0.5, 2**units)

        rank = max(0, 6 - units)  # Start from κ=6, reduce by evidence units
        print(f"{target:10.2f}              | {units:2d}                   | {rank:2d}")

    print()

    # Method 3: Ordinal scaling
    print("📏 METHOD 3: ORDINAL SCALING")
    print("   Use ordinal arithmetic properties directly:")
    print("   • κ = 0: Complete belief (no doubt)")
    print("   • κ = 1: Very strong belief")
    print("   • κ = 2: Strong belief")
    print("   • κ = 3: Moderate belief")
    print("   • κ = 4: Weak belief")
    print("   • κ = 5: Very weak belief")
    print("   • κ = 6: Complete uncertainty")
    print("   • κ ≥ 7: Strong disbelief")


def main():
    """
    Main function that runs the comprehensive Bayesian-Ranking bridge analysis.
    """
    print("🎯 BAYESIAN-RANKING PROGRAMMING COMPREHENSIVE BRIDGE")
    print("=" * 70)
    print()
    print("This analysis bridges Bayesian probability theory with ranked programming's")
    print("ordinal disbelief ranks, showing their epistemological equivalence.")
    print()

    # Generate the main bridge table
    bridge_data = generate_bridge_table()

    # Demonstrate evidence accumulation
    demonstrate_evidence_accumulation()

    # Explain the factor of 2
    explain_factor_of_two()

    # Show systematic approaches
    demonstrate_systematic_approaches()

    print("\n" + "=" * 70)
    print("🎉 ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print("Key Insights:")
    print("• 5 evidence units transform 50% uncertainty to 97% confidence (Bayesian)")
    print("• Same 5 units reduce κ=6 to κ=1 (very strong belief in ranking terms)")
    print("• The factor of 2 is justified by information theory and empirical patterns")
    print("• Both frameworks agree on the transformative power of evidence accumulation")


if __name__ == "__main__":
    main()
