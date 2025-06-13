# Examples and Regression Testing

All example files in this directory (e.g., `hidden_markov.py`, `ranked_let.py`, etc.) are used as regression tests for the ranked programming library.

- If you add or modify an example file, ensure its output remains consistent with the expected regression tests in `../tests/`.
- Regression tests will run these examples and check their output. If you change the output format or logic, update the corresponding regression test.
- To add your own examples without affecting tests, use a different filename or subdirectory, or coordinate with the test suite maintainers.

This policy ensures that the core examples remain stable and that changes to the library do not unintentionally break expected behavior.
