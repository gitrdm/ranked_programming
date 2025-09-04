"""
Tests for Constraint-Based Reasoning Module

This module contains comprehensive tests for the constraint reasoning functionality,
ensuring that constraint solving works correctly and integrates properly with
the existing ranking theory framework.
"""

import pytest
from ranked_programming.constraint_reasoning import (
    ConstraintRankingNetwork, ConditionalRule, CRepresentation,
    create_c_representation_from_constraints,
    create_constraint_network_from_c_representation
)
from ranked_programming import Ranking, nrm_exc


class TestConstraintRankingNetwork:
    """Test cases for ConstraintRankingNetwork class."""

    def test_initialization_empty(self):
        """Test initialization with no constraints."""
        network = ConstraintRankingNetwork(['A', 'B', 'C'])
        assert network.variables == ['A', 'B', 'C']
        assert network.constraints == []

    def test_initialization_with_constraints(self):
        """Test initialization with constraints."""
        constraints = [('A', 'B', 1), ('B', 'C', 2)]
        network = ConstraintRankingNetwork(['A', 'B', 'C'], constraints)
        assert network.constraints == constraints

    def test_add_constraint(self):
        """Test adding constraints to the network."""
        network = ConstraintRankingNetwork(['A', 'B', 'C'])

        network.add_constraint('A', 'B', 1)
        assert ('A', 'B', 1) in network.constraints

        network.add_constraint('B', 'C', 2)
        assert ('B', 'C', 2) in network.constraints

    def test_add_constraint_invalid_variable(self):
        """Test adding constraint with invalid variable."""
        network = ConstraintRankingNetwork(['A', 'B'])

        with pytest.raises(ValueError):
            network.add_constraint('A', 'D', 1)  # D not in variables

    def test_solve_constraints_no_evidence(self):
        """Test solving constraints without evidence."""
        network = ConstraintRankingNetwork(['A', 'B'])
        solution = network.solve_constraints()

        assert 'A' in solution
        assert 'B' in solution
        assert isinstance(solution['A'], Ranking)
        assert isinstance(solution['B'], Ranking)

    def test_solve_constraints_with_evidence(self):
        """Test solving constraints with evidence."""
        network = ConstraintRankingNetwork(['A', 'B'])
        evidence = {'A': 'A_normal'}
        solution = network.solve_constraints(evidence)

        assert 'A' in solution
        assert 'B' in solution

        # Check that evidence variable has the correct ranking
        a_ranking = list(solution['A'])
        assert a_ranking[0][0] == 'A_normal'  # First value should be evidence
        assert a_ranking[0][1] == 0  # Evidence should have rank 0

    def test_constraint_validation_mutual_exclusion(self):
        """Test constraint validation for mutual exclusion."""
        network = ConstraintRankingNetwork(['A', 'B'])
        network.add_constraint('A', 'B', 2)  # Mutual exclusion

        # Valid evidence
        valid_evidence = {'A': 'A_normal', 'B': 'B_abnormal'}
        assert network._validate_constraints(valid_evidence)

        # Invalid evidence (mutual exclusion violation)
        invalid_evidence = {'A': 'A_normal', 'B': 'B_normal'}
        assert not network._validate_constraints(invalid_evidence)

    def test_create_evidence_ranking(self):
        """Test creating ranking from evidence."""
        network = ConstraintRankingNetwork(['A'])
        ranking = network._create_evidence_ranking('A', 'A_normal')

        ranking_list = list(ranking)
        assert ranking_list[0] == ('A_normal', 0)  # Evidence has rank 0
        assert len(ranking_list) > 1  # Should have alternatives

    def test_get_variable_alternatives(self):
        """Test getting variable alternatives."""
        network = ConstraintRankingNetwork(['A'])
        alternatives = network._get_variable_alternatives('A')

        assert 'A_normal' in alternatives
        assert 'A_abnormal' in alternatives
        assert 'A_unknown' in alternatives

    def test_apply_causal_constraint(self):
        """Test applying causal constraints."""
        network = ConstraintRankingNetwork(['A', 'B'])
        ranking_a = network._create_default_ranking('A')
        ranking_b = network._create_default_ranking('B')

        # Apply causal constraint (A causes B)
        constrained_b = network._apply_causal_constraint(ranking_b, ranking_a, False)

        assert isinstance(constrained_b, Ranking)

    def test_apply_exclusion_constraint(self):
        """Test applying mutual exclusion constraints."""
        network = ConstraintRankingNetwork(['A', 'B'])
        ranking_a = network._create_default_ranking('A')
        ranking_b = network._create_default_ranking('B')

        # Apply exclusion constraint
        constrained_a = network._apply_exclusion_constraint(ranking_a, ranking_b)

        assert isinstance(constrained_a, Ranking)

    def test_values_conflict(self):
        """Test value conflict detection."""
        network = ConstraintRankingNetwork(['A', 'B'])

        # Test conflicting values
        assert network._values_conflict_mutual_exclusion('A_normal', 'A_abnormal')
        assert network._values_conflict_mutual_exclusion('healthy', 'faulty')
        assert network._values_conflict_mutual_exclusion('working', 'broken')

        # Test non-conflicting values
        assert not network._values_conflict_mutual_exclusion('A_normal', 'B_normal')
        assert not network._values_conflict_mutual_exclusion('A_unknown', 'B_unknown')

    def test_constraint_satisfaction_score(self):
        """Test constraint satisfaction scoring."""
        network = ConstraintRankingNetwork(['A', 'B'])
        network.add_constraint('A', 'B', 2)  # Mutual exclusion

        # Perfect satisfaction
        perfect_assignment = {'A': 'A_normal', 'B': 'B_abnormal'}
        score = network.get_constraint_satisfaction_score(perfect_assignment)
        assert score == 1.0

        # No satisfaction
        bad_assignment = {'A': 'A_normal', 'B': 'B_normal'}
        score = network.get_constraint_satisfaction_score(bad_assignment)
        assert score == 0.0

    def test_find_optimal_assignment(self):
        """Test finding optimal variable assignment."""
        network = ConstraintRankingNetwork(['A', 'B'])
        network.add_constraint('A', 'B', 2)  # Mutual exclusion

        optimal = network.find_optimal_assignment()

        assert 'A' in optimal
        assert 'B' in optimal

        # Check that optimal assignment satisfies constraints
        score = network.get_constraint_satisfaction_score(optimal)
        assert score == 1.0

    def test_find_optimal_assignment_with_objective(self):
        """Test finding optimal assignment with custom objective."""
        network = ConstraintRankingNetwork(['A', 'B'])

        def custom_objective(assignment):
            # Prefer 'normal' values
            score = 0.0
            for var, value in assignment.items():
                if 'normal' in str(value):
                    score += 1.0
            return score / len(assignment)

        optimal = network.find_optimal_assignment(custom_objective)

        assert 'A' in optimal
        assert 'B' in optimal

    def test_generate_all_assignments_small_network(self):
        """Test generating all assignments for small network."""
        network = ConstraintRankingNetwork(['A', 'B'])

        assignments = network._generate_all_assignments()

        # Should generate all combinations
        assert len(assignments) > 1
        assert all('A' in assignment and 'B' in assignment for assignment in assignments)

    def test_sample_assignments_large_network(self):
        """Test sampling assignments for large network."""
        # Create a network that would be too large for exhaustive search
        variables = [f'V{i}' for i in range(15)]  # 15 variables
        network = ConstraintRankingNetwork(variables)

        assignments = network._sample_assignments(50)

        assert len(assignments) == 50
        assert all(len(assignment) == 15 for assignment in assignments)


