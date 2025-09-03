"""
Ranked Let with Multiple Penalty Analysis

This example demonstrates the same rlet and rlet_star logic as the original ranked_let.py,
but applies multiple penalty algorithms to analyze decision-making under uncertainty.

**Original Logic Preserved:**
- Independent uncertainty: beer and peanuts chosen independently
- Dependent uncertainty: peanut consumption depends on beer consumption
- Same ranking structures and lazy evaluation

**Penalty Analysis Added:**
- Applies MDL, Adaptive, Confidence, and Fixed penalties
- Analyzes decision quality based on different criteria
- Shows how penalty choice affects preference rankings
- Demonstrates trade-offs between different penalty approaches

**Key Concepts:**
- **Independent Uncertainty**: Beer and peanuts chosen separately
- **Dependent Uncertainty**: Peanut choice depends on beer choice
- **Penalty Algorithms**: Different ways to evaluate decision outcomes
- **Decision Analysis**: How penalties affect choice preferences

**Expected Output:**
**Key Insights and Common Confusions:**

**Understanding Penalty Effects on Rankings:**
This example demonstrates an important concept: penalties modify existing plausibility rankings,
they don't replace them. The final ranking depends on both the original base rankings AND the
penalty adjustments.

**Why Different Scenarios Show Different Behaviors:**
- Independent scenario: "no beer and peanuts" starts with lowest rank (0), so even after penalties
  for non-healthy choices, it can remain the top choice after renormalization
- Dependent scenario: "no beer and no peanuts" already has the lowest rank (0), so penalties
  on non-healthy choices properly increase their ranks relative to the healthy choice

**Penalty Algorithm Differences:**
- MDL: Information-theoretic penalties based on violation patterns
- Adaptive: Learning-based, starts conservative (penalty=0)
- Confidence: Statistical bounds, starts conservative (penalty=0)
- Fixed: Constant penalty regardless of context

**Important: Don't Expect All Non-Preferred Choices to Have Higher Ranks**
The original ranking distribution matters! If a non-preferred choice has a very low base rank,
penalties might not be enough to push it below preferred choices with higher base ranks.

**Expected Output:**
1. Original decision rankings for both independent and dependent scenarios
2. Penalty calculations showing how different algorithms assess decision quality
3. Comparative rankings demonstrating how penalties modify base plausibility
4. Clear examples of when penalties do/don't change the top choice
"""
from ranked_programming.rp_core import (
    Ranking, nrm_exc, rlet, rlet_star, pr_all
)
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty

def get_decision_rankings():
    """Get the original decision rankings from both scenarios"""

    # Independent uncertainty setup
    def beer_and_peanuts(b, p):
        return f"{'beer' if b else 'no beer'} and {'peanuts' if p else 'no peanuts'}"

    b = Ranking(lambda: nrm_exc(False, True, 1))  # Normally don't drink beer
    p = Ranking(lambda: nrm_exc(True, False, 1))  # Normally eat peanuts

    # Independent scenario
    independent_ranking = list(Ranking(lambda: rlet([
        ('b', b),
        ('p', p)
    ], beer_and_peanuts)))

    # Dependent uncertainty setup
    def peanuts_depends_on_beer(b):
        if b:
            return Ranking(lambda: nrm_exc(True, False, 1))  # If beer, normally peanuts
        else:
            return Ranking(lambda: [(False, 0)])  # If no beer, always no peanuts

    # Dependent scenario
    dependent_ranking = list(Ranking(lambda: rlet_star([
        ('b', b),
        ('p', peanuts_depends_on_beer)
    ], beer_and_peanuts)))

    return independent_ranking, dependent_ranking

