from dfs_engine.markets.aggregate import (
    consensus_for_market,
    coverage_report,
    dedupe_quotes,
    merge_snapshots,
    sweep,
)
from dfs_engine.markets.base import MarketSource
from dfs_engine.markets.catalog import canonical_stat
from dfs_engine.markets.draftkings import parse_dk_payload
from dfs_engine.markets.fileset import (
    CsvPropSource,
    JsonSnapshotSource,
    load_snapshot,
    save_snapshot,
)
from dfs_engine.markets.the_odds_api import parse_event_props
from dfs_engine.models import MarketSnapshot, normalize_name
from dfs_engine.odds.conversions import BookQuote


ODDS_API_EVENT = {
    "id": "evt1",
    "home_team": "Buffalo Bills",
    "away_team": "Kansas City Chiefs",
    "bookmakers": [
        {"key": "draftkings", "markets": [
            {"key": "player_pass_yds", "last_update": "2026-09-22T15:00:00Z", "outcomes": [
                {"name": "Over", "description": "Josh Allen", "price": -115, "point": 264.5},
                {"name": "Under", "description": "Josh Allen", "price": -105, "point": 264.5},
            ]},
            {"key": "player_anytime_td", "outcomes": [
                {"name": "Yes", "description": "James Cook", "price": 120},
                {"name": "No", "description": "James Cook", "price": -150},
            ]},
        ]},
        {"key": "fanduel", "markets": [
            {"key": "player_pass_yds", "outcomes": [
                {"name": "Over", "description": "Josh Allen", "price": -110, "point": 264.5},
                {"name": "Under", "description": "Josh Allen", "price": -110, "point": 264.5},
            ]},
            {"key": "player_pass_yds_alternate", "outcomes": [
                {"name": "Over", "description": "Josh Allen", "price": 150, "point": 299.5},
            ]},
        ]},
    ],
}


def test_odds_api_parser_buckets_books_and_alternates():
    snap = MarketSnapshot(sport="nfl")
    added = parse_event_props(ODDS_API_EVENT, snap, sport="nfl", source="the_odds_api")
    assert added == 3  # pass_yards@264.5, pass_yards@299.5, anytime_td
    key = (normalize_name("Josh Allen"), "pass_yards")
    market = snap.props[key]
    assert market.books == {"draftkings", "fanduel"}
    lines = market.lines()
    assert set(lines) == {264.5, 299.5}
    assert len(lines[264.5]) == 2                     # both books on the main line
    td = snap.props[(normalize_name("James Cook"), "anytime_td")]
    assert td.quotes[0].two_sided


def test_odds_api_consensus_devigs_both_sides():
    snap = MarketSnapshot(sport="nfl")
    parse_event_props(ODDS_API_EVENT, snap, sport="nfl", source="t")
    cons = consensus_for_market(snap.props[(normalize_name("Josh Allen"), "pass_yards")])
    assert cons is not None
    main = [p for p in cons.points if p.line == 264.5][0]
    assert 0.48 < main.prob_over < 0.55               # de-vigged, not the raw -115
    assert main.two_sided_books == 2


DK_PAYLOAD = {
    "events": [{"id": "77", "name": "Chiefs at Bills",
                "participants": [{"name": "Bills", "venueRole": "Home"},
                                 {"name": "Chiefs", "venueRole": "Away"}]}],
    "markets": [{"id": "m1", "eventId": "77", "name": "Receptions",
                 "marketType": {"name": "Receptions"}}],
    "selections": [
        {"marketId": "m1", "label": "Over", "points": 5.5,
         "displayOdds": {"american": "-125"},
         "participants": [{"name": "Stefon Diggs", "type": "Player"}]},
        {"marketId": "m1", "label": "Under", "points": 5.5,
         "displayOdds": {"american": "+100"},
         "participants": [{"name": "Stefon Diggs", "type": "Player"}]},
    ],
}


def test_draftkings_parser_reads_the_content_payload():
    snap = MarketSnapshot(sport="nfl")
    assert parse_dk_payload(DK_PAYLOAD, snap, sport="nfl") == 1
    assert snap.games[0].home_team == "Bills"
    quote = snap.props[(normalize_name("Stefon Diggs"), "receptions")].quotes[0]
    assert (quote.over, quote.under, quote.line) == (-125.0, 100.0, 5.5)


def test_csv_source_accepts_an_arbitrary_aggregator_export(tmp_path):
    path = tmp_path / "props.csv"
    path.write_text(
        "Player,Market,Line,Sportsbook,Over Odds,Under Odds\n"
        "Christian McCaffrey,Rushing Yards,74.5,betmgm,-110,-110\n"
        "Christian McCaffrey,Rushing Yards,74.5,caesars,-115,-105\n"
        "Christian McCaffrey,Receptions,4.5,betmgm,105,-130\n")
    snap = CsvPropSource(path=path).fetch("nfl")
    assert not snap.errors
    assert len(snap.props) == 2
    rush = snap.props[(normalize_name("Christian McCaffrey"), "rush_yards")]
    assert rush.books == {"betmgm", "caesars"}


def test_dedupe_keeps_the_two_sided_quote_from_the_same_book():
    quotes = [BookQuote("dk", 5.5, -110, None), BookQuote("dk", 5.5, -112, -108)]
    deduped = dedupe_quotes(quotes)
    assert len(deduped) == 1 and deduped[0].two_sided


def test_merge_combines_sources_without_double_counting_a_book():
    a = MarketSnapshot(sport="nfl", sources=["the_odds_api"])
    parse_event_props(ODDS_API_EVENT, a, sport="nfl", source="the_odds_api")
    b = MarketSnapshot(sport="nfl", sources=["draftkings"])
    parse_event_props(ODDS_API_EVENT, b, sport="nfl", source="draftkings")
    merged = merge_snapshots([a, b])
    market = merged.props[(normalize_name("Josh Allen"), "pass_yards")]
    assert len(market.lines()[264.5]) == 2      # dk + fd once each, not four times


def test_snapshot_roundtrip(tmp_path):
    snap = MarketSnapshot(sport="nfl", sources=["x"])
    parse_event_props(ODDS_API_EVENT, snap, sport="nfl", source="x")
    path = save_snapshot(snap, tmp_path / "snap.json")
    again = load_snapshot(path)
    assert again.sport == "nfl"
    assert set(again.props) == set(snap.props)
    assert JsonSnapshotSource(path=path).fetch("nfl").summary()["quotes"] == \
        snap.summary()["quotes"]


class _Boom(MarketSource):
    name = "boom"

    def fetch(self, sport, **kwargs):
        raise RuntimeError("book is down")


def test_a_failing_source_is_recorded_not_fatal():
    snap = sweep("nfl", [_Boom()])
    assert snap.props == {}
    assert any("book is down" in e for e in snap.errors)


def test_coverage_report_names_the_uncovered_players():
    snap = MarketSnapshot(sport="nfl")
    parse_event_props(ODDS_API_EVENT, snap, sport="nfl", source="x")
    report = coverage_report(snap, [normalize_name("Josh Allen"), normalize_name("Nobody Here")])
    assert report["players_with_any_market"] == 1
    assert report["uncovered"] == [normalize_name("Nobody Here")]


def test_unknown_market_labels_are_ignored_rather_than_guessed():
    assert canonical_stat("Some Novelty Market") is None
    assert canonical_stat("") is None
