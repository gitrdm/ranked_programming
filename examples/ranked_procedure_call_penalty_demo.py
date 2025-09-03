"""
Ranked Procedure Call with Multiple Penalty Analysis

This example demonstrates the same procedure call logic as the original ranked_procedure_call.py,
but applies multiple penalty algorithms to analyze how penalties affect function application rankings.

**Original Logic Preserved:**
- Scenario 1: Deterministic addition (5 + 10)
- Scenario 2: Uncertain argument (normally 10, exceptionally 20)
- Scenario 3: Uncertain operation (normally +, exceptionally -) and uncertain argument
- Same ranking structures and lazy evaluation

**Penalty Analysis Added:**
- Applies MDL, Adaptive, Confidence, and Fixed penalties to each scenario
- Analyzes how penalties affect procedure call outcomes
- Shows how penalty choice affects result rankings
- Demonstrates trade-offs between different penalty approaches

**Key Concepts:**
- **Procedure Call Uncertainty**: Function application with uncertain arguments/operations
- **Penalty Algorithms**: Different ways to evaluate procedure call quality
- **Result Analysis**: How penalties affect the ranking of computation outcomes
- **Decision Quality**: Evaluating the desirability of different computational results

**Key Insights and Common Confusions:**

**Understanding Penalty Effects on Rankings:**
This example demonstrates an important concept: penalties modify existing plausibility rankings,
they don't replace them. The final ranking depends on both the original base rankings AND the
penalty adjustments.

**Why Different Scenarios Show Different Behaviors:**
- Deterministic scenario: Single result, penalties have minimal effect
- Uncertain argument: Penalties can shift preference between normal/exceptional values
- Uncertain operation: Penalties can dramatically change preference between addition/subtraction

**Penalty Algorithm Differences:**
- MDL: Information-theoretic penalties based on violation patterns
- Adaptive: Learning-based, starts conservative (penalty=0)
- Confidence: Statistical bounds, starts conservative (penalty=0)
- Fixed: Constant penalty regardless of context

**Important: Don't Expect All Non-Preferred Results to Have Higher Ranks**
The original ranking distribution matters! If a non-preferred result has a very low base rank,
penalties might not be enough to push it below preferred results with higher base ranks.

**Understanding Large Penalty Values (like PRACTICAL_INFINITY):**
When you see very large penalty values, it's NOT a bug - it's the correct mathematical response!
This happens when NO results satisfy your predicate (e.g., asking for even results when all results are odd).
- **MDL penalty**: Returns PRACTICAL_INFINITY when M=0 (no results satisfy predicate)
- **Adaptive penalty**: Returns PRACTICAL_INFINITY when empirical success rate is 0%
- **Confidence penalty**: Returns PRACTICAL_INFINITY when M=0
- **Why this makes sense**: Information-theoretically, impossible evidence deserves infinite penalty
- **Ranking effect**: All results get the same penalty, so relative ordering is preserved

**Expected Output:**
1. Original procedure call rankings for all three scenarios
2. Penalty calculations showing how different algorithms assess result quality
3. Comparative rankings demonstrating how penalties modify base plausibility
4. Clear examples of when penalties do/don't change the top result
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty

def print_ranking(title, ranking):
    """Print ranking in a formatted way"""
    print(title)
    print("Rank  Value\n------------")
    results = sorted(ranking, key=lambda x: (x[1], x[0]))
    for value, rank in results:
        print(f"{rank:<5} {value}")
    print("Done")

def get_procedure_call_rankings():
    """Get the original procedure call rankings from all scenarios"""

    # Scenario 1: Deterministic addition
    ranking1 = Ranking(lambda: [(5 + 10, 0)])

    # Scenario 2: Uncertain argument (normally 10, exceptionally 20)
    arg2 = Ranking(lambda: nrm_exc(10, 20, 1))
    ranking2 = Ranking(lambda: rlet_star([
        ('arg', arg2)
    ], lambda arg: 5 + arg))

    # Scenario 3: Uncertain op (normally +, exceptionally -) and uncertain arg
    op3 = Ranking(lambda: nrm_exc(lambda x, y: x + y, lambda x, y: y - x, 1))
    arg3 = Ranking(lambda: nrm_exc(10, 20, 1))
    ranking3 = Ranking(lambda: rlet_star([
        ('op', op3),
        ('arg', arg3)
    ], lambda op, arg: op(5, arg)))

    return ranking1, ranking2, ranking3

def analyze_procedure_calls_with_penalties():
    """Apply penalty analysis to procedure call scenarios"""

    print("="*80)
    print("RANKED PROCEDURE CALL ANALYSIS WITH MULTIPLE PENALTIES")
    print("="*80)

    ranking1, ranking2, ranking3 = get_procedure_call_rankings()

    print("\n1. ORIGINAL PROCEDURE CALL BEHAVIOR:")

    print("\nScenario 1: Deterministic addition (5 + 10)")
    print_ranking("", ranking1)

    print("\nScenario 2: Uncertain argument (normally 10, exceptionally 20)")
    print_ranking("", ranking2)
    print("Note: Normal case (15) has rank 0, exceptional case (25) has rank 1")

    print("\nScenario 3: Uncertain operation and argument")
    print_ranking("", ranking3)
    print("Note: Addition results have lower ranks than subtraction results")

    # Define result quality predicates
    def prefer_exact_15(result):
        """Predicate: strongly prefer exactly 15 (the expected normal result)"""
        return result == 15

    def penalize_large_results(result):
        """Predicate: penalize results larger than 15"""
        return result <= 15

    def prefer_small_values(result):
        """Predicate: prefer results less than or equal to 15"""
        return result <= 15

    def avoid_odd_results(result):
        """Predicate: avoid odd-numbered results"""
        return result % 2 == 0

    print("\n2. PENALTY ANALYSIS FOR RESULT QUALITY:")
    print("Note: Penalties modify existing rankings, they don't replace them!")
    print("      The final ranking depends on BOTH original base rankings AND penalty adjustments.")
    print("      Watch for large penalty values (PRACTICAL_INFINITY) - this happens when NO results")
    print("      satisfy the predicate, which is the correct mathematical response!")

    scenarios = [
        ("Scenario 1: Deterministic", ranking1),
        ("Scenario 2: Uncertain Argument", ranking2),
        ("Scenario 3: Uncertain Operation", ranking3)
    ]

    for scenario_name, ranking in scenarios:
        print(f"\n=== {scenario_name.upper()} ===")

        for predicate_name, predicate, description in [
            ("exact_15", prefer_exact_15, "Strongly prefer exactly 15 (expected normal result)"),
            ("penalize_large", penalize_large_results, "Penalize results larger than 15"),
            ("prefer_small", prefer_small_values, "Prefer results ≤ 15"),
            ("avoid_odd", avoid_odd_results, "Avoid odd-numbered results (will show large penalties since all results are odd!)")
        ]:
            print(f"\n{description}:")

            # MDL penalty
            penalty_mdl = mdl_evidence_penalty(ranking, predicate)
            observed_mdl = list(observe_e(penalty_mdl, predicate, ranking))
            top_mdl = observed_mdl[0]
            print(f"MDL penalty ({penalty_mdl}): {top_mdl[0]} (rank {top_mdl[1]})")
            if len(observed_mdl) > 1:
                print(f"  Full ranking: {[(v, r) for v, r in observed_mdl[:3]]}")

            # Adaptive penalty
            penalty_adaptive = adaptive_evidence_penalty(ranking, predicate, f"result_{predicate_name}")
            observed_adaptive = list(observe_e(penalty_adaptive, predicate, ranking))
            top_adaptive = observed_adaptive[0]
            print(f"Adaptive penalty ({penalty_adaptive}): {top_adaptive[0]} (rank {top_adaptive[1]})")
            if len(observed_adaptive) > 1:
                print(f"  Full ranking: {[(v, r) for v, r in observed_adaptive[:3]]}")

            # Confidence penalty
            penalty_confidence = confidence_evidence_penalty(ranking, predicate)
            observed_confidence = list(observe_e(penalty_confidence, predicate, ranking))
            top_confidence = observed_confidence[0]
            print(f"Confidence penalty ({penalty_confidence}): {top_confidence[0]} (rank {top_confidence[1]})")
            if len(observed_confidence) > 1:
                print(f"  Full ranking: {[(v, r) for v, r in observed_confidence[:3]]}")

            # Fixed penalty
            observed_fixed = list(observe_e(1, predicate, ranking))
            top_fixed = observed_fixed[0]
            print(f"Fixed penalty (1): {top_fixed[0]} (rank {top_fixed[1]})")
            if len(observed_fixed) > 1:
                print(f"  Full ranking: {[(v, r) for v, r in observed_fixed[:3]]}")

    print("\n" + "="*80)
    print("ANALYSIS: PROCEDURE CALL INSIGHTS")
    print("="*80)

    print("\nProcedure Call Pattern Analysis:")
    print("- Deterministic: Single predictable result")
    print("- Uncertain Argument: Normal vs exceptional input values")
    print("- Uncertain Operation: Different operations with same inputs")

    print("\nPenalty Algorithm Comparison:")
    print("- MDL: Information-theoretic assessment of result quality")
    print("- Adaptive: Learns from result patterns over time")
    print("- Confidence: Statistical bounds on result reliability")
    print("- Fixed: Constant penalty regardless of result characteristics")

    print("\nKey Observations:")
    print("- Penalties can shift preferences between normal and exceptional results")
    print("- Different quality criteria affect rankings differently (e.g., penalizing large results)")
    print("- Original ranking distributions heavily influence penalty effectiveness")
    print("- Some scenarios show ranking changes (e.g., Scenario 2 with 'penalize large results')")
    print("- MDL penalties often show more variation than adaptive/confidence algorithms")
    print("- Fixed penalties provide consistent but sometimes less nuanced adjustments")
    print("- Large penalty values (PRACTICAL_INFINITY) indicate NO results satisfy the predicate")
    print("  This is correct behavior, not a bug - represents 'impossible evidence'")

if __name__ == "__main__":
    analyze_procedure_calls_with_penalties()
