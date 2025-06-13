"""
Literate Example: Ranked Procedure Call (Python, semantically aligned with Racket)

This example demonstrates ranked function application using rlet_star, matching the Racket example.

- Scenario 1: Deterministic addition.
- Scenario 2: Uncertain argument (normally 10, exceptionally 20).
- Scenario 3: Uncertain operation (normally +, exceptionally -) and uncertain argument.

Outputs are formatted for direct comparison with the Racket output.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star

def print_ranking(title, ranking):
    print(title)
    print("Rank  Value\n------------")
    results = sorted(ranking, key=lambda x: (x[1], x[0]))
    for value, rank in results:
        print(f"{rank:<5} {value}")
    print("Done")

def ranked_procedure_call_example():
    # Scenario 1: Deterministic addition
    ranking1 = Ranking(lambda: [(5 + 10, 0)])
    print_ranking("", ranking1)

    # Scenario 2: Uncertain argument (normally 10, exceptionally 20)
    arg2 = Ranking(lambda: nrm_exc(10, 20, 1))
    ranking2 = Ranking(lambda: rlet_star([
        ('arg', arg2)
    ], lambda arg: 5 + arg))
    print_ranking("", ranking2)

    # Scenario 3: Uncertain op (normally +, exceptionally -) and uncertain arg
    op3 = Ranking(lambda: nrm_exc(lambda x, y: x + y, lambda x, y: y - x, 1))
    arg3 = Ranking(lambda: nrm_exc(10, 20, 1))
    ranking3 = Ranking(lambda: rlet_star([
        ('op', op3),
        ('arg', arg3)
    ], lambda op, arg: op(5, arg)))
    print_ranking("", ranking3)

if __name__ == "__main__":
    ranked_procedure_call_example()
