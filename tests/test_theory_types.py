"""
Tests for theory_types module.

This module tests the type aliases and constants defined in theory_types.py
to ensure they work correctly and provide proper type safety.
"""

import pytest
from typing import get_type_hints

from ranked_programming.theory_types import (
    DisbeliefRank,
    BeliefRank,
    Proposition,
    INFINITE_DISBELIEF,
    CERTAINTY_RANK
)


class TestTheoryTypes:
    """Test the theoretical type aliases."""

    def test_disbelief_rank_type(self):
        """Test that DisbeliefRank is properly defined as int."""
        # Check that it's an int type alias
        assert DisbeliefRank == int

        # Test that it accepts integer values
        rank: DisbeliefRank = 0
        assert rank == 0

        rank = 5
        assert rank == 5

        # Test that it can be used in type hints
        hints = get_type_hints(self.test_disbelief_rank_type)
        # This should not raise an error

    def test_belief_rank_type(self):
        """Test that BeliefRank is properly defined as int."""
        assert BeliefRank == int

        # Test positive belief (belief)
        belief: BeliefRank = 2
        assert belief == 2

        # Test negative belief (disbelief)
        disbelief: BeliefRank = -1
        assert disbelief == -1

        # Test suspension of judgment
        suspension: BeliefRank = 0
        assert suspension == 0

    def test_proposition_type(self):
        """Test that Proposition is properly defined as Callable."""
        # Test with a simple proposition
        is_even: Proposition = lambda x: x % 2 == 0
        assert is_even(2) is True
        assert is_even(3) is False

        # Test with a more complex proposition
        is_positive: Proposition = lambda x: x > 0
        assert is_positive(5) is True
        assert is_positive(-3) is False

        # Test proposition that works with any type
        is_string: Proposition = lambda x: isinstance(x, str)
        assert is_string("hello") is True
        assert is_string(42) is False


class TestTheoryConstants:
    """Test the theoretical constants."""

    def test_infinite_disbelief(self):
        """Test the INFINITE_DISBELIEF constant."""
        assert INFINITE_DISBELIEF == float('inf')
        assert INFINITE_DISBELIEF > 1000000  # Much larger than any practical rank
        assert INFINITE_DISBELIEF == float('inf')  # Consistent

    def test_certainty_rank(self):
        """Test the CERTAINTY_RANK constant."""
        assert CERTAINTY_RANK == 0
        assert isinstance(CERTAINTY_RANK, int)

    def test_constant_types(self):
        """Test that constants have correct types."""
        # INFINITE_DISBELIEF should be a float
        assert isinstance(INFINITE_DISBELIEF, float)

        # CERTAINTY_RANK should be an int (and thus a DisbeliefRank)
        assert isinstance(CERTAINTY_RANK, int)
        assert isinstance(CERTAINTY_RANK, DisbeliefRank)


class TestTheoryTypeIntegration:
    """Test integration between types and constants."""

    def test_disbelief_rank_with_constants(self):
        """Test using constants with DisbeliefRank type."""
        normal_rank: DisbeliefRank = CERTAINTY_RANK
        assert normal_rank == 0

        impossible_rank: DisbeliefRank = INFINITE_DISBELIEF
        assert impossible_rank == float('inf')

    def test_proposition_with_ranks(self):
        """Test using propositions to compute ranks."""
        # Simple proposition
        is_zero: Proposition = lambda x: x == 0

        # Simulate a ranking function that uses the proposition
        def compute_rank(value, proposition: Proposition) -> DisbeliefRank:
            return CERTAINTY_RANK if proposition(value) else 1

        assert compute_rank(0, is_zero) == CERTAINTY_RANK
        assert compute_rank(1, is_zero) == 1

    def test_belief_rank_calculations(self):
        """Test belief rank calculations using the types."""
        def compute_belief_rank(disbelief_A: DisbeliefRank,
                               disbelief_not_A: DisbeliefRank) -> BeliefRank:
            """Compute τ(A) = κ(∼A) - κ(A)"""
            return disbelief_not_A - disbelief_A

        # Test belief case: τ(A) > 0
        belief: BeliefRank = compute_belief_rank(1, 3)  # κ(A)=1, κ(∼A)=3
        assert belief == 2
        assert belief > 0

        # Test disbelief case: τ(A) < 0
        disbelief: BeliefRank = compute_belief_rank(3, 1)  # κ(A)=3, κ(∼A)=1
        assert disbelief == -2
        assert disbelief < 0

        # Test suspension of judgment: τ(A) = 0
        suspension: BeliefRank = compute_belief_rank(2, 2)  # κ(A)=2, κ(∼A)=2
        assert suspension == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_infinite_disbelief_operations(self):
        """Test operations involving infinite disbelief."""
        # Addition with infinite disbelief
        result = INFINITE_DISBELIEF + 5
        assert result == float('inf')

        # Comparison with infinite disbelief
        assert INFINITE_DISBELIEF > 1000
        assert 1000 < INFINITE_DISBELIEF

    def test_proposition_with_none(self):
        """Test propositions that handle None values."""
        is_none: Proposition = lambda x: x is None
        assert is_none(None) is True
        assert is_none(42) is False

    def test_large_rank_values(self):
        """Test with large rank values."""
        large_rank: DisbeliefRank = 1000000
        assert large_rank == 1000000

        # Test that it's still smaller than infinite
        assert large_rank < INFINITE_DISBELIEF
