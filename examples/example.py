#%%
from ranked_programming.rp_core import Ranking, nrm_exc, rlet, pr_all
#%%
def example_usage():
    # Example usage of the Ranking class and combinators
    def gen1():
        yield (1, 0)
        yield (2, 1)

    def gen2():
        yield (3, 0)
        yield (4, 2)

    # Create a ranking using nrm_exc
    ranking = Ranking(lambda: nrm_exc(gen1(), gen2(), 1))
    
    # Use rlet to bind values
    ranked = Ranking(lambda: rlet([
        ('x', gen1),
        ('y', gen2)
    ], lambda x, y: (x[0] + y[0], x[1] + y[1])))

    # Print all results
    print("Results from nrm_exc:")
    for item in ranking.to_eager():
        print(item)

    print("\nResults from rlet:")
    for item in ranked.to_eager():
        print(item)