"""
Ranking Network Example (Python, semantically aligned with Racket)

This example matches the Boolean network and ranking logic of the canonical Racket version.
"""
from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star

def network():
    def H():
        return Ranking(lambda: nrm_exc(False, True, 15))
    def B(h):
        if h:
            return Ranking(lambda: nrm_exc(False, True, 4))
        else:
            return Ranking(lambda: nrm_exc(True, False, 8))
    def F():
        return Ranking(lambda: nrm_exc(True, False, 10))
    def S(b, f):
        if b and f:
            return Ranking(lambda: nrm_exc(True, False, 3))
        elif b and not f:
            return Ranking(lambda: nrm_exc(False, True, 13))
        elif not b and f:
            return Ranking(lambda: nrm_exc(False, True, 11))
        else:
            return Ranking(lambda: nrm_exc(False, True, 27))
    # Full network: (H, B, F, S)
    return rlet_star([
        ('h', H()),
        ('b', lambda h: B(h)),
        ('f', F()),
        ('s', lambda b, f: S(b, f))
    ], lambda h, b, f, s: (h, b, f, s))

def print_ranking(title, ranking, limit=100):
    if title:
        print(title)
    print("Rank  Value\n------------")
    filtered = [item for item in ranking if isinstance(item[0], tuple) and len(item[0]) == 4]
    results = sorted(filtered, key=lambda x: (x[1], x[0]))[:limit]
    for value, rank in results:
        val_str = "(" + " ".join("#t" if v else "#f" for v in value) + ")"
        print(f"{rank:<5} {val_str}")
    print("Done")

def print_s_given_f_true():
    filtered = [(item, r) for item, r in network() if isinstance(item, tuple) and len(item) == 4]
    ranking = [(s, r) for (h, b, f, s), r in filtered if f]
    from collections import defaultdict
    min_ranks = defaultdict(lambda: float('inf'))
    for s, r in ranking:
        if r < min_ranks[s]:
            min_ranks[s] = r
    results = sorted(min_ranks.items(), key=lambda x: (x[1], x[0]))
    print("\nRank  Value\n------------")
    for s, rank in results:
        print(f"{rank:<5} {'#t' if s else '#f'}")
    print("Done")

def main():
    print_ranking("", list(network()))
    print_s_given_f_true()

if __name__ == "__main__":
    main()
