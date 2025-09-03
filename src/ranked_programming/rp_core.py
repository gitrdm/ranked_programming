"""
Compatibility and re-export layer for ranked programming core API.

This module exists to maintain backward compatibility for legacy code, tests, and examples
that import from `ranked_programming.rp_core`. All public API symbols are re-exported from
the new modular files (ranking_class, ranking_combinators, ranking_observe, ranking_utils).

New development and user code should prefer importing from `ranked_programming.rp_api` or
the new modules directly. This file may be deprecated in the future.

Exports:
    - Ranking
    - nrm_exc, rlet, rlet_star, either_of, ranked_apply
    - observe, observe_e, observe_all
    - limit, cut, pr_all, pr_first
    - _flatten_ranking_like, _normalize_ranking (for advanced/legacy use)

Note: Use double backticks (``) for any asterisk or special character in docstrings to avoid Sphinx warnings.
"""

from .ranking_class import Ranking, _flatten_ranking_like, _normalize_ranking
from .ranking_combinators import nrm_exc, rlet, rlet_star, either_of, ranked_apply, either_or, bang, construct_ranking, rank_of, failure, rf_equal, rf_to_hash, rf_to_assoc, rf_to_stream
from .ranking_observe import observe, observe_e, observe_all, observe_r, observe_e_x
from .ranking_utils import limit, cut, pr_all, pr_first, pr_first_n, pr_until, pr, is_rank, is_ranking
from .mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty

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
    'observe_r',
    'observe_e_x',
    'limit',
    'cut',
    'pr_all',
    'pr_first',
    'pr_first_n',
    'pr_until',
    'pr',
    '_flatten_ranking_like',
    '_normalize_ranking',
    'either_or',
    'bang',
    'construct_ranking',
    'rank_of',
    'failure',
    'rf_equal',
    'rf_to_hash',
    'rf_to_assoc',
    'rf_to_stream',
    'is_rank',
    'is_ranking',
    'mdl_evidence_penalty',
    'adaptive_evidence_penalty',
    'confidence_evidence_penalty',
]
