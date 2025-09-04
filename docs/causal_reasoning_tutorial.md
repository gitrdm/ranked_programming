# Causal Reasoning Tutorial for Ranked Programming

## Introduction to Causal Reasoning

Causal reasoning is the process of understanding cause-and-effect relationships in complex systems. In ranked programming, we use ranking theory to model and analyze causal relationships, interventions, and counterfactuals.

This tutorial covers:
- Basic causal inference concepts
- Intervention analysis
- Counterfactual reasoning
- Causal discovery algorithms
- Practical examples

## 1. Basic Causal Concepts

### Direct Causation

A variable X is a direct cause of Y if intervening on X changes the value of Y.

```python
from ranked_programming import Ranking, nrm_exc
from ranked_programming.causal_reasoning import CausalReasoner

# Create a simple causal model: Treatment → Outcome
ranking = Ranking(lambda: nrm_exc(
    ('treatment', 'good_outcome'),    # Normal case
    ('treatment', 'bad_outcome'),     # Exceptional case
    1
))

reasoner = CausalReasoner()
treatment_given = lambda x: x[0] == 'treatment'
good_outcome = lambda x: x[1] == 'good_outcome'

is_cause, strength = reasoner.is_direct_cause(
    treatment_given, good_outcome, [], ranking
)

print(f"Treatment causes good outcome: {is_cause}")
print(f"Causal strength: {strength}")
```

### Causal Strength

Causal strength measures how strongly one variable influences another. Higher values indicate stronger causal relationships.

## 2. Intervention Analysis

Interventions allow us to understand what happens when we force a variable to take a specific value, regardless of its natural causes.

```python
# What happens if we force treatment to be given?
factual, counterfactual = reasoner.counterfactual_reasoning(
    ranking,
    {treatment_given: True},  # Intervene: force treatment
    good_outcome             # Query: what happens to outcome?
)

print(f"Natural outcome probability: {factual}")
print(f"Outcome with forced treatment: {counterfactual}")
print(f"Causal effect: {counterfactual - factual}")
```

## 3. Conditional Causal Analysis

Sometimes causal relationships depend on background conditions.

```python
# Define a background condition
background_condition = lambda x: x[2] == 'favorable_conditions'

conditional_results = reasoner.conditional_causal_analysis(
    treatment_given, good_outcome, background_condition, ranking
)

print("Conditional causal analysis:")
print(f"Unconditional effect: {conditional_results['unconditional_effect']}")
print(f"Effect when conditions favorable: {conditional_results['conditional_true_effect']}")
print(f"Effect when conditions unfavorable: {conditional_results['conditional_false_effect']}")
```

## 4. Causal Discovery

Causal discovery algorithms can automatically find causal relationships from observational data.

```python
# Define variables to analyze
variables = [
    lambda x: x[0] == 'treatment',
    lambda x: x[1] == 'outcome',
    lambda x: x[2] == 'confounder'
]

# Run PC algorithm for causal discovery
causal_matrix = reasoner.pc_algorithm(variables, ranking)

# Print discovered relationships
for (i, j), strength in causal_matrix.items():
    if strength > 0:
        var_names = ['Treatment', 'Outcome', 'Confounder']
        print(f"{var_names[i]} → {var_names[j]} (strength: {strength})")
```

## 5. Confounding and Mediation

### Confounding

Confounding occurs when a third variable affects both the cause and effect, creating a spurious association.

```python
# Model with confounding: X ← C → Y
confounded_ranking = Ranking(lambda: nrm_exc(
    ('x_true', 'c_true', 'y_true'),   # Confounder affects both
    ('x_false', 'c_true', 'y_false'), # Confounder affects both
    1
))

x_cause = lambda x: x[0] == 'x_true'
y_effect = lambda x: x[2] == 'y_true'
confounder = lambda x: x[1] == 'c_true'

# Test for confounding
unconditional_corr = reasoner.analyze_conditional_independence(
    x_cause, y_effect, confounder, confounded_ranking
)

print(f"Variables are conditionally independent: {unconditional_corr['conditionally_independent']}")
```

### Mediation

Mediation occurs when a causal effect is transmitted through an intermediate variable.

