"""
Public API for ranked programming (Python, lazy-only).

This module re-exports the official, user-facing API for ranked programming, aggregating
all public combinators, classes, and utilities from the core modules. Users should import
from this module for a stable, documented interface:

    from ranked_programming import rp_api as rp

This file is the recommended entry point for all new code and documentation.

Exports:
    - Ranking
    - nrm_exc, rlet, rlet_star, either_of, ranked_apply
    - observe, observe_e, observe_all
    - limit, cut, pr_all, pr_first
"""
from .ranking_class import Ranking
from .ranking_combinators import nrm_exc, rlet, rlet_star, either_of, ranked_apply
from .ranking_observe import observe, observe_e, observe_all
from .ranking_utils import limit, cut, pr_all, pr_first
