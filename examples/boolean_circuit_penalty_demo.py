"""
Boolean Circuit with Fault Analysis and Multiple Penalties

This example demonstrates the original boolean circuit logic with fault modeling,
then applies different penalty algorithms to analyze circuit reliability.

**Original Circuit Logic:**
- Fixed inputs: i1=False, i2=False, i3=True
- Circuit: ((not i1) if N else False) or i2) if O1 else False) or i3) if O2 else False
- Fault variables: N, O1, O2 (normally True, exceptionally False with rank 1)
- Uses rlet to combine uncertainties across all fault variables

**Penalty Analysis:**
After demonstrating the original circuit behavior, this example applies different
penalty types to analyze circuit reliability and fault tolerance.

**Key Concepts:**
- **Fault Modeling**: N, O1, O2 represent component reliability
- **Circuit Logic**: Complex boolean expression with fault propagation
- **Penalty Types**: MDL, Adaptive, Confidence, Fixed penalties
- **Reliability Analysis**: How different penalties affect fault assessment

**Expected Output:**
1. Original circuit ranking with all fault combinations
2. Penalty calculations for reliability predicates
3. Comparative analysis of different penalty approaches
4. Practical insights for circuit reliability engineering
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, pr_all
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty

def boolean_circuit():
    """Original circuit logic with fault modeling"""
    # Fault variables (normally True, exceptionally False with rank 1)
    N = Ranking(lambda: nrm_exc(True, False, 1))
    O1 = Ranking(lambda: nrm_exc(True, False, 1))
    O2 = Ranking(lambda: nrm_exc(True, False, 1))

    def circuit(N, O1, O2):
        # Fixed inputs as in original example
        i1, i2, i3 = False, False, True

        # Circuit logic: ((not i1) if N else False) or i2) if O1 else False) or i3) if O2 else False
        l1 = (not i1) if N else False
        l2 = (l1 or i2) if O1 else False
        out = (l2 or i3) if O2 else False
        return (N, O1, O2, out)

    ranking = Ranking(lambda: rlet([
        ('N', N),
        ('O1', O1),
        ('O2', O2)
    ], circuit))

    return list(ranking)

def analyze_circuit_reliability():
    """Apply penalty analysis to circuit reliability"""
    print("="*80)
    print("BOOLEAN CIRCUIT RELIABILITY ANALYSIS WITH MULTIPLE PENALTIES")
    print("="*80)

    # Get original circuit ranking
    circuit_ranking = boolean_circuit()

    print("\n1. ORIGINAL CIRCUIT BEHAVIOR:")
    print("Rank  (N, O1, O2, output)")
    print("---------------------------")
    for (N, O1, O2, output), rank in circuit_ranking:
        print(f"{rank:>4} ({N!r}, {O1!r}, {O2!r}, {output!r})")

    print(f"\nTotal combinations: {len(circuit_ranking)}")

    # Count successful vs failed outputs
    successful = sum(1 for (_, _, _, output), _ in circuit_ranking if output == True)
    failed = len(circuit_ranking) - successful
    print(f"Successful outputs: {successful}")
    print(f"Failed outputs: {failed}")

    # Define reliability predicate: circuit should produce True output
    def reliability_predicate(result):
        N, O1, O2, output = result
        return output == True

    print("\n2. PENALTY ANALYSIS FOR RELIABILITY:")
    print("Applying different penalties to assess circuit fault tolerance...")

    # MDL penalty for reliability
    penalty_mdl = mdl_evidence_penalty(circuit_ranking, reliability_predicate)
    print(f"\nMDL penalty for reliability: {penalty_mdl}")
    observed_mdl = list(observe_e(penalty_mdl, reliability_predicate, circuit_ranking))
    print("Top 8 most reliable configurations (MDL penalty):")
    for i, (config, rank) in enumerate(observed_mdl[:8]):
        N, O1, O2, output = config
        print(f"  {i+1}. {config}: rank {rank}")

    # Adaptive penalty for reliability
    penalty_adaptive = adaptive_evidence_penalty(circuit_ranking, reliability_predicate, "circuit_reliability")
    print(f"\nAdaptive penalty for reliability: {penalty_adaptive}")
    observed_adaptive = list(observe_e(penalty_adaptive, reliability_predicate, circuit_ranking))
    print("Top 8 most reliable configurations (Adaptive penalty):")
    for i, (config, rank) in enumerate(observed_adaptive[:8]):
        N, O1, O2, output = config
        print(f"  {i+1}. {config}: rank {rank}")

    # Confidence penalty for reliability
    penalty_confidence = confidence_evidence_penalty(circuit_ranking, reliability_predicate)
    print(f"\nConfidence penalty for reliability: {penalty_confidence}")
    observed_confidence = list(observe_e(penalty_confidence, reliability_predicate, circuit_ranking))
    print("Top 8 most reliable configurations (Confidence penalty):")
    for i, (config, rank) in enumerate(observed_confidence[:8]):
        N, O1, O2, output = config
        print(f"  {i+1}. {config}: rank {rank}")

    # Fixed penalty for comparison
    observed_fixed = list(observe_e(1, reliability_predicate, circuit_ranking))
    print("\nFixed penalty (1) for reliability:")
    print("Top 8 most reliable configurations (Fixed penalty):")
    for i, (config, rank) in enumerate(observed_fixed[:8]):
        N, O1, O2, output = config
        print(f"  {i+1}. {config}: rank {rank}")

    print("\n" + "="*80)
    print("ANALYSIS: FAULT TOLERANCE INSIGHTS")
    print("="*80)

    # Analyze which configurations are most/least reliable
    all_true_config = next((config for config, rank in observed_mdl if config == (True, True, True, True)), None)
    all_false_config = next((config for config, rank in observed_mdl if config == (False, False, False, False)), None)

    print("\nFault Tolerance Analysis:")
    if all_true_config:
        all_true_rank = next(rank for config, rank in observed_mdl if config == all_true_config)
        print(f"- All components working (True, True, True): rank {all_true_rank}")
    if all_false_config:
        all_false_rank = next(rank for config, rank in observed_mdl if config == all_false_config)
        print(f"- All components failed (False, False, False): rank {all_false_rank}")

    print("\nPenalty Comparison:")
    print("- MDL: Information-theoretic assessment of fault impact")
    print("- Adaptive: Learns from reliability patterns over time")
    print("- Confidence: Statistical bounds on fault tolerance")
    print("- Fixed: Simple binary reliability assessment")

    print("\nPractical Applications:")
    print("- Circuit design: Identify most fault-tolerant configurations")
    print("- Reliability engineering: Quantify impact of component failures")
    print("- Safety analysis: Assess critical failure modes")
    print("- Maintenance planning: Prioritize component reliability improvements")

    print("\n" + "="*80)
    print("WHY RANKS DIFFER: PENALTY APPLICATION EXPLANATION")
    print("="*80)

    print("\nORIGINAL vs PENALTY-APPLIED RANKINGS:")
    print("Original rankings (no penalties):")
    for (config, rank) in circuit_ranking:
        N, O1, O2, output = config
        status = "SUCCESS" if output else "PENALTY"
        print(f"  {config}: original_rank={rank}, status={status}")

    print("\nAfter applying penalty=1 to failed outputs:")
    print("Formula: new_rank = original_rank + penalty (if output=False)")
    print("Then renormalize: subtract minimum rank to make lowest=0")

    for (config, orig_rank) in circuit_ranking:
        N, O1, O2, output = config
        if not output:  # Failed output gets penalty
            penalized_rank = orig_rank + 1
            print(f"  {config}: {orig_rank} + 1 = {penalized_rank} (penalized)")
        else:  # Success keeps original rank
            print(f"  {config}: {orig_rank} + 0 = {orig_rank} (no penalty)")

    print("\nAfter renormalization (subtract min rank=0):")
    print("Final ranks are the same as penalized ranks since min=0")
    print("This explains why (False,False,False,False) goes from rank 3 → rank 4")

    print("\nKEY INSIGHT:")
    print("- Original: Raw plausibility rankings from circuit logic")
    print("- With penalties: Adjusted rankings based on reliability requirements")
    print("- Renormalization ensures lowest rank is always 0")

    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_circuit_reliability()
