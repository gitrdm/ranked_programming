# test_addInts.py -- Python test for SWIG-wrapped Nim C API
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../build")))
import ranked_core

def test_addInts():
    assert ranked_core.addInts(2, 3) == 5
    assert ranked_core.addInts(-1, 1) == 0
    print("addInts SWIG binding works!")

if __name__ == "__main__":
    test_addInts()
