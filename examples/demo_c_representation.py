#!/usr/bin/env python3
"""
Demo: C-Representation Framework

This demo showcases the c-representation capabilities of the hybrid framework,
demonstrating Kern-Isberner's c-representations with conditional rules and impacts.

It demonstrates:
- ConditionalRule creation and acceptance conditions
- CRepresentation with multiple rules
- World ranking based on rule violations
- Conversion to Ranking objects
- Hybrid integration with constraint networks
- Skeptical inference (placeholder)
"""

from ranked_programming.constraint_reasoning import (
    ConditionalRule, CRepresentation,
    create_c_representation_from_constraints,
    create_constraint_network_from_c_representation
)
from ranked_programming import Ranking


def demo_conditional_rules():
    """Demonstrate ConditionalRule functionality."""
    print("=== ConditionalRule Demo ===")

    # Define world representations
    world_rain_wet = {'rain': True, 'ground_wet': True}
    world_rain_dry = {'rain': True, 'ground_wet': False}
    world_no_rain_wet = {'rain': False, 'ground_wet': True}
    world_no_rain_dry = {'rain': False, 'ground_wet': False}

    # Rule: If it rains, then the ground is wet
    condition = lambda w: w['rain']
    consequent = lambda w: w['ground_wet']
    rule = ConditionalRule(condition, consequent, impact=2)

    print(f"Rule impact: {rule.impact}")

    # Test rule acceptance
    print("\nRule acceptance test:")
    worlds = [world_rain_wet, world_rain_dry, world_no_rain_wet, world_no_rain_dry]
    world_names = ["Rain∧Wet", "Rain∧¬Wet", "¬Rain∧Wet", "¬Rain∧¬Wet"]

    for world, name in zip(worlds, world_names):
        accepted = rule.accepts(world)
        print(f"  {name}: {'✓' if accepted else '✗'}")

    # Test negative impact handling
    print("\nNegative impact handling:")
    bad_rule = ConditionalRule(condition, consequent, impact=-5)
    print(f"Original impact: -5, Actual impact: {bad_rule.impact}")


def demo_c_representation():
    """Demonstrate CRepresentation functionality."""
    print("\n=== CRepresentation Demo ===")

    # Define possible worlds
    worlds = [
        {'A': True, 'B': True, 'C': True},
        {'A': True, 'B': True, 'C': False},
        {'A': True, 'B': False, 'C': True},
        {'A': True, 'B': False, 'C': False},
        {'A': False, 'B': True, 'C': True},
        {'A': False, 'B': True, 'C': False},
        {'A': False, 'B': False, 'C': True},
        {'A': False, 'B': False, 'C': False},
    ]

    # Knowledge base: A → B → C
    rules = []

    # Rule 1: If A then B (impact 2)
    condition1 = lambda w: w['A']
    consequent1 = lambda w: w['B']
    rules.append(ConditionalRule(condition1, consequent1, impact=2))

    # Rule 2: If B then C (impact 1)
    condition2 = lambda w: w['B']
    consequent2 = lambda w: w['C']
    rules.append(ConditionalRule(condition2, consequent2, impact=1))

    c_rep = CRepresentation(rules)

    print("World ranking based on rule violations:")
    print("World\t\tRank\tViolations")
    print("-" * 40)

    for world in worlds:
        rank = c_rep.rank_world(world)
        world_str = f"{'A' if world['A'] else '¬A'} {'B' if world['B'] else '¬B'} {'C' if world['C'] else '¬C'}"
        print(f"{world_str}\t{rank}")

    # Convert to Ranking object
    ranking = c_rep.to_ranking_function(worlds)
    print(f"\nConverted to Ranking object with {len(list(ranking))} worlds")


def demo_hybrid_integration():
    """Demonstrate hybrid integration between constraint networks and c-representations."""
    print("\n=== Hybrid Integration Demo ===")

    # Start with constraint network
    variables = ['X', 'Y', 'Z']
    constraints = [
        ('X', 'Y', 1),  # X → Y (causal)
        ('Y', 'Z', 1),  # Y → Z (causal)
        ('X', 'Z', 2),  # X ⊕ Z (mutual exclusion)
    ]

    print("Original constraint network:")
    print(f"Variables: {variables}")
    print(f"Constraints: {constraints}")

    # Convert to c-representation
    c_rep = create_c_representation_from_constraints(constraints, variables)
    print(f"\nConverted to CRepresentation with {len(c_rep.rules)} rules:")

    for i, rule in enumerate(c_rep.rules):
        print(f"  Rule {i+1}: impact = {rule.impact}")

    # Convert back to constraint network
    constraint_network = create_constraint_network_from_c_representation(c_rep, variables)
    print(f"\nConverted back to ConstraintRankingNetwork:")
    print(f"Variables: {constraint_network.variables}")
    print(f"Constraints: {constraint_network.constraints}")


