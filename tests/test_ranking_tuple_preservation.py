from ranked_programming.rp_core import Ranking, nrm_exc, rlet_star

def test_tuple_preservation():
    # Ranking with a tuple as value
    r = Ranking(lambda: [((True, False, True), 0)])
    results = list(r)
    assert results == [((True, False, True), 0)], f"Expected tuple to be preserved, got {results}"

def test_tuple_preservation_with_nrm_exc():
    # nrm_exc with a tuple as the normal value
    r = Ranking(lambda: nrm_exc((True, False, True), (False, True, False), 1))
    results = list(r)
    assert results == [((True, False, True), 0), ((False, True, False), 1)], f"Expected tuples to be preserved, got {results}"

def test_tuple_preservation_with_rlet_star():
    # rlet_star with tuple values
    def a():
        return Ranking(lambda: [(True, 0), (False, 1)])
    def b(a):
        return Ranking(lambda: [((a, not a, True), 0)])
    r = Ranking(lambda: rlet_star([
        ('a', a()),
        ('b', b)
    ], lambda a, b: b))
    results = list(r)
    for value, rank in results:
        assert isinstance(value, tuple) and len(value) == 3, f"Expected tuple of length 3, got {value}"
    print("test_tuple_preservation_with_rlet_star passed")

if __name__ == "__main__":
    test_tuple_preservation()
    test_tuple_preservation_with_nrm_exc()
    test_tuple_preservation_with_rlet_star()
    print("All tuple preservation tests passed")
