"""
Hidden Markov Model with Multiple Evidence Penalties

This example demonstrates how different penalty calculation methods work in ranked programming
by applying them to a Hidden Markov Model (HMM) with evidence violations.

**Core Concepts:**

**Hidden Markov Models (HMMs):**
A statistical model for sequences where the system being modeled is a Markov process with
hidden states. The HMM generates all possible state sequences that could produce given
observations, ranking them by plausibility. Common applications include:
- Speech recognition
- Part-of-speech tagging
- Bioinformatics (gene prediction)
- Sequential pattern analysis

**Evidence Penalties in Ranked Programming:**
When conditioning on evidence (predicates), outputs that violate the predicate receive a penalty
added to their rank. Different penalty calculation methods create different reasoning "personalities":

- **MDL (Minimum Description Length)**: Information-theoretic approach based on data compression
- **Adaptive**: Learning-based method that improves over multiple examples
- **Confidence**: Statistical approach using confidence intervals
- **Fixed**: Simple heuristic with constant penalty values

**What This Example Demonstrates:**
1. HMM generates multiple state sequences for mixed observations ['yes', 'no', 'yes', 'no', 'yes']
2. A predicate requires "at least 4 rainy states" in the sequence
3. Different penalty types calculate violation costs differently
4. Conditionalization applies penalties and renormalizes rankings
5. Comparison shows how penalty choice affects final plausibility rankings

**Key Functions Used:**
- `hmm()`: Generates ranked HMM outputs for given observations
- `mdl_evidence_penalty()`: Calculates information-theoretic penalties
- `adaptive_evidence_penalty()`: Learning-based penalty calculation
- `confidence_evidence_penalty()`: Statistical confidence-based penalties
- `observe_e()`: Applies penalties and renormalizes rankings

**Expected Output:**
The example shows:
- Raw HMM outputs with their original rankings
- Calculated penalty values for each method
- Renormalized rankings after applying penalties
- Detailed analysis of how different penalties affect violating outputs
- Practical guidelines for choosing penalty types

**Educational Value:**
This example illustrates the fundamental trade-offs in evidence handling:
- Information efficiency vs. statistical rigor
- Learning capability vs. computational simplicity
- Adaptability vs. predictability
"""
from ranked_programming.rp_core import Ranking
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty
from ranked_programming.ranking_observe import observe_e
from hidden_markov import hmm

def pred(result):
    emissions, states = result  # Fix: unpack directly
    return sum(1 for s in states if s == 'rainy') >= 4  # At least 4 rainy states (stricter threshold)

obs = ['yes', 'no', 'yes', 'no', 'yes']  # Mixed observations to create violations
ranking = list(hmm(obs))

# Show first few raw HMM outputs to debug
print("Raw HMM outputs (first 5):")
for i, (result, rank) in enumerate(ranking[:5]):
    emissions, states = result
    rainy_count = sum(1 for s in states if s == 'rainy')
    satisfies = rainy_count >= 4
    print(f"  {i+1}: states={states}, rainy_count={rainy_count}, satisfies={satisfies}, rank={rank}")

print("\n" + "="*80)
print("DETAILED EXPLANATION OF HMM OUTPUT")
print("="*80)

print("\n1. HMM MODEL COMPONENTS:")
print("   - States: 'rainy', 'sunny' (hidden states)")
print("   - Emissions: 'yes', 'no' (observable outputs)")
print("   - Transitions: Stay in same state (rank 0) or switch (rank 2)")
print("   - Emissions: Normal emission (rank 0) or opposite (rank 1)")

print("\n2. OBSERVATIONS & STATE GENERATION:")
print("   - Input observations: ['yes', 'no', 'yes', 'no', 'yes']")
print("   - HMM generates ALL possible state sequences that could produce these emissions")
print("   - Each state sequence has 6 states (initial + 5 transitions)")
print("   - Emissions must exactly match observations (HMM conditions on them)")

