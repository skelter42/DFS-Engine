import pytest

from dfs_engine.odds.conversions import (
    BookQuote,
    american_to_decimal,
    american_to_prob,
    consensus_over_prob,
    devig,
    devig_two_way,
    hold_pct,
    prob_to_american,
)


def test_american_decimal_roundtrip():
    for odds in (-350, -180, -110, 100, 145, 900):
        assert prob_to_american(american_to_prob(odds)) == pytest.approx(odds, rel=1e-9)
        assert american_to_decimal(odds) > 1.0


def test_even_money_devig_is_symmetric():
    assert devig_two_way(-110, -110) == pytest.approx(0.5)


def test_devig_removes_the_hold():
    raw = [american_to_prob(-135), american_to_prob(115)]
    assert sum(raw) > 1.0
    for method in ("multiplicative", "additive", "power", "shin"):
        fair = devig(raw, method)
        assert sum(fair) == pytest.approx(1.0, abs=1e-6)
        assert 0 < fair[0] < 1


def test_devig_methods_order_favourites_consistently():
    raw = [american_to_prob(-300), american_to_prob(240)]
    results = {m: devig(raw, m)[0] for m in ("multiplicative", "additive", "power", "shin")}
    # Every method must keep the favourite a favourite and shrink the raw price.
    for method, prob in results.items():
        assert 0.5 < prob < american_to_prob(-300), method


def test_one_sided_market_shaves_a_typical_hold():
    only_over = devig_two_way(-120, None)
    assert only_over < american_to_prob(-120)


def test_hold_is_positive_for_a_real_two_sided_market():
    assert hold_pct([-110, -110]) == pytest.approx(0.0476, abs=1e-3)


def test_consensus_is_robust_to_one_outlier_book():
    quotes = [
        BookQuote("dk", 5.5, -115, -105),
        BookQuote("fd", 5.5, -118, -102),
        BookQuote("mgm", 5.5, -112, -108),
        BookQuote("rogue", 5.5, -400, 320),   # stale/outlier book
    ]
    point = consensus_over_prob(quotes)
    assert point is not None
    assert point.n_books == 4
    assert point.prob_over == pytest.approx(0.52, abs=0.03)  # median, not dragged to 0.8
    assert point.dispersion > 0.1                            # disagreement is reported


def test_consensus_weight_rewards_books_and_agreement():
    tight = consensus_over_prob([BookQuote(b, 5.5, -110, -110) for b in "abcde"])
    thin = consensus_over_prob([BookQuote("a", 5.5, -110, None)])
    assert tight.weight > thin.weight


def test_consensus_rejects_mixed_lines():
    with pytest.raises(ValueError):
        consensus_over_prob([BookQuote("a", 5.5, -110, -110), BookQuote("b", 6.5, -110, -110)])