```python
# Mediation model: X → M → Y
mediated_ranking = Ranking(lambda: nrm_exc(
    ('x_true', 'm_true', 'y_true'),   # X causes M, M causes Y
    ('x_true', 'm_false', 'y_false'), # X fails to cause M
    1
))

x_var = lambda x: x[0] == 'x_true'
m_mediator = lambda x: x[1] == 'm_true'
y_outcome = lambda x: x[2] == 'y_true'

# Analyze mediation
total_effect, _ = reasoner.is_direct_cause(x_var, y_outcome, [], mediated_ranking)
direct_effect, _ = reasoner.is_direct_cause(x_var, y_outcome, [m_mediator], mediated_ranking)

mediated_effect = total_effect - direct_effect
print(f"Total effect: {total_effect}")
print(f"Direct effect: {direct_effect}")
print(f"Mediated effect: {mediated_effect}")
```

## 6. Advanced Topics

### Causal Effect Estimation

```python
# Estimate average causal effect
effect_strength = reasoner.causal_effect_strength(
    treatment_given, good_outcome, ranking
)
print(f"Average causal effect: {effect_strength}")
```

### Multiple Interventions

```python
# Analyze combined interventions
combined_intervention = {
    treatment_given: True,
    background_condition: True
}

factual, counterfactual = reasoner.counterfactual_reasoning(
    ranking, combined_intervention, good_outcome
)
```

### Causal Model Validation

```python
# Validate a proposed causal graph
proposed_graph = {
    'treatment': ['outcome'],
    'confounder': ['treatment', 'outcome']
}

validation_results = reasoner.validate_causal_assumptions(
    proposed_graph, ranking, variables
)
```

## 7. Practical Applications

### Medical Diagnosis

```python
# Model symptom → disease → test_result
symptom_present = lambda x: x[0] == 'symptom'
disease_present = lambda x: x[1] == 'disease'
test_positive = lambda x: x[2] == 'positive'

# Analyze diagnostic accuracy
is_cause, strength = reasoner.is_direct_cause(
    disease_present, test_positive, [symptom_present], medical_ranking
)
```

### Policy Analysis

```python
# Model policy → behavior → outcome
policy_implemented = lambda x: x[0] == 'policy'
behavior_changed = lambda x: x[1] == 'changed'
outcome_improved = lambda x: x[2] == 'improved'

# Evaluate policy effectiveness
effect = reasoner.causal_effect_strength(
    policy_implemented, outcome_improved, policy_ranking
)
```

### Quality Control

```python
# Model defect → failure → cost
defect_present = lambda x: x[0] == 'defect'
system_fails = lambda x: x[1] == 'fails'
cost_incurred = lambda x: x[2] == 'high_cost'

# Analyze quality impact
is_cause, strength = reasoner.is_direct_cause(
    defect_present, cost_incurred, [], quality_ranking
)
```

## 8. Best Practices

### 1. Define Clear Propositions

```python
# Good: Clear, unambiguous propositions
treatment_administered = lambda x: x['treatment_dose'] > 0
outcome_successful = lambda x: x['recovery_time'] < 7

# Avoid: Vague or ambiguous propositions
good_treatment = lambda x: x['treatment'] == 'good'  # What is "good"?
```

### 2. Consider Background Knowledge

```python
# Include relevant background conditions
reasoner = CausalReasoner({
    'domain': 'medicine',
    'assumptions': ['no_unmeasured_confounding', 'intervention_possible']
})
```

### 3. Validate Assumptions

```python
# Test for conditional independence
independence_test = reasoner.analyze_conditional_independence(
    cause, effect, potential_confounder, ranking
)

if not independence_test['conditionally_independent']:
    print("Warning: Potential confounding detected")
```

### 4. Use Multiple Methods

```python
# Combine different causal analysis approaches
direct_causation = reasoner.is_direct_cause(cause, effect, [], ranking)
intervention_effect = reasoner.counterfactual_reasoning(ranking, {cause: True}, effect)
conditional_analysis = reasoner.conditional_causal_analysis(cause, effect, condition, ranking)

# Cross-validate results
consistent = all([
    direct_causation[0] == (intervention_effect[1] > intervention_effect[0]),
    abs(direct_causation[1] - (intervention_effect[1] - intervention_effect[0])) < 0.1
])
```

## 9. Common Pitfalls

### 1. Ignoring Confounding

