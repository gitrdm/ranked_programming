"""
Tests for Constraint-Based Reasoning Module

This module contains comprehensive tests for the constraint reasoning functionality,
ensuring that constraint solving works correctly and integrates properly with
the existing ranking theory framework.
"""

import pytest
from ranked_programming.constraint_reasoning import ConstraintRankingNetwork
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