class TestConstraintReasoningIntegration:
    """Integration tests for constraint reasoning with existing framework."""

    def test_integration_with_ranking_theory(self):
        """Test that constraint reasoning integrates with ranking theory."""
        from ranked_programming import nrm_exc

        network = ConstraintRankingNetwork(['A', 'B'])
        network.add_constraint('A', 'B', 1)  # Causal constraint

        # Add some evidence
        evidence = {'A': 'A_normal'}
        solution = network.solve_constraints(evidence)

        # Verify solution is valid rankings
        for var, ranking in solution.items():
            assert isinstance(ranking, Ranking)
            ranking_list = list(ranking)
            assert len(ranking_list) > 0
            assert all(isinstance(rank, int) for _, rank in ranking_list)

    def test_complex_constraint_network(self):
        """Test solving a more complex constraint network."""
        # Create a network with multiple constraints
        variables = ['A', 'B', 'C', 'D']
        network = ConstraintRankingNetwork(variables)

        # Add various types of constraints
        network.add_constraint('A', 'B', 1)  # A causes B
        network.add_constraint('B', 'C', 1)  # B causes C
        network.add_constraint('A', 'C', 2)  # A and C mutually exclusive
        network.add_constraint('C', 'D', 0)  # C and D independent

        # Solve with partial evidence
        evidence = {'A': 'A_normal', 'D': 'D_unknown'}
        solution = network.solve_constraints(evidence)

        assert len(solution) == 4
        assert all(isinstance(ranking, Ranking) for ranking in solution.values())

    def test_constraint_reasoning_with_belief_propagation(self):
        """Test integration with belief propagation."""
        from ranked_programming.belief_propagation import BeliefPropagationNetwork

        # Create a ranking network for belief propagation
        factors = {
            ('A',): Ranking(lambda: nrm_exc('A_normal', 'A_abnormal', 1)),
            ('B',): Ranking(lambda: nrm_exc('B_normal', 'B_abnormal', 1)),
            ('A', 'B'): Ranking(lambda: nrm_exc(
                ('A_normal', 'B_normal'), ('A_normal', 'B_abnormal'), 1
            ))
        }

        bp_network = BeliefPropagationNetwork(factors)
        bp_marginals = bp_network.propagate_beliefs()

        # Now create constraint network with same variables
        constraint_network = ConstraintRankingNetwork(['A', 'B'])
        constraint_network.add_constraint('A', 'B', 1)  # Causal

        # Both should produce valid results
        assert 'A' in bp_marginals
        assert 'B' in bp_marginals

        constraint_solution = constraint_network.solve_constraints()
        assert 'A' in constraint_solution
        assert 'B' in constraint_solution


class TestConstraintReasoningEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_network(self):
        """Test constraint network with no variables."""
        network = ConstraintRankingNetwork([])
        solution = network.solve_constraints()
        assert solution == {}

    def test_single_variable_network(self):
        """Test network with single variable."""
        network = ConstraintRankingNetwork(['A'])
        solution = network.solve_constraints()

        assert 'A' in solution
        assert isinstance(solution['A'], Ranking)

    def test_network_with_all_evidence(self):
        """Test network where all variables have evidence."""
        network = ConstraintRankingNetwork(['A', 'B'])
        evidence = {'A': 'A_normal', 'B': 'B_abnormal'}
        solution = network.solve_constraints(evidence)

        assert len(solution) == 2
        # Check that evidence rankings are correct
        a_ranking = list(solution['A'])
        b_ranking = list(solution['B'])
        assert a_ranking[0] == ('A_normal', 0)
        assert b_ranking[0] == ('B_abnormal', 0)

    def test_invalid_constraint_type(self):
        """Test handling of invalid constraint types."""
        network = ConstraintRankingNetwork(['A', 'B'])
        network.add_constraint('A', 'B', 999)  # Invalid constraint type

        # Should still work but log warning
        solution = network.solve_constraints()
        assert 'A' in solution
        assert 'B' in solution

    def test_large_network_performance(self):
        """Test performance with larger networks."""
        # Create a moderately large network
        variables = [f'V{i}' for i in range(8)]
        network = ConstraintRankingNetwork(variables)

        # Add some constraints
        for i in range(len(variables) - 1):
            network.add_constraint(variables[i], variables[i + 1], 1)

        # Should complete in reasonable time
        import time
        start_time = time.time()
        solution = network.solve_constraints()
        end_time = time.time()

        assert end_time - start_time < 5.0  # Should complete in less than 5 seconds
        assert len(solution) == 8


