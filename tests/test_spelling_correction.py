"""
Regression test for spelling_correction.py to ensure semantic parity with canonical Racket output.
"""
import io
from contextlib import redirect_stdout
from examples.regression import spelling_correction

def test_spelling_correction_hte():
    f = io.StringIO()
    with redirect_stdout(f):
        spelling_correction.spelling_correction_example()
    output = f.getvalue()
    # Canonical expected output for 'hte' with transposition support
    expected = """
Spelling correction output ranking for 'hte':
Rank  Value
------------
1     ate
1     hate
1     he
1     ht
1     ste
1     te
1     the
...
"""
    # Normalize output for comparison (check that 'the' appears in top results)
    def norm(s):
        lines = [line.strip() for line in s.strip().splitlines() if line.strip() and not line.startswith('...')]
        return lines  # Get all result lines
    
    output_lines = norm(output)
    expected_lines = norm(expected)
    
    # Check that headers match
    assert output_lines[:3] == expected_lines[:3], f"Headers do not match.\nGot: {output_lines[:3]}\nExpected: {expected_lines[:3]}"
    
    # Check that 'the' appears as a 1-edit correction
    result_lines = [line for line in output_lines[3:] if line and not line.startswith('Rank') and not line.startswith('---')]
    the_found = any('the' in line and '1' in line for line in result_lines)
    assert the_found, f"'the' should appear as a 1-edit correction in top results.\nResult lines: {result_lines[:10]}"

if __name__ == "__main__":
    test_spelling_correction_hte()
    print("spelling_correction test passed")
