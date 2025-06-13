"""
Test for the ranking_network example, ensuring output matches canonical Racket logic.
"""
import io
import sys
from contextlib import redirect_stdout
from examples import ranking_network

def test_ranking_network_full():
    f = io.StringIO()
    with redirect_stdout(f):
        ranking_network.main()
    output = f.getvalue()
    # Canonical output for the full network (tuples of length 4)
    expected = """
Rank  Value
------------
0     (#f #t #t #f)
8     (#f #f #t #f)
10    (#f #t #f #f)
11    (#f #t #t #t)
15    (#t #f #t #f)
18    (#f #f #f #f)
19    (#t #t #t #t)
21    (#f #t #f #t)
22    (#t #t #t #f)
25    (#t #f #f #f)
28    (#t #f #t #t)
29    (#t #t #f #t)
32    (#t #t #f #f)
35    (#f #f #t #t)
38    (#t #f #f #t)
45    (#f #f #f #t)
Done

Rank  Value
------------
0     #f
11    #t
Done
"""
    # Normalize whitespace for comparison
    def norm(s):
        return '\n'.join(line.strip() for line in s.strip().splitlines())
    assert norm(output) == norm(expected), f"Output did not match expected.\nGot:\n{output}\nExpected:\n{expected}"

if __name__ == "__main__":
    test_ranking_network_full()
    print("ranking_network test passed")