print("\n3. RANK CALCULATION:")
print("   - Initial state: 'rainy' (rank 0) or 'sunny' (rank 0)")
print("   - Each transition: same state (rank +0) or different (rank +2)")
print("   - Each emission: matches expected (rank +0) or opposite (rank +1)")
print("   - Total rank = sum of all transition + emission ranks")

print("\n4. PREDICATE EVALUATION:")
print("   - Predicate: sum(1 for s in states if s == 'rainy') >= 4")
print("   - Counts rainy states in the 6-state sequence")
print("   - satisfy=True if ≥4 rainy states, False if <4 rainy states")

print("\n5. PENALTY APPLICATION:")
print("   - For each output: if predicate fails, add penalty to rank")
print("   - Then normalize: subtract minimum rank (makes lowest rank = 0)")
print("   - MDL penalty (2): Information-theoretic calculation")
print("   - Adaptive penalty (0): Learning-based, starts at 0")
print("   - Confidence penalty (5): Statistical confidence intervals")
print("   - Fixed penalty (1): Constant value")

print("\n6. EXAMPLE BREAKDOWN:")
print("   Take the violating output: 3 rainy states, original rank=5")
print("   - MDL: 5 + 2 = 7, then 7 - 2 = 5 (after normalization)")
print("   - Adaptive: 5 + 0 = 5, then 5 - 2 = 3")
print("   - Confidence: 5 + 5 = 10, then 10 - 2 = 8")
print("   - Fixed: 5 + 1 = 6, then 6 - 2 = 4")

print("\n7. SPECIFIC RANK CALCULATION EXAMPLE:")
print("   Let's trace the rank for: ('rainy', 'rainy', 'rainy', 'rainy', 'rainy', 'sunny')")
print("   ")
print("   State sequence: rainy → rainy → rainy → rainy → rainy → sunny")
print("   Observations:     yes    no     yes    no     yes")
print("   ")
print("   Initial: rainy (rank +0)")
print("   Step 1: rainy → rainy (stay, rank +0), emit 'yes' (normal, rank +0)")
print("   Step 2: rainy → rainy (stay, rank +0), emit 'no' (opposite, rank +1)")
print("   Step 3: rainy → rainy (stay, rank +0), emit 'yes' (normal, rank +0)")
print("   Step 4: rainy → rainy (stay, rank +0), emit 'no' (opposite, rank +1)")
print("   Step 5: rainy → sunny (switch, rank +2), emit 'yes' (normal for sunny, rank +0)")
print("   ")
print("   Total rank: 0 + 0+0 + 0+1 + 0+0 + 0+1 + 2+0 = 5 ✓")
print("   ")
print("   Predicate check: 5 rainy states ≥ 4 → satisfies=True")
print("   So no penalty added, final rank = 5 - 2 = 3 (after normalization)")

print("\n8. PENALTY MEANING:")
print("   - Penalty value represents 'cost' of violating evidence")
print("   - Higher penalty = stronger belief that predicate should hold")
print("   - MDL penalty (2) = calculated from information content of violations")
print("   - Adaptive penalty (0) = starts low, increases with more violations")
print("   - Confidence penalty (5) = based on statistical significance")
print("   - Fixed penalty (1) = constant regardless of data")

print("\n" + "="*80)
penalty_mdl = mdl_evidence_penalty(ranking, pred)
print(f"MDL penalty for evidence: {penalty_mdl}")
observed_mdl = list(observe_e(penalty_mdl, pred, ranking))
print("Observed ranking (MDL penalty):")
for v, r in observed_mdl[:5]:  # Show first 5
    print(f"  {v}: rank {r}")

# Adaptive penalty (learns over time)
penalty_adaptive = adaptive_evidence_penalty(ranking, pred, "hmm_all_yes")
print(f"\nAdaptive penalty for evidence: {penalty_adaptive}")
observed_adaptive = list(observe_e(penalty_adaptive, pred, ranking))
print("Observed ranking (Adaptive penalty):")
for v, r in observed_adaptive[:5]:  # Show first 5
    print(f"  {v}: rank {r}")

