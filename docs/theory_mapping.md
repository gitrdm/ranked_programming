# Theory-to-Implementation Mapping

## Overview

This document provides a comprehensive mapping between Wolfgang Spohn's Ranking Theory concepts and their implementation in the ranked_programming Python library. It serves as a bridge between theoretical foundations and practical usage.

## Table of Contents

1. [Negative Ranking Function (κ)](#negative-ranking-function-κ)
2. [Belief Function (τ)](#belief-function-τ)
3. [Conditional Ranks (κ(B|A))](#conditional-ranks-κba)
4. [Law of Disjunction](#law-of-disjunction)
5. [Core Combinators](#core-combinators)
6. [Implementation Details](#implementation-details)

## Negative Ranking Function (κ)

### Theoretical Definition

The **negative ranking function κ: Ω → ℕ ∪ {∞}** assigns to each possible world ω a natural number representing the degree of disbelief:

- κ(ω) = 0: ω is not disbelieved (normal/certain)
- κ(ω) = n > 0: ω is disbelieved to degree n (exceptional/surprising)
- κ(ω) = ∞: ω is impossible

### Implementation Mapping

```python
from ranked_programming import Ranking, nrm_exc

# Create a ranking with disbelief ranks
ranking = Ranking(lambda: nrm_exc('normal', 'exceptional', 2))
# κ('normal') = 0, κ('exceptional') = 2

# Query disbelief ranks
kappa_normal = ranking.disbelief_rank(lambda x: x == 'normal')  # Returns: 0
kappa_exceptional = ranking.disbelief_rank(lambda x: x == 'exceptional')  # Returns: 2
kappa_impossible = ranking.disbelief_rank(lambda x: x == 'impossible')  # Returns: float('inf')
```

### Key Properties

- **Minimality**: κ(A) = min{κ(ω) | ω ∈ A} for any proposition A
- **Additivity**: κ(A ∪ B) = min(κ(A), κ(B)) (law of disjunction)
- **Conditional**: κ(A|B) = κ(A ∧ B) - κ(B) when κ(B) < ∞

## Belief Function (τ)

### Theoretical Definition

The **belief function τ: Ω → ℤ** is derived from the negative ranking function:

τ(A) = κ(∼A) - κ(A)

**Interpretation:**
- τ(A) > 0: Positive belief in A (∼A is more disbelieved than A)
- τ(A) < 0: Disbelief in A (A is more disbelieved than ∼A)
- τ(A) = 0: Suspension of judgment (equal disbelief in A and ∼A)

### Implementation Mapping

```python
from ranked_programming import Ranking, nrm_exc

# Create ranking: healthy (normal) vs sick (exceptional)
ranking = Ranking(lambda: nrm_exc('healthy', 'sick', 3))

# Compute belief ranks
tau_healthy = ranking.belief_rank(lambda x: x == 'healthy')  # Returns: 3 (strong belief)
tau_sick = ranking.belief_rank(lambda x: x == 'sick')        # Returns: -3 (strong disbelief)

# Suspension of judgment example
suspension = Ranking(lambda: [('A', 1), ('B', 1)])
tau_A = suspension.belief_rank(lambda x: x == 'A')  # Returns: 0 (suspension)
```

### Relationship to κ

The belief function provides an intuitive measure of belief strength:

- **Strong belief**: τ(A) >> 0 (κ(∼A) ≫ κ(A))
- **Strong disbelief**: τ(A) << 0 (κ(A) ≫ κ(∼A))
- **Suspension**: τ(A) = 0 (κ(A) = κ(∼A))

## Conditional Ranks (κ(B|A))

### Theoretical Definition

**Conditional disbelief** represents disbelief in B given that A is true:

κ(B|A) = κ(A ∧ B) - κ(A)

This enables reasoning about dependencies and conditional probabilities in ranking terms.

### Implementation Mapping

```python
from ranked_programming import Ranking, nrm_exc

# Create ranking with joint possibilities
ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

# κ(A∧B) = 0, κ(A) = 0, so κ(B|A) = 0 - 0 = 0
conditional = ranking.conditional_disbelief(
    lambda x: x[0] == 'A',      # Condition A
    lambda x: x[1] == 'B'       # Consequent B
)
# Returns: 0.0
```

### Properties

- **Normalization**: κ(B|A) ≥ 0 when κ(A) < ∞
- **Composition**: κ(C|A∧B) = κ(C∧A∧B) - κ(A∧B)
- **Chain Rule**: κ(A∧B) = κ(A) + κ(B|A) (when κ(A) < ∞)

## Law of Disjunction

### Theoretical Definition

The **law of disjunction** is a fundamental axiom of ranking theory:

κ(A ∪ B) = min(κ(A), κ(B))

This enables efficient computation of disjunctive possibilities and is the basis for the `nrm_exc` combinator.

### Implementation Mapping

```python
from ranked_programming import Ranking, nrm_exc

# Law of disjunction in action
ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

kappa_A = ranking.disbelief_rank(lambda x: x == 'A')        # κ(A) = 0
kappa_B = ranking.disbelief_rank(lambda x: x == 'B')        # κ(B) = 1
kappa_A_or_B = ranking.disbelief_rank(lambda x: x in ['A', 'B'])  # κ(A∪B) = 0

# Verify: κ(A∪B) = min(κ(A), κ(B))
assert kappa_A_or_B == min(kappa_A, kappa_B)  # True
```

### Applications

- **Choice Points**: Representing alternative possibilities
- **Exception Handling**: Normal vs exceptional execution paths
- **Uncertainty Modeling**: Graded alternatives in decision making

## Core Combinators

### `nrm_exc(v1, v2, rank2)`

**Theoretical Mapping:** Implements the law of disjunction

```python
# Theory: κ(A∪B) = min(κ(A), κ(B))
# Implementation:
ranking = nrm_exc('normal', 'exceptional', 2)
# Result: κ('normal') = 0, κ('exceptional') = 2
```

### `observe_e(evidence, predicate, ranking)`

**Theoretical Mapping:** Implements conditional ranking renormalization

```python
# Theory: κ(·|E) - conditional ranks given evidence E
# Implementation:
conditioned = observe_e(2, lambda x: x % 2 == 0, ranking)
# Renormalizes ranks relative to even numbers
```

### `Ranking` Class Methods

**New Theoretical Methods (Phase 1):**
- `disbelief_rank(proposition)` → κ(A)
- `belief_rank(proposition)` → τ(A)
- `conditional_disbelief(condition, consequent)` → κ(B|A)

## Implementation Details

### Type System

```python
from ranked_programming.theory_types import (
    DisbeliefRank,    # int | float (for infinity)
    BeliefRank,       # int
    Proposition       # Callable[[Any], bool]
)

# Type annotations ensure theoretical correctness
def disbelief_rank(self, proposition: Proposition) -> DisbeliefRank:
    """Compute κ(A) for proposition A."""
```

### Infinity Handling

The implementation properly handles infinite ranks:

```python
# Theoretical: κ(impossible) = ∞
kappa_impossible = ranking.disbelief_rank(lambda x: False)
assert kappa_impossible == float('inf')

# Belief rank handles infinity correctly
tau_impossible = ranking.belief_rank(lambda x: False)
# Returns: -∞ (strong disbelief in impossibility)
```

### Performance Characteristics

- **Lazy Evaluation**: Rankings are computed on-demand
- **Deduplication**: Automatic elimination of redundant possibilities
- **Memory Efficiency**: Generator-based implementation for large spaces

## Examples in Context

### Medical Diagnosis

```python
# Model: Healthy (normal) vs Various illnesses (graded exceptions)
diagnosis = Ranking(lambda: nrm_exc(
    ('healthy', 'no_symptoms'),
    nrm_exc(
        ('mild_illness', 'mild_symptoms'),
        ('severe_illness', 'severe_symptoms'),
        2  # Severe is much more exceptional
    ),
    1  # Any illness is somewhat exceptional
))

# Theoretical analysis
kappa_healthy = diagnosis.disbelief_rank(lambda x: x[0] == 'healthy')  # κ(healthy) = 0
tau_healthy = diagnosis.belief_rank(lambda x: x[0] == 'healthy')       # τ(healthy) = 2

kappa_symptoms = diagnosis.disbelief_rank(lambda x: x[1] != 'no_symptoms')  # κ(symptoms) = 1
kappa_severe = diagnosis.disbelief_rank(lambda x: x[1] == 'severe_symptoms')  # κ(severe) = 3
```

### Fault Diagnosis

```python
# Model boolean circuit faults
circuit = Ranking(lambda: nrm_exc(
    'all_gates_working',
    nrm_exc(
        'gate1_faulty',
        nrm_exc('gate2_faulty', 'gate3_faulty', 1),
        1
    ),
    2  # Any fault is surprising
))

# Conditional diagnosis
kappa_fault1_given_problem = circuit.conditional_disbelief(
    lambda x: x != 'all_gates_working',  # Given there's a problem
    lambda x: x == 'gate1_faulty'        # Fault is in gate1
)
```

## Conclusion

This mapping document shows how the ranked_programming library provides direct access to Spohn's theoretical constructs while maintaining computational efficiency and practical usability. The implementation bridges the gap between philosophical theory and programming practice, enabling developers to reason about uncertainty using rigorous theoretical foundations.

For practical examples, see `examples/spohn_theory_demo.py`.</content>
<parameter name="filePath">/home/rdmerrio/Documents/repos/ranked_programming/docs/theory_mapping.md