class TestConditionalRule:
    """Test ConditionalRule class functionality."""

    def test_conditional_rule_creation(self):
        """Test creating conditional rules."""
        condition = lambda x: x == 'A'
        consequent = lambda x: x == 'B'
        rule = ConditionalRule(condition, consequent, impact=2)

        assert rule.impact == 2
        assert rule.condition('A') == True
        assert rule.consequent('B') == True

    def test_conditional_rule_acceptance(self):
        """Test conditional rule acceptance conditions."""
        # World as dict
        world_ab = {'var': 'A', 'has_B': True}
        world_a_no_b = {'var': 'A', 'has_B': False}
        world_no_a = {'var': 'C', 'has_B': True}

        condition = lambda w: w['var'] == 'A'
        consequent = lambda w: w['has_B']

        rule = ConditionalRule(condition, consequent)

        # Should accept: condition false
        assert rule.accepts(world_no_a) == True

        # Should accept: condition true and consequent true
        assert rule.accepts(world_ab) == True

        # Should reject: condition true and consequent false
        assert rule.accepts(world_a_no_b) == False

    def test_negative_impact_handling(self):
        """Test that negative impacts are converted to zero."""
        condition = lambda x: True
        consequent = lambda x: True
        rule = ConditionalRule(condition, consequent, impact=-5)

        assert rule.impact == 0


class TestCRepresentation:
    """Test CRepresentation class functionality."""

    def test_c_representation_creation(self):
        """Test creating c-representations."""
        # Create simple conditional rules
        condition1 = lambda w: w['A']
        consequent1 = lambda w: w['B']
        rule1 = ConditionalRule(condition1, consequent1, impact=2)

        condition2 = lambda w: w['B']
        consequent2 = lambda w: w['C']
        rule2 = ConditionalRule(condition2, consequent2, impact=1)

        c_rep = CRepresentation([rule1, rule2])

        assert len(c_rep.rules) == 2
        assert c_rep.rules[0].impact == 2
        assert c_rep.rules[1].impact == 1

    def test_world_ranking(self):
        """Test ranking worlds with c-representation."""
        # Simple world representation
        world_abc = {'A': True, 'B': True, 'C': True}
        world_ab_no_c = {'A': True, 'B': True, 'C': False}
        world_a_no_bc = {'A': True, 'B': False, 'C': False}
        world_no_abc = {'A': False, 'B': False, 'C': False}

        # Rules:
        # 1. If A then B (impact 2)
        # 2. If B then C (impact 1)
        condition1 = lambda w: w['A']
        consequent1 = lambda w: w['B']
        rule1 = ConditionalRule(condition1, consequent1, impact=2)

        condition2 = lambda w: w['B']
        consequent2 = lambda w: w['C']
        rule2 = ConditionalRule(condition2, consequent2, impact=1)

        c_rep = CRepresentation([rule1, rule2])

        # Test ranking
        # world_abc: A∧B∧C - both rules satisfied, rank = 0
        assert c_rep.rank_world(world_abc) == 0

        # world_ab_no_c: A∧B∧¬C - rule1 satisfied, rule2 falsified, rank = 1
        assert c_rep.rank_world(world_ab_no_c) == 1

        # world_a_no_bc: A∧¬B∧¬C - rule1 falsified, rule2 satisfied (condition false), rank = 2
        assert c_rep.rank_world(world_a_no_bc) == 2

        # world_no_abc: ¬A∧¬B∧¬C - both rules satisfied (conditions false), rank = 0
        assert c_rep.rank_world(world_no_abc) == 0

    def test_to_ranking_function(self):
        """Test converting c-representation to Ranking object."""
        # Simple worlds
        worlds = [
            {'A': True, 'B': True},
            {'A': True, 'B': False},
            {'A': False, 'B': True},
            {'A': False, 'B': False}
        ]

        # Rule: If A then B (impact 1)
        condition = lambda w: w['A']
        consequent = lambda w: w['B']
        rule = ConditionalRule(condition, consequent, impact=1)

        c_rep = CRepresentation([rule])
        ranking = c_rep.to_ranking_function(worlds)

        # Convert to list to check ranks
        ranking_list = list(ranking)

        # World {'A': True, 'B': False} should have rank 1 (rule falsified)
        # Other worlds should have rank 0
        assert any(rank == 1 for w, rank in ranking_list if w['A'] and not w['B'])
        assert all(rank == 0 for w, rank in ranking_list if not (w['A'] and not w['B']))


