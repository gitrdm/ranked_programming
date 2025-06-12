"""
API layer for ranked programming (Python, lazy-only).
Literate documentation and type hints included.

This module re-exports the lazy combinators and utilities from rp_core,
providing a clean, user-facing API for ranked programming.
"""
from .rp_core import (
    Ranking,
    nrm_exc,
    rlet,
    rlet_star,
    either_of,
    ranked_apply,
    observe,
    observe_e,
    observe_all,
    limit,
    cut,
    pr_all,
    pr_first,
)
