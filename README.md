# Ranked Programming

A Python library for ranked programming based on Wolfgang Spohn's Ranking Theory. Provides combinators and utilities for reasoning about uncertainty, surprise, and ranked choices in computation using a computationally simpler alternative to probabilistic methods.

This package is used being used as a platform for experimenting with Ranking Theory concepts in places where Bayesian concepts would play a role. This is not a long-term use package and so is likely
not to be maintained but at the time of writing the package includes a fairly complete implementation of...

- **Ranking Theory Theoretical Foundations** with κ, τ, and conditional ranks 
- **A C-Representation Framework** with Kern-Isberner's formalism
- **A Hybrid Integration** combining constraint networks with c-representations

## Synopsis

This library implements **Ranked Programming** based on Wolfgang Spohn's **Ranking Theory** - a philosophical framework for modeling uncertainty that distinguishes between "normal" and "exceptional" occurrences rather than using probabilities.

### Core Idea

While probabilistic programming is powerful, not all uncertainty is probabilistic. Some types of uncertainty are better described by distinguishing between what is "normal" and what is "exceptional". For instance, in fault diagnosis, we might know that a component normally works and only exceptionally fails, without knowing the specific probabilities of failure.

**Ranking Theory** provides an alternative: instead of probabilities, it uses integer "ranks" to measure uncertainty as degrees of surprise. Qualitatively this resemebles,

- **Rank 0:** Not surprising (a normal occurrence)
- **Rank 1:** Surprising (an exceptional occurrence)
- **Rank 2:** Even more surprising
- **Infinity (∞):** Impossible

### Ranked Programming

This library implements a programming model based on these principles. Expressions can have ranked choices, which normally return one value (with a rank of 0) but can exceptionally return another (with a rank of 1 or higher). 

**Key Features:**
- **Theoretical Foundation**: Explicit implementation of Spohn's Ranking Theory with κ (disbelief), τ (belief), and conditional ranks
- **Causal Reasoning**: Complete causal inference toolkit using ranking-theoretic foundations
- **Belief Propagation**: Efficient inference in large ranking networks using Shenoy's algorithm
- **Constraint Solving**: SMT-powered constraint reasoning with Z3 integration
- **C-Representations**: Kern-Isberner's formalism for structured knowledge bases
- **Lazy Evaluation**: Efficient handling of infinite or large search spaces
- **Comprehensive Testing**: 190+ tests ensuring reliability

**Potential use cases:** 
- Fault diagnosis in boolean circuits
- Spelling correction algorithms
- Ranking-based Hidden Markov Models
- Ranking networks for diagnostics
- **C-Representation Knowledge Bases** for structured reasoning
- **Hybrid Constraint-Causal Systems** combining multiple reasoning paradigms
- **Causal Discovery and Analysis** in complex systems
- **Belief Propagation Networks** for large-scale inference
- Any scenario where uncertainty is best described by "normal vs. exceptional" rather than precise probabilities

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gitrdm/ranked-programming.git
   cd ranked-programming
   ```
2. **Install dependencies (recommended: use conda):**
   ```bash
   conda env create -f environment.yml
   conda activate ranked-programming
   ```
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install the package (editable mode):**
   ```bash
   pip install -e .
   ```

## Quick Start

```python
from ranked_programming import nrm_exc, Ranking
from ranked_programming.causal_reasoning import CausalReasoner
from ranked_programming.belief_propagation import BeliefPropagationNetwork

# 1. Basic ranking with normal/exceptional choices
ranking = Ranking(lambda: nrm_exc('healthy', 'faulty', 2))
print("Basic ranking:", list(ranking))

# 2. Theoretical functions
kappa = ranking.disbelief_rank(lambda x: x == 'healthy')  # κ(healthy) = 0
tau = ranking.belief_rank(lambda x: x == 'healthy')       # τ(healthy) = 2
print(f"κ(healthy) = {kappa}, τ(healthy) = {tau}")

# 3. Causal reasoning
reasoner = CausalReasoner()
# ... causal analysis code ...

# 4. Constraint-based reasoning
from ranked_programming.constraint_reasoning import ConstraintRankingNetwork

# Create constraint network
network = ConstraintRankingNetwork(['A', 'B', 'C'])
network.add_constraint('A', 'B', 2)  # Mutual exclusion between A and B
network.add_constraint('B', 'C', 1)  # Causal constraint B → C

# Solve with evidence
evidence = {'A': 'normal'}
result = network.solve_constraints(evidence)
print("Constraint solving result:", {k: list(v) for k, v in result.items()})
```

## Theoretical Foundation

This library explicitly implements **Wolfgang Spohn's Ranking Theory** with direct access to theoretical constructs:

```python
from ranked_programming import nrm_exc, Ranking

