# Ranked Programming (Python Port of Racket Library)

A Python library for ranked programming. Provides combinators and utilities for reasoning about uncertainty, surprise, and ranked choices in computation.

## Important Note on Examples and Testing

**All example files in the `examples/` directory are used as regression tests.**

- If you add or modify an example file (e.g., `examples/hidden_markov.py`), you must ensure that its output remains consistent with the expected regression tests.
- Regression tests in `tests/` will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or directory, or disable regression checks for that file.

This ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.

## Synopsis

This project is a Python port of the code introduced in the paper "Ranked Programming" by Tjitze Rienstra. As mentioned in the paper, "Ranked Programming" is based on the philosophy of "Ranking Theory" as developed by Wolfgang Spohn. It explores a novel approach to modeling uncertainty that is not based on probability.

### Core Idea

While probabilistic programming is a powerful tool, not all uncertainty is probabilistic. Some types of uncertainty are better described by distinguishing between what is "normal" and what is "exceptional". For instance, in fault diagnosis, we might know that a component normally works and only exceptionally fails, without knowing the specific probabilities of failure.

**Ranking Theory** provides an alternative: instead of probabilities, it uses integer "ranks" to measure uncertainty as degrees of surprise:

- **Rank 0:** Not surprising (a normal occurrence)
- **Rank 1:** Surprising (an exceptional occurrence)
- **Rank 2:** Even more surprising
- **Infinity (∞):** Impossible

### Ranked Programming

This library implements a programming model based on these principles, originally proposed as "Ranked Scheme" (an extension of Scheme). The goal is to provide a simple and flexible way to create models that involve uncertainty, but with a computationally simpler, coarser-grained approach than traditional probabilistic methods.

In this model, expressions can have ranked choices, which normally return one value (with a rank of 0) but can exceptionally return another (with a rank of 1 or higher). The final rank of a result can be thought of as the number of exceptions that had to occur for that result to be produced. The system can then perform inference on these models to find the least surprising outcomes given certain observations.

This approach has shown applications in:
- Diagnosing faults in boolean circuits
- Spelling correction algorithms
- Ranking-based Hidden Markov Models
- Ranking networks for diagnostics
- Or any scenario where uncertainty is best described by "normal vs. exceptional" rather than precise probabilities

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gitrdm/ranked-programming.git
   cd ranked-programming/python
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

## Usage

Import the API in your Python code:

```python
from ranked_programming import rp_api as rp

r = rp.construct_ranking((1, 0), (2, 1))
print(r)
```

## Examples

See the `python/examples/` directory for full scripts that duplicate the Racket examples:

- `boolean_circuit.py` — Boolean circuit with uncertainty
- `ranked_let.py` — Independent and dependent uncertainty with `rlet` and `rlet_star`
- `ranked_procedure_call.py` — Uncertain function application
- `spelling_correction.py` — Spelling correction with ranked choices
- `hidden_markov.py` — Simple hidden Markov model
- `localisation.py` — Robot localisation
- `recursion.py` — Recursion with ranked choices
- `ranking_network.py` — Simple ranking network
- `google_10000_english_no_swears.py` — Large vocabulary demo (mocked)

Run an example:
```bash
python examples/boolean_circuit.py
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

- Spohn, Wolfgang. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press. ISBN-10: 0199697507, ISBN-13: 978-0199697502.

  Marketing blurb:
  Wolfgang Spohn presents the first full account of the dynamic laws of belief, by means of ranking theory. This book is his presentation of ranking theory and its ramifications. He motivates and introduces the basic notion of a ranking function, which recognises degrees of belief and at the same time accounts for belief simpliciter. He provides a measurement theory for ranking functions, accounts for auto-epistemology in ranking-theoretic terms, and explicates the basic notion of a (deductive or non-deductive) reason. The rich philosophical applications of Spohn's theory include: a new account of lawlikeness, an account of ceteris paribus laws, a new perspective on dispositions, a rich and detailed theory of deterministic causation, an understanding of natural modalities as an objectification of epistemic modalities, an account of the experiential basis of belief--and thus a restructuring of the debate on foundationalism and coherentism (and externalism and contextualism)--and, finally, a revival of fundamental a priori principles of reason fathoming the basics of empiricism and the relation between reason and truth, and concluding in a proof of a weak principle of causality. All this is accompanied by thorough comparative discussions, on a general level as well as within each topic, and in particular with respect to probability theory.

## Deduplication Policy

All core combinators in this library always deduplicate values by their hashable identity, keeping only the first occurrence (with the minimal rank) for each hashable value. Unhashable values (such as lists or dicts) are always yielded, even if repeated. This deduplication is always enabled and is not user-configurable. Deduplication is performed lazily as values are generated, so infinite/lazy structures are supported.

For more details, see the Python reference documentation (`docs/python_reference.md`) and the Sphinx API docs.
