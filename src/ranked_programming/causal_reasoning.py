#!/usr/bin/env python3
"""
Causal Reasoning Module for Ranked Programming

This module implements causal reasoning capabilities for the ranked_programming library,
building on Wolfgang Spohn's Ranking Theory. It provides tools for causal discovery,
causal inference, and causal analysis using ranking-theoretic foundations.

The implementation follows a projectivist approach to causation, where causal relationships
are analyzed through their effects on ranking functions and belief dynamics.

Author: Ranked Programming Library
Date: September 2025
"""

from typing import Any, Callable, List, Dict, Set, Tuple, Optional, Union
from collections import defaultdict
import itertools

from ranked_programming import Ranking, nrm_exc, observe_e
from ranked_programming.theory_types import Proposition, DisbeliefRank, BeliefRank


class CausalReasoner:
    """
    Causal Reasoner for Ranking Theory

    This class provides methods for causal analysis using ranking functions.
    It implements projectivist causal inference based on Spohn's framework.

    Key Concepts:
    - Direct causation: A is a direct cause of B if intervening on A changes B
    - Causal strength: Measured by ranking function differences
    - Causal discovery: Finding causal relationships from observational data
    """

    def __init__(self, background_knowledge: Optional[Dict[str, Any]] = None):
        """
        Initialize the Causal Reasoner.

        Args:
            background_knowledge: Dictionary of background assumptions and constraints
        """
        self.background_knowledge = background_knowledge or {}
        self.causal_graph = defaultdict(set)  # Adjacency list for causal relationships
        self.causal_strengths = {}  # Store strength of causal relationships

    def is_direct_cause(self,
                       cause_prop: Proposition,
                       effect_prop: Proposition,
                       background_vars: List[Proposition],
                       ranking: Ranking) -> Tuple[bool, float]:
        """
        Test if A is a direct cause of B given background variables.

        This implements the interventionist theory of causation:
        A causes B if intervening on A while holding background variables
        fixed changes the probability/ranking of B.

        Args:
            cause_prop: Proposition representing the potential cause A
            effect_prop: Proposition representing the potential effect B
            background_vars: List of propositions for background variables
            ranking: The observational ranking function

        Returns:
            Tuple[bool, float]: (is_direct_cause, causal_strength)
        """
        # Get baseline ranking of effect
        baseline_tau = ranking.belief_rank(effect_prop)

        # Simulate intervention: force cause to be true
        intervened_ranking = self._intervene(ranking, cause_prop, True)

        # Get ranking of effect after intervention
        intervened_tau = intervened_ranking.belief_rank(effect_prop)

        # Calculate causal strength as difference
        causal_strength = intervened_tau - baseline_tau

        # A is a direct cause if intervening on A changes B's ranking
        is_direct_cause = abs(causal_strength) > 0.5  # Threshold for significance

        return is_direct_cause, causal_strength

    def _intervene(self, ranking: Ranking, intervention_prop: Proposition,
                   intervention_value: bool) -> Ranking:
        """
        Simulate an intervention on a variable.

        In causal inference, an intervention forces a variable to a specific value,
        breaking any causal links into that variable.

        Args:
            ranking: Original ranking function
            intervention_prop: Variable to intervene on
            intervention_value: Value to force the variable to

        Returns:
            Ranking: New ranking function after intervention
        """
        # For intervention, we modify the ranking to reflect the forced value
        # This is a simplified implementation - full causal inference would be more complex

        def intervened_generator():
            for value, rank in ranking:
                if intervention_prop(value) == intervention_value:
                    # Keep values that satisfy the intervention
                    yield (value, rank)
                else:
                    # Values that don't satisfy intervention get infinite rank
                    # (representing impossibility under intervention)
                    yield (value, float('inf'))

        return Ranking(lambda: intervened_generator())

    def discover_causal_relationships(self,
                                    variables: List[Proposition],
                                    ranking: Ranking,
                                    max_lags: int = 1) -> Dict[Tuple[int, int], float]:
        """
        Discover causal relationships between variables using ranking differences.

        This implements a simple constraint-based causal discovery algorithm
        that looks for correlations in ranking function changes.

        Args:
            variables: List of propositions representing variables
            ranking: Observational ranking function
            max_lags: Maximum temporal lag to consider (for time series)

        Returns:
            Dict[Tuple[int, int], float]: Causal strengths between variable pairs
        """
        n_vars = len(variables)
        causal_matrix = {}

        for i in range(n_vars):
            for j in range(n_vars):
                if i != j:
                    # Test if variable i causes variable j
                    is_cause, strength = self.is_direct_cause(
                        variables[i], variables[j], variables, ranking
                    )

                    if is_cause:
                        causal_matrix[(i, j)] = strength
                        self.causal_graph[i].add(j)
                        self.causal_strengths[(i, j)] = strength

        return causal_matrix

    def analyze_causal_path(self,
                           start_var: Proposition,
                           end_var: Proposition,
                           variables: List[Proposition],
                           ranking: Ranking) -> List[Tuple[int, float]]:
        """
        Analyze the causal path from start variable to end variable.

        This finds the causal chain and quantifies the causal effect at each step.

        Args:
            start_var: Starting variable in the causal chain
            end_var: Ending variable in the causal chain
            variables: All variables in the system
            ranking: Observational ranking function

        Returns:
            List[Tuple[int, float]]: Path of causal effects
        """
        # Find indices of start and end variables
        try:
            start_idx = variables.index(start_var)
            end_idx = variables.index(end_var)
        except ValueError:
            return []

        # For now, implement direct causal path
        # More complex path finding would require graph algorithms
        is_direct, strength = self.is_direct_cause(
            variables[start_idx], variables[end_idx], variables, ranking
        )

        if is_direct:
            return [(end_idx, strength)]
        else:
            return []

    def counterfactual_reasoning(self,
                               factual_ranking: Ranking,
                               intervention: Dict[Proposition, bool],
                               query_prop: Proposition) -> Tuple[float, float]:
        """
        Perform counterfactual reasoning.

        "What would the ranking of Q be if we had intervened on X instead of what actually happened?"

        Args:
            factual_ranking: The actual observed ranking
            intervention: Dictionary of interventions {variable: value}
            query_prop: Proposition to query after intervention

        Returns:
            Tuple[float, float]: (factual_value, counterfactual_value)
        """
        # Get factual value
        factual_value = factual_ranking.belief_rank(query_prop)

        # Apply interventions to get counterfactual
        counterfactual_ranking = factual_ranking
        for var_prop, value in intervention.items():
            counterfactual_ranking = self._intervene(counterfactual_ranking, var_prop, value)

        counterfactual_value = counterfactual_ranking.belief_rank(query_prop)

        return factual_value, counterfactual_value

    def causal_effect_strength(self,
                             cause_prop: Proposition,
                             effect_prop: Proposition,
                             ranking: Ranking) -> float:
        """
        Quantify the strength of causal effect using ranking theory.

        This measures how much intervening on the cause changes the effect's ranking.

        Args:
            cause_prop: Cause proposition
            effect_prop: Effect proposition
            ranking: Observational ranking

        Returns:
            float: Causal effect strength (difference in τ values)
        """
        # Baseline effect ranking
        baseline_tau = ranking.belief_rank(effect_prop)

        # Intervene on cause (set to true)
        intervened_true = self._intervene(ranking, cause_prop, True)
        tau_true = intervened_true.belief_rank(effect_prop)

        # Intervene on cause (set to false)
        intervened_false = self._intervene(ranking, cause_prop, False)
        tau_false = intervened_false.belief_rank(effect_prop)

        # Average causal effect
        # Handle infinite values by using a large finite value
        from ranked_programming.theory_types import PRACTICAL_INFINITY
        
        def safe_value(x):
            if x == float('inf'):
                return PRACTICAL_INFINITY
            elif x == float('-inf'):
                return -PRACTICAL_INFINITY
            else:
                return x
        
        tau_true_safe = safe_value(tau_true)
        tau_false_safe = safe_value(tau_false)
        baseline_safe = safe_value(baseline_tau)
        
        causal_effect = (tau_true_safe - baseline_safe) - (tau_false_safe - baseline_safe)

        return causal_effect

    def conditional_causal_analysis(self,
                                  cause_prop: Proposition,
                                  effect_prop: Proposition,
                                  condition_prop: Proposition,
                                  ranking: Ranking) -> Dict[str, float]:
        """
        Perform conditional causal analysis using ranking theory.

        This analyzes the causal relationship between cause and effect conditional
        on a background condition using the Ranking.filter() method.

        Args:
            cause_prop: Cause proposition
            effect_prop: Effect proposition
            condition_prop: Background condition proposition
            ranking: Observational ranking

        Returns:
            Dict[str, float]: Conditional causal analysis results
        """
        results = {}

        # Overall causal effect (unconditional)
        results['unconditional_effect'] = self.causal_effect_strength(
            cause_prop, effect_prop, ranking
        )

        # Conditional on background condition being true
        conditional_true_ranking = ranking.filter(condition_prop)
        conditional_true_list = list(conditional_true_ranking)
        if len(conditional_true_list) > 0:  # Check if there are any values
            # Create a new ranking from the filtered values
            true_ranking = Ranking(lambda: conditional_true_list)
            # Check if the ranking has any finite values for the propositions
            if (true_ranking.disbelief_rank(cause_prop) < float('inf') and 
                true_ranking.disbelief_rank(effect_prop) < float('inf')):
                results['conditional_true_effect'] = self.causal_effect_strength(
                    cause_prop, effect_prop, true_ranking
                )
            else:
                results['conditional_true_effect'] = 0.0
        else:
            results['conditional_true_effect'] = 0.0

        # Conditional on background condition being false
        conditional_false_ranking = ranking.filter(lambda x: not condition_prop(x))
        conditional_false_list = list(conditional_false_ranking)
        if len(conditional_false_list) > 0:  # Check if there are any values
            # Create a new ranking from the filtered values
            false_ranking = Ranking(lambda: conditional_false_list)
            # Check if the ranking has any finite values for the propositions
            if (false_ranking.disbelief_rank(cause_prop) < float('inf') and 
                false_ranking.disbelief_rank(effect_prop) < float('inf')):
                results['conditional_false_effect'] = self.causal_effect_strength(
                    cause_prop, effect_prop, false_ranking
                )
            else:
                results['conditional_false_effect'] = 0.0
        else:
            results['conditional_false_effect'] = 0.0

        # Calculate conditional difference
        results['conditional_difference'] = (
            results['conditional_true_effect'] - results['conditional_false_effect']
        )

        return results

    def analyze_conditional_independence(self,
                                       var1_prop: Proposition,
                                       var2_prop: Proposition,
                                       condition_prop: Proposition,
                                       ranking: Ranking) -> Dict[str, float]:
        """
        Analyze conditional independence between two variables given a condition.

        This uses ranking theory to test if two variables are independent conditional
        on a third variable, which is a key concept in causal inference.

        Args:
            var1_prop: First variable proposition
            var2_prop: Second variable proposition
            condition_prop: Conditioning variable proposition
            ranking: Observational ranking

        Returns:
            Dict[str, float]: Conditional independence analysis results
        """
        results = {}

        # Unconditional correlation (measured by belief rank difference)
        unconditional_tau1 = ranking.belief_rank(var1_prop)
        unconditional_tau2 = ranking.belief_rank(var2_prop)
        results['unconditional_correlation'] = abs(unconditional_tau1 - unconditional_tau2)

        # Conditional correlation given condition is true
        conditional_true_ranking = ranking.filter(condition_prop)
        if len(list(conditional_true_ranking)) > 0:
            conditional_tau1_true = conditional_true_ranking.belief_rank(var1_prop)
            conditional_tau2_true = conditional_true_ranking.belief_rank(var2_prop)
            results['conditional_true_correlation'] = abs(conditional_tau1_true - conditional_tau2_true)
        else:
            results['conditional_true_correlation'] = 0.0

        # Conditional correlation given condition is false
        conditional_false_ranking = ranking.filter(lambda x: not condition_prop(x))
        if len(list(conditional_false_ranking)) > 0:
            conditional_tau1_false = conditional_false_ranking.belief_rank(var1_prop)
            conditional_tau2_false = conditional_false_ranking.belief_rank(var2_prop)
            results['conditional_false_correlation'] = abs(conditional_tau1_false - conditional_tau2_false)
        else:
            results['conditional_false_correlation'] = 0.0

        # Test for conditional independence
        # If correlation decreases significantly when conditioning, suggests dependence
        independence_threshold = 0.1
        results['conditionally_independent'] = (
            results['conditional_true_correlation'] < independence_threshold and
            results['conditional_false_correlation'] < independence_threshold
        )

        return results

    def validate_causal_assumptions(self,
                                  causal_graph: Dict[int, Set[int]],
                                  ranking: Ranking,
                                  variables: List[Proposition]) -> Dict[str, bool]:
        """
        Validate causal assumptions using ranking theory tests.

        Args:
            causal_graph: Assumed causal graph (adjacency list)
            ranking: Observational ranking
            variables: List of variable propositions

        Returns:
            Dict[str, bool]: Validation results
        """
        validation_results = {
            'no_cycles': self._check_no_cycles(causal_graph),
            'causal_markov': self._check_causal_markov(causal_graph, ranking, variables),
            'faithfulness': self._check_faithfulness(causal_graph, ranking, variables)
        }

        return validation_results

    def _check_no_cycles(self, graph: Dict[int, Set[int]]) -> bool:
        """
        Check if the causal graph contains cycles using topological sort.
        
        A causal graph should be a DAG (Directed Acyclic Graph).
        
        Args:
            graph: Causal graph as adjacency list
            
        Returns:
            bool: True if no cycles detected, False otherwise
        """
        # Kahn's algorithm for cycle detection
        # Get all nodes (both sources and targets)
        all_nodes = set(graph.keys())
        for neighbors in graph.values():
            all_nodes.update(neighbors)
        
        in_degree = {node: 0 for node in all_nodes}
        
        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node in in_degree if in_degree[node] == 0]
        processed_count = 0
        
        while queue:
            current = queue.pop(0)
            processed_count += 1
            
            # Reduce in-degree of neighbors
            if current in graph:
                for neighbor in list(graph[current]):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # If we processed all nodes, no cycles exist
        return processed_count == len(in_degree)

    def _check_causal_markov(self, graph: Dict[int, Set[int]],
                           ranking: Ranking, variables: List[Proposition]) -> bool:
        """
        Check if the causal Markov condition holds.
        
        The causal Markov condition states that each variable is independent of 
        its non-descendants given its parents.
        
        Args:
            graph: Causal graph as adjacency list
            ranking: Observational ranking function
            variables: List of variable propositions
            
        Returns:
            bool: True if Markov condition holds
        """
        def get_parents(node: int) -> Set[int]:
            """Get parents of a node in the graph."""
            parents = set()
            for potential_parent in graph:
                if node in graph[potential_parent]:
                    parents.add(potential_parent)
            return parents
        
        def get_non_descendants(node: int) -> Set[int]:
            """Get non-descendants of a node."""
            # Simple implementation - in practice would need proper graph traversal
            descendants = set()
            to_visit = list(graph.get(node, set()))
            
            while to_visit:
                current = to_visit.pop()
                if current not in descendants:
                    descendants.add(current)
                    to_visit.extend(graph.get(current, set()))
            
            all_nodes = set(graph.keys()) | set().union(*graph.values())
            return all_nodes - descendants - {node}
        
        # Check Markov condition for each node
        for node in graph:
            parents = get_parents(node)
            non_descendants = get_non_descendants(node)
            
            # Remove parents from non-descendants
            non_descendants -= parents
            
            if non_descendants:
                # Check conditional independence
                independence_result = self.analyze_conditional_independence(
                    variables[node], 
                    lambda x: any(var(x) for var in [variables[nd] for nd in non_descendants if nd < len(variables)]),
                    lambda x: all(var(x) for var in [variables[p] for p in parents if p < len(variables)]),
                    ranking
                )
                
                # If not conditionally independent, Markov condition violated
                if not independence_result.get('conditionally_independent', True):
                    return False
        
        return True

    def _check_faithfulness(self, graph: Dict[int, Set[int]],
                          ranking: Ranking, variables: List[Proposition]) -> bool:
        """
        Check if the faithfulness condition holds.
        
        The faithfulness condition states that all conditional independencies 
        in the data are represented in the causal graph (no extra independencies).
        
        Args:
            graph: Causal graph as adjacency list
            ranking: Observational ranking function
            variables: List of variable propositions
            
        Returns:
            bool: True if faithfulness holds
        """
        def get_d_connected_nodes(node1: int, node2: int, 
                                conditioned_set: Set[int]) -> bool:
            """
            Check if two nodes are d-connected given a conditioning set.
            This is a simplified version - full implementation would need proper d-separation.
            """
            # For now, check if they're connected through paths not blocked by conditioners
            # This is a placeholder for a more sophisticated d-separation algorithm
            return node1 != node2  # Simplified assumption
        
        # Check all pairs of variables
        n_vars = len(variables)
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                # Check conditional independence for different conditioning sets
                for k in range(n_vars):
                    if k != i and k != j:
                        # Test if i and j are conditionally independent given k
                        independence_result = self.analyze_conditional_independence(
                            variables[i], variables[j], variables[k], ranking
                        )
                        
                        # If they are conditionally independent but d-connected, 
                        # faithfulness is violated
                        if (independence_result.get('conditionally_independent', False) and
                            get_d_connected_nodes(i, j, {k})):
                            return False
        
        return True

    def pc_algorithm(self, variables: List[Proposition], ranking: Ranking, 
                   alpha: float = 0.05) -> Dict[Tuple[int, int], float]:
        """
        Implement the PC (Peter-Clark) algorithm for causal discovery.
        
        The PC algorithm is a constraint-based method that:
        1. Starts with a complete undirected graph
        2. Removes edges between unconditionally independent variables
        3. Removes edges between conditionally independent variables
        4. Determines edge orientations based on collider detection
        
        Args:
            variables: List of variable propositions
            ranking: Observational ranking function
            alpha: Significance threshold for independence tests
            
        Returns:
            Dict[Tuple[int, int], float]: Discovered causal relationships with strengths
        """
        n_vars = len(variables)
        causal_matrix = {}
        
        # Step 1: Find skeleton (undirected graph) using conditional independence tests
        skeleton = self._find_skeleton(variables, ranking, alpha)
        
        # Step 2: Determine edge orientations
        oriented_graph = self._orient_edges(skeleton, variables, ranking)
        
        # Convert to causal matrix format
        for i in oriented_graph:
            for j in oriented_graph[i]:
                # Test causal direction
                is_cause, strength = self.is_direct_cause(
                    variables[i], variables[j], variables, ranking
                )
                if is_cause:
                    causal_matrix[(i, j)] = strength
        
        return causal_matrix
    
    def _find_skeleton(self, variables: List[Proposition], ranking: Ranking, 
                      alpha: float) -> Dict[int, Set[int]]:
        """
        Find the skeleton (undirected graph) by testing conditional independence.
        
        Args:
            variables: List of variable propositions
            ranking: Observational ranking function
            alpha: Significance threshold
            
        Returns:
            Dict[int, Set[int]]: Undirected skeleton graph
        """
        n_vars = len(variables)
        skeleton = {i: set(range(n_vars)) - {i} for i in range(n_vars)}
        
        # Test for unconditional independence
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                independence_result = self.analyze_conditional_independence(
                    variables[i], variables[j], lambda x: True, ranking
                )
                
                if independence_result.get('unconditional_correlation', 1.0) < alpha:
                    # Remove edge if unconditionally independent
                    skeleton[i].discard(j)
                    skeleton[j].discard(i)
        
        # Test for conditional independence with increasing conditioning set sizes
        max_conditioning_size = min(3, n_vars - 2)  # Limit for computational feasibility
        
        for conditioning_size in range(1, max_conditioning_size + 1):
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    if j not in skeleton[i]:
                        continue
                        
                    # Try different conditioning sets
                    for condition_set in itertools.combinations(
                        [k for k in range(n_vars) if k != i and k != j], 
                        conditioning_size
                    ):
                        # Test conditional independence
                        condition_prop = lambda x: all(variables[k](x) for k in condition_set)
                        independence_result = self.analyze_conditional_independence(
                            variables[i], variables[j], condition_prop, ranking
                        )
                        
                        if independence_result.get('conditional_true_correlation', 1.0) < alpha:
                            # Remove edge if conditionally independent
                            skeleton[i].discard(j)
                            skeleton[j].discard(i)
                            break
        
        return skeleton
    
    def _orient_edges(self, skeleton: Dict[int, Set[int]], 
                     variables: List[Proposition], ranking: Ranking) -> Dict[int, Set[int]]:
        """
        Orient edges in the skeleton to create a DAG.
        
        This is a simplified version of the PC algorithm's orientation rules.
        
        Args:
            skeleton: Undirected skeleton graph
            variables: List of variable propositions
            ranking: Observational ranking function
            
        Returns:
            Dict[int, Set[int]]: Directed causal graph
        """
        oriented = {i: set() for i in skeleton}
        
        # Simple orientation based on causal strength
        for i in skeleton:
            for j in skeleton[i]:
                if j > i:  # Avoid duplicate work
                    # Test both directions
                    is_i_cause, strength_i_to_j = self.is_direct_cause(
                        variables[i], variables[j], variables, ranking
                    )
                    is_j_cause, strength_j_to_i = self.is_direct_cause(
                        variables[j], variables[i], variables, ranking
                    )
                    
                    # Orient based on stronger causal relationship
                    if abs(strength_i_to_j) > abs(strength_j_to_i):
                        oriented[i].add(j)
                    elif abs(strength_j_to_i) > abs(strength_i_to_j):
                        oriented[j].add(i)
                    # If equal strength, leave undirected (could be bidirected or unoriented)
        
        return oriented

    def learn_causal_structure_from_combinators(self, 
                                               base_ranking: Ranking,
                                               combinators: List[Callable[[Ranking], Ranking]],
                                               variables: List[Proposition]) -> Dict[Tuple[int, int], float]:
        """
        Learn causal structure by analyzing how combinators affect ranking functions.
        
        This method integrates causal discovery with the existing combinator framework
        by observing how different combinators change the ranking relationships.
        
        Args:
            base_ranking: Base observational ranking
            combinators: List of combinator functions to apply
            variables: List of variable propositions
            
        Returns:
            Dict[Tuple[int, int], float]: Learned causal relationships
        """
        causal_matrix = {}
        n_vars = len(variables)
        
        # Apply each combinator and observe changes
        for combinator in combinators:
            try:
                transformed_ranking = combinator(base_ranking)
                
                # Compare ranking changes for each variable pair
                for i in range(n_vars):
                    for j in range(n_vars):
                        if i != j:
                            # Measure how the combinator affects the relationship
                            base_correlation = self._measure_correlation(
                                variables[i], variables[j], base_ranking
                            )
                            transformed_correlation = self._measure_correlation(
                                variables[i], variables[j], transformed_ranking
                            )
                            
                            # If correlation changes significantly, there might be a causal link
                            correlation_change = abs(transformed_correlation - base_correlation)
                            
                            if correlation_change > 0.1:  # Threshold for significance
                                # Determine direction based on combinator type
                                direction = self._infer_direction_from_combinator(
                                    combinator, variables[i], variables[j], 
                                    base_ranking, transformed_ranking
                                )
                                
                                if direction == (i, j):
                                    causal_matrix[(i, j)] = correlation_change
                                elif direction == (j, i):
                                    causal_matrix[(j, i)] = correlation_change
                                    
            except Exception:
                # Skip combinators that fail to apply
                continue
        
        return causal_matrix
    
    def _measure_correlation(self, var1: Proposition, var2: Proposition, 
                           ranking: Ranking) -> float:
        """
        Measure correlation between two variables in a ranking.
        
        Args:
            var1: First variable proposition
            var2: Second variable proposition
            ranking: Ranking function
            
        Returns:
            float: Correlation measure
        """
        # Simple correlation measure based on belief rank difference
        tau1 = ranking.belief_rank(var1)
        tau2 = ranking.belief_rank(var2)
        return abs(tau1 - tau2)
    
    def _infer_direction_from_combinator(self, combinator: Callable[[Ranking], Ranking],
                                       var1: Proposition, var2: Proposition,
                                       base_ranking: Ranking, transformed_ranking: Ranking) -> Tuple[int, int]:
        """
        Infer causal direction based on how a combinator affects variables.
        
        This is a heuristic approach that looks at which variable's ranking
        changes more under the combinator transformation.
        
        Args:
            combinator: The combinator function applied
            var1: First variable proposition
            var2: Second variable proposition
            base_ranking: Original ranking
            transformed_ranking: Ranking after combinator application
            
        Returns:
            Tuple[int, int]: Inferred causal direction (cause, effect)
        """
        # Measure ranking changes
        base_tau1 = base_ranking.belief_rank(var1)
        base_tau2 = base_ranking.belief_rank(var2)
        transformed_tau1 = transformed_ranking.belief_rank(var1)
        transformed_tau2 = transformed_ranking.belief_rank(var2)
        
        change1 = abs(transformed_tau1 - base_tau1)
        change2 = abs(transformed_tau2 - base_tau2)
        
        # Assume the variable with less change is the cause
        # (more stable under transformation)
        if change1 < change2:
            return (0, 1)  # var1 -> var2 (placeholder indices)
        else:
            return (1, 0)  # var2 -> var1


