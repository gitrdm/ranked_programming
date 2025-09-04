#!/usr/bin/env python3
"""
Evidence Accumulation and Rank Scale Analysis

This analysis examines:
1. What constitutes "large" disbelief ranks in ranked programming
2. How much evidence is needed to reduce surprise to belief
3. Practical interpretation of rank magnitudes

Author: Ranked Programming Library
Date: September 2025
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ranked_programming import Ranking, observe_e, nrm_exc


def rank_scale_interpretation():
    """
    Interpret what different rank magnitudes typically mean.
    """
    print("📏 Rank Scale Interpretation")
    print("=" * 40)

    print("\n🔢 TYPICAL RANK MAGNITUDES:")
    print("   κ = 0:  Expected/normal outcome")
    print("   κ = 1:  Slightly surprising")
    print("   κ = 2:  Moderately surprising")
    print("   κ = 3:  Very surprising")
    print("   κ = 4:  Extremely surprising")
    print("   κ = 5:  Highly improbable")
    print("   κ = 6:  Very rare/exceptional")
    print("   κ = 7:  Extraordinary circumstances")
    print("   κ = 8:  Practically impossible")
    print("   κ = 9:  Theoretically unlikely")
    print("   κ = 10+: Extraordinary/impossible")

    print("\n📊 RELATIVE SURPRISE LEVELS:")
    print("   κ = 1 vs κ = 0:  'Hmm, that's odd'")
    print("   κ = 3 vs κ = 0:  'That's very surprising!'")
    print("   κ = 5 vs κ = 0:  'I can't believe this happened!'")
    print("   κ = 8 vs κ = 0:  'This defies all expectations!'")

    print("\n🎯 PRACTICAL CONTEXT:")
    print("   • κ ≤ 3:  Manageable surprise levels")
    print("   • κ = 4-6:  Significant but possible surprises")
    print("   • κ = 7-10: Extraordinary events")
    print("   • κ > 10:  Practically impossible scenarios")


def evidence_accumulation_mechanics():
    """
    Demonstrate how evidence reduces disbelief ranks.
    """
    print("\n" + "=" * 60)
    print("⚡ Evidence Accumulation Mechanics")
    print("=" * 60)

    print("\n📚 BASIC PRINCIPLE:")
    print("   Evidence reduces disbelief through ordinal subtraction")
    print("   observe_e(evidence_rank) reduces disbelief by evidence strength")

    print("\n🔄 EVIDENCE REDUCTION PROCESS:")
    print("   Initial disbelief: κ = κ₀")
    print("   Evidence strength: ε = evidence_rank")
    print("   New disbelief: κ' = max(0, κ₀ - ε)")

    print("\n📊 CONCRETE EXAMPLES:")

    # Example 1: Moderate surprise
    initial_rank = 3
    evidence_strength = 2
    final_rank = max(0, initial_rank - evidence_strength)

    print(f"\n1️⃣ Moderate Surprise Reduction:")
    print(f"   Initial: κ = {initial_rank} (very surprising)")
    print(f"   Evidence: ε = {evidence_strength} (strong evidence)")
    print(f"   Final:   κ = {final_rank} (now expected)")
    print(f"   Change:  {initial_rank} → {final_rank} (reduced by {evidence_strength})")

    # Example 2: High surprise
    initial_rank = 5
    evidence_strength = 3
    final_rank = max(0, initial_rank - evidence_strength)

    print(f"\n2️⃣ High Surprise Reduction:")
    print(f"   Initial: κ = {initial_rank} (highly improbable)")
    print(f"   Evidence: ε = {evidence_strength} (very strong evidence)")
    print(f"   Final:   κ = {final_rank} (moderately surprising)")
    print(f"   Change:  {initial_rank} → {final_rank} (reduced by {evidence_strength})")

    # Example 3: Complete belief
    initial_rank = 5
    evidence_strength = 5
    final_rank = max(0, initial_rank - evidence_strength)

    print(f"\n3️⃣ Complete Belief Achievement:")
    print(f"   Initial: κ = {initial_rank} (highly improbable)")
    print(f"   Evidence: ε = {evidence_strength} (overwhelming evidence)")
    print(f"   Final:   κ = {final_rank} (now completely believed)")
    print(f"   Change:  {initial_rank} → {final_rank} (reduced by {evidence_strength})")


def multiple_evidence_scenario():
    """
    Show how multiple pieces of evidence accumulate.
    """
    print("\n" + "=" * 60)
    print("🔄 Multiple Evidence Accumulation")
    print("=" * 60)

    print("\n📈 CUMULATIVE EVIDENCE EXAMPLE:")
    print("   Starting with κ = 8 (extraordinary event)")
    print("   Receiving multiple pieces of evidence...")

    current_rank = 8
    evidence_pieces = [2, 1, 3, 2]  # Different strengths of evidence

    print(f"\n   Initial disbelief: κ = {current_rank}")

    for i, evidence in enumerate(evidence_pieces, 1):
        new_rank = max(0, current_rank - evidence)
        reduction = current_rank - new_rank
        print(f"   Evidence {i} (ε={evidence}): κ = {current_rank} → {new_rank} (reduced by {reduction})")
        current_rank = new_rank

    print(f"\n   Final disbelief: κ = {current_rank}")
    print(f"   Total evidence strength: {sum(evidence_pieces)}")
    print(f"   Total reduction: {8 - current_rank}")


def practical_evidence_thresholds():
    """
    Show practical thresholds for different surprise levels.
    """
    print("\n" + "=" * 60)
    print("🎯 Practical Evidence Thresholds")
    print("=" * 60)

    print("\n📋 EVIDENCE NEEDED FOR COMPLETE BELIEF:")

    surprise_levels = [
        (1, "Slightly surprising"),
        (2, "Moderately surprising"),
        (3, "Very surprising"),
        (4, "Extremely surprising"),
        (5, "Highly improbable"),
        (6, "Very rare"),
        (7, "Extraordinary"),
        (8, "Practically impossible")
    ]

    print("   Surprise Level (κ) | Description | Evidence for κ→0")
    print("   ───────────────────┼─────────────┼─────────────────")

    for rank, description in surprise_levels:
        evidence_needed = rank  # To reach κ=0
        print(f"   {rank:>17}  │ {description:<19} │ {evidence_needed}")

    print("\n💡 KEY INSIGHTS:")
    print("   • Evidence strength needed = initial disbelief rank")
    print("   • Multiple weaker evidences can accumulate")
    print("   • Evidence can be stronger than needed (overshoot to κ=0)")
    print("   • No upper limit on evidence strength")


def ranking_combination_effects():
    """
    Show how ranking combination affects evidence requirements.
    """
    print("\n" + "=" * 60)
    print("🔗 Ranking Combination Effects")
    print("=" * 60)

    print("\n🏗️ COMBINATION SCENARIOS:")

    print("\n1️⃣ INDEPENDENT EVIDENCE COMBINATION:")
    print("   Two independent surprising events:")
    print("   κ₁ = 3, κ₂ = 3")
    print("   Combined disbelief: κ₁ + κ₂ = 6")
    print("   Evidence needed for complete belief: 6+")

    print("\n2️⃣ CONDITIONAL RANKING:")
    print("   If A is true, then B becomes less surprising:")
    print("   κ(A) = 2, κ(B|A) = 1")
    print("   Combined: κ(A ∧ B) = κ(A) + κ(B|A) = 3")
    print("   Evidence needed: 3")

    print("\n3️⃣ EVIDENCE STRENGTHENING:")
    print("   Strong evidence can reduce multiple disbeliefs:")
    print("   Multiple hypotheses with κ=2 each")
    print("   One strong evidence (ε=5) can confirm all of them")

    print("\n📊 PRACTICAL IMPLICATION:")
    print("   • Combination can increase total surprise")
    print("   • Evidence requirements scale with combination complexity")
    print("   • Strong evidence can efficiently resolve multiple uncertainties")


def real_world_calibration():
    """
    Provide real-world examples of rank calibration.
    """
    print("\n" + "=" * 60)
    print("🌍 Real-World Rank Calibration")
    print("=" * 60)

    print("\n🏥 MEDICAL DIAGNOSIS EXAMPLE:")
    print("   κ('common_cold') = 0          # Expected")
    print("   κ('unusual_symptoms') = 2     # Moderately surprising")
    print("   κ('rare_disease') = 5         # Highly improbable")
    print("   ")
    print("   Evidence needed for belief:")
    print("   • For unusual symptoms: 2 pieces of confirming evidence")
    print("   • For rare disease: 5 pieces of strong evidence")
    print("   • Could be: lab results + symptoms + medical history + specialist opinion + treatment response")

    print("\n🔍 SCIENTIFIC DISCOVERY EXAMPLE:")
    print("   κ('expected_result') = 0      # Based on theory")
    print("   κ('anomalous_result') = 4     # Surprising but possible")
    print("   κ('paradigm_shifting') = 8    # Extraordinary")
    print("   ")
    print("   Evidence accumulation:")
    print("   • Initial anomaly: needs 4 confirmations")
    print("   • Paradigm shift: needs 8+ independent verifications")
    print("   • Each peer review, replication, theoretical explanation counts as evidence")

    print("\n💻 SOFTWARE TESTING EXAMPLE:")
    print("   κ('normal_execution') = 0     # Expected behavior")
    print("   κ('minor_bug') = 2            # Common issue")
    print("   κ('critical_failure') = 6     # Serious problem")
    print("   ")
    print("   Evidence for resolution:")
    print("   • Minor bug: 2 test cases showing fix")
    print("   • Critical failure: 6 comprehensive tests + code review + user validation")


def scale_practicality_analysis():
    """
    Analyze the practicality of different rank scales.
    """
    print("\n" + "=" * 60)
    print("⚖️ Scale Practicality Analysis")
    print("=" * 60)

    print("\n📏 RECOMMENDED SCALES BY DOMAIN:")

    print("\n🎲 GAMES/AI:")
    print("   Typical range: κ = 0-10")
    print("   Evidence accumulation: Fast-paced, many small evidences")
    print("   Example: Game states, move evaluations")

    print("\n🏥 MEDICAL/HEALTHCARE:")
    print("   Typical range: κ = 0-8")
    print("   Evidence accumulation: Careful, high-stakes")
    print("   Example: Diagnosis, treatment decisions")

    print("\n🔬 SCIENTIFIC RESEARCH:")
    print("   Typical range: κ = 0-12")
    print("   Evidence accumulation: Rigorous, peer-reviewed")
    print("   Example: Hypothesis testing, experimental validation")

    print("\n💼 BUSINESS/DECISION MAKING:")
    print("   Typical range: κ = 0-6")
    print("   Evidence accumulation: Practical, time-sensitive")
    print("   Example: Risk assessment, investment decisions")

    print("\n✅ PRACTICAL GUIDELINES:")
    print("   • Most applications: κ = 0-8 range")
    print("   • High-precision domains: κ = 0-12 range")
    print("   • Simple applications: κ = 0-5 range")
    print("   • Evidence strength typically matches or exceeds surprise level")


if __name__ == "__main__":
    rank_scale_interpretation()
    evidence_accumulation_mechanics()
    multiple_evidence_scenario()
    practical_evidence_thresholds()
    ranking_combination_effects()
    real_world_calibration()
    scale_practicality_analysis()
