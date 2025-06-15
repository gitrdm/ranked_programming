# test_alwaysTrue.py -- Disabled: was a hello-world test for initial FFI pipeline
# This test is now disabled because alwaysTrue is not part of the real API.
# To re-enable, add alwaysTrue to the C API and SWIG interface.
import pytest
pytest.skip("Disabled: alwaysTrue was a hello-world test, not part of the real API.", allow_module_level=True)

# def test_alwaysTrue():
#     assert ranked_core.alwaysTrue() == True
#     print("alwaysTrue SWIG binding works!")

# if __name__ == "__main__":
#     test_alwaysTrue()
