#!/usr/bin/env python3
"""
Practical Evidence Accumulation Demo

Demonstrates how disbelief ranks change with evidence using the actual
ranked programming library.

Author: Ranked Programming Library
Date: September 2025
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ranked_programming import Ranking, observe_e
from ranked_programming.ranking_combinators import nrm_exc


def demonstrate_evidence_accumulation():
    """
    Show practical evidence accumulation with real Ranking objects.
    """
    print("🔬 Practical Evidence Accumulation Demo")
    print("=" * 50)

    print("\n🎯 STARTING SCENARIO:")
    print("   Hypothesis: 'It will rain tomorrow' with high surprise")
    initial_ranking = Ranking(lambda: nrm_exc(True, False, 5))  # Highly improbable
    print(f"   Initial disbelief rank: κ = {list(initial_ranking)[1][1]}")
    print("   Interpretation: 'This would be very surprising!'")

    print("\n📊 EVIDENCE ACCUMULATION PROCESS:")

    # Evidence 1: Weather forecast shows 80% chance
    evidence1 = lambda: nrm_exc(True, False, 0)  # Strong evidence for rain
    updated1 = Ranking(lambda: observe_e(2, lambda x: x == True, initial_ranking))
    print(f"\n1️⃣ Evidence 1 - Weather forecast (ε=2):")
    print(f"   Before: κ = {list(initial_ranking)[1][1]}")
    print(f"   After:  κ = {list(updated1)[0][1]}")
    print("   Change: Reduced by 2 (still quite surprising)")

    # Evidence 2: Dark clouds observed
    evidence2 = lambda: nrm_exc(True, False, 0)  # Evidence for rain
    updated2 = Ranking(lambda: observe_e(1, lambda x: x == True, updated1))
    print(f"\n2️⃣ Evidence 2 - Dark clouds (ε=1):")
    print(f"   Before: κ = {list(updated1)[0][1]}")
    print(f"   After:  κ = {list(updated2)[0][1]}")
    print("   Change: Reduced by 1 (moderately surprising)")

    # Evidence 3: Barometer dropping significantly
    evidence3 = lambda: nrm_exc(True, False, 0)  # Strong evidence for rain
    updated3 = Ranking(lambda: observe_e(3, lambda x: x == True, updated2))
    print(f"\n3️⃣ Evidence 3 - Barometer drop (ε=3):")
    print(f"   Before: κ = {list(updated2)[0][1]}")
    print(f"   After:  κ = {list(updated3)[0][1]}")
    print("   Change: Reduced by 3 (now expected!)")

    print("\n✅ FINAL RESULT:")
    print(f"   Started with: κ = {list(initial_ranking)[1][1]} (highly improbable)")
    print(f"   Ended with:   κ = {list(updated3)[0][1]} (completely believed)")
    print(f"   Total evidence: {2 + 1 + 3} = 6 units")
    print("   Transformation: Surprise → Belief through evidence accumulation")

def demonstrate_overshoot():
    """
    Show what happens when evidence is stronger than needed.
    """
    print("\n" + "=" * 50)
    print("💪 Evidence Overshoot Demonstration")
    print("=" * 50)

    print("\n🎯 SCENARIO: Minor surprise with overwhelming evidence")

    initial = Ranking(2)  # Moderately surprising
    evidence = Ranking(5)  # Very strong evidence (stronger than needed)
    result = observe_e(initial, evidence)

    print(f"   Initial surprise: κ = {initial.disbelief_rank()}")
    print(f"   Evidence strength: ε = {evidence.disbelief_rank()}")
    print(f"   Result: κ = {result.disbelief_rank()}")
    print("   Note: Evidence was stronger than needed, but result is still κ=0"
    print("   (you can't get 'more than believed' - it floors at 0)"

def demonstrate_multiple_hypotheses():
    """
    Show evidence affecting multiple related hypotheses.
    """
    print("\n" + "=" * 50)
    print("🔗 Multiple Hypotheses Evidence")
    print("=" * 50)

    print("\n🎯 SCENARIO: Three related surprising events")

    # Three independent surprising hypotheses
    hyp1 = Ranking(3)  # Very surprising
    hyp2 = Ranking(3)  # Very surprising
    hyp3 = Ranking(3)  # Very surprising

    print("   Three independent hypotheses:")
    print(f"   H₁: κ = {hyp1.disbelief_rank()}")
    print(f"   H₂: κ = {hyp2.disbelief_rank()}")
    print(f"   H₃: κ = {hyp3.disbelief_rank()}")

    # Strong evidence that affects all three
    strong_evidence = Ranking(4)  # Very strong evidence

    result1 = observe_e(hyp1, strong_evidence)
    result2 = observe_e(hyp2, strong_evidence)
    result3 = observe_e(hyp3, strong_evidence)

    print("
   After strong evidence (ε=4):"    print(f"   H₁: κ = {result1.disbelief_rank()}")
    print(f"   H₂: κ = {result2.disbelief_rank()}")
    print(f"   H₃: κ = {result3.disbelief_rank()}")
    print("   All reduced significantly by the same evidence!"

def demonstrate_evidence_thresholds():
    """
    Show exact evidence needed for different surprise levels.
    """
    print("\n" + "=" * 50)
    print("🎯 Exact Evidence Thresholds")
    print("=" * 50)

    print("\n📋 EVIDENCE REQUIRED TO REACH COMPLETE BELIEF:")

    test_cases = [
        (1, "Slightly surprising"),
        (2, "Moderately surprising"),
        (3, "Very surprising"),
        (4, "Extremely surprising"),
        (5, "Highly improbable"),
        (6, "Very rare"),
        (7, "Extraordinary"),
        (8, "Practically impossible")
    ]

    for initial_rank, description in test_cases:
        initial = Ranking(initial_rank)
        evidence = Ranking(initial_rank)  # Exact evidence needed
        result = observe_e(initial, evidence)

        print("2d"
              "2d"
              "d")

    print("\n💡 KEY OBSERVATIONS:")
    print("   • Exact evidence (ε = κ) reduces surprise to belief")
    print("   • Stronger evidence (ε > κ) also works (overshoot)")
    print("   • Weaker evidence (ε < κ) reduces but doesn't eliminate surprise")


def demonstrate_gradual_accumulation():
    """
    Show how many small evidences can accumulate to overcome high surprise.
    """
    print("\n" + "=" * 50)
    print("📈 Gradual Evidence Accumulation")
    print("=" * 50)

    print("\n🎯 SCENARIO: High surprise overcome by many small evidences")

    initial = Ranking(8)  # Practically impossible
    print(f"   Starting disbelief: κ = {initial.disbelief_rank()}")

    # Many small pieces of evidence
    small_evidences = [Ranking(1) for _ in range(8)]  # 8 pieces of weak evidence

    current = initial
    total_evidence = 0

    print("\n   Accumulating evidence step by step:")
    for i, evidence in enumerate(small_evidences, 1):
        previous = current.disbelief_rank()
        current = observe_e(current, evidence)
        new_rank = current.disbelief_rank()
        reduction = previous - new_rank
        total_evidence += 1

        print("2d"
              "d"
              "d"
              "d")

        if new_rank == 0:
            print(f"   🎉 Belief achieved after {i} pieces of evidence!")
            break

    print("
✅ FINAL RESULT:"    print(f"   Started with: κ = {initial.disbelief_rank()} (practically impossible)")
    print(f"   Ended with:   κ = {current.disbelief_rank()} (completely believed)")
    print(f"   Total evidence pieces: {total_evidence}")
    print("   Many small evidences can overcome high surprise!"


if __name__ == "__main__":
    demonstrate_evidence_accumulation()
    demonstrate_overshoot()
    demonstrate_multiple_hypotheses()
    demonstrate_evidence_thresholds()
    demonstrate_gradual_accumulation()