```python
# Wrong: Ignoring potential confounders
is_cause, _ = reasoner.is_direct_cause(cause, effect, [], ranking)

# Better: Control for known confounders
is_cause, _ = reasoner.is_direct_cause(cause, effect, [confounder1, confounder2], ranking)
```

### 2. Over-interpreting Correlation

```python
# Correlation ≠ Causation
correlation = reasoner.analyze_conditional_independence(cause, effect, [], ranking)
if not correlation['conditionally_independent']:
    print("Variables are correlated, but causation needs further analysis")
```

### 3. Assuming Linearity

```python
# Causal effects can be non-linear
# Test interventions at different levels
for intervention_value in [0.1, 0.5, 0.9]:
    _, effect = reasoner.counterfactual_reasoning(
        ranking, {cause: intervention_value}, effect
    )
    print(f"Intervention {intervention_value} → Effect {effect}")
```

## 10. Integration with Existing Code

### Combining with Combinators

```python
# Use existing combinators in causal analysis
from ranked_programming import observe_e

# Create intervened ranking
intervened_ranking = Ranking(lambda: observe_e(
    0,  # Hard intervention
    lambda x: cause(x),  # Intervention condition
    original_ranking
))

# Analyze effects
reasoner = CausalReasoner()
effect_analysis = reasoner.causal_effect_strength(
    cause, effect, intervened_ranking
)
```

### Working with Belief Propagation

```python
# Integrate with belief propagation networks
from ranked_programming.belief_propagation import BeliefPropagationNetwork

# Create causal network
causal_network = BeliefPropagationNetwork({
    'cause': cause_ranking,
    'effect': effect_ranking,
    'confounder': confounder_ranking
})

# Propagate beliefs with interventions
results = causal_network.propagate_beliefs({
    'cause': lambda x: True  # Intervene on cause
})
```

### Using CP-SAT strategies (optional)

When OR-Tools is installed, you can switch to CP-SAT-backed strategies for faster separating-set search and minimal repairs on larger instances.

Install and enable:

```bash
pip install -e .[cp-sat]
# Optional: run CP-SAT tests
ORTOOLS_AVAILABLE=1 pytest -q
```

Example usage (guarded import):

```python
try:
    from ranked_programming.causal import (
        CPSATSeparatingSetFinder,
        CPSATMinimalRepair,
        SeparatingSetRequest,
        ranked_ci,
        StructuralRankingModel,
        Variable,
    )
    from ranked_programming.ranking_class import Ranking
    from ranked_programming.ranking_combinators import nrm_exc

    # Small chain X->Z->Y
    X = Variable("X", (False, True), (), lambda: Ranking.from_generator(nrm_exc, False, True, 1))
    Z = Variable("Z", (False, True), ("X",), lambda x: x)
    Y = Variable("Y", (False, True), ("Z",), lambda z: z)
    srm = StructuralRankingModel([X, Z, Y])

    # Separating set via CP-SAT
    z_finder = CPSATSeparatingSetFinder()
    Zset = z_finder.find(SeparatingSetRequest("X", "Y", ["Z"], k_max=1), srm, ranked_ci)
    print("CP-SAT separating set for X–Y:", Zset)

    # Minimal repairs via CP-SAT
    mr = CPSATMinimalRepair()
    repairs = mr.repairs(srm, target="Y", desired_value=True, candidates=["Z", "X"], max_size=1)
    print("CP-SAT minimal repairs for Y=True:", repairs)
except ImportError:
    print("Install OR-Tools: pip install -e .[cp-sat]")
```

The CP-SAT implementations minimize set sizes and iterate with no-good cuts, validating each candidate using SRM surgery semantics to keep results sound.

## Backends and extras (optional)

To enable solver-backed strategies (e.g., CP-SAT) for separating sets and minimal repairs:

- Install extras:
  - `pip install -e .[cp-sat]` for OR-Tools CP-SAT
  - `pip install -e .[maxsat]` for PySAT/MaxSAT (optional)
  - `pip install -e .[asp]` for clingo/ASP (optional)
- Run CP-SAT tests (optional):
  - `ORTOOLS_AVAILABLE=1 pytest -q`

The library falls back to greedy strategies when optional backends are not installed. APIs are available under `ranked_programming.causal` (e.g., `CPSATSeparatingSetFinder`, `CPSATMinimalRepair`).
