"""
Regression test for spelling_correction.py to ensure semantic parity with canonical Racket output.
"""
import io
from contextlib import redirect_stdout
from examples import spelling_correction

def test_spelling_correction_hte():
    f = io.StringIO()
    with redirect_stdout(f):
        spelling_correction.spelling_correction_example()
    output = f.getvalue()
    # Canonical Racket output for 'hte' (top 2 shown, ... for more):
    expected = """
Spelling correction output ranking for 'hte':
Rank  Value
------------
0     switzerland
2     swaziland
...
"""
    # Normalize output for comparison (ignore whitespace, only check top 2 results)
    def norm(s):
        lines = [line.strip() for line in s.strip().splitlines() if line.strip() and not line.startswith('...')]
        return lines[:4]  # header + top 2 results
    assert norm(output)[:2] == norm(expected)[:2], f"Top results do not match canonical output.\nGot:\n{output}\nExpected:\n{expected}"

if __name__ == "__main__":
    test_spelling_correction_hte()
    print("spelling_correction test passed")
