from dfs_engine.odds_ingest import normalize_event


def test_pair_quotes_by_player_book_and_exact_strike():
    event = {"id": "event1", "bookmakers": [{"key": "bookA", "markets": [
        {"key": "player_shots_on_goal", "last_update": "2026-09-29T12:00:00Z",
         "outcomes": [
             {"name": "Over", "description": "Alex Example", "point": 2.5, "price": -120},
             {"name": "Under", "description": "Alex Example", "point": 2.5, "price": 100},
             {"name": "Over", "description": "Alex Example", "point": 3.5, "price": 150},
             {"name": "Under", "description": "Alex Example", "point": 4.5, "price": -190},
             {"name": "Over", "description": "Unknown", "point": 2.5, "price": -110},
         ]}]}]}
    result = normalize_event(event, "NHL", {"event1": "FLA@CAR"},
                             {"event1|Alex Example": "123"})
    assert result["players"]["123"]["markets"]["shots"] == [{
        "threshold": 3, "book": "bookA", "captured_at_utc": "2026-09-29T12:00:00Z",
        "over": -120, "under": 100}]
    assert any(x["reason"] == "one_sided_quote" for x in result["skipped"])
    assert any(x["reason"] == "unmapped_player" for x in result["skipped"])