# Create a ranking with normal/exceptional choices
ranking = Ranking(lambda: nrm_exc('normal', 'exceptional', 1))

# Access theoretical functions directly
kappa_A = ranking.disbelief_rank(lambda x: x == 'normal')      # κ(A) = 0
tau_A = ranking.belief_rank(lambda x: x == 'normal')           # τ(A) = 1
kappa_B_given_A = ranking.conditional_disbelief(
    lambda x: x == 'normal',    # Condition A
    lambda x: x == 'exceptional' # Consequent B
)  # κ(B|A)
```

**Key Theoretical Methods:**
- `disbelief_rank(proposition)` - Computes κ(A): degree of disbelief in proposition A
- `belief_rank(proposition)` - Computes τ(A): belief function τ(A) = κ(∼A) - κ(A)
- `conditional_disbelief(condition, consequent)` - Computes κ(B|A): conditional disbelief

**Causal Reasoning Methods:**
- `is_direct_cause(cause, effect, background)` - Tests for direct causation using intervention
- `causal_effect_strength(cause, effect)` - Quantifies causal effect strength
- `conditional_causal_analysis(cause, effect, condition)` - Conditional causal analysis
- `pc_algorithm(variables, ranking)` - Constraint-based causal discovery (PC algorithm)
- `validate_causal_assumptions(graph, ranking, variables)` - Validates causal assumptions

**Belief Propagation Methods:**
- `BeliefPropagationNetwork` - Efficient inference in ranking networks
- `propagate_beliefs(evidence)` - Message passing with evidence integration
- `Shenoy's pointwise addition` - Mathematical foundation for combining rankings
- `marginalize(variable)` - Extract marginal distributions from networks

## Bayesian↔Ranking Bridge (intuition)

If you think in probabilities but want the intuition for ranks, a principled bridge is to
use log-odds “bits” as evidence units. With base 2 (one bit per unit):

- From probability to a rank-like measure: k ≈ log2(p/(1−p))
- From a rank-like measure to probability: p ≈ 1 / (1 + 2^(−k))

Interpretation:
- k=0 corresponds to p=50% (neutral). Each +1 in k is “one more bit” in favor (LR×2).
- A compact working range 0..10 already spans ≈50% → 99.9%.

Evidence accumulation:
- Start at k=0 (50%); after n evidence units (bits), k≈n → p≈1/(1+2^(−n)).
- Example: 5 units → p≈1/(1+2^(−5))≈0.969 (≈97%).

Alternative mapping for rare events:
- κ ≈ −log2(p) (when p is small) gives a simple “disbelief in a rare event.”

Explore these mappings in `examples/bayesian_ranking_comprehensive_bridge.py` and adjust bases
or ranges to match your domain intuition.

### At-a-glance mapping (base 2)

Recommended default: one unit = one bit (LR×2). The table below maps k (bits) to p and vice versa.

Bits to probability

| k (bits) | p ≈ 1 / (1 + 2^−k) |
|----------|----------------------|
| 0 | 50.0% |
| 1 | 66.7% |
| 2 | 80.0% |
| 3 | 88.9% |
| 4 | 94.1% |
| 5 | 97.0% |
| 6 | 98.5% |
| 7 | 99.2% |
| 8 | 99.6% |
| 9 | 99.8% |
| 10 | 99.9% |

Selected probabilities to bits

| p | k ≈ log2(p/(1−p)) |
|----|--------------------|
| 0.60 | 0.6 |
| 0.70 | 1.2 |
| 0.80 | 2.0 |
| 0.90 | 3.2 |
| 0.95 | 4.3 |
| 0.99 | 6.6 |

Notes
- Round k to taste (nearest int for quick classification). For example, 0.99 → k≈7.
- Change the base if you want a different “unit of evidence” than a factor of 2.

## Causal Reasoning

This library now includes a complete causal reasoning toolkit based on ranking theory:

```python
from ranked_programming.causal_reasoning import CausalReasoner
from ranked_programming import Ranking, nrm_exc

# Create observational data
ranking = Ranking(lambda: nrm_exc(
    ('A_true', 'B_true'),    # Normal case
    ('A_true', 'B_false'),   # Exceptional case
    1
))

# Test for causation
reasoner = CausalReasoner()
is_cause, strength = reasoner.is_direct_cause(
    lambda x: x[0] == 'A_true',   # Cause: A is true
    lambda x: x[1] == 'B_true',   # Effect: B is true
    [],                          # Background variables
    ranking
)

print(f"A causes B: {is_cause}, Strength: {strength}")

# Conditional causal analysis
results = reasoner.conditional_causal_analysis(
    lambda x: x[0] == 'A_true',   # Cause
    lambda x: x[1] == 'B_true',   # Effect
    lambda x: x[2] == 'C_true',   # Condition
    ranking
)

# Constraint-based causal discovery
causal_matrix = reasoner.pc_algorithm(
    [lambda x: x[0] == 'A_true', lambda x: x[1] == 'B_true'],
    ranking
)
```

