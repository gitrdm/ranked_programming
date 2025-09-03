# Ranked Programming

A Python library for ranked programming based on Wolfgang Spohn's Ranking Theory. Provides combinators and utilities for reasoning about uncertainty, surprise, and ranked choices in computation using a computationally simpler alternative to probabilistic methods.

## Important Note on Examples and Testing

**All example files in the `examples/regression` directory are used as regression tests.**

- If you add or modify an example file (e.g., `examples/regression/hidden_markov.py`), you must ensure that its output remains consistent with the expected regression tests.
- Regression tests in `tests/` will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or directory, or disable regression checks for that file.

This ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.

## Synopsis

This library implements **Ranked Programming** based on Wolfgang Spohn's **Ranking Theory** - a philosophical framework for modeling uncertainty that distinguishes between "normal" and "exceptional" occurrences rather than using probabilities.

### Core Idea

While probabilistic programming is powerful, not all uncertainty is probabilistic. Some types of uncertainty are better described by distinguishing between what is "normal" and what is "exceptional". For instance, in fault diagnosis, we might know that a component normally works and only exceptionally fails, without knowing the specific probabilities of failure.

**Ranking Theory** provides an alternative: instead of probabilities, it uses integer "ranks" to measure uncertainty as degrees of surprise:

- **Rank 0:** Not surprising (a normal occurrence)
- **Rank 1:** Surprising (an exceptional occurrence)
- **Rank 2:** Even more surprising
- **Infinity (∞):** Impossible

### Ranked Programming

This library implements a programming model based on these principles. Expressions can have ranked choices, which normally return one value (with a rank of 0) but can exceptionally return another (with a rank of 1 or higher). The final rank of a result represents the number of exceptions that had to occur for that result to be produced.

**Key Features:**
- **Theoretical Foundation**: Explicit implementation of Spohn's Ranking Theory with κ (disbelief), τ (belief), and conditional ranks
- **Lazy Evaluation**: Efficient handling of infinite or large search spaces
- **Type Safety**: Full type annotations and modern Python support
- **Comprehensive Testing**: 110+ tests ensuring reliability
- **Backward Compatibility**: All existing code continues to work unchanged

**Applications:**
- Fault diagnosis in boolean circuits
- Spelling correction algorithms
- Ranking-based Hidden Markov Models
- Ranking networks for diagnostics
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

## Usage

Import the API in your Python code:

```python
from ranked_programming import rp_api as rp

r = rp.construct_ranking((1, 0), (2, 1))
print(r)
```

## Examples

See the `examples/` directory for full scripts demonstrating various applications:

- `boolean_circuit.py` — Boolean circuit with uncertainty
- `ranked_let.py` — Independent and dependent uncertainty with `rlet` and `rlet_star`
- `ranked_procedure_call.py` — Uncertain function application
- `spelling_correction.py` — Spelling correction with ranked choices
- `hidden_markov.py` — Simple hidden Markov model
- `localisation.py` — Robot localisation
- `recursion.py` — Recursion with ranked choices
- `ranking_network.py` — Simple ranking network
- `google_10000_english_no_swears.py` — Large vocabulary demo (uses small subset by default; --full flag loads real data)

Run an example:
```bash
python examples/boolean_circuit.py
```

## Recent Developments

**September 2025: Phase 1 Theoretical Enhancements Complete ✅**

This library has undergone significant theoretical enhancements to make Wolfgang Spohn's Ranking Theory more explicit:

### ✅ Completed Enhancements

- **Theory Types Module**: Added `src/ranked_programming/theory_types.py` with type aliases and constants
- **Ranking Class Extensions**: Added three new methods to the `Ranking` class:
  - `disbelief_rank(proposition)` - κ(A): degree of disbelief
  - `belief_rank(proposition)` - τ(A): belief function  
  - `conditional_disbelief(condition, consequent)` - κ(B|A): conditional disbelief
