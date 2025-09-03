"""
Theory Types for Ranked Programming.

This module provides type aliases and constants for working with Wolfgang Spohn's
Ranking Theory in the ranked_programming library. These types make the theoretical
foundations of the library more explicit and provide better type safety.

**Theoretical Foundation:**

This module formalizes the mathematical types used in Spohn's Ranking Theory:

- **Negative Ranking Function (κ)**: κ: W → ℕ∪{∞} maps worlds to disbelief ranks
- **Two-Sided Ranking Function (τ)**: τ(A) = κ(∼A) - κ(A) measures belief strength
- **Conditional Ranks**: κ(B|A) = κ(A∧B) - κ(A) enables belief revision

**Usage:**

    from ranked_programming.theory_types import DisbeliefRank, BeliefRank, Proposition
    from ranked_programming.theory_types import INFINITE_DISBELIEF, CERTAINTY_RANK

    # Type hints for theory-aware functions
    def disbelief_rank(proposition: Proposition) -> DisbeliefRank:
        # Implementation here
        pass

**Constants:**

- ``INFINITE_DISBELIEF``: Represents maximal disbelief (κ(∅) = ∞)
- ``CERTAINTY_RANK``: Represents no disbelief (κ(W) = 0)

See the main API documentation for examples of how these types are used in practice.
"""

from typing import Callable, Any

# Core theoretical types
DisbeliefRank = int
"""Type alias for disbelief ranks from Spohn's negative ranking function κ.

Disbelief ranks represent degrees of disbelief/surprise, where:
- 0 = no disbelief (certain/normal)
- Higher values = greater disbelief
- ∞ = maximal disbelief (impossible)

This corresponds to κ: W → ℕ∪{∞} in Spohn's theory.
"""

BeliefRank = int
"""Type alias for belief ranks from Spohn's two-sided ranking function τ.

Belief ranks measure belief strength, where:
- Positive values indicate belief
- Negative values indicate disbelief
- Zero indicates suspension of judgment

This corresponds to τ(A) = κ(∼A) - κ(A) in Spohn's theory.
"""

Proposition = Callable[[Any], bool]
"""Type alias for propositions used in ranking functions.

A proposition is a predicate function that evaluates to True or False
for a given world/state. Propositions are used to define the conditions
and consequences in ranking-theoretic operations.

Example:
    healthy = lambda patient: patient.temperature < 98.6
    has_fever = lambda patient: patient.temperature > 100.4
"""

# Theoretical constants
INFINITE_DISBELIEF = float('inf')
"""Constant representing infinite disbelief.

This represents the maximal degree of disbelief, corresponding to κ(∅) = ∞
in Spohn's theory, where ∅ is the empty set of worlds (contradiction).
"""

CERTAINTY_RANK = 0
"""Constant representing certainty (no disbelief).

This represents zero disbelief, corresponding to κ(W) = 0 in Spohn's theory,
where W is the set of all possible worlds (tautology).
"""
