import io
import sys
import pytest
from examples.regression import hidden_markov

def test_hidden_markov_regression():
    captured = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = captured
    try:
        # Test three observation sequences as in the example
        hidden_markov.print_hmm(['no', 'no', 'yes', 'no', 'no'])
        hidden_markov.print_hmm(['yes', 'yes', 'yes', 'no', 'no'])
        hidden_markov.print_hmm(['yes', 'yes', 'yes', 'yes', 'yes', 'yes'])
    finally:
        sys.stdout = sys_stdout
    output = captured.getvalue()
    # Check that the most probable (lowest-rank) state sequence for each block matches expected
    # (We only check the first line after the header for each block)
    blocks = output.split('Done')
    expected_first_lines = [
        # For ['no', 'no', 'yes', 'no', 'no']
        "    4 (('no', 'no', 'yes', 'no', 'no'), ('rainy', 'rainy', 'rainy', 'rainy', 'rainy', 'rainy'))",
        # For ['yes', 'yes', 'yes', 'no', 'no']
        "    2 (('yes', 'yes', 'yes', 'no', 'no'), ('rainy', 'rainy', 'rainy', 'rainy', 'rainy', 'rainy'))",
        # For ['yes', 'yes', 'yes', 'yes', 'yes', 'yes']
        "    0 (('yes', 'yes', 'yes', 'yes', 'yes', 'yes'), ('rainy', 'rainy', 'rainy', 'rainy', 'rainy', 'rainy', 'rainy'))"
    ]
    for i, block in enumerate(blocks[:-1]):
        lines = [l for l in block.splitlines() if l.strip() and not l.startswith('Hidden Markov Model output') and not l.startswith('Rank') and not l.startswith('-')]
        assert lines[0].strip() == expected_first_lines[i].strip(), f"Mismatch in block {i+1}:\n{lines[0]}\n!=\n{expected_first_lines[i]}"
