import io
import sys
import pytest
from examples import ranked_let

def test_ranked_let_regression():
    captured = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = captured
    try:
        ranked_let.ranked_let_example()
    finally:
        sys.stdout = sys_stdout
    output = captured.getvalue()
    # Only check the dependent uncertainty output for parity with Racket
    expected = """Dependent uncertainty (rlet_star):
Rank  Value
------------
    0 no beer and no peanuts
    1 beer and peanuts
    2 beer and no peanuts
Done
"""
    # Extract only the dependent uncertainty block
    dep_block = []
    in_dep = False
    for line in output.splitlines():
        if line.strip().startswith('Dependent uncertainty'):
            in_dep = True
        if in_dep:
            dep_block.append(line)
        if in_dep and line.strip() == 'Done':
            break
    dep_output = "\n".join(dep_block) + "\n"
    # Strip leading/trailing whitespace for robust comparison
    assert dep_output.strip() == expected.strip(), f"Regression output mismatch:\n{dep_output}\n!=\n{expected}"
