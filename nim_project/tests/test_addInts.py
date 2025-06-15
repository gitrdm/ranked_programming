# test_addInts.py -- Disabled: was a hello-world test for initial FFI pipeline
# This test is now disabled because addInts is not part of the real API.
# To re-enable, add addInts to the C API and SWIG interface.
import pytest
pytest.skip("Disabled: addInts was a hello-world test, not part of the real API.", allow_module_level=True)

# def test_addInts():
#     assert ranked_core.addInts(2, 3) == 5
#     assert ranked_core.addInts(-1, 1) == 0
#     print("addInts SWIG binding works!")

# if __name__ == "__main__":
#     test_addInts()
