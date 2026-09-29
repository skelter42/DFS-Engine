"""Normalize The Odds API event odds; never fuzzy-match player identities."""

from __future__ import annotations

from collections import defaultdict
import argparse
import json
from pathlib import Path


# Keys verified against the provider's published player-market catalog.
MARKET_KEYS = {
    "MLB": {
        "batter_hits": "hits", "batter_total_bases": "total_bases",
        "batter_home_runs": "home_runs", "batter_rbis": "rbi",
        "batter_runs_scored": "runs", "batter_walks": "walks",
        "batter_stolen_bases": "stolen_bases", "batter_triples": "triples",
        "pitcher_strikeouts": "strikeouts", "pitcher_outs": "outs",
        "pitcher_earned_runs": "earned_runs", "pitcher_hits_allowed": "hits_allowed",
        "pitcher_walks": "walks_allowed",
    },
    "NHL": {
        "player_goals": "goals", "player_assists": "assists",
        "player_shots_on_goal": "shots", "player_blocked_shots": "blocks",
        "player_total_saves": "saves", "player_points": "points",
    },
}
EVENT_KEYS = {"MLB": {"pitcher_record_a_win": "win"}, "NHL": {}}


def normalize_event(event: dict, sport: str, event_games: dict[str, str],
                    player_ids: dict[str, str]) -> dict:
    """Return paired quotes indexed by DFS ID with a missing-pair audit.

    `event_games` maps provider event ID to *this DK slate's* game ID;
    `player_ids` maps `event ID|provider player name` to DFS ID. A missing or
    ambiguous identity is skipped, never silently attached to a namesake.
    Input must use oddsFormat=american. Accept main and alternate market keys.
    """
    if sport not in MARKET_KEYS:
        raise ValueError("Supported sports: MLB and NHL")
    event_id = event["id"]
    if event_id not in event_games:
        raise ValueError(f"Provider event {event_id} is not mapped to the DK slate")
    grouped = defaultdict(dict)
    skipped = []
    for book in event.get("bookmakers", []):
        for market in book.get("markets", []):
            key = market["key"].removesuffix("_alternate")
            stat = MARKET_KEYS[sport].get(key)
            event_stat = EVENT_KEYS[sport].get(key)
            if not (stat or event_stat):
                continue
            time = market.get("last_update") or book.get("last_update")
            for outcome in market.get("outcomes", []):
                name = outcome.get("description")
                identity = f"{event_id}|{name}"
                player_id = player_ids.get(identity)
                if not player_id:
                    skipped.append({"market": market["key"], "player": name,
                                    "reason": "unmapped_player"})
                    continue
                side = outcome.get("name", "").lower()
                if event_stat:
                    if side not in {"yes", "no"}:
                        continue
                    lookup = (player_id, event_stat, book["key"], time, "event")
                else:
                    if side not in {"over", "under"} or outcome.get("point") is None:
                        continue
                    point = float(outcome["point"])
                    if point < 0:
                        continue
                    # A 0.5 line wins for 1+; 1.5 wins for 2+, etc.
                    threshold = int(point) + 1
                    lookup = (player_id, stat, book["key"], time, threshold)
                price = outcome.get("price")
                if not isinstance(price, (int, float)) or abs(price) < 100 or not time:
                    skipped.append({"market": market["key"], "player": name,
                                    "reason": "not_american_odds_or_missing_time"})
                    continue
                grouped[lookup][side] = price
    players: dict[str, dict] = {}
    for (player_id, stat, book, time, strike), sides in grouped.items():
        required = {"yes", "no"} if strike == "event" else {"over", "under"}
        if not required.issubset(sides):
            skipped.append({"dfs_id": player_id, "stat": stat, "book": book,
                            "reason": "one_sided_quote"})
            continue
        entry = players.setdefault(player_id, {"game": event_games[event_id],
                                               "markets": {}, "event_markets": {}})
        quote = {"book": book, "captured_at_utc": time, **sides}
        if strike == "event":
            entry["event_markets"].setdefault(stat, []).append(quote)
        else:
            # Constrain API key interpretation: a 0.5 count strike is 1+.
            entry["markets"].setdefault(stat, []).append(
                {"threshold": strike, **quote})
    return {"players": players, "skipped": skipped}


def assemble_inputs(template: dict, events: list[dict], event_games: dict[str, str],
                    player_ids: dict[str, str]) -> tuple[dict, dict]:
    """Merge live event quotes into prevalidated slate/role/component priors."""
    data = json.loads(json.dumps(template))
    sport = data["sport"]
    if sport not in {"MLB", "NHL"}:
        raise ValueError("Odds importer supports MLB/NHL")
    skipped = []
    for event in events:
        result = normalize_event(event, sport, event_games, player_ids)
        skipped.extend(result["skipped"])
        for player_id, quote_data in result["players"].items():
            if player_id not in data["players"]:
                skipped.append({"dfs_id": player_id, "reason": "not_in_slate_template"})
                continue
            target = data["players"][player_id]
            if target.get("game") != quote_data["game"] or quote_data["game"] not in data["games"]:
                raise ValueError(f"Market event / slate mismatch for DFS ID {player_id}")
            for group in ("markets", "event_markets"):
                for stat, quotes in quote_data[group].items():
                    target.setdefault(group, {}).setdefault(stat, []).extend(quotes)
    return data, {"unpaired_or_unmapped": skipped,
                  "mapped_players_with_markets": sum(bool(v.get("markets") or v.get("event_markets"))
                                                     for v in data["players"].values())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize event player odds into DK slate inputs")
    for name in ("template", "events", "event-map", "player-map", "output", "audit"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    template = json.loads(args.template.read_text())
    events = json.loads(args.events.read_text())
    if isinstance(events, dict):
        events = [events]
    result, audit = assemble_inputs(template, events,
        json.loads(args.event_map.read_text()), json.loads(args.player_map.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    args.audit.write_text(json.dumps(audit, indent=2) + "\n")


if __name__ == "__main__":
    main()
