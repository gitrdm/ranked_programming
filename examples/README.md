# Examples and Demos

This directory contains example files and demonstrations for the ranked programming library.

## Directory Structure

- `regression/` - **Regression test files** (see `regression/README.md`)
- Main directory - **Demo and educational examples**

## Regression Tests vs. Demos

### Regression Tests (`regression/` directory)
- **Purpose**: Ensure library stability and prevent regressions
- **Testing**: Automatically tested by the test suite
- **Stability**: Output must remain consistent
- **Files**: `hidden_markov.py`, `ranked_let.py`, `ranked_procedure_call.py`

### Demo Examples (main directory)
- **Purpose**: Educational examples, experiments, and demonstrations
- **Testing**: Not automatically tested (may be used in some unit tests)
- **Flexibility**: Can be modified, updated, or experimental
- **Files**: All other `.py` files in this directory

## Adding New Examples

- **For demos/experiments**: Add to the main examples directory
- **For regression tests**: Add to `regression/` directory and create corresponding test
- **For educational content**: Use the main directory with clear documentation

## File Categories

### Core Demos
- `*_mdl.py` - Examples with MDL (Minimum Description Length) penalties
- `*_penalty_demo.py` - Demonstrations of different penalty algorithms
- `example.py` - Basic usage examples

### Domain-Specific Examples
- `boolean_circuit*.py` - Boolean circuit modeling
- `hidden_markov*.py` - Hidden Markov Model applications
- `localisation*.py` - Localization problems
- `ranking_network*.py` - Network ranking examples
- `recursion*.py` - Recursive ranking examples
- `spelling_correction*.py` - Spelling correction applications

### Utility and Analysis
- `compare_hmm_outputs.py` - HMM output comparison tools
- `mdl_penalty_estimation.py` - Penalty estimation utilities
- `google_10000_english_no_swears.py` - Text processing examples

This organization keeps regression tests stable while allowing the examples directory to evolve with new demonstrations and educational content.
