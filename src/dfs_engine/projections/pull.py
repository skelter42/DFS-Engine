"""Pull industry projections and sportsbook props in Python.

A summarized page fetch is not a source. Market Inputs runs this module and
records the raw row count. Claude's 2026-09-29 pack pulled on the order of
3,000 prop rows this way. A full board that comes back as a few dozen lines
is a failed pull, not a thin slate.

Books: DraftKings, FanDuel, BetMGM, plus any other book the endpoint returns.
Industry: numeric DFS projection sites only. Articles are not industry.
"""

from __future__ import annotations

import csv
import os
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

MLB_PROP_MARKETS = [
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
]
NHL_PROP_MARKETS = [
    "player_goal_scorer_anytime",
    "player_points",
    "player_assists",
    "player_shots_on_goal",
    "player_blocked_shots",
    "player_total_saves",
]


def _get(url: str, params: dict | None = None, timeout: int = 60) -> requests.Response:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response


def pull_odds_api(sport: str, markets: list[str], api_key: str | None = None) -> list[dict]:
    """Raw two-sided player props from The Odds API. One row per book outcome."""
    key = api_key or os.environ.get("ODDS_API_KEY")
    if not key:
        raise RuntimeError("ODDS_API_KEY is not set. Python cannot pull the book board without it.")
    sport_key = SPORT_KEYS[sport]
    rows: list[dict] = []
    for market in markets:
        payload = _get(
            f"{ODDS_API}/sports/{sport_key}/odds",
            {
                "apiKey": key,
                "regions": "us",
                "markets": market,
                "oddsFormat": "american",
                "bookmakers": "draftkings,fanduel,betmgm",
            },
        ).json()
        for event in payload:
            for book in event.get("bookmakers", []):
                for mk in book.get("markets", []):
                    for outcome in mk.get("outcomes", []):
                        rows.append(
                            {
                                "game": f"{event.get('away_team')} @ {event.get('home_team')}",
                                "book": book.get("key"),
                                "market": mk.get("key"),
                                "player": outcome.get("description") or outcome.get("name"),
                                "side": outcome.get("name"),
                                "line": outcome.get("point"),
                                "odds": outcome.get("price"),
                            }
                        )
    return rows


def pull_dk_category(league_id: int, category_id: int, subcategory_id: int) -> list[dict]:
    """DraftKings sportsbook JSON. Used when the Odds API key is absent."""
    url = f"{DK_BOOK}/leagues/{league_id}/categories/{category_id}/subcategories/{subcategory_id}"
    payload = _get(url).json()
    rows: list[dict] = []
    for market in payload.get("markets", []) or payload.get("selections", []) or []:
        rows.append(market)
    return rows


def pull_dff(sport: str) -> list[dict]:
    """Daily Fantasy Fuel numeric projections. One industry leader, not the blend."""
    url = f"https://www.dailyfantasyfuel.com/{sport}/projections/draftkings"
    html = _get(url).text
    return [{"source": "dailyfantasyfuel", "sport": sport, "bytes": len(html), "html": html}]


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
