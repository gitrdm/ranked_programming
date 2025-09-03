"""
Tests for theory methods in Ranking class.

This module tests the new theoretical methods added to the Ranking class:
- disbelief_rank(): Implements κ function from Spohn's theory
- belief_rank(): Implements τ function from Spohn's theory
- conditional_disbelief(): Implements κ(B|A) from Spohn's theory
"""

import pytest
from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.ranking_observe import observe_e


class TestDisbeliefRank:
    """Test the disbelief_rank method (κ function)."""

    def test_simple_disbelief_rank(self):
        """Test disbelief_rank on simple rankings."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # κ(A) should be 0 (A is normal)
        assert ranking.disbelief_rank(lambda x: x == 'A') == 0

        # κ(B) should be 1 (B is exceptional)
        assert ranking.disbelief_rank(lambda x: x == 'B') == 1

    def test_disbelief_rank_with_multiple_values(self):
        """Test disbelief_rank when multiple values satisfy the proposition."""
        ranking = Ranking(lambda: [('A', 0), ('A', 2), ('B', 1)])

        # Should return the minimum rank for values satisfying the proposition
        assert ranking.disbelief_rank(lambda x: x == 'A') == 0

    def test_disbelief_rank_impossible_proposition(self):
        """Test disbelief_rank when no values satisfy the proposition."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # κ(impossible) should be ∞
        assert ranking.disbelief_rank(lambda x: x == 'C') == float('inf')

    def test_disbelief_rank_empty_ranking(self):
        """Test disbelief_rank on empty ranking."""
        ranking = Ranking(lambda: [])

        # Any proposition on empty ranking should be ∞
        assert ranking.disbelief_rank(lambda x: True) == float('inf')


class TestBeliefRank:
    """Test the belief_rank method (τ function)."""

    def test_belief_rank_positive(self):
        """Test belief_rank when τ(A) > 0 (belief in A)."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))
        # κ(A) = 0, κ(∼A) = κ(B) = 1, so τ(A) = 1 - 0 = 1 > 0

        belief = ranking.belief_rank(lambda x: x == 'A')
        assert belief == 1.0
        assert belief > 0  # Indicates belief

    def test_belief_rank_negative(self):
        """Test belief_rank when τ(A) < 0 (disbelief in A)."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))
        # κ(B) = 1, κ(∼B) = κ(A) = 0, so τ(B) = 0 - 1 = -1 < 0

        belief = ranking.belief_rank(lambda x: x == 'B')
        assert belief == -1.0
        assert belief < 0  # Indicates disbelief

    def test_belief_rank_suspension(self):
        """Test belief_rank when τ(A) = 0 (suspension of judgment)."""
        # Create a ranking where κ(A) = κ(∼A)
        ranking = Ranking(lambda: [('A', 1), ('B', 1)])

        belief = ranking.belief_rank(lambda x: x == 'A')
        assert belief == 0.0  # Suspension of judgment

    def test_belief_rank_with_infinity(self):
        """Test belief_rank when one disbelief is infinite."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # Test with impossible proposition
        belief = ranking.belief_rank(lambda x: x == 'C')
        # κ(C) = ∞, κ(∼C) = 0, so τ(C) = 0 - ∞ = -∞
        assert belief == float('-inf')


class TestConditionalDisbelief:
    """Test the conditional_disbelief method (κ(B|A))."""

    def test_conditional_disbelief_simple(self):
        """Test conditional disbelief on simple case."""
        # Create ranking with (A∧B) and (A∧∼B)
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

        # κ(A∧B) = 0, κ(A) = 0, so κ(B|A) = 0 - 0 = 0
        conditional = ranking.conditional_disbelief(
            lambda x: x[0] == 'A',      # A
            lambda x: x[1] == 'B'       # B
        )
        assert conditional == 0.0

    def test_conditional_disbelief_with_penalty(self):
        """Test conditional disbelief when condition has penalty."""
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))
        conditioned = Ranking(lambda: observe_e(2, lambda x: x[0] == 'A', ranking))

        # After conditioning with evidence=2, ranks are renormalized
        # κ(A∧B) = 0, κ(A) = 0, so κ(B|A) = 0 - 0 = 0
        conditional = conditioned.conditional_disbelief(
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B'
        )
        assert conditional == 0.0

    def test_conditional_disbelief_impossible_condition(self):
        """Test conditional disbelief when condition is impossible."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # Condition 'C' is impossible
        conditional = ranking.conditional_disbelief(
            lambda x: x == 'C',  # Impossible condition
            lambda x: x == 'A'   # Any consequent
        )
        assert conditional == float('inf')

    def test_conditional_disbelief_complex(self):
        """Test conditional disbelief with more complex ranking."""
        # Create ranking: A∧B (rank 0), A∧∼B (rank 1), ∼A∧B (rank 2)
        ranking = Ranking(lambda: [
            (('A', 'B'), 0),
            (('A', 'not_B'), 1),
            (('not_A', 'B'), 2)
        ])

        # κ(B|A) = κ(A∧B) - κ(A) = 0 - 0 = 0
        conditional = ranking.conditional_disbelief(
            lambda x: x[0] == 'A',      # A
            lambda x: x[1] == 'B'       # B
        )
        assert conditional == 0.0

        # κ(∼B|A) = κ(A∧∼B) - κ(A) = 1 - 0 = 1
        conditional_not = ranking.conditional_disbelief(
            lambda x: x[0] == 'A',      # A
            lambda x: x[1] != 'B'       # ∼B
        )
        assert conditional_not == 1.0


