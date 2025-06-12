"""
Example: Ranked Procedure Call (Python port)
Demonstrates ranked_apply for uncertain function application.
"""
from ranked_programming.rp_api import nrm_exc, rlet_star, pr_all

def ranked_procedure_call_example():
    # Uncertain operation: normally add, exceptionally multiply
    op = nrm_exc(lambda x, y: x + y, lambda x, y: x * y, 1)
    # Uncertain arguments: normally 10, exceptionally 20
    arg = nrm_exc(10, 20, 1)
    # Apply uncertain operation to uncertain arguments using rlet_star
    ranking = rlet_star([
        ('op', op),
        ('arg', arg)
    ], lambda op, arg: op(5, arg))
    print("Ranked procedure call output:")
    pr_all(ranking)

if __name__ == "__main__":
    ranked_procedure_call_example()
