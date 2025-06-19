"""
Ranked Programming Python package.

This package provides a lazy, generator-based framework for ranked programming, including
combinators, observation/normalization utilities, and pretty-printing tools. The main user-facing
API is available via `rp_api`.

Typical usage:
    from ranked_programming import rp_api as rp
    r = rp.nrm_exc(1, 2, 1)
    ...
"""
from .rp_core import *

__version__ = "1.1.0"