class TestTheoryIntegration:
    """Test integration between theory methods."""

    def test_tau_from_kappa_relationship(self):
        """Test that τ(A) = κ(∼A) - κ(A)."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # Manual calculation
        kappa_A = ranking.disbelief_rank(lambda x: x == 'A')
        kappa_not_A = ranking.disbelief_rank(lambda x: x != 'A')
        expected_tau = kappa_not_A - kappa_A

        # Method result
        actual_tau = ranking.belief_rank(lambda x: x == 'A')

        assert actual_tau == expected_tau

    def test_conditional_rank_consistency(self):
        """Test that conditional ranks are computed consistently."""
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

        # κ(B|A) should equal κ(∼B|A) - κ(B|A) or similar relationships
        kappa_B_given_A = ranking.conditional_disbelief(
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B'
        )

        kappa_not_B_given_A = ranking.conditional_disbelief(
            lambda x: x[0] == 'A',
            lambda x: x[1] != 'B'
        )

        # These should be consistent with the ranking structure
        assert kappa_B_given_A == 0.0
        assert kappa_not_B_given_A == 1.0

    def test_theory_laws_hold(self):
        """Test that basic theoretical laws hold."""
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        # Law: κ(A) = 0 ∨ κ(∼A) = 0 (at least one should be 0)
        kappa_A = ranking.disbelief_rank(lambda x: x == 'A')
        kappa_not_A = ranking.disbelief_rank(lambda x: x != 'A')

        assert kappa_A == 0 or kappa_not_A == 0

        # τ(A) should be consistent with κ values
        tau_A = ranking.belief_rank(lambda x: x == 'A')
        expected_tau = kappa_not_A - kappa_A
        assert tau_A == expected_tau


class TestEdgeCases:
    """Test edge cases for theory methods."""

    def test_single_value_ranking(self):
        """Test theory methods on ranking with single value."""
        ranking = Ranking(lambda: [('A', 0)])

        assert ranking.disbelief_rank(lambda x: x == 'A') == 0
        assert ranking.disbelief_rank(lambda x: x == 'B') == float('inf')
        assert ranking.belief_rank(lambda x: x == 'A') == float('inf')  # κ(∼A) = ∞, κ(A) = 0, so τ(A) = ∞ - 0 = ∞

    def test_large_rank_values(self):
        """Test with large rank values."""
        ranking = Ranking(lambda: [('A', 1000), ('B', 2000)])

        assert ranking.disbelief_rank(lambda x: x == 'A') == 1000
        assert ranking.disbelief_rank(lambda x: x == 'B') == 2000

        # τ(A) = κ(B) - κ(A) = 2000 - 1000 = 1000
        assert ranking.belief_rank(lambda x: x == 'A') == 1000

    def test_infinite_ranks(self):
        """Test handling of infinite ranks."""
        # Create a ranking where A is impossible but B is possible
        ranking = Ranking(lambda: [('B', 0), ('A', float('inf'))])

        assert ranking.disbelief_rank(lambda x: x == 'A') == float('inf')
        assert ranking.disbelief_rank(lambda x: x == 'B') == 0
        assert ranking.belief_rank(lambda x: x == 'A') == float('-inf')  # κ(∼A) = 0, κ(A) = ∞, so τ(A) = 0 - ∞ = -∞
