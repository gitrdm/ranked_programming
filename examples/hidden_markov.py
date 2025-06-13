"""
Literate Example: Hidden Markov Model (Python)

This example demonstrates ranked programming for a simple Hidden Markov Model (HMM) with two states, matching the Racket version.

- States: 'rainy', 'sunny'.
- Transitions: normally stay in the same state, exceptionally switch (using nrm_exc, rank 2).
- Emissions: each state emits a symbol, with normal and exceptional outcomes (using nrm_exc, rank 1).
- Recursively builds a sequence of states and emissions, conditioning on observations.
- The output is a ranking of all possible state sequences, ranked by plausibility.

Run this file to see the ranked output for the HMM scenario.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star, observe, pr_all
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default to INFO, can be set to DEBUG for tracing
    format='[%(levelname)s] %(message)s'
)
# Allow debug mode via environment variable
if os.environ.get('HMM_DEBUG', '0') == '1':
    logging.getLogger().setLevel(logging.DEBUG)

def init():
    return Ranking(lambda: nrm_exc('rainy', 'sunny', 0))

def trans(s):
    if s == 'rainy':
        return Ranking(lambda: nrm_exc('rainy', 'sunny', 2))
    else:
        return Ranking(lambda: nrm_exc('sunny', 'rainy', 2))

def emit(s):
    if s == 'rainy':
        return Ranking(lambda: nrm_exc('yes', 'no', 1))
    else:
        return Ranking(lambda: nrm_exc('no', 'yes', 1))

def hmm(obs):
    def helper(states, emissions, rank, obs):
        if not obs:
            yield ((emissions, states), rank)
        else:
            prev_state = states[-1]
            for next_state, t_rank in trans(prev_state):
                for emission, e_rank in emit(next_state):
                    if emission == obs[0]:
                        result = (emissions + (emission,), states + (next_state,), rank + t_rank + e_rank)
                        logging.debug(f"obs={obs}, states={states}, emissions={emissions}, rank={rank}, prev_state={prev_state}, next_state={next_state}, t_rank={t_rank}, emission={emission}, e_rank={e_rank}, result={result}")
                        yield from helper(states + (next_state,), emissions + (emission,), rank + t_rank + e_rank, obs[1:])
    return Ranking(lambda: (result for init_state, init_rank in init() for result in helper((init_state,), tuple(), init_rank, obs)))

def print_hmm(obs):
    print(f"Hidden Markov Model output ranking for observations: {obs}")
    ranking = hmm(obs)
    pr_all(ranking)

if __name__ == "__main__":
    # Example 1: corresponds to (pr (hmm `("no" "no" "yes" "no" "no"))) in Racket
    print_hmm(['no', 'no', 'yes', 'no', 'no'])
    # Example 2: corresponds to (pr (hmm `("yes" "yes" "yes" "no" "no"))) in Racket
    print_hmm(['yes', 'yes', 'yes', 'no', 'no'])
    # Example 3: all "rainy" path (should yield rank 0 for all-rainy)
    print_hmm(['yes', 'yes', 'yes', 'yes', 'yes', 'yes'])

