import numpy as np
import pytest

from dfs_engine.projections.scoring import DK_NBA, DK_NFL, DK_NFL_DST, FD_NFL, get_rule


def test_dk_nfl_bonus_is_a_tail_event_not_a_mean():
    """A 100-yard bonus cannot be recovered from the mean; it needs the distribution."""
    rng = np.random.default_rng(0)
    comps = {"rec_yards": rng.gamma(2.0, 40.0, 50_000),
             "receptions": rng.poisson(5.0, 50_000),
             "rec_td": rng.poisson(0.5, 50_000)}
    sampled = float(DK_NFL.score(comps).mean())
    linear = DK_NFL.score_expectation({k: float(np.mean(v)) for k, v in comps.items()})
    assert sampled > linear                       # bonuses add value
    bonus_share = (sampled - linear) / sampled
    assert 0.01 < bonus_share < 0.15              # and it is a plausible share


def test_fd_nfl_yardage_bonuses_match_current_rules():
    comps = {
        "pass_yards": np.array([299.0, 300.0]),
        "rush_yards": np.array([99.0, 100.0]),
        "rec_yards": np.array([99.0, 100.0]),
    }
    scores = FD_NFL.score(comps)
    linear = np.array([
        299 * 0.04 + 99 * 0.1 + 99 * 0.1,
        300 * 0.04 + 100 * 0.1 + 100 * 0.1,
    ])
    assert scores[0] == pytest.approx(linear[0])
    assert scores[1] == pytest.approx(linear[1] + 9.0)


def test_dk_dst_points_allowed_tiers():
    pa = np.array([0, 3, 10, 17, 24, 30, 41], dtype=float)
    scores = DK_NFL_DST.score({"points_allowed": pa})
    assert list(scores) == [10.0, 7.0, 4.0, 1.0, 0.0, -1.0, -4.0]


def test_dk_nba_double_double_and_triple_double():
    comps = {
        "points": np.array([25.0, 25.0, 8.0]),
        "rebounds": np.array([11.0, 4.0, 3.0]),
        "assists": np.array([10.0, 3.0, 2.0]),
        "threes": np.zeros(3), "steals": np.zeros(3),
        "blocks": np.zeros(3), "turnovers": np.zeros(3),
    }
    scores = DK_NBA.score(comps)
    base = 25 + 1.25 * 11 + 1.5 * 10
    assert scores[0] == pytest.approx(base + 3.0)   # triple-double: +1.5 then +1.5
    assert scores[1] == pytest.approx(25 + 1.25 * 4 + 1.5 * 3)  # no double-double


def test_missing_components_score_as_zero_not_as_an_error():
    assert DK_NFL.score({"rush_yards": np.array([80.0])})[0] == pytest.approx(8.0)


def test_rule_lookup_falls_back_to_the_all_slot():
    assert get_rule("dk", "nfl", "all") is DK_NFL
    assert get_rule("dk", "nfl", "unknown-role") is DK_NFL
    with pytest.raises(KeyError):
        get_rule("dk", "cricket")
