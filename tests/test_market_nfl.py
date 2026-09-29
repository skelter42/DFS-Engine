import csv
import json

import pytest

from dfs_engine.cli import build_nfl_import
from dfs_engine.market_nfl import InsufficientMarket, estimate_stat, fair_over, project_player


def test_no_vig_pass_td_line_is_not_expected_tds():
    probability = fair_over(131, -170)
    assert probability == pytest.approx(0.4074, abs=0.001)
    fit = estimate_stat("pass_tds", [{"threshold": 2, "over": 131, "under": -170}])
    assert 1.3 < fit.mean < 1.5
    assert fit.mean != 1.5


def test_yards_need_spread_or_alternate_and_include_bonus():
    line = {"threshold": 79.5, "over": -110, "under": -110}
    with pytest.raises(InsufficientMarket):
        estimate_stat("rush_yds", [line])
    fit = estimate_stat("rush_yds", [line], sigma_prior=30)
    assert fit.mean > 79.5
    assert 0 < fit.at_least(100) < 0.5
    alternate = {"threshold": 99.5, "over": 170, "under": -210}
    fit2 = estimate_stat("rush_yds", [line, alternate])
    assert fit2.method == "priced_alternate_yards"
    assert fit2.at_least(100) == pytest.approx(fair_over(170, -210), abs=0.03)


def test_all_components_required_and_scoring_once():
    stats = dict.fromkeys(("pass_yds", "pass_tds", "interceptions", "rush_yds",
                           "receptions", "rec_yds", "offensive_tds", "fumbles_lost"), 0)
    stats.update(pass_yds=250, pass_tds=2, interceptions=1)
    player = {"prior_stats": stats, "bonus_probs": {
        "pass_yds": 0.15, "rush_yds": 0, "rec_yds": 0}}
    assert project_player(player)["projection"] == pytest.approx(17.45)
    del stats["interceptions"]
    with pytest.raises(InsufficientMarket):
        project_player(player)


def test_csv_roundtrip_preserves_own_and_zeros(tmp_path):
    source, inputs, output, audit = [tmp_path / x for x in
                                     ("source.csv", "input.json", "out.csv", "audit.json")]
    source.write_text("Name,DFS ID,Proj,Own\nA,1,11,22\nB,2,0,4\nC,3,5,8\n")
    stats = dict.fromkeys(("pass_yds", "pass_tds", "interceptions", "rush_yds",
                           "receptions", "rec_yds", "offensive_tds", "fumbles_lost"), 0)
    stats["receptions"] = 4
    inputs.write_text(json.dumps({"sport": "NFL", "site": "DraftKings",
        "slate": "test", "as_of_utc": "2026-09-29T16:00:00Z",
        "lock_utc": "2026-09-29T20:00:00Z", "players": {
        "1": {"prior_stats": stats, "bonus_probs": {
            "pass_yds": 0, "rush_yds": 0, "rec_yds": 0}}}}))
    build_nfl_import(source, inputs, output, audit)
    with output.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["Own"] for r in rows] == ["22", "4", "8"]
    assert [float(r["Proj"]) for r in rows] == [4, 0, 5]
    assert json.loads(audit.read_text())["rows"][2]["status"] == "uncovered_source_preserved"


def test_stale_quotes_do_not_replace_industry_component():
    prior = dict.fromkeys(("pass_yds", "pass_tds", "interceptions", "rush_yds",
                           "receptions", "rec_yds", "offensive_tds", "fumbles_lost"), 0)
    prior["rush_yds"] = 40
    player = {"prior_stats": prior, "as_of_utc": "2026-09-29T16:00:00Z",
        "markets": {"rush_yds": [{"threshold": 60.5, "over": -110, "under": -110,
                                 "book": "example", "captured_at_utc": "2026-09-29T10:00:00Z"}]},
        "bonus_probs": {"pass_yds": 0, "rush_yds": 0.1, "rec_yds": 0}}
    assert project_player(player)["stats"]["rush_yds"] == 40
    assert project_player(player)["provenance"]["rush_yds"] == "industry_component_prior"