- **Comprehensive Documentation**: Updated all core docstrings with theoretical references
- **Extensive Testing**: Added 30+ new tests (110 total) with 100% pass rate
- **Backward Compatibility**: Zero breaking changes - all existing code works unchanged

### 🔄 Next Phase: Educational Examples & Documentation

Phase 2 will focus on:
- Theory demonstration examples
- Theory-to-implementation mapping documentation
- Enhanced educational tutorials
- Complete theory-focused documentation

## References

- Rienstra, Tjitze. "Ranked Programming." (Original Racket implementation paper).
- Spohn, Wolfgang. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press. ISBN-10: 0199697507, ISBN-13: 978-0199697502.
- For algorithmic details, see the background document: `docs/Background/Ranking Theory Algorithmic Realization_.md` (in this repository), which discusses c-representations, conditionalization, and computational implementations of Ranking Theory.

  Marketing blurb:
  Wolfgang Spohn presents the first full account of the dynamic laws of belief, by means of ranking theory. This book is his presentation of ranking theory and its ramifications. He motivates and introduces the basic notion of a ranking function, which recognises degrees of belief and at the same time accounts for belief simpliciter. He provides a measurement theory for ranking functions, accounts for auto-epistemology in ranking-theoretic terms, and explicates the basic notion of a (deductive or non-deductive) reason. The rich philosophical applications of Spohn's theory include: a new account of lawlikeness, an account of ceteris paribus laws, a new perspective on dispositions, a rich and detailed theory of deterministic causation, an understanding of natural modalities as an objectification of epistemic modalities, an account of the experiential basis of belief--and thus a restructuring of the debate on foundationalism and coherentism (and externalism and contextualism)--and, finally, a revival of fundamental a priori principles of reason fathoming the basics of empiricism and the relation between reason and truth, and concluding in a proof of a weak principle of causality. All this is accompanied by thorough comparative discussions, on a general level as well as within each topic, and in particular with respect to probability theory.

## Deduplication Policy
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

## License

See [LICENSE](../LICENSE).

## Original Racket Project

This Python library is a port of the original Racket ranked programming library by Tjitze Rienstra:

- [Ranked Programming (Racket, original)](https://github.com/tjitze/ranked-programming.git)

## References

- Rienstra, Tjitze. "Ranked Programming." (Original Racket implementation paper).
- Spohn, Wolfgang. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press. ISBN-10: 0199697507, ISBN-13: 978-0199697502.
- For algorithmic details, see the background document: `docs/Background/Ranking Theory Algorithmic Realization_.md` (in this repository), which discusses c-representations, conditionalization, and computational implementations of Ranking Theory.

  Marketing blurb:
  Wolfgang Spohn presents the first full account of the dynamic laws of belief, by means of ranking theory. This book is his presentation of ranking theory and its ramifications. He motivates and introduces the basic notion of a ranking function, which recognises degrees of belief and at the same time accounts for belief simpliciter. He provides a measurement theory for ranking functions, accounts for auto-epistemology in ranking-theoretic terms, and explicates the basic notion of a (deductive or non-deductive) reason. The rich philosophical applications of Spohn's theory include: a new account of lawlikeness, an account of ceteris paribus laws, a new perspective on dispositions, a rich and detailed theory of deterministic causation, an understanding of natural modalities as an objectification of epistemic modalities, an account of the experiential basis of belief--and thus a restructuring of the debate on foundationalism and coherentism (and externalism and contextualism)--and, finally, a revival of fundamental a priori principles of reason fathoming the basics of empiricism and the relation between reason and truth, and concluding in a proof of a weak principle of causality. All this is accompanied by thorough comparative discussions, on a general level as well as within each topic, and in particular with respect to probability theory.

## Deduplication Policy

All core combinators in this library always deduplicate values by their hashable identity, keeping only the first occurrence (with the minimal rank) for each hashable value. Unhashable values (such as lists or dicts) are always yielded, even if repeated. This deduplication is always enabled and is not user-configurable. Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported.

For more details, see the Python reference documentation (`docs/python_reference.md`) and the Sphinx API docs.
