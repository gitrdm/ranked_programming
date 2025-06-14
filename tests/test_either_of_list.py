from ranked_programming.rp_core import Ranking, nrm_exc, either_of

def test_either_of_list_weekdays_weekend():
    # (define weekdays (list "mon" "tue" "wed" "thu" "fri"))
    # (define weekend (list "sat" "sun"))
    weekdays = [(d, 0) for d in ["mon", "tue", "wed", "thu", "fri"]]
    weekend = [(d, 0) for d in ["sat", "sun"]]
    ranking = Ranking(lambda: nrm_exc(either_of(weekdays), either_of(weekend)))
    result = list(ranking)
    # All weekdays at rank 0, all weekend at rank 1
    for day in ["mon", "tue", "wed", "thu", "fri"]:
        assert (day, 0) in result
    for day in ["sat", "sun"]:
        assert (day, 1) in result
    assert len(result) == 7
