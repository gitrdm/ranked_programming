"""
Boolean Circuit with Multiple Evidence Penalties

This example demonstrates how different penalty calculation methods work in ranked programming
by applying them to a simple boolean circuit with evidence violations.

**Core Concepts:**

**Boolean Circuit Analysis:**
A digital circuit that processes binary inputs through logical gates. This example uses a 3-input
AND gate where all inputs must be 1 for the output to be 1. The circuit generates all possible
input combinations, but we apply evidence that requires the output to be True.

**Evidence Penalties in Ranked Programming:**
When conditioning on evidence (predicates), circuit inputs that violate the predicate receive a penalty
added to their rank. Different penalty calculation methods create different reasoning "personalities":

- **MDL (Minimum Description Length)**: Information-theoretic approach based on data compression
- **Adaptive**: Learning-based method that improves over multiple examples
- **Confidence**: Statistical approach using confidence intervals
- **Fixed**: Simple heuristic with constant penalty values

**What This Example Demonstrates:**
1. Generate all possible 3-bit inputs for a boolean circuit
2. Apply predicate requiring circuit output = True (only (1,1,1) satisfies)
3. Different penalty types calculate violation costs differently
4. Conditionalization applies penalties and renormalizes rankings
5. Comparison shows how penalty choice affects final plausibility rankings

**Key Functions Used:**
- `mdl_evidence_penalty()`: Calculates information-theoretic penalties
- `adaptive_evidence_penalty()`: Learning-based penalty calculation
- `confidence_evidence_penalty()`: Statistical confidence-based penalties
- `observe_e()`: Applies penalties and renormalizes rankings

**Expected Output:**
The example shows:
- All possible circuit inputs with their original rankings
- Calculated penalty values for each method
- Renormalized rankings after applying penalties
- Detailed analysis of how different penalties affect violating inputs
- Practical guidelines for choosing penalty types

**Educational Value:**
This example illustrates penalty differences in a simple, deterministic domain:
- Information efficiency vs. statistical rigor
- Learning capability vs. computational simplicity
- Adaptability vs. predictability
"""
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty

def circuit_output(inputs):
    # Simple AND circuit for illustration
    return inputs[0] and inputs[1] and inputs[2]

# All possible 3-bit inputs
inputs = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
# Assign rank 0 to all
ranking = [(inp, 0) for inp in inputs]

# Predicate: output must be True (only (1,1,1) satisfies this)
pred = lambda x: circuit_output(x) == 1

print("Boolean Circuit Analysis with Multiple Penalties")
print("="*50)
print(f"Circuit: 3-input AND gate")
print(f"Predicate: output must be True")
print(f"Only input (1,1,1) satisfies the predicate")
print()

print("All possible inputs and their circuit outputs:")
for inp, rank in ranking:
    output = circuit_output(inp)
    satisfies = pred(inp)
    print(f"  {inp}: output={int(output)}, satisfies={satisfies}, rank={rank}")
print()

# MDL penalty
penalty_mdl = mdl_evidence_penalty(ranking, pred)
print(f"MDL penalty for evidence: {penalty_mdl}")
observed_mdl = list(observe_e(penalty_mdl, pred, ranking))
print("Observed ranking (MDL penalty):")
for v, r in observed_mdl:
    print(f"  {v}: rank {r}")

# Adaptive penalty (learns over time)
penalty_adaptive = adaptive_evidence_penalty(ranking, pred, "boolean_circuit")
print(f"\nAdaptive penalty for evidence: {penalty_adaptive}")
observed_adaptive = list(observe_e(penalty_adaptive, pred, ranking))
print("Observed ranking (Adaptive penalty):")
for v, r in observed_adaptive:
    print(f"  {v}: rank {r}")

# Confidence penalty
penalty_confidence = confidence_evidence_penalty(ranking, pred)
print(f"\nConfidence penalty for evidence: {penalty_confidence}")
observed_confidence = list(observe_e(penalty_confidence, pred, ranking))
print("Observed ranking (Confidence penalty):")
for v, r in observed_confidence:
    print(f"  {v}: rank {r}")

# For comparison, show with fixed penalty 1
observed_fixed = list(observe_e(1, pred, ranking))
print("\nObserved ranking (fixed penalty=1):")
for v, r in observed_fixed:
    print(f"  {v}: rank {r}")

print("\n" + "="*60)
print("ANALYSIS: Penalty Type Differences in Boolean Circuit")
print("="*60)
print("Notice how the 7 violating inputs get different penalties:")
print("- Only (1,1,1) satisfies the predicate")
print("- All other inputs (1,1,0), (1,0,1), (1,0,0), (0,1,1), (0,1,0), (0,0,1), (0,0,0) are penalized")
print()
violating_input = (1, 1, 0)  # One of the violating inputs
print(f"Taking violating input {violating_input} as example:")
print("- MDL penalty: reflects information content of violations")
print("- Adaptive penalty: starts conservative, learns over time")
print("- Confidence penalty: statistical approach, wider intervals")
print("- Fixed penalty: constant regardless of context")
print()
print("This demonstrates how penalty choice affects deterministic reasoning!")

print("\n" + "="*80)
print("WHEN TO USE EACH PENALTY TYPE - BOOLEAN CIRCUIT PERSPECTIVE")
print("="*80)
print("Based on this deterministic circuit example, here are the insights:")
print("   ")
print("   🎯 MDL PENALTY:")
print("      - Calculates penalty based on how 'surprising' violations are")
print("      - In deterministic domains: penalty reflects constraint strictness")
print("      - Good for: Understanding constraint violation costs")
print("   ")
print("   🔄 ADAPTIVE PENALTY:")
print("      - Learns from experience across multiple circuit analyses")
print("      - In deterministic domains: adapts to common violation patterns")
print("      - Good for: Repeated analysis of similar constraint problems")
print("   ")
print("   📊 CONFIDENCE PENALTY:")
print("      - Uses statistical confidence for deterministic constraints")
print("      - In deterministic domains: provides conservative bounds")
print("      - Good for: Risk-averse constraint satisfaction")
print("   ")
print("   🔧 FIXED PENALTY:")
print("      - Simple constant penalty for all violations")
print("      - In deterministic domains: predictable and fast")
print("      - Good for: Real-time constraint checking")
print("   ")
print("   💡 KEY INSIGHT:")
print("      Even in deterministic domains, penalty choice matters for:")
print("      - Expressing different levels of constraint importance")
print("      - Balancing computational efficiency vs. expressiveness")
print("      - Adapting to different application requirements")

print("\n" + "="*80)