# Utility functions for causal analysis

def create_causal_model(variables: Dict[str, Proposition],
                       causal_relationships: List[Tuple[str, str, float]]) -> 'CausalReasoner':
        """
        Create a causal reasoner from a declarative causal model.

        Args:
            variables: Dictionary mapping variable names to propositions
            causal_relationships: List of (cause, effect, strength) tuples

        Returns:
            CausalReasoner: Configured causal reasoner
        """
        reasoner = CausalReasoner()

        # Build causal graph
        for cause_name, effect_name, strength in causal_relationships:
            if cause_name in variables and effect_name in variables:
                cause_idx = list(variables.keys()).index(cause_name)
                effect_idx = list(variables.keys()).index(effect_name)
                reasoner.causal_graph[cause_idx].add(effect_idx)
                reasoner.causal_strengths[(cause_idx, effect_idx)] = strength

        return reasoner


def analyze_intervention_effects(ranking: Ranking,
                               interventions: Dict[Proposition, bool],
                               queries: List[Proposition]) -> Dict[str, float]:
    """
    Analyze the effects of multiple interventions on query variables.

    Args:
        ranking: Base ranking function
        interventions: Dictionary of interventions
        queries: List of propositions to query

    Returns:
        Dict[str, float]: Effects on each query variable
    """
    # Apply all interventions
    current_ranking = ranking
    for var_prop, value in interventions.items():
        current_ranking = CausalReasoner()._intervene(current_ranking, var_prop, value)

    # Query effects
    effects = {}
    for query_prop in queries:
        effects[f"query_{len(effects)}"] = current_ranking.belief_rank(query_prop)

    return effects

