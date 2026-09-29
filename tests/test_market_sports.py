import csv
import json

import pytest

from dfs_engine.cli import build_import
from dfs_engine.market_nfl import InsufficientMarket
from dfs_engine.market_sports import (project_mlb_hitter, project_mlb_pitcher,
                                      project_nhl_goalie, project_nhl_skater)


def test_mlb_hit_identity_prevents_home_run_double_counting():
    # An HR is one hit and four total bases; the hit component is 10 DK,
    # and the run/RBI are additional real box-score events.
    stats = {"hits": 1, "total_bases": 4, "triples": 0, "home_runs": 1,
             "rbi": 1, "runs": 1, "walks": 0, "hbp": 0, "stolen_bases": 0}
    assert project_mlb_hitter({"prior_stats": stats})["projection"] == 14
    stats["total_bases"] = 2
    with pytest.raises(InsufficientMarket):
        project_mlb_hitter({"prior_stats": stats})


def test_mlb_pitcher_uses_outs_and_separate_bonus_probabilities():
    player = {"prior_stats": {"outs": 18, "strikeouts": 6, "earned_runs": 2,
        "hits_allowed": 5, "walks_allowed": 2, "hbp_allowed": 0},
        "event_priors": {"win": 0.5, "complete_game": 0.02,
                         "complete_game_shutout": 0.01, "no_hitter": 0.001}}
    assert project_mlb_pitcher(player)["projection"] == pytest.approx(19.38)


def test_nhl_shots_bonus_uses_distribution_not_threshold_line():
    player = {"prior_stats": {"goals": 0.2, "assists": 0.4, "shots": 3,
        "blocks": 1, "shorthanded_points": 0, "shootout_goals": 0},
        "bonus_priors": {"hat_trick": 0.001, "five_shots": 0.2,
                         "three_blocks": 0.06, "three_points": 0.02}}
    result = project_nhl_skater(player)
    assert result["projection"] == pytest.approx(10.343)
    del player["bonus_priors"]["five_shots"]
    with pytest.raises(InsufficientMarket):
        project_nhl_skater(player)


def test_nhl_goalie_shutout_can_coexist_with_shootout_loss():
    player = {"prior_stats": {"saves": 30, "goals_against": 2,
                              "goalie_goals": 0, "goalie_assists": 0},
        "event_priors": {"win": 0.45, "shutout": 0.46, "ot_loss": 0.1},
        "bonus_priors": {"saves35": 0.2}}
    assert project_nhl_goalie(player)["projection"] == pytest.approx(19.34)


def test_multisport_export_requires_active_role_and_exact_game(tmp_path):
    source, inputs, output, audit = [tmp_path / x for x in
                                     ("source.csv", "input.json", "out.csv", "audit.json")]
    source.write_text("Name,DFS ID,Proj,Own\nA,1,8,22\nB,2,6,18\n")
    stats = {"hits": 1, "total_bases": 1, "triples": 0, "home_runs": 0,
             "rbi": 0, "runs": 0, "walks": 0, "hbp": 0, "stolen_bases": 0}
    data = {"sport": "MLB", "site": "DraftKings", "slate": "one game",
            "as_of_utc": "2026-09-29T17:00:00Z", "lock_utc": "2026-09-29T18:00:00Z",
            "games": ["PHI@ATL"], "players": {
                "1": {"game": "PHI@ATL", "kind": "hitter", "active_role": True,
                      "prior_stats": stats},
                "2": {"game": "PHI@ATL", "kind": "hitter", "active_role": False,
                      "prior_stats": stats}}}
    inputs.write_text(json.dumps(data))
    build_import(source, inputs, output, audit)
    with output.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [float(r["Proj"]) for r in rows] == [3, 6]
    assert [r["Own"] for r in rows] == ["22", "18"]
    assert json.loads(audit.read_text())["rows"][1]["status"] == "uncovered_source_preserved"
    data["players"]["1"]["game"] = "CWS@HOU"
    inputs.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="off-slate"):
        build_import(source, inputs, output, audit)