def demo_ranking_theory_integration():
    """Demonstrate integration with ranking theory operations."""
    print("\n=== Ranking Theory Integration Demo ===")

    # Create a simple domain
    worlds = [
        {'healthy': True, 'working': True},
        {'healthy': True, 'working': False},
        {'healthy': False, 'working': True},
        {'healthy': False, 'working': False}
    ]

    # Rule: If healthy then working
    condition = lambda w: w['healthy']
    consequent = lambda w: w['working']
    rule = ConditionalRule(condition, consequent, impact=1)

    c_rep = CRepresentation([rule])
    ranking = c_rep.to_ranking_function(worlds)

    print("World rankings:")
    for world, rank in ranking:
        world_str = f"{'H' if world['healthy'] else '¬H'} {'W' if world['working'] else '¬W'}"
        print(f"  {world_str}: rank {rank}")

    # Test ranking theory operations
    healthy_prop = lambda w: w['healthy']

    disbelief_rank = ranking.disbelief_rank(healthy_prop)
    belief_rank = ranking.belief_rank(healthy_prop)

    print("\nRanking theory analysis:")
    print(f"  κ(healthy) = {disbelief_rank}")
    print(f"  τ(healthy) = {belief_rank}")

    if belief_rank > 0:
        print("  → Belief in healthy")
    elif belief_rank < 0:
        print("  → Disbelief in healthy")
    else:
        print("  → Suspension of judgment about healthy")


def demo_skeptical_inference():
    """Demonstrate skeptical inference (placeholder implementation)."""
    print("\n=== Skeptical Inference Demo ===")

    worlds = [
        {'A': True, 'B': True},
        {'A': True, 'B': False},
        {'A': False, 'B': True},
        {'A': False, 'B': False}
    ]

    # Simple rule: If A then B
    condition = lambda w: w['A']
    consequent = lambda w: w['B']
    rule = ConditionalRule(condition, consequent, impact=1)

    c_rep = CRepresentation([rule])

    # Test queries
    queries = [
        (lambda w: w['A'], "A is true"),
        (lambda w: w['B'], "B is true"),
        (lambda w: w['A'] and w['B'], "A and B are both true"),
        (lambda w: not w['A'], "A is false")
    ]

    print("Skeptical inference results (placeholder):")
    for query, description in queries:
        result = c_rep.skeptical_inference(query, worlds)
        print(f"  {description}: {result}")


def demo_large_c_representation():
    """Demonstrate c-representation with larger knowledge base."""
    print("\n=== Large C-Representation Demo ===")

    # Create chain of implications: A → B → C → D → E
    variables = ['A', 'B', 'C', 'D', 'E']
    rules = []

    for i in range(len(variables) - 1):
        condition = lambda w, i=i: w[variables[i]]
        consequent = lambda w, i=i: w[variables[i + 1]]
        rules.append(ConditionalRule(condition, consequent, impact=1))

    c_rep = CRepresentation(rules)

    # Test with extreme worlds
    all_true = {var: True for var in variables}
    all_false = {var: False for var in variables}
    mixed = {var: (i % 2 == 0) for i, var in enumerate(variables)}

    print(f"C-Representation with {len(rules)} rules:")
    print(f"  All true world rank: {c_rep.rank_world(all_true)}")
    print(f"  All false world rank: {c_rep.rank_world(all_false)}")
    print(f"  Mixed world rank: {c_rep.rank_world(mixed)}")


if __name__ == "__main__":
    print("C-Representation Framework Demo")
    print("=" * 50)

    demo_conditional_rules()
    demo_c_representation()
    demo_hybrid_integration()
    demo_ranking_theory_integration()
    demo_skeptical_inference()
    demo_large_c_representation()

    print("\n" + "=" * 50)
    print("Demo completed successfully!")
