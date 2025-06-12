# Ranked Programming (Python Port)

A Python library for ranked programming, ported from the canonical Racket library. Provides combinators, macros, and utilities for reasoning about uncertainty, surprise, and ranked choices in computation.

## Synopsis

This project is a Python implementation of the concepts introduced in the paper "Ranked Programming" by Tjitze Rienstra. It explores a novel approach to modeling uncertainty that is not based on probability.

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
   conda activate ranked-programming-py
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

- All API functions and combinators are documented with literate docstrings.
- See `python/docs/index.md` for a full API reference and usage guide.

## Testing

Run all tests with:
```bash
pytest
```

## License

See [LICENSE](../LICENSE).