def analyze_decisions_with_penalties():
    """Apply penalty analysis to decision scenarios"""

    print("="*80)
    print("RANKED LET DECISION ANALYSIS WITH MULTIPLE PENALTIES")
    print("="*80)

    independent_ranking, dependent_ranking = get_decision_rankings()

    print("\n1. ORIGINAL DECISION BEHAVIOR:")

    print("\nIndependent Uncertainty (rlet):")
    print("Rank  Decision")
    print("----------------")
    for decision, rank in independent_ranking:
        print(f"{rank:>4}  {decision}")
    print("Note: 'no beer and peanuts' has rank 0 (lowest), so penalties on non-healthy choices")
    print("      may not be enough to push it below 'beer and peanuts' which has higher base rank")

    print("\nDependent Uncertainty (rlet_star):")
    print("Rank  Decision")
    print("----------------")
    for decision, rank in dependent_ranking:
        print(f"{rank:>4}  {decision}")
    print("Note: 'no beer and no peanuts' has rank 0 (lowest), so penalties properly increase")
    print("      ranks of non-healthy choices relative to the healthy choice")

    # Define decision quality predicates
    def healthy_choice(decision):
        """Predicate: healthy choice (no beer and no peanuts)"""
        return "no beer" in decision and "no peanuts" in decision

    def social_choice(decision):
        """Predicate: social choice (beer with peanuts)"""
        return "beer" in decision and "peanuts" in decision

    def moderate_choice(decision):
        """Predicate: moderate choice (either beer without peanuts or no beer with peanuts)"""
        has_beer = "beer" in decision and "no beer" not in decision
        has_peanuts = "peanuts" in decision and "no peanuts" not in decision
        return (has_beer and not has_peanuts) or (not has_beer and has_peanuts)

    print("\n2. PENALTY ANALYSIS FOR DECISION QUALITY:")
    print("Note: Penalties modify existing rankings, they don't replace them!")
    print("      The final ranking depends on BOTH original base rankings AND penalty adjustments.")
    print("      If a non-preferred choice has a very low base rank, penalties might not be enough")
    print("      to push it below preferred choices with higher base ranks.")

    # Analyze independent scenario
    print("\n=== INDEPENDENT SCENARIO ANALYSIS ===")

    for predicate_name, predicate, description in [
        ("healthy", healthy_choice, "Prefer healthy choices (no beer, no peanuts)"),
        ("social", social_choice, "Prefer social choices (beer with peanuts)"),
        ("moderate", moderate_choice, "Prefer moderate choices (beer/no peanuts OR no beer/peanuts)")
    ]:
        print(f"\n{description}:")

        # MDL penalty
        penalty_mdl = mdl_evidence_penalty(independent_ranking, predicate)
        observed_mdl = list(observe_e(penalty_mdl, predicate, independent_ranking))
        print(f"MDL penalty ({penalty_mdl}): {observed_mdl[0][0]} (rank {observed_mdl[0][1]})")

        # Adaptive penalty
        penalty_adaptive = adaptive_evidence_penalty(independent_ranking, predicate, f"decision_{predicate_name}")
        observed_adaptive = list(observe_e(penalty_adaptive, predicate, independent_ranking))
        print(f"Adaptive penalty ({penalty_adaptive}): {observed_adaptive[0][0]} (rank {observed_adaptive[0][1]})")

        # Confidence penalty
        penalty_confidence = confidence_evidence_penalty(independent_ranking, predicate)
        observed_confidence = list(observe_e(penalty_confidence, predicate, independent_ranking))
        print(f"Confidence penalty ({penalty_confidence}): {observed_confidence[0][0]} (rank {observed_confidence[0][1]})")

        # Fixed penalty
        observed_fixed = list(observe_e(1, predicate, independent_ranking))
        print(f"Fixed penalty (1): {observed_fixed[0][0]} (rank {observed_fixed[0][1]})")

    # Analyze dependent scenario
    print("\n=== DEPENDENT SCENARIO ANALYSIS ===")

    for predicate_name, predicate, description in [
        ("healthy", healthy_choice, "Prefer healthy choices"),
        ("social", social_choice, "Prefer social choices"),
        ("moderate", moderate_choice, "Prefer moderate choices")
    ]:
        print(f"\n{description}:")

        # MDL penalty
        penalty_mdl = mdl_evidence_penalty(dependent_ranking, predicate)
        observed_mdl = list(observe_e(penalty_mdl, predicate, dependent_ranking))
        print(f"MDL penalty ({penalty_mdl}): {observed_mdl[0][0]} (rank {observed_mdl[0][1]})")

        # Adaptive penalty
        penalty_adaptive = adaptive_evidence_penalty(dependent_ranking, predicate, f"dependent_{predicate_name}")
        observed_adaptive = list(observe_e(penalty_adaptive, predicate, dependent_ranking))
        print(f"Adaptive penalty ({penalty_adaptive}): {observed_adaptive[0][0]} (rank {observed_adaptive[0][1]})")

        # Confidence penalty
        penalty_confidence = confidence_evidence_penalty(dependent_ranking, predicate)
        observed_confidence = list(observe_e(penalty_confidence, predicate, dependent_ranking))
        print(f"Confidence penalty ({penalty_confidence}): {observed_confidence[0][0]} (rank {observed_confidence[0][1]})")

        # Fixed penalty
        observed_fixed = list(observe_e(1, predicate, dependent_ranking))
        print(f"Fixed penalty (1): {observed_fixed[0][0]} (rank {observed_fixed[0][1]})")

    print("\n" + "="*80)
    print("ANALYSIS: DECISION-MAKING INSIGHTS")
    print("="*80)

    print("\nDecision Pattern Analysis:")
    print("- Independent: Beer and peanuts chosen separately")
    print("- Dependent: Peanut choice depends on beer choice")
    print("- Total combinations: 4 (independent) vs 3 (dependent)")

    print("\nPenalty Algorithm Comparison:")
    print("- MDL: Information-theoretic assessment of decision quality")
    print("- Adaptive: Learns from decision patterns over time")
    print("- Confidence: Statistical bounds on decision outcomes")
    print("- Fixed: Simple preference-based decision ranking")

    print("\nPredicate Analysis:")
    print("- Healthy: No beer + no peanuts (most restrictive)")
    print("- Social: Beer + peanuts (social drinking scenario)")
    print("- Moderate: Beer/no peanuts OR no beer/peanuts (balanced choice)")

    print("\nPractical Applications:")
    print("- Personal decision making: Health vs. social preferences")
    print("- Resource allocation: Independent vs. dependent choices")
    print("- Risk assessment: How penalties affect decision rankings")
    print("- Learning systems: Adaptive penalties for preference evolution")

    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_decisions_with_penalties()
