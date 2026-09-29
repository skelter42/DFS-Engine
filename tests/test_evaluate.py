import json

from dfs_engine.evaluate import score_snapshot


def test_evaluation_is_paired_and_ignores_unprojected_rows(tmp_path):
    audit, actuals = tmp_path / "audit.json", tmp_path / "actual.csv"
    audit.write_text(json.dumps({"sport": "NHL", "slate": "test", "as_of_utc": "2026-09-29T12:00:00Z",
        "rows": [
            {"dfs_id": "1", "status": "market_component_projection",
             "source_projection": 8, "projection": 10},
            {"dfs_id": "2", "status": "uncovered_source_preserved",
             "source_projection": 20},
            {"dfs_id": "3", "status": "industry_component_projection",
             "source_projection": 5, "projection": 6}]}))
    actuals.write_text("DFS ID,DK Points\n1,9\n2,25\n3,7\n")
    report = score_snapshot(audit, actuals)
    assert report["paired_count"] == 2
    assert report["source"]["mae"] == 1.5
    assert report["engine"]["mae"] == 1
    assert report["engine_mae_minus_source"] == -0.5
