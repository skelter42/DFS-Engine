import pytest

from dfs_engine.central_projection import central_projection, industry_baseline


AS_OF = "2026-09-29T18:00:00Z"
SOURCES = [
    {"source_group": "model-A", "site": "DraftKings", "as_of_utc": AS_OF, "points": 10,
     "forecast_type": "pregame_projection", "slate": "test", "source_url": "https://example.com/a"},
    {"source_group": "model-B", "site": "DraftKings", "as_of_utc": AS_OF, "points": 12,
     "forecast_type": "pregame_projection", "slate": "test", "source_url": "https://example.com/b"},
    {"source_group": "model-B", "site": "DraftKings", "as_of_utc": "2026-09-29T17:00:00Z", "points": 90,
     "forecast_type": "pregame_projection", "slate": "test", "source_url": "https://example.com/b-old"},
    {"source_group": "wrong-site", "site": "FanDuel", "as_of_utc": AS_OF, "points": 40,
     "forecast_type": "pregame_projection", "slate": "test", "source_url": "https://example.com/fd"},
    {"source_group": "dk-ppg", "site": "DraftKings", "as_of_utc": AS_OF, "points": 35,
     "forecast_type": "historical_average", "slate": "test", "source_url": "https://example.com/ppg"},
]


def test_consensus_groups_sources_and_rejects_wrong_scoring():
    baseline, groups = industry_baseline({"as_of_utc": AS_OF, "slate": "test", "industry_fpts": SOURCES})
    assert baseline == 11
    assert groups == ["model-A", "model-B"]


def test_homer_delta_gets_full_dk_hit_value_without_tb_market():
    player = {"as_of_utc": AS_OF, "slate": "test", "industry_fpts": SOURCES,
        "component_priors": {"home_runs": 0.2},
        "markets": {"home_runs": [{"threshold": 1, "over": 150, "under": -180,
                                    "book": "B", "captured_at_utc": AS_OF}]}}
    result = central_projection(player, "MLB", "hitter")
    assert result["projection"] == pytest.approx(11 + result["component_deltas"]["home_runs"], abs=.0001)
    assert 12 < result["projection"] < 13
    assert result["market_weights_used"]["home_runs"] == .5
    assert len(result["industry_groups"]) == 2

    player["market_weights"] = {"home_runs": 0}
    assert central_projection(player, "MLB", "hitter")["projection"] == 11
    player["market_weights"] = {"home_runs": 1}
    assert central_projection(player, "MLB", "hitter")["projection"] > 13


def test_nhl_shot_market_adjusts_floor_and_bonus_without_simming():
    player = {"as_of_utc": AS_OF, "slate": "test", "industry_fpts": SOURCES,
        "component_priors": {"shots": 3}, "bonus_priors": {"five_shots": .18},
        "dispersion_prior": {"shots": 6},
        "markets": {"shots": [{"threshold": 4, "over": 130, "under": -160,
                               "book": "B", "captured_at_utc": AS_OF}]}}
    result = central_projection(player, "NHL", "skater")
    assert "shots" in result["component_deltas"]
    assert "five_shots" in result["component_deltas"]
    assert result["projection"] == pytest.approx(11 + sum(result["component_deltas"].values()), abs=.0001)
