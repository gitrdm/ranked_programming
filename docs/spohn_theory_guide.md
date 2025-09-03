# Spohn's Ranking Theory: A Comprehensive Guide

## Introduction

Wolfgang Spohn's **Ranking Theory** provides a philosophical framework for reasoning about uncertainty that differs fundamentally from probability theory. Instead of assigning probabilities to propositions, ranking theory assigns **degrees of disbelief** to possible worlds.

This guide explains ranking theory concepts and their implementation in the ranked_programming library.

## Core Concepts

### The Negative Ranking Function (κ)

The fundamental concept in ranking theory is the **negative ranking function κ** (kappa):

```
κ: Ω → ℕ ∪ {∞}
```

Where Ω is the set of all possible worlds, and κ assigns to each world a natural number (or infinity) representing the degree of disbelief in that world.

#### Interpretation of κ Values

- **κ(ω) = 0**: World ω is not disbelieved (normal/certain)
- **κ(ω) = 1**: World ω is disbelieved to degree 1 (somewhat surprising)
- **κ(ω) = 2**: World ω is disbelieved to degree 2 (more surprising)
- **κ(ω) = ∞**: World ω is impossible

#### Proposition Rankings

For any proposition A (set of worlds), the disbelief rank is:

```
κ(A) = min{κ(ω) | ω ∈ A}
```

This means κ(A) is the smallest disbelief rank among all worlds where A is true.

### The Belief Function (τ)

The **belief function τ** (tau) is derived from the negative ranking function:

```
τ(A) = κ(∼A) - κ(A)
```

Where ∼A is the negation of proposition A.

#### Interpretation of τ Values

- **τ(A) > 0**: Positive belief in A (∼A is more disbelieved than A)
- **τ(A) < 0**: Disbelief in A (A is more disbelieved than ∼A)
- **τ(A) = 0**: Suspension of judgment (equal disbelief in A and ∼A)

### Conditional Ranks

**Conditional disbelief** represents disbelief in B given that A is true:

```
κ(B|A) = κ(A ∧ B) - κ(A)
```

This enables reasoning about dependencies and conditional relationships.

## Fundamental Laws

### Law of Disjunction

The most important law in ranking theory:

```
κ(A ∪ B) = min(κ(A), κ(B))
```

This law enables efficient computation of disjunctive possibilities and is the foundation for the `nrm_exc` combinator.

### Law of Conjunction

For conjunctions:

```
κ(A ∧ B) = κ(A) + κ(B|A)
```

When κ(A) < ∞, this shows how conditional ranks compose.

### Consistency Conditions

Ranking functions must satisfy:
1. κ(⊤) = 0 (the necessary proposition has rank 0)
2. κ(⊥) = ∞ (the impossible proposition has rank ∞)
3. κ(A) ≤ κ(B) when A ⊆ B (monotonicity)

## Philosophical Foundations

### Comparison with Probability Theory

| Aspect | Probability Theory | Ranking Theory |
|--------|-------------------|----------------|
| **Basic Concept** | Degree of belief (0-1) | Degree of disbelief (ℕ ∪ {∞}) |
| **Uncertainty** | Precise numerical values | Ordinal ranking |
| **Computation** | Multiplication/addition | Min/max operations |
| **Conditioning** | Bayes' theorem | Rank subtraction |
| **Application** | Statistical inference | Qualitative reasoning |

### Advantages of Ranking Theory

1. **Computational Simplicity**: Ordinal operations (min/max) vs numerical calculations
2. **Qualitative Reasoning**: Captures "normal vs exceptional" distinctions
3. **Philosophical Clarity**: Explicit representation of disbelief
4. **Default Reasoning**: Natural handling of default assumptions

## Implementation in Ranked Programming

### Basic Usage

```python
from ranked_programming import Ranking, nrm_exc

# Create a ranking: normal case vs exceptional case
ranking = Ranking(lambda: nrm_exc('normal', 'exceptional', 2))

# Query theoretical values
kappa_normal = ranking.disbelief_rank(lambda x: x == 'normal')        # 0
kappa_exceptional = ranking.disbelief_rank(lambda x: x == 'exceptional')  # 2
tau_normal = ranking.belief_rank(lambda x: x == 'normal')             # 2
```

### Law of Disjunction Example

