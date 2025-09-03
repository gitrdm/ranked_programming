import io
import sys
import pytest
from examples.regression import ranked_procedure_call

def test_ranked_procedure_call_regression():
    captured = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = captured
    try:
        ranked_procedure_call.ranked_procedure_call_example()
    finally:
        sys.stdout = sys_stdout
    output = captured.getvalue()
    # Split into blocks for each scenario
    blocks = [b.strip() for b in output.strip().split('Done') if b.strip()]
    # Expected outputs (order and values as printed)
    expected_blocks = [
        "Rank  Value\n------------\n0     15",
        "Rank  Value\n------------\n0     15\n1     25",
        # Accept either order for rank 1 values, and allow extra rank 2 value
        None
    ]
    # Check first two blocks strictly
    for i in range(2):
        assert blocks[i] == expected_blocks[i], f"Mismatch in block {i+1}:\n{blocks[i]}\n!=\n{expected_blocks[i]}"
    # Third block: check required values and ranks, allow extra values
    third_lines = set(line.strip() for line in blocks[2].splitlines() if line.strip())
    required = set([
        "Rank  Value",
        "------------",
        "0     15",
        "1     25",
        "1     5"
    ])
    assert required.issubset(third_lines), f"Missing required lines in block 3:\n{blocks[2]}"
