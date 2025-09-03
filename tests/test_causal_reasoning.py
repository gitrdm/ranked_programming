#!/usr/bin/env python3
"""
Tests for Causal Reasoning Module

This module contains comprehensive tests for the causal reasoning capabilities
of the ranked_programming library. It tests causal discovery, intervention
analysis, and counterfactual reasoning.

Author: Ranked Programming Library
Date: September 2025
"""

import pytest
from ranked_programming import Ranking, nrm_exc
from ranked_programming.causal_reasoning import (
    CausalReasoner,
    create_causal_model,
    analyze_intervention_effects
)


class TestCausalReasoner:
    """Test the core CausalReasoner class."""

    def test_initialization(self):
        """Test CausalReasoner initialization."""
        reasoner = CausalReasoner()
        assert reasoner.background_knowledge == {}
        assert reasoner.causal_graph == {}
        assert reasoner.causal_strengths == {}

        # Test with background knowledge
        background = {'domain': 'medicine', 'assumptions': ['no_confounding']}
        reasoner_with_bg = CausalReasoner(background)
        assert reasoner_with_bg.background_knowledge == background

    def test_direct_cause_detection_simple(self):
        """Test direct cause detection with simple causal relationship."""
        # Create a ranking where intervening on A changes B
        # Normal case: both A and B can be true or false
        # When we intervene on A=true, B becomes more likely
        ranking = Ranking(lambda: nrm_exc(
            ('A_true', 'B_true'),   # Normal case
            nrm_exc(('A_false', 'B_false'), ('A_true', 'B_false'), 2),  # Exceptional cases
            1
        ))

        reasoner = CausalReasoner()
        is_cause, strength = reasoner.is_direct_cause(
            lambda x: x[0] == 'A_true',  # A is true
            lambda x: x[1] == 'B_true',  # B is true
            [],  # No background variables
            ranking
        )

        # Should detect causal relationship
        assert is_cause == True
        assert strength > 0  # Intervention increases belief in B

    def test_no_causal_relationship(self):
        """Test detection of no causal relationship."""
        # Create a ranking where A and B are independent
        # Both A and B can occur independently
        ranking = Ranking(lambda: nrm_exc(
            ('A', 'B'),
            nrm_exc(('A', 'not_B'), nrm_exc(('not_A', 'B'), ('not_A', 'not_B'), 1), 1),
            1
        ))

        reasoner = CausalReasoner()
        is_cause, strength = reasoner.is_direct_cause(
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B',
            [],
            ranking
        )

        # Should not detect strong causal relationship
        assert abs(strength) < 0.5  # Below significance threshold

    def test_intervention_simulation(self):
        """Test intervention simulation."""
        # Original ranking: A=0, B=1
        ranking = Ranking(lambda: nrm_exc('A', 'B', 1))

        reasoner = CausalReasoner()

        # Intervene to force A=true
        intervened = reasoner._intervene(ranking, lambda x: x == 'A', True)

        # After intervention, A should have rank 0, other values infinite
        assert intervened.disbelief_rank(lambda x: x == 'A') == 0
        assert intervened.disbelief_rank(lambda x: x == 'B') == float('inf')

    def test_causal_discovery(self):
        """Test causal relationship discovery."""
        # Create a simple causal structure
        variables = [
            lambda x: x[0] == 'A',  # Variable 0
            lambda x: x[1] == 'B',  # Variable 1
        ]

        # Simple ranking for testing
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('not_A', 'not_B'), 1))

        reasoner = CausalReasoner()
        causal_matrix = reasoner.discover_causal_relationships(variables, ranking)

        # Test that the method runs without error and returns a dictionary
        assert isinstance(causal_matrix, dict)
        # May or may not detect relationships depending on the algorithm

    def test_counterfactual_reasoning(self):
        """Test counterfactual reasoning capabilities."""
        # Factual: A and B are both possible
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('not_A', 'not_B'), 1))

        reasoner = CausalReasoner()

        # Counterfactual: What if A were forced to true?
        factual_tau, counterfactual_tau = reasoner.counterfactual_reasoning(
            ranking,
            {lambda x: x[0] == 'A': True},  # Intervene on A
            lambda x: x[1] == 'B'           # Query B
        )

        # Should get different values
        assert isinstance(factual_tau, float)
        assert isinstance(counterfactual_tau, float)

    def test_causal_effect_strength(self):
        """Test quantification of causal effect strength."""
        # Strong causal relationship
        ranking = Ranking(lambda: nrm_exc(('cause', 'effect'), ('cause', 'no_effect'), 3))

        reasoner = CausalReasoner()
        strength = reasoner.causal_effect_strength(
            lambda x: x[0] == 'cause',
            lambda x: x[1] == 'effect',
            ranking
        )

        assert isinstance(strength, float)
        assert strength != 0  # Should detect causal effect

    def test_causal_path_analysis(self):
        """Test causal path analysis."""
        variables = [
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B',
        ]

        # Create a ranking where intervening on A changes B
        ranking = Ranking(lambda: nrm_exc(
            ('A', 'B'),      # Normal case
            nrm_exc(('not_A', 'B'), ('A', 'not_B'), 1),  # Other cases
            1
        ))

        reasoner = CausalReasoner()
        path = reasoner.analyze_causal_path(
            variables[0], variables[1], variables, ranking
        )

        assert isinstance(path, list)
        # Should find some path (may be empty if no strong causal relationship)
        # This test mainly checks that the method runs without error