# Confidence penalty
penalty_confidence = confidence_evidence_penalty(ranking, pred)
print(f"\nConfidence penalty for evidence: {penalty_confidence}")
observed_confidence = list(observe_e(penalty_confidence, pred, ranking))
print("Observed ranking (Confidence penalty):")
for v, r in observed_confidence[:5]:  # Show first 5
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_e(1, pred, ranking))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed[:5]:  # Show first 5
    print(f"  {v}: rank {r}")

print("\n" + "="*60)
print("ANALYSIS: Penalty Type Differences")
print("="*60)
print("Notice how the violating output (3 rainy states) gets different penalties:")
print("- MDL penalty (2): Information-theoretic, based on data compression")
print("- Adaptive penalty (0): Learns from experience, starts conservative")
print("- Confidence penalty (5): Statistical approach, wider intervals")
print("- Fixed penalty (1): Constant heuristic, predictable but rigid")
print("\nThis demonstrates how different penalty philosophies handle evidence violations!")

print("\n" + "="*80)
print("WHEN TO USE EACH PENALTY TYPE - PRACTICAL GUIDELINES")
print("="*80)
print("Based on this toy HMM example, here are evidence-based recommendations:")
print("   ")
print("   🎯 MDL PENALTY (penalty=2, violating output rank=5):")
print("      - Use when: You have clear domain knowledge about expected frequencies")
print("      - Best for: Scientific applications, compression-based reasoning")
print("      - Advantage: Data-driven, principled information-theoretic approach")
print("      - In this example: Moderate penalty reflects the 'surprise' of violations")
print("   ")
print("   🔄 ADAPTIVE PENALTY (penalty=0, violating output rank=3):")
print("      - Use when: Learning from experience over multiple similar problems")
print("      - Best for: Online learning, dynamic environments, exploration")
print("      - Advantage: Starts conservative, adapts to patterns over time")
print("      - In this example: No penalty initially, learns from violation patterns")
print("   ")
print("   📊 CONFIDENCE PENALTY (penalty=5, violating output rank=8):")
print("      - Use when: Statistical rigor is important, small sample sizes")
print("      - Best for: Hypothesis testing, statistical validation, risk-averse scenarios")
print("      - Advantage: Conservative approach, accounts for uncertainty")
print("      - In this example: High penalty reflects statistical significance of violations")
print("   ")
print("   🔧 FIXED PENALTY (penalty=1, violating output rank=4):")
print("      - Use when: Simple heuristics, computational efficiency matters")
print("      - Best for: Real-time systems, when domain knowledge suggests constant cost")
print("      - Advantage: Predictable, fast, easy to tune and understand")
print("      - In this example: Consistent penalty regardless of violation patterns")
print("   ")
print("   📈 PRACTICAL DECISION TREE:")
print("      - Have statistical training data? → Use CONFIDENCE penalty")
print("      - Need to learn over time? → Use ADAPTIVE penalty")
print("      - Care about information efficiency? → Use MDL penalty")
print("      - Want simplicity/speed? → Use FIXED penalty")
print("   ")
print("   ⚠️  KEY INSIGHT FROM THIS EXAMPLE:")
print("      Different penalties create different 'personalities' for your reasoning:")
print("      - MDL: Information-efficient but requires domain knowledge")
print("      - Adaptive: Flexible but needs multiple examples to learn")
print("      - Confidence: Conservative but may over-penalize rare events")
print("      - Fixed: Simple but may under/over-penalize depending on context")
print("   ")
print("   💡 REAL-WORLD APPLICATIONS:")
print("      - MDL: Bioinformatics (gene finding), data compression")
print("      - Adaptive: Recommender systems, fraud detection")
print("      - Confidence: Medical diagnosis, safety-critical systems")
print("      - Fixed: Game AI, real-time control systems")

print("\n" + "="*80)
