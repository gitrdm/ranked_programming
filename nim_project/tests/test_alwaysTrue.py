# test_alwaysTrue.py -- Python smoke test for alwaysTrue Nim export
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../build")))
import ranked_core

def test_alwaysTrue():
    assert ranked_core.alwaysTrue() == True
    print("alwaysTrue SWIG binding works!")

if __name__ == "__main__":
    test_alwaysTrue()
