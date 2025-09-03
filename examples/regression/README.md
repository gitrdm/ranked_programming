# Regression Test Examples

The files in this directory are the **actual regression test examples** used by the ranked programming library's test suite.

## Regression Test Files

- `hidden_markov.py` - Hidden Markov Model example (tested by `test_hidden_markov_regression.py`)
- `ranked_let.py` - Ranked let expressions example (tested by `test_ranked_let_regression.py`)
- `ranked_procedure_call.py` - Procedure call with uncertainty example (tested by `test_ranked_procedure_call_regression.py`)
- `spelling_correction.py` - Spelling correction example (tested by `test_spelling_correction.py`)

## Important Notes

- **Do not modify these files** without updating the corresponding regression tests in `../tests/`
- Changes to output format or logic require corresponding test updates
- These files ensure the core library functionality remains stable
- If you need to experiment or create new examples, use the main `../examples/` directory

## Regression Testing

The test suite runs these examples and compares their output against expected results. Any changes to these files should maintain backward compatibility or update the tests accordingly.

This separation ensures that regression tests remain stable while allowing the main examples directory to contain experimental demos and educational materials.