```python
# κ(A∪B) = min(κ(A), κ(B))
ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

kappa_A = ranking.disbelief_rank(lambda x: x == 'A')        # 0
kappa_B = ranking.disbelief_rank(lambda x: x == 'B')        # 1
kappa_A_or_B = ranking.disbelief_rank(lambda x: x in ['A', 'B'])  # 0

assert kappa_A_or_B == min(kappa_A, kappa_B)  # True
```

### Conditional Reasoning

```python
# Model: Weather affects activity
weather = Ranking(lambda: nrm_exc(
    ('sunny', 'outdoor'),
    nrm_exc(
        ('sunny', 'indoor'),
        ('rainy', 'indoor'),
        1
    ),
    2  # Rainy weather is exceptional
))

# Conditional: activity given weather
kappa_indoor_given_sunny = weather.conditional_disbelief(
    lambda w: w[0] == 'sunny',     # Given sunny weather
    lambda w: w[1] == 'indoor'     # Indoor activity
)
```

## Advanced Concepts

### Ranking Dynamics

Ranking theory includes principles for how rankings change with new information:

1. **Conditionalization**: κ(·|E) = κ(· ∧ E) - κ(E)
2. **Upranking**: Increasing disbelief in certain possibilities
3. **Default Reasoning**: Natural handling of default assumptions

### Multiple Extensions

A ranking function can have multiple extensions when there are ties in disbelief ranks. This allows modeling of incomplete information.

### Comparative Rankings

Ranking theory naturally supports comparative judgments:
- A is more believable than B: κ(A) < κ(B)
- A is equally believable as B: κ(A) = κ(B)

## Applications

### Fault Diagnosis

```python
# Boolean circuit diagnosis
circuit = Ranking(lambda: nrm_exc(
    'all_components_ok',
    nrm_exc(
        'component_A_failed',
        nrm_exc('component_B_failed', 'component_C_failed', 1),
        1
    ),
    3  # Any failure is highly exceptional
))

# Diagnostic reasoning
kappa_failure_A = circuit.disbelief_rank(lambda x: x == 'component_A_failed')
tau_failure_A = circuit.belief_rank(lambda x: x == 'component_A_failed')
```

### Medical Reasoning

```python
# Symptom-based diagnosis
diagnosis = Ranking(lambda: nrm_exc(
    ('healthy', 'no_symptoms'),
    nrm_exc(
        ('viral', 'fever'),
        nrm_exc(
            ('bacterial', 'fever'),
            ('chronic', 'fatigue'),
            1
        ),
        1
    ),
    2
))

# Conditional diagnosis
kappa_bacterial_given_fever = diagnosis.conditional_disbelief(
    lambda case: case[1] == 'fever',
    lambda case: case[0] == 'bacterial'
)
```

### Spelling Correction

```python
# Model: correct word vs common misspellings
correction = Ranking(lambda: nrm_exc(
    'correct_spelling',
    nrm_exc(
        'missing_letter',
        nrm_exc(
            'wrong_letter',
            nrm_exc('transposed_letters', 'extra_letter', 1),
            1
        ),
        1
    ),
    2  # Any misspelling is exceptional
))
```

## Relationship to Other Theories

### Probability Theory

Ranking theory can be embedded in probability theory:
- κ(ω) = -log P(ω) (up to scaling)
- τ(A) relates to log odds ratios

### Belief Functions

Ranking theory provides a foundation for Dempster-Shafer theory and other belief function approaches.

### Default Logic

Ranking theory formalizes default assumptions and non-monotonic reasoning.

## Further Reading

### Primary Sources

- Spohn, W. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press.
- Spohn, W. (1988). "Ordinal Conditional Functions: A Dynamic Theory of Epistemic States." In *Causation in Decision, Belief Change, and Statistics* (pp. 105-134).

### Applications

- Rienstra, T. (2014). "Ranked Programming." Master's thesis exploring computational implementations.
- Various papers on fault diagnosis, medical reasoning, and AI applications.

## Conclusion

Ranking theory provides a powerful alternative to probability theory for reasoning about uncertainty, particularly when the distinction between "normal" and "exceptional" is more important than precise numerical probabilities. The ranked_programming library makes these theoretical concepts accessible through a practical programming interface.

The theory's emphasis on ordinal relationships and computational simplicity makes it particularly suitable for applications where qualitative reasoning is more appropriate than quantitative calculations.</content>
<parameter name="filePath">/home/rdmerrio/Documents/repos/ranked_programming/docs/spohn_theory_guide.md
