# Theoretical Foundations of Ranking Theory

## Mathematical Framework

This document presents the formal mathematical foundations of Wolfgang Spohn's Ranking Theory, providing the theoretical basis for the ranked_programming library implementation.

## Basic Definitions

### Possible Worlds and Propositions

Let Ω be a set of **possible worlds**. A **proposition** A is a subset of Ω, representing all worlds where A is true.

### Negative Ranking Function

A **negative ranking function** κ is a function:

```
κ: Ω → ℕ ∪ {∞}
```

Where ℕ is the set of natural numbers {0, 1, 2, ...} and ∞ represents impossibility.

#### Axioms of Ranking Functions

1. **Existence of Normal Worlds**: ∃ω ∈ Ω such that κ(ω) = 0
2. **Finiteness**: The set {ω ∈ Ω | κ(ω) < ∞} is finite
3. **Monotonicity**: If A ⊆ B then κ(A) ≥ κ(B)

### Proposition Rankings

For any proposition A ⊆ Ω:

```
κ(A) = min{κ(ω) | ω ∈ A}        if A ≠ ∅
κ(A) = ∞                        if A = ∅
```

## Derived Functions

### Belief Function (τ)

The **belief function** τ is defined as:

```
τ(A) = κ(∼A) - κ(A)
```

Where ∼A = Ω ∖ A is the complement of A.

#### Properties of τ

- **Range**: τ: 2^Ω → ℤ ∪ {±∞}
- **Symmetry**: τ(∼A) = -τ(A)
- **Normalization**: τ(⊤) = 0, τ(⊥) = -∞

### Conditional Rankings

The **conditional disbelief** in B given A:

```
κ(B|A) = κ(A ∧ B) - κ(A)    if κ(A) < ∞
κ(B|A) = ∞                   if κ(A) = ∞
```

## Fundamental Laws

### Law of Disjunction

For any propositions A, B:

```
κ(A ∪ B) = min(κ(A), κ(B))
```

**Proof:**
- If κ(A) ≤ κ(B), then κ(A ∪ B) = κ(A) = min(κ(A), κ(B))
- If κ(B) < κ(A), then κ(A ∪ B) = κ(B) = min(κ(A), κ(B))

### Law of Conjunction

For any propositions A, B:

```
κ(A ∧ B) = κ(A) + κ(B|A)
```

**Proof:**
κ(A ∧ B) = min{κ(ω) | ω ∈ A ∧ B}
κ(A) = min{κ(ω) | ω ∈ A}
κ(B|A) = κ(A ∧ B) - κ(A)

### Chain Rule

For propositions A, B, C:

```
κ(A ∧ B ∧ C) = κ(A) + κ(B|A) + κ(C|A∧B)
```

## Ranking Dynamics

### Conditionalization

When new evidence E is observed, rankings are updated:

```
κ'(·) = κ(·|E) = κ(· ∧ E) - κ(E)
```

This preserves the ranking function properties.

### Upranking

Increasing disbelief in a proposition A:

```
κ'(ω) = κ(ω) + n    for ω ∈ A
κ'(ω) = κ(ω)       for ω ∉ A
```

## Implementation in Ranked Programming

### Combinator Semantics

#### `nrm_exc(v1, v2, n)`

**Mathematical Semantics:**
```
κ(v1) = 0
κ(v2) = n
κ(other) = ∞
```

**Theoretical Justification:** Implements the law of disjunction for binary choices.

#### `observe_e(e, p, r)`

**Mathematical Semantics:**
```
κ'(ω) = κ(ω) + e    if ¬p(ω)
κ'(ω) = κ(ω)        if p(ω)
κ''(ω) = κ'(ω) - min{κ'(ω') | ω' ∈ Ω}
```

**Theoretical Justification:** Implements conditionalization with evidence penalty.

### Method Implementations

#### `disbelief_rank(proposition)`

**Implementation:**
```python
def disbelief_rank(self, proposition: Callable[[Any], bool]) -> float:
    satisfying_ranks = [rank for value, rank in self if proposition(value)]
    return min(satisfying_ranks) if satisfying_ranks else float('inf')
```

**Mathematical Correctness:** Directly implements κ(A) = min{κ(ω) | ω ∈ A}

#### `belief_rank(proposition)`

**Implementation:**
```python
def belief_rank(self, proposition: Callable[[Any], bool]) -> float:
    disbelief_A = self.disbelief_rank(proposition)
    disbelief_not_A = self.disbelief_rank(lambda x: not proposition(x))
    return disbelief_not_A - disbelief_A
```

**Mathematical Correctness:** Directly implements τ(A) = κ(∼A) - κ(A)

#### `conditional_disbelief(condition, consequent)`

**Implementation:**
```python
def conditional_disbelief(self, condition, consequent):
    disbelief_A_and_B = self.disbelief_rank(lambda x: condition(x) and consequent(x))
    disbelief_A = self.disbelief_rank(condition)
    if disbelief_A == float('inf'):
        return float('inf')
    return disbelief_A_and_B - disbelief_A
```

**Mathematical Correctness:** Directly implements κ(B|A) = κ(A∧B) - κ(A)

## Formal Properties

### Consistency

A ranking function κ is **consistent** if:
1. κ(⊤) = 0
2. κ(⊥) = ∞
3. κ(A ∪ B) = min(κ(A), κ(B)) for all A, B
4. κ(A ∧ B) = κ(A) + κ(B|A) for all A, B where κ(A) < ∞

### Uniqueness

For finite Ω, ranking functions are uniquely determined by their values on singletons.

### Extensions

When rankings have ties, multiple extensions are possible, representing incomplete information.

## Relationship to Probability Theory

### Probabilistic Embeddings

Any ranking function can be embedded in probability theory:

```
P(ω) ∝ 2^{-κ(ω)}    for κ(ω) < ∞
P(ω) = 0            for κ(ω) = ∞
```

### Comparative Probability

Ranking theory can represent comparative probability judgments:
- A is more probable than B: κ(A) < κ(B)
- A and B are equally probable: κ(A) = κ(B)

## Computational Complexity

### Basic Operations

- **κ(A)**: O(|Ω|) - linear in the size of the possibility space
- **τ(A)**: O(|Ω|) - requires computing both κ(A) and κ(∼A)
- **κ(B|A)**: O(|Ω|) - requires computing κ(A∧B) and κ(A)

### Optimizations

The lazy evaluation in ranked_programming provides:
- **Memory Efficiency**: O(1) space for infinite generators
- **Time Efficiency**: Amortized O(1) per element for large rankings
- **Compositional Efficiency**: Combinators compose without full enumeration

## Philosophical Implications

### Epistemic States

Ranking functions represent **epistemic states** - states of belief and disbelief.

### Default Reasoning

Ranking theory provides a natural foundation for default assumptions and non-monotonic reasoning.

### Causation

The theory supports causal reasoning through conditional rankings and their dynamics.

## Conclusion

The mathematical framework of ranking theory provides a rigorous foundation for the ranked_programming library. The implementation maintains mathematical correctness while providing computational efficiency and practical usability.

The formal properties ensure that the library's operations correspond precisely to the theoretical constructs, enabling reliable reasoning about uncertainty using ranking-theoretic principles.</content>
<parameter name="filePath">/home/rdmerrio/Documents/repos/ranked_programming/docs/theoretical_foundations.md
