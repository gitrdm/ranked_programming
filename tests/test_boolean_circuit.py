"""
Regression test for boolean_circuit.py to ensure semantic parity with canonical Racket output.
"""
import io
from contextlib import redirect_stdout
from examples import boolean_circuit

def test_boolean_circuit():
    f = io.StringIO()
    with redirect_stdout(f):
        boolean_circuit.boolean_circuit()
    output = f.getvalue()
    # Canonical Racket output for the boolean circuit:
    expected = """
Rank  Value
------------
0     (#t #t #f)
1     (#t #f #f)
1     (#f #t #f)
2     (#f #f #f)
Done
"""
    # Parse output to extract only the (a, b, c) tuples and their ranks where output is False
    import re
    lines = output.splitlines()
    results = []
    for line in lines:
        m = re.match(r"\s*(\d+) \((True|False), (True|False), (True|False), (True|False)\)", line)
        if m:
            rank = int(m.group(1))
            a, b, c, out = (m.group(2) == 'True', m.group(3) == 'True', m.group(4) == 'True', m.group(5) == 'True')
            if not out:  # Only include outputs where the circuit output is False
                results.append((rank, a, b, c))
    # Normalize ranks so the lowest rank is 0
    if results:
        min_rank = min(r for r, _, _, _ in results)
        results = [(r - min_rank, a, b, c) for r, a, b, c in results]
    # Canonical expected results (from Racket)
    expected_results = [
        (0, True, True, False),
        (1, True, False, False),
        (1, False, True, False),
        (2, False, False, False),
    ]
    assert results == expected_results, f"Boolean circuit output does not match canonical Racket output.\nGot: {results}\nExpected: {expected_results}"

if __name__ == "__main__":
    test_boolean_circuit()
    print("boolean_circuit test passed")
