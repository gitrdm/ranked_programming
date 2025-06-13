"""
Compatibility and re-export layer for ranked programming core API.

This module exists to maintain backward compatibility for legacy code, tests, and examples
that import from `ranked_programming.rp_core`. All public API symbols are re-exported from
the new modular files (ranking_class, ranking_combinators, ranking_observe, ranking_utils).

New development and user code should prefer importing from `ranked_programming.rp_api` or
the new modules directly. This file may be deprecated in the future.
"""

from .ranking_class import Ranking, _flatten_ranking_like, _normalize_ranking
from .ranking_combinators import nrm_exc, rlet, rlet_star, either_of, ranked_apply
from .ranking_observe import observe, observe_e, observe_all
from .ranking_utils import limit, cut, pr_all, pr_first

__all__ = [
    'Ranking',
    'nrm_exc',
    'rlet',
    'rlet_star',
    'either_of',
    'ranked_apply',
    'observe',
    'observe_e',
    'observe_all',
    'limit',
    'cut',
    'pr_all',
    'pr_first',
    '_flatten_ranking_like',
    '_normalize_ranking',
]
