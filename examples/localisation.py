"""
Robot Localisation Example (Python, aligned to Racket)
"""
from ranked_programming.rp_core import Ranking, nrm_exc

def neighbouring(s):
    x, y = s
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1)
    ]

def surrounding(s):
    x, y = s
    return [
        (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
        (x + 1, y), (x + 1, y + 1), (x, y + 1),
        (x - 1, y + 1), (x - 1, y)
    ]

def observable(s):
    def gen():
        yield (s, 0)
        for cell in surrounding(s):
            yield (cell, 1)
    return Ranking(gen)

def hmm(obs_seq, initial_state=(0, 3)):
    if not obs_seq:
        return Ranking(lambda: [([initial_state], 0)])
    else:
        def generator():
            for prev_path, prev_rank in hmm(obs_seq[:-1], initial_state):
                prev_state = prev_path[-1]
                for s, move_rank in Ranking(lambda: [(n, 0) for n in neighbouring(prev_state)]):
                    for (o, obs_rank) in observable(s):
                        print(f"DEBUG: prev_path={prev_path}, prev_state={prev_state}, s={s}, o={o}, obs_seq[-1]={obs_seq[-1]}, rank={prev_rank + move_rank + obs_rank}")
                        if o == obs_seq[-1]:
                            debug_path = prev_path + [s]
                            yield (debug_path, prev_rank + move_rank + obs_rank)
        return Ranking(generator)

def localisation_example():
    # Canonical Racket observation sequence
    obs_seq = [
        (0, 3), (2, 3), (3, 3), (3, 2), (4, 1), (2, 1), (3, 0), (1, 0)
    ]
    ranking = hmm(obs_seq, initial_state=(0, 3))
    print("Rank  Value\n------------")
    results = sorted(ranking, key=lambda x: (x[1], x[0]))
    for path, rank in results:
        racket_path = "(" + " ".join(f"({x} {y})" for x, y in path) + ")"
        print(f"{rank:<5} {racket_path}")
    print("Done")

if __name__ == "__main__":
    localisation_example()