**Causal Reasoning Features:**
- **Intervention Analysis**: Test causal relationships using interventions
- **Effect Strength Quantification**: Measure the strength of causal effects
- **Conditional Analysis**: Analyze causation under specific conditions
- **Causal Discovery**: Automatically discover causal structures from data
- **Structure Validation**: Validate causal assumptions and model correctness

## Belief Propagation

This library includes efficient belief propagation for large ranking networks using Shenoy's pointwise addition algorithm:

```python
from ranked_programming.belief_propagation import BeliefPropagationNetwork
from ranked_programming import Ranking, nrm_exc

# Create a ranking network (e.g., A → B → C)
factors = {
    ('A',): Ranking(lambda: nrm_exc('A_healthy', 'A_faulty', 2)),
    ('A', 'B'): Ranking(lambda: nrm_exc(
        ('A_healthy', 'B_good'),
        ('A_healthy', 'B_bad'),
        1
    )),
    ('B', 'C'): Ranking(lambda: nrm_exc(
        ('B_good', 'C_working'),
        ('B_good', 'C_broken'),
        1
    ))
}

# Create belief propagation network
network = BeliefPropagationNetwork(factors)

# Compute marginals without evidence
marginals = network.propagate_beliefs()
print("Marginal for A:", list(marginals['A']))

# Add evidence and recompute
evidence = {'A': lambda x: x == 'A_healthy'}
marginals_with_evidence = network.propagate_beliefs(evidence)
print("Marginal for A with evidence:", list(marginals_with_evidence['A']))
```

**Belief Propagation Features:**
- **Shenoy's Algorithm**: Mathematically sound pointwise addition for ranking combination
- **Message Passing**: Efficient inference in large networks through message passing
- **Evidence Integration**: Proper conditioning using observe_e combinator
- **Marginal Computation**: Extract marginal distributions from complex networks
- **Scalability**: Handles large networks with caching and lazy evaluation
- **Recursion Safety**: Robust error handling for complex ranking compositions

## Constraint-Based Reasoning

This library now includes constraint-based reasoning capabilities with SMT integration for solving complex ranking constraints:

```python
from ranked_programming.constraint_reasoning import ConstraintRankingNetwork
from ranked_programming import Ranking, nrm_exc

# Create a constraint network
network = ConstraintRankingNetwork(['Component_A', 'Component_B', 'System_Status'])

# Add constraints
network.add_constraint('Component_A', 'Component_B', 2)  # Mutual exclusion
network.add_constraint('Component_A', 'System_Status', 1)  # Causal relationship
network.add_constraint('Component_B', 'System_Status', 1)  # Causal relationship

# Solve with evidence
evidence = {'Component_A': 'working'}
result = network.solve_constraints(evidence)

print("Component A status:", list(result['Component_A']))
print("Component B status:", list(result['Component_B']))
print("System status:", list(result['System_Status']))
```

**Constraint-Based Reasoning Features:**
- **SMT Integration**: Uses Z3 SMT solver for efficient constraint solving
- **Multiple Constraint Types**: Mutual exclusion, causal, and exclusion constraints
- **Evidence Integration**: Proper conditioning with partial evidence
- **Scalable Solving**: Handles complex constraint networks efficiently
- **Fallback Support**: Graceful degradation to brute-force when SMT unavailable
- **Optimization**: Minimizes disbelief ranks in constraint satisfaction

## Some Examples

See the `examples/` directory for full scripts demonstrating various applications:

- `boolean_circuit.py` — Boolean circuit with uncertainty
- `ranked_let.py` — Independent and dependent uncertainty with `rlet` and `rlet_star`
- `ranked_procedure_call.py` — Uncertain function application
- `spelling_correction.py` — Spelling correction with ranked choices
- `hidden_markov.py` — Simple hidden Markov model
- `localisation.py` — Robot localisation
- `recursion.py` — Recursion with ranked choices
- `ranking_network.py` — Simple ranking network
- `spohn_theory_demo.py` — Complete demonstration of Spohn's theory (κ, τ, conditional ranks)
- `causal_reasoning_demo.py` — Causal discovery and inference examples
- `belief_propagation_example.py` — Belief propagation in ranking networks
- `demo_smt_constraints.py` — SMT-only constraint solving demonstrations
- `demo_c_representation.py` — C-representation framework demonstrations
- `causal_boolean_circuit.py` — Causal analysis integration with boolean circuits
- `causal_ranking_network.py` — Causal analysis integration with ranking networks
- `google_10000_english_no_swears.py` — Large vocabulary demo (uses small subset by default; --full flag loads real data)

