"""Pull industry projections and sportsbook props for any slate.

Inputs are sport and date. Nothing in this module is a player, a game, or a slate.
A summarized page fetch is not a source. Reject a feed whose lines do not vary.
"""

from __future__ import annotations

import csv
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

ODDS_API = "https://api.the-odds-api.com/v4"
DK_BOOK = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1"

SPORT_KEYS = {
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "nfl": "americanfootball_nfl",
    "nba": "basketball_nba",
}

# Markets the blend knows how to ask for. Sport modules own the site-point conversion.
PROP_MARKETS = {
    "mlb": [
        "batter_hits",
        "batter_total_bases",
        "batter_home_runs",
        "batter_rbis",
        "batter_runs_scored",
        "batter_stolen_bases",
        "pitcher_strikeouts",
        "pitcher_outs",
        "pitcher_earned_runs",
        "pitcher_hits_allowed",
        "pitcher_walks",
    ],
    "nhl": [
        "player_goal_scorer_anytime",
        "player_points",
        "player_assists",
        "player_shots_on_goal",
        "player_blocked_shots",
        "player_total_saves",
    ],
    "nfl": [
        "player_pass_yds",
        "player_pass_tds",
        "player_rush_yds",
        "player_reception_yds",
        "player_receptions",
        "player_anytime_td",
    ],
    "nba": [
        "player_points",
        "player_rebounds",
        "player_assists",
        "player_threes",
        "player_steals",
        "player_blocks",
    ],
}


def _get(url: str, params: dict | None = None, timeout: int = 60) -> requests.Response:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response


def slate_window(slate_date: str) -> tuple[str, str]:
    """UTC window covering the slate date. The caller passes YYYY-MM-DD."""
    day = date.fromisoformat(slate_date)
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")


def pull_odds_api(sport: str, slate_date: str, api_key: str | None = None) -> list[dict]:
    """Raw book outcomes for every configured market on that date."""
    key = api_key or os.environ.get("ODDS_API_KEY")
    if not key:
        raise RuntimeError("ODDS_API_KEY is not set. Python cannot pull the book board without it.")
    start, end = slate_window(slate_date)
    rows: list[dict] = []
    for market in PROP_MARKETS[sport]:
        payload = _get(
            f"{ODDS_API}/sports/{SPORT_KEYS[sport]}/odds",
            {
                "apiKey": key,
                "regions": "us",
                "markets": market,
                "oddsFormat": "american",
                "bookmakers": "draftkings,fanduel,betmgm",
                "commenceTimeFrom": start,
                "commenceTimeTo": end,
            },
        ).json()
        for event in payload:
            for book in event.get("bookmakers", []):
                for mk in book.get("markets", []):
                    for outcome in mk.get("outcomes", []):
                        rows.append(
                            {
                                "sport": sport,
                                "date": slate_date,
                                "commence": event.get("commence_time"),
                                "game": f"{event.get('away_team')} @ {event.get('home_team')}",
                                "book": book.get("key"),
                                "market": mk.get("key"),
                                "player": outcome.get("description") or outcome.get("name"),
                                "side": outcome.get("name"),
                                "line": outcome.get("point"),
                                "odds": outcome.get("price"),
                            }
                        )
    if rows and not lines_vary(rows):
        raise RuntimeError("prop lines do not vary by player. This is a flattened fetch, not a board.")
    return rows


def lines_vary(rows: list[dict]) -> bool:
    lines = {row.get("line") for row in rows if row.get("line") is not None}
    return len(lines) > 1


def pull_dk_category(league_id: int, category_id: int, subcategory_id: int) -> list[dict]:
    """DraftKings sportsbook JSON for a league category. Ids come from the sport module."""
    url = f"{DK_BOOK}/leagues/{league_id}/categories/{category_id}/subcategories/{subcategory_id}"
    payload = _get(url).json()
    return list(payload.get("markets", []) or payload.get("selections", []) or [])


def pull_dff(sport: str) -> str:
    """Daily Fantasy Fuel page for that sport. Caller parses the table in Python."""
    url = f"https://www.dailyfantasyfuel.com/{sport}/projections/draftkings"
    return _get(url).text


def write_rows(path: str | Path, rows: list[dict]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return 0
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames and not isinstance(row[key], (dict, list)):
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
