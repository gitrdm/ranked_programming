"""
Test for the recursion example, ensuring output matches canonical Racket logic.
"""
import io
from contextlib import redirect_stdout
from examples import recursion

def test_recursion_example():
    f = io.StringIO()
    with redirect_stdout(f):
        recursion.recursion_example()
    output = f.getvalue()
    expected = """
Full recursion ranking (recur(1)):
Rank  Value
------------
    0 1
    1 2
    2 4
    3 8
    4 16
    5 32
    6 64
    7 128
    8 256
    9 512
...

Observed recursion ranking (values > 100):
Rank  Value
------------
    0 128
    1 256
    2 512
    3 1024
    4 2048
    5 4096
    6 8192
    7 16384
...
"""
    def norm(s):
        return '\n'.join(line.strip() for line in s.strip().splitlines())
    assert norm(output) == norm(expected), f"Output did not match expected.\nGot:\n{output}\nExpected:\n{expected}"

if __name__ == "__main__":
    test_recursion_example()
    print("recursion test passed")