Run an example:
```bash
python examples/boolean_circuit.py
```

Run belief propagation examples:
```bash
python examples/belief_propagation_example.py
```

## Running All Examples

You can run all example scripts at once using the provided `run_examples.sh` script:

```bash
./run_examples.sh
```

To run a specific example, pass the filename as an argument:

```bash
./run_examples.sh boolean_circuit.py
```

This will execute the example(s) and print their output in order.

## Documentation

This project uses [Sphinx](https://www.sphinx-doc.org/) to generate API and user documentation from docstrings and reStructuredText files.

### Prerequisites
- Sphinx and the `sphinx-autodoc-typehints` extension (install with `pip install sphinx sphinx-autodoc-typehints` or see `requirements-dev.txt`)

### Building the Docs

1. Change to the `docs/` directory:
   ```bash
   cd docs
   ```
2. Build the HTML documentation:
   ```bash
   make html
   ```
3. Open the generated documentation:
   - Open `docs/build/html/index.html` in your browser.

All API functions and combinators are documented with literate docstrings. For more details, see the generated HTML docs or the source docstrings.

## Testing

Run all tests with:
```bash
pytest
```

**Test Coverage**: 190+ comprehensive tests covering:
- Core ranking theory functionality
- Theoretical method implementations (κ, τ, conditional ranks)
- Causal reasoning and discovery algorithms
- Belief propagation and message passing
- Constraint-based reasoning with SMT integration
- **C-Representation Framework** with conditional rules and world ranking
- **Hybrid Integration** between constraint networks and c-representations
- Integration with existing combinators
- Edge cases and error handling

## Important Note on Examples and Testing

**All example files in the `examples/regression` directory are ports of the original racket code and are used as regression tests.**

- If you add or modify an example/regression file (e.g., `examples/regression/hidden_markov.py`), you must ensure that its output remains consistent with the expected regression tests.
- Regression tests in `tests/` will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or directory, or disable regression checks for that file.

This ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.

## References

- Rienstra, Tjitze. "Ranked Programming." (Original Racket implementation paper and racket project https://github.com/tjitze/ranked-programming.).
- Spohn, Wolfgang. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press. ISBN-10: 0199697507, ISBN-13: 978-0199697502.
- For algorithmic details, see the background document: `docs/Background/Ranking Theory Algorithmic Realization_.md` (in this repository), which discusses c-representations, conditionalization, and computational implementations of Ranking Theory.

  Marketing blurb:
  Wolfgang Spohn presents the first full account of the dynamic laws of belief, by means of ranking theory. This book is his presentation of ranking theory and its ramifications. He motivates and introduces the basic notion of a ranking function, which recognizes degrees of belief and at the same time accounts for belief simpliciter. He provides a measurement theory for ranking functions, accounts for auto-epistemology in ranking-theoretic terms, and explicates the basic notion of a (deductive or non-deductive) reason. The rich philosophical applications of Spohn's theory include: a new account of lawlikeness, an account of ceteris paribus laws, a new perspective on dispositions, a rich and detailed theory of deterministic causation, an understanding of natural modalities as an objectification of epistemic modalities, an account of the experiential basis of belief--and thus a restructuring of the debate on foundationalism and coherentism (and externalism and contextualism)--and, finally, a revival of fundamental a priori principles of reason fathoming the basics of empiricism and the relation between reason and truth, and concluding in a proof of a weak principle of causality. All this is accompanied by thorough comparative discussions, on a general level as well as within each topic, and in particular with respect to probability theory.

## Deduplication Policy

All core combinators in this library always deduplicate values by their hashable identity, keeping only the first occurrence (with the minimal rank) for each hashable value. Unhashable values (such as lists or dicts) are always yielded, even if repeated. This deduplication is always enabled and is not user-configurable. Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported.

For more details, see the Python reference documentation (`docs/python_reference.md`) and the Sphinx API docs.

## License

See [LICENSE](../LICENSE).

## Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

This library is experimental and intended for research and educational purposes. It implements theoretical concepts from Ranking Theory and may contain bugs, incomplete implementations, or conceptual errors. The authors make no guarantees about the correctness, completeness, or suitability of this software for any particular purpose.

**No Warranties:**
- No warranty of merchantability
- No warranty of fitness for a particular purpose
- No warranty of non-infringement
- No guarantee of accuracy or reliability
- No guarantee of maintenance or support

**Limitations:**
- This is experimental software
- May contain bugs or theoretical errors
- Not intended for production use without thorough testing
- Results should be validated independently
- Use at your own risk

By using this software, you acknowledge that you have read this disclaimer and agree to use the software at your own risk.

# ranked_programming

A Python library for ranked programming based on Wolfgang Spohn's Ranking Theory. Provides combinators and utilities for reasoning about uncertainty, surprise, and ranked choices in computation using a computationally simpler alternative to probabilistic methods.

This package is used being used as a platform for experimenting with Ranking Theory concepts in places where Bayesian concepts would play a role. This is not a long-term use package and so is likely
not to be maintained but at the time of writing the package includes a fairly complete implementation of...

- **Ranking Theory Theoretical Foundations** with κ, τ, and conditional ranks 
- **A C-Representation Framework** with Kern-Isberner's formalism
- **A Hybrid Integration** combining constraint networks with c-representations

## Synopsis

This library implements **Ranked Programming** based on Wolfgang Spohn's **Ranking Theory** - a philosophical framework for modeling uncertainty that distinguishes between "normal" and "exceptional" occurrences rather than using probabilities.

### Core Idea

While probabilistic programming is powerful, not all uncertainty is probabilistic. Some types of uncertainty are better described by distinguishing between what is "normal" and what is "exceptional". For instance, in fault diagnosis, we might know that a component normally works and only exceptionally fails, without knowing the specific probabilities of failure.

**Ranking Theory** provides an alternative: instead of probabilities, it uses integer "ranks" to measure uncertainty as degrees of surprise. Qualitatively this resemebles,

- **Rank 0:** Not surprising (a normal occurrence)
- **Rank 1:** Surprising (an exceptional occurrence)
- **Rank 2:** Even more surprising
- **Infinity (∞):** Impossible

### Ranked Programming

This library implements a programming model based on these principles. Expressions can have ranked choices, which normally return one value (with a rank of 0) but can exceptionally return another (with a rank of 1 or higher). 

**Key Features:**
- **Theoretical Foundation**: Explicit implementation of Spohn's Ranking Theory with κ (disbelief), τ (belief), and conditional ranks
- **Causal Reasoning**: Complete causal inference toolkit using ranking-theoretic foundations
- **Belief Propagation**: Efficient inference in large ranking networks using Shenoy's algorithm
- **Constraint Solving**: SMT-powered constraint reasoning with Z3 integration
- **C-Representations**: Kern-Isberner's formalism for structured knowledge bases
- **Lazy Evaluation**: Efficient handling of infinite or large search spaces
- **Comprehensive Testing**: 190+ tests ensuring reliability

**Potential use cases:** 
- Fault diagnosis in boolean circuits
- Spelling correction algorithms
- Ranking-based Hidden Markov Models
- Ranking networks for diagnostics
- **C-Representation Knowledge Bases** for structured reasoning
- **Hybrid Constraint-Causal Systems** combining multiple reasoning paradigms
- **Causal Discovery and Analysis** in complex systems
- **Belief Propagation Networks** for large-scale inference
- Any scenario where uncertainty is best described by "normal vs. exceptional" rather than precise probabilities

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gitrdm/ranked-programming.git
   cd ranked-programming
   ```
2. **Install dependencies (recommended: use conda):**
   ```bash
   conda env create -f environment.yml
   conda activate ranked-programming
   ```
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install the package (editable mode):**
   ```bash
   pip install -e .
   ```

## Quick Start

```python
from ranked_programming import nrm_exc, Ranking
from ranked_programming.causal_reasoning import CausalReasoner
from ranked_programming.belief_propagation import BeliefPropagationNetwork

# 1. Basic ranking with normal/exceptional choices
ranking = Ranking(lambda: nrm_exc('healthy', 'faulty', 2))
print("Basic ranking:", list(ranking))

# 2. Theoretical functions
kappa = ranking.disbelief_rank(lambda x: x == 'healthy')  # κ(healthy) = 0
tau = ranking.belief_rank(lambda x: x == 'healthy')       # τ(healthy) = 2
print(f"κ(healthy) = {kappa}, τ(healthy) = {tau}")

# 3. Causal reasoning
reasoner = CausalReasoner()
# ... causal analysis code ...

# 4. Constraint-based reasoning
from ranked_programming.constraint_reasoning import ConstraintRankingNetwork

# Create constraint network
network = ConstraintRankingNetwork(['A', 'B', 'C'])
network.add_constraint('A', 'B', 2)  # Mutual exclusion between A and B
network.add_constraint('B', 'C', 1)  # Causal constraint B → C

# Solve with evidence
evidence = {'A': 'normal'}
result = network.solve_constraints(evidence)
print("Constraint solving result:", {k: list(v) for k, v in result.items()})
```

## Theoretical Foundation

This library explicitly implements **Wolfgang Spohn's Ranking Theory** with direct access to theoretical constructs:

```python
from ranked_programming import nrm_exc, Ranking

# Create a ranking with normal/exceptional choices
ranking = Ranking(lambda: nrm_exc('normal', 'exceptional', 1))

# Access theoretical functions directly
kappa_A = ranking.disbelief_rank(lambda x: x == 'normal')      # κ(A) = 0
tau_A = ranking.belief_rank(lambda x: x == 'normal')           # τ(A) = 1
kappa_B_given_A = ranking.conditional_disbelief(
    lambda x: x == 'normal',    # Condition A
    lambda x: x == 'exceptional' # Consequent B
)  # κ(B|A)
```

**Key Theoretical Methods:**
- `disbelief_rank(proposition)` - Computes κ(A): degree of disbelief in proposition A
- `belief_rank(proposition)` - Computes τ(A): belief function τ(A) = κ(∼A) - κ(A)
- `conditional_disbelief(condition, consequent)` - Computes κ(B|A): conditional disbelief

**Causal Reasoning Methods:**
- `is_direct_cause(cause, effect, background)` - Tests for direct causation using intervention
- `causal_effect_strength(cause, effect)` - Quantifies causal effect strength
- `conditional_causal_analysis(cause, effect, condition)` - Conditional causal analysis
- `pc_algorithm(variables, ranking)` - Constraint-based causal discovery (PC algorithm)
- `validate_causal_assumptions(graph, ranking, variables)` - Validates causal assumptions

**Belief Propagation Methods:**
- `BeliefPropagationNetwork` - Efficient inference in ranking networks
- `propagate_beliefs(evidence)` - Message passing with evidence integration
- `Shenoy's pointwise addition` - Mathematical foundation for combining rankings
- `marginalize(variable)` - Extract marginal distributions from networks

## Bayesian↔Ranking Bridge (intuition)

If you think in probabilities but want the intuition for ranks, a principled bridge is to
use log-odds “bits” as evidence units. With base 2 (one bit per unit):

- From probability to a rank-like measure: k ≈ log2(p/(1−p))
- From a rank-like measure to probability: p ≈ 1 / (1 + 2^(−k))

Interpretation:
- k=0 corresponds to p=50% (neutral). Each +1 in k is “one more bit” in favor (LR×2).
- A compact working range 0..10 already spans ≈50% → 99.9%.

Evidence accumulation:
- Start at k=0 (50%); after n evidence units (bits), k≈n → p≈1/(1+2^(−n)).
- Example: 5 units → p≈1/(1+2^(−5))≈0.969 (≈97%).

Alternative mapping for rare events:
- κ ≈ −log2(p) (when p is small) gives a simple “disbelief in a rare event.”

Explore these mappings in `examples/bayesian_ranking_comprehensive_bridge.py` and adjust bases
or ranges to match your domain intuition.

### At-a-glance mapping (base 2)

Recommended default: one unit = one bit (LR×2). The table below maps k (bits) to p and vice versa.

Bits to probability

| k (bits) | p ≈ 1 / (1 + 2^−k) |
|----------|----------------------|
| 0 | 50.0% |
| 1 | 66.7% |
| 2 | 80.0% |
| 3 | 88.9% |
| 4 | 94.1% |
| 5 | 97.0% |
| 6 | 98.5% |
| 7 | 99.2% |
| 8 | 99.6% |
| 9 | 99.8% |
| 10 | 99.9% |

Selected probabilities to bits

| p | k ≈ log2(p/(1−p)) |
|----|--------------------|
| 0.60 | 0.6 |
| 0.70 | 1.2 |
| 0.80 | 2.0 |
| 0.90 | 3.2 |
| 0.95 | 4.3 |
| 0.99 | 6.6 |

Notes
- Round k to taste (nearest int for quick classification). For example, 0.99 → k≈7.
- Change the base if you want a different “unit of evidence” than a factor of 2.

## Causal Reasoning

This library now includes a complete causal reasoning toolkit based on ranking theory:

```python
from ranked_programming.causal_reasoning import CausalReasoner
from ranked_programming import Ranking, nrm_exc

# Create observational data
ranking = Ranking(lambda: nrm_exc(
    ('A_true', 'B_true'),    # Normal case
    ('A_true', 'B_false'),   # Exceptional case
    1
))

# Test for causation
reasoner = CausalReasoner()
is_cause, strength = reasoner.is_direct_cause(
    lambda x: x[0] == 'A_true',   # Cause: A is true
    lambda x: x[1] == 'B_true',   # Effect: B is true
    [],                          # Background variables
    ranking
)

print(f"A causes B: {is_cause}, Strength: {strength}")

# Conditional causal analysis
results = reasoner.conditional_causal_analysis(
    lambda x: x[0] == 'A_true',   # Cause
    lambda x: x[1] == 'B_true',   # Effect
    lambda x: x[2] == 'C_true',   # Condition
    ranking
)

# Constraint-based causal discovery
causal_matrix = reasoner.pc_algorithm(
    [lambda x: x[0] == 'A_true', lambda x: x[1] == 'B_true'],
    ranking
)
```

**Causal Reasoning Features:**
- **Intervention Analysis**: Test causal relationships using interventions
- **Effect Strength Quantification**: Measure the strength of causal effects
- **Conditional Analysis**: Analyze causation under specific conditions
- **Causal Discovery**: Automatically discover causal structures from data
- **Structure Validation**: Validate causal assumptions and model correctness

## Belief Propagation

This library includes efficient belief propagation for large ranking networks using Shenoy's pointwise addition algorithm:

```python
from ranked_programming.belief_propagation import BeliefPropagationNetwork
from ranked_programming import Ranking, nrm_exc

# Create a ranking network (e.g., A → B → C)
factors = {
    ('A',): Ranking(lambda: nrm_exc('A_healthy', 'A_faulty', 2)),
    ('A', 'B'): Ranking(lambda: nrm_exc(
        ('A_healthy', 'B_good'),
        ('A_healthy', 'B_bad'),
        1
    )),
    ('B', 'C'): Ranking(lambda: nrm_exc(
        ('B_good', 'C_working'),
        ('B_good', 'C_broken'),
        1
    ))
}

# Create belief propagation network
network = BeliefPropagationNetwork(factors)

# Compute marginals without evidence
marginals = network.propagate_beliefs()
print("Marginal for A:", list(marginals['A']))

# Add evidence and recompute
evidence = {'A': lambda x: x == 'A_healthy'}
marginals_with_evidence = network.propagate_beliefs(evidence)
print("Marginal for A with evidence:", list(marginals_with_evidence['A']))
```

**Belief Propagation Features:**
- **Shenoy's Algorithm**: Mathematically sound pointwise addition for ranking combination
- **Message Passing**: Efficient inference in large networks through message passing
- **Evidence Integration**: Proper conditioning using observe_e combinator
- **Marginal Computation**: Extract marginal distributions from complex networks
- **Scalability**: Handles large networks with caching and lazy evaluation
- **Recursion Safety**: Robust error handling for complex ranking compositions

## Constraint-Based Reasoning

This library now includes constraint-based reasoning capabilities with SMT integration for solving complex ranking constraints:

```python
from ranked_programming.constraint_reasoning import ConstraintRankingNetwork
from ranked_programming import Ranking, nrm_exc

# Create a constraint network
network = ConstraintRankingNetwork(['Component_A', 'Component_B', 'System_Status'])

# Add constraints
network.add_constraint('Component_A', 'Component_B', 2)  # Mutual exclusion
network.add_constraint('Component_A', 'System_Status', 1)  # Causal relationship
network.add_constraint('Component_B', 'System_Status', 1)  # Causal relationship

# Solve with evidence
evidence = {'Component_A': 'working'}
result = network.solve_constraints(evidence)

print("Component A status:", list(result['Component_A']))
print("Component B status:", list(result['Component_B']))
print("System status:", list(result['System_Status']))
```

**Constraint-Based Reasoning Features:**
- **SMT Integration**: Uses Z3 SMT solver for efficient constraint solving
- **Multiple Constraint Types**: Mutual exclusion, causal, and exclusion constraints
- **Evidence Integration**: Proper conditioning with partial evidence
- **Scalable Solving**: Handles complex constraint networks efficiently
- **Fallback Support**: Graceful degradation to brute-force when SMT unavailable
- **Optimization**: Minimizes disbelief ranks in constraint satisfaction

## Some Examples

See the `examples/` directory for full scripts demonstrating various applications:

- `boolean_circuit.py` — Boolean circuit with uncertainty
- `ranked_let.py` — Independent and dependent uncertainty with `rlet` and `rlet_star`
- `ranked_procedure_call.py` — Uncertain function application
- `spelling_correction.py` — Spelling correction with ranked choices
- `hidden_markov.py` — Simple hidden Markov model
- `localisation.py` — Robot localisation
- `recursion.py` — Recursion with ranked choices
- `ranking_network.py` — Simple ranking network
- `spohn_theory_demo.py` — Complete demonstration of Spohn's theory (κ, τ, conditional ranks)
- `causal_reasoning_demo.py` — Causal discovery and inference examples
- `belief_propagation_example.py` — Belief propagation in ranking networks
- `demo_smt_constraints.py` — SMT-only constraint solving demonstrations
- `demo_c_representation.py` — C-representation framework demonstrations
- `causal_boolean_circuit.py` — Causal analysis integration with boolean circuits
- `causal_ranking_network.py` — Causal analysis integration with ranking networks
- `google_10000_english_no_swears.py` — Large vocabulary demo (uses small subset by default; --full flag loads real data)

Run an example:
```bash
python examples/boolean_circuit.py
```

Run belief propagation examples:
```bash
python examples/belief_propagation_example.py
```

## Running All Examples

You can run all example scripts at once using the provided `run_examples.sh` script:

```bash
./run_examples.sh
```

To run a specific example, pass the filename as an argument:

```bash
./run_examples.sh boolean_circuit.py
```

This will execute the example(s) and print their output in order.

## Documentation

This project uses [Sphinx](https://www.sphinx-doc.org/) to generate API and user documentation from docstrings and reStructuredText files.

### Prerequisites
- Sphinx and the `sphinx-autodoc-typehints` extension (install with `pip install sphinx sphinx-autodoc-typehints` or see `requirements-dev.txt`)

### Building the Docs

1. Change to the `docs/` directory:
   ```bash
   cd docs
   ```
2. Build the HTML documentation:
   ```bash
   make html
   ```
3. Open the generated documentation:
   - Open `docs/build/html/index.html` in your browser.

All API functions and combinators are documented with literate docstrings. For more details, see the generated HTML docs or the source docstrings.

## Testing

Run all tests with:
```bash
pytest
```

**Test Coverage**: 190+ comprehensive tests covering:
- Core ranking theory functionality
- Theoretical method implementations (κ, τ, conditional ranks)
- Causal reasoning and discovery algorithms
- Belief propagation and message passing
- Constraint-based reasoning with SMT integration
- **C-Representation Framework** with conditional rules and world ranking
- **Hybrid Integration** between constraint networks and c-representations
- Integration with existing combinators
- Edge cases and error handling

## Important Note on Examples and Testing

**All example files in the `examples/regression` directory are ports of the original racket code and are used as regression tests.**

- If you add or modify an example/regression file (e.g., `examples/regression/hidden_markov.py`), you must ensure that its output remains consistent with the expected regression tests.
- Regression tests in `tests/` will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or directory, or disable regression checks for that file.

This ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.

## References

- Rienstra, Tjitze. "Ranked Programming." (Original Racket implementation paper and racket project https://github.com/tjitze/ranked-programming.).
- Spohn, Wolfgang. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press. ISBN-10: 0199697507, ISBN-13: 978-0199697502.
- For algorithmic details, see the background document: `docs/Background/Ranking Theory Algorithmic Realization_.md` (in this repository), which discusses c-representations, conditionalization, and computational implementations of Ranking Theory.

  Marketing blurb:
  Wolfgang Spohn presents the first full account of the dynamic laws of belief, by means of ranking theory. This book is his presentation of ranking theory and its ramifications. He motivates and introduces the basic notion of a ranking function, which recognizes degrees of belief and at the same time accounts for belief simpliciter. He provides a measurement theory for ranking functions, accounts for auto-epistemology in ranking-theoretic terms, and explicates the basic notion of a (deductive or non-deductive) reason. The rich philosophical applications of Spohn's theory include: a new account of lawlikeness, an account of ceteris paribus laws, a new perspective on dispositions, a rich and detailed theory of deterministic causation, an understanding of natural modalities as an objectification of epistemic modalities, an account of the experiential basis of belief--and thus a restructuring of the debate on foundationalism and coherentism (and externalism and contextualism)--and, finally, a revival of fundamental a priori principles of reason fathoming the basics of empiricism and the relation between reason and truth, and concluding in a proof of a weak principle of causality. All this is accompanied by thorough comparative discussions, on a general level as well as within each topic, and in particular with respect to probability theory.

## Deduplication Policy

All core combinators in this library always deduplicate values by their hashable identity, keeping only the first occurrence (with the minimal rank) for each hashable value. Unhashable values (such as lists or dicts) are always yielded, even if repeated. This deduplication is always enabled and is not user-configurable. Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported.

For more details, see the Python reference documentation (`docs/python_reference.md`) and the Sphinx API docs.

## License

See [LICENSE](../LICENSE).

## Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

This library is experimental and intended for research and educational purposes. It implements theoretical concepts from Ranking Theory and may contain bugs, incomplete implementations, or conceptual errors. The authors make no guarantees about the correctness, completeness, or suitability of this software for any particular purpose.

**No Warranties:**
- No warranty of merchantability
- No warranty of fitness for a particular purpose
- No warranty of non-infringement
- No guarantee of accuracy or reliability
- No guarantee of maintenance or support

**Limitations:**
- This is experimental software
- May contain bugs or theoretical errors
- Not intended for production use without thorough testing
- Results should be validated independently
- Use at your own risk

By using this software, you acknowledge that you have read this disclaimer and agree to use the software at your own risk.

# Causal quickstart (Section 7)

Run the end-to-end causal demo (SRM + identification + constraints):

```bash
python examples/causal_srm_identification_demo.py
```

Optional backends (CP-SAT):

```bash
pip install -e .[cp-sat]
ORTOOLS_AVAILABLE=1 pytest -q
```