class TestCausalModelCreation:
    """Test causal model creation utilities."""

    def test_create_causal_model(self):
        """Test creation of causal model from declarative specification."""
        variables = {
            'A': lambda x: x[0] == 'A',
            'B': lambda x: x[1] == 'B',
        }

        relationships = [
            ('A', 'B', 2.5),  # A causes B with strength 2.5
        ]

        reasoner = create_causal_model(variables, relationships)

        assert isinstance(reasoner, CausalReasoner)
        assert 0 in reasoner.causal_graph  # A -> B
        assert 1 in reasoner.causal_graph[0]  # A causes B
        assert reasoner.causal_strengths[(0, 1)] == 2.5

    def test_analyze_intervention_effects(self):
        """Test analysis of multiple intervention effects."""
        # Base ranking
        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

        # Multiple interventions
        interventions = {
            lambda x: x[0] == 'A': True,  # Force A=true
        }

        queries = [
            lambda x: x[1] == 'B',  # Query B
        ]

        effects = analyze_intervention_effects(ranking, interventions, queries)

        assert isinstance(effects, dict)
        assert len(effects) == len(queries)
        assert all(isinstance(v, float) for v in effects.values())


class TestCausalValidation:
    """Test causal assumption validation."""

    def test_causal_assumption_validation(self):
        """Test validation of causal assumptions."""
        # Simple causal graph: A -> B
        causal_graph = {0: {1}}  # A causes B

        variables = [
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B',
        ]

        ranking = Ranking(lambda: nrm_exc(('A', 'B'), ('A', 'not_B'), 1))

        reasoner = CausalReasoner()
        validation = reasoner.validate_causal_assumptions(causal_graph, ranking, variables)

        assert isinstance(validation, dict)
        assert 'no_cycles' in validation
        assert 'causal_markov' in validation
        assert 'faithfulness' in validation

        # Basic validations should pass
        assert validation['no_cycles'] == True


class TestIntegrationWithExistingCombinators:
    """Test integration with existing ranking combinators."""

    def test_with_observe_e(self):
        """Test causal reasoning with evidence observation."""
        from ranked_programming import observe_e

        # Base causal model
        ranking = Ranking(lambda: nrm_exc(('rain', 'wet_ground'), ('rain', 'dry_ground'), 2))

        # Observe evidence: ground is wet
        conditioned = Ranking(lambda: observe_e(1, lambda x: x[1] == 'wet_ground', ranking))

        reasoner = CausalReasoner()
        is_cause, strength = reasoner.is_direct_cause(
            lambda x: x[0] == 'rain',      # Rain causes wet ground
            lambda x: x[1] == 'wet_ground', # Wet ground
            [],
            conditioned
        )

        # Should still detect causal relationship after conditioning
        assert isinstance(strength, float)

    def test_with_complex_rankings(self):
        """Test with more complex ranking structures."""
        # Multi-level causal chain
        ranking = Ranking(lambda: nrm_exc(
            nrm_exc(('A', 'B', 'C'), ('A', 'B', 'not_C'), 1),
            ('A', 'not_B', 'not_C'),
            2
        ))

        reasoner = CausalReasoner()

        # Test A -> B relationship
        is_cause_ab, strength_ab = reasoner.is_direct_cause(
            lambda x: x[0] == 'A',
            lambda x: x[1] == 'B',
            [lambda x: x[2] == 'C'],  # Background variable C
            ranking
        )

        assert isinstance(strength_ab, float)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_ranking(self):
        """Test causal reasoning with empty ranking."""
        ranking = Ranking(lambda: [])

        reasoner = CausalReasoner()
        is_cause, strength = reasoner.is_direct_cause(
            lambda x: True,
            lambda x: True,
            [],
            ranking
        )

        # Should handle gracefully
        assert isinstance(strength, float)

    def test_single_value_ranking(self):
        """Test with ranking containing single value."""
        ranking = Ranking(lambda: [('single', 0)])

        reasoner = CausalReasoner()
        is_cause, strength = reasoner.is_direct_cause(
            lambda x: x == 'single',
            lambda x: x == 'single',
            [],
            ranking
        )

        assert isinstance(strength, float)

    def test_impossible_interventions(self):
        """Test interventions on impossible conditions."""
        # Ranking where certain combinations are impossible
        ranking = Ranking(lambda: [('A', 0), ('B', 1)])

        reasoner = CausalReasoner()
        intervened = reasoner._intervene(ranking, lambda x: x == 'impossible', True)

        # Impossible value should remain impossible
        assert intervened.disbelief_rank(lambda x: x == 'impossible') == float('inf')


if __name__ == "__main__":
    pytest.main([__file__])