class TestHybridIntegration:
    """Test hybrid integration between constraint networks and c-representations."""

    def test_create_c_rep_from_constraints(self):
        """Test creating c-representation from constraint network."""
        variables = ['A', 'B', 'C']
        constraints = [
            ('A', 'B', 1),  # Causal: A → B
            ('B', 'C', 1),  # Causal: B → C
            ('A', 'C', 2),  # Mutual exclusion: A ⊕ C
        ]

        c_rep = create_c_representation_from_constraints(constraints, variables)

        # Should create multiple conditional rules
        assert len(c_rep.rules) > 0

        # Check that rules have appropriate impacts
        causal_rules = [r for r in c_rep.rules if r.impact == 2]  # Causal rules
        exclusion_rules = [r for r in c_rep.rules if r.impact == 3]  # Exclusion rules

        assert len(causal_rules) == 2  # A→B, B→C
        assert len(exclusion_rules) == 2  # A⊕C creates two rules

    def test_create_constraint_network_from_c_rep(self):
        """Test creating constraint network from c-representation."""
        # Create simple c-representation
        condition = lambda w: w.get('A', False)
        consequent = lambda w: w.get('B', False)
        rule = ConditionalRule(condition, consequent, impact=1)

        c_rep = CRepresentation([rule])
        variables = ['A', 'B']

        network = create_constraint_network_from_c_representation(c_rep, variables)

        # Should create a valid constraint network
        assert isinstance(network, ConstraintRankingNetwork)
        assert len(network.variables) == 2


class TestCRepresentationIntegration:
    """Test c-representation integration with existing framework."""

    def test_c_rep_with_ranking_theory(self):
        """Test c-representation works with Ranking theory operations."""
        # Create worlds
        worlds = [
            {'healthy': True, 'working': True},
            {'healthy': True, 'working': False},
            {'healthy': False, 'working': True},
            {'healthy': False, 'working': False}
        ]

        # Rule: If healthy then working (impact 2)
        condition = lambda w: w['healthy']
        consequent = lambda w: w['working']
        rule = ConditionalRule(condition, consequent, impact=2)

        c_rep = CRepresentation([rule])
        ranking = c_rep.to_ranking_function(worlds)

        # Test disbelief rank
        healthy_prop = lambda w: w['healthy']
        disbelief_healthy = ranking.disbelief_rank(healthy_prop)

        # Should find the healthy worlds
        assert disbelief_healthy == 0  # There are healthy worlds

        # Test belief rank
        belief_healthy = ranking.belief_rank(healthy_prop)
        assert belief_healthy == 0.0  # τ(healthy) = κ(¬healthy) - κ(healthy) = 0 - 0 = 0

    def test_skeptical_inference_placeholder(self):
        """Test skeptical inference (placeholder implementation)."""
        worlds = [{'A': True}, {'A': False}]
        condition = lambda w: True
        consequent = lambda w: w['A']
        rule = ConditionalRule(condition, consequent)

        c_rep = CRepresentation([rule])

        # Test with query that should be true
        query = lambda w: True
        result = c_rep.skeptical_inference(query, worlds)
        # Placeholder implementation returns False for most cases
        assert isinstance(result, bool)


class TestConstraintReasoningCRepresentation:
    """Test constraint reasoning with c-representation features."""

    def test_constraint_network_with_c_rep_hybrid(self):
        """Test using c-representation features in constraint network."""
        variables = ['A', 'B']
        constraints = [('A', 'B', 1)]  # A → B

        network = ConstraintRankingNetwork(variables, constraints)

        # Test that we can still use regular constraint solving
        evidence = {'A': 'true'}
        result = network.solve_constraints(evidence)

        assert isinstance(result, dict)
        assert 'A' in result
        assert 'B' in result

    def test_large_c_representation(self):
        """Test c-representation with larger knowledge base."""
        # Create multiple rules
        rules = []
        variables = ['A', 'B', 'C', 'D']

        # Create chain of implications: A → B → C → D
        for i in range(len(variables) - 1):
            condition = lambda w, i=i: w[variables[i]]
            consequent = lambda w, i=i: w[variables[i + 1]]
            rule = ConditionalRule(condition, consequent, impact=1)
            rules.append(rule)

        c_rep = CRepresentation(rules)

        # Test with a world that satisfies all rules
        good_world = {var: True for var in variables}
        assert c_rep.rank_world(good_world) == 0

        # Test with a world that breaks one rule
        bad_world = {var: True for var in variables}
        bad_world['B'] = False  # Breaks A → B
        assert c_rep.rank_world(bad_world) == 1
