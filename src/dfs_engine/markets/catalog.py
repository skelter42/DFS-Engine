"""Canonical stat vocabulary and per-provider market-key mappings.

Books each name the same market differently. Everything is normalised to the
canonical stat names used by ``projections/scoring.py`` so a DraftKings
"Passing Yards" market and a The-Odds-API ``player_pass_yds`` market land in
the same bucket and can be de-vigged across books.
"""

from __future__ import annotations

import re

# Canonical component names per sport. These must match the keys consumed by
# projections/scoring.py and the sport adapters.
CANONICAL_STATS: dict[str, tuple[str, ...]] = {
    "nfl": (
        "pass_yards", "pass_td", "pass_attempts", "pass_completions", "interception",
        "rush_yards", "rush_attempts", "rush_td", "receptions", "rec_yards", "rec_td",
        "anytime_td", "fumble_lost",
    ),
    "nba": (
        "points", "rebounds", "assists", "threes", "steals", "blocks", "turnovers",
        "points_rebounds_assists", "points_rebounds", "points_assists", "rebounds_assists",
    ),
    "mlb": (
        "hits", "total_bases", "home_runs", "rbi", "runs", "walks", "stolen_bases",
        "singles", "doubles", "triples", "hits_runs_rbis",
        "strikeouts", "outs", "earned_runs", "hits_allowed", "walks_allowed", "win",
    ),
    "nhl": (
        "goals", "assists", "nhl_points", "shots", "blocks", "saves", "goals_against",
        "win", "power_play_points",
    ),
    "tennis": ("aces", "double_faults", "total_games", "match_won", "sets_won"),
}

# Stats where a *count* distribution is appropriate, and the prior dispersion
# (negative-binomial r; None == Poisson) used when only one line is posted.
# Sports share canonical stat names (NBA and NHL both post "blocks" and
# "assists"), so genuinely different shapes live in COUNT_DISPERSION_BY_SPORT.
COUNT_DISPERSION: dict[str, float | None] = {
    "receptions": 12.0, "rush_attempts": 20.0, "pass_attempts": 40.0,
    "pass_completions": 30.0, "pass_td": 6.0, "rush_td": None, "rec_td": None,
    "interception": None, "fumble_lost": None,
    "points": 25.0, "rebounds": 14.0, "assists": 10.0, "threes": 6.0,
    "steals": None, "blocks": None, "turnovers": 8.0,
    "points_rebounds_assists": 30.0, "points_rebounds": 28.0,
    "points_assists": 26.0, "rebounds_assists": 12.0,
    "hits": None, "total_bases": 3.0, "home_runs": None, "rbi": 2.0, "runs": None,
    "walks": None, "stolen_bases": None, "singles": None, "doubles": None,
    "triples": None, "hits_runs_rbis": 4.0,
    "strikeouts": 12.0, "outs": 25.0, "earned_runs": 3.0, "hits_allowed": 8.0,
    "walks_allowed": None,
    "goals": None, "nhl_points": None, "shots": 8.0,
    "saves": 20.0, "goals_against": 4.0, "power_play_points": None,
    "aces": 8.0, "double_faults": 6.0, "total_games": 30.0,
}

#: Sport-specific overrides for stat names shared across sports.
COUNT_DISPERSION_BY_SPORT: dict[str, dict[str, float | None]] = {
    "nhl": {"blocks": 5.0, "assists": None},
    "nba": {"blocks": None, "assists": 10.0},
}


def dispersion_for(stat: str, sport: str | None = None) -> float | None:
    """Prior negative-binomial dispersion for ``stat`` (None means Poisson)."""
    if sport:
        override = COUNT_DISPERSION_BY_SPORT.get(sport.lower())
        if override and stat in override:
            return override[stat]
    return COUNT_DISPERSION.get(stat)


# Continuous stats modelled lognormally, with a coefficient of variation prior.
CONTINUOUS_CV: dict[str, float] = {
    "pass_yards": 0.32,
    "rush_yards": 0.62,
    "rec_yards": 0.68,
}

# Binary markets: the de-vigged "yes" price is the expectation directly.
BINARY_STATS = {"anytime_td", "win", "match_won"}

# The Odds API v4 market keys -> canonical stat.
ODDS_API_MARKETS: dict[str, str] = {
    "player_pass_yds": "pass_yards",
    "player_pass_tds": "pass_td",
    "player_pass_attempts": "pass_attempts",
    "player_pass_completions": "pass_completions",
    "player_pass_interceptions": "interception",
    "player_rush_yds": "rush_yards",
    "player_rush_attempts": "rush_attempts",
    "player_rush_tds": "rush_td",
    "player_receptions": "receptions",
    "player_reception_yds": "rec_yards",
    "player_reception_tds": "rec_td",
    "player_anytime_td": "anytime_td",
    "player_points": "points",
    "player_rebounds": "rebounds",
    "player_assists": "assists",
    "player_threes": "threes",
    "player_blocks": "blocks",
    "player_steals": "steals",
    "player_turnovers": "turnovers",
    "player_points_rebounds_assists": "points_rebounds_assists",
    "player_points_rebounds": "points_rebounds",
    "player_points_assists": "points_assists",
    "player_rebounds_assists": "rebounds_assists",
    "batter_hits": "hits",
    "batter_total_bases": "total_bases",
    "batter_home_runs": "home_runs",
    "batter_rbis": "rbi",
    "batter_runs_scored": "runs",
    "batter_walks": "walks",
    "batter_stolen_bases": "stolen_bases",
    "batter_singles": "singles",
    "batter_doubles": "doubles",
    "batter_triples": "triples",
    "batter_hits_runs_rbis": "hits_runs_rbis",
    "pitcher_strikeouts": "strikeouts",
    "pitcher_outs": "outs",
    "pitcher_earned_runs": "earned_runs",
    "pitcher_hits_allowed": "hits_allowed",
    "pitcher_walks": "walks_allowed",
    "pitcher_record_a_win": "win",
    "player_goals": "goals",
    "player_assists_nhl": "assists",
    "player_points_nhl": "nhl_points",
    "player_shots_on_goal": "shots",
    "player_blocked_shots": "blocks",
    "player_total_saves": "saves",
    "player_power_play_points": "power_play_points",
}

#: Markets requested per sport from The Odds API (standard + alternate ladders).
ODDS_API_SPORT_MARKETS: dict[str, tuple[str, ...]] = {
    "nfl": (
        "player_pass_yds", "player_pass_tds", "player_pass_attempts",
        "player_pass_completions", "player_pass_interceptions", "player_rush_yds",
        "player_rush_attempts", "player_rush_tds", "player_receptions",
        "player_reception_yds", "player_reception_tds", "player_anytime_td",
    ),
    "nba": (
        "player_points", "player_rebounds", "player_assists", "player_threes",
        "player_blocks", "player_steals", "player_turnovers",
        "player_points_rebounds_assists",
    ),
    "mlb": (
        "batter_hits", "batter_total_bases", "batter_home_runs", "batter_rbis",
        "batter_runs_scored", "batter_walks", "batter_stolen_bases", "batter_singles",
        "batter_doubles", "batter_hits_runs_rbis", "pitcher_strikeouts",
        "pitcher_outs", "pitcher_earned_runs", "pitcher_hits_allowed",
        "pitcher_walks", "pitcher_record_a_win",
    ),
    "nhl": (
        "player_goals", "player_shots_on_goal", "player_blocked_shots",
        "player_total_saves", "player_power_play_points",
    ),
    "tennis": (),
}

ODDS_API_SPORT_KEYS: dict[str, str] = {
    "nfl": "americanfootball_nfl",
    "ncaaf": "americanfootball_ncaaf",
    "nba": "basketball_nba",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "tennis": "tennis_atp",
}

#: DraftKings Sportsbook league ids (public site content API).
DK_LEAGUE_IDS: dict[str, int] = {
    "nfl": 88808, "ncaaf": 87637, "nba": 42648, "mlb": 84240, "nhl": 42133,
}

#: Free-text market labels (DraftKings / FanDuel / aggregator exports) -> canonical.
LABEL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"pass(ing)?\s*yards?", "pass_yards"),
    (r"pass(ing)?\s*(tds?|touchdowns?)", "pass_td"),
    (r"pass(ing)?\s*attempts?", "pass_attempts"),
    (r"(pass(ing)?\s*)?completions?", "pass_completions"),
    (r"interceptions?\s*thrown", "interception"),
    (r"rush(ing)?\s*yards?", "rush_yards"),
    (r"rush(ing)?\s*attempts?|carries", "rush_attempts"),
    (r"rush(ing)?\s*(tds?|touchdowns?)", "rush_td"),
    (r"receiving\s*yards?|rec\.?\s*yards?", "rec_yards"),
    (r"receptions?", "receptions"),
    (r"receiving\s*(tds?|touchdowns?)", "rec_td"),
    (r"anytime\s*(td|touchdown)", "anytime_td"),
    (r"^(player\s*)?points$|total\s*points", "points"),
    (r"^(player\s*)?rebounds$|total\s*rebounds", "rebounds"),
    (r"^(player\s*)?assists$|total\s*assists", "assists"),
    (r"three\s*pointers?\s*made|3\s*pt\s*made|threes", "threes"),
    (r"^steals$", "steals"),
    (r"^blocks$|blocked\s*shots", "blocks"),
    (r"^turnovers$", "turnovers"),
    (r"pts\s*\+\s*reb\s*\+\s*ast|points.*rebounds.*assists", "points_rebounds_assists"),
    (r"total\s*bases", "total_bases"),
    (r"home\s*runs?", "home_runs"),
    (r"^hits$|batter\s*hits", "hits"),
    (r"^rbis?$|runs\s*batted\s*in", "rbi"),
    (r"runs\s*scored", "runs"),
    (r"stolen\s*bases?", "stolen_bases"),
    (r"^singles$", "singles"),
    (r"^doubles$", "doubles"),
    (r"^triples$", "triples"),
    (r"hits\s*\+\s*runs\s*\+\s*rbis?", "hits_runs_rbis"),
    (r"strikeouts?\s*(thrown)?|^ks$", "strikeouts"),
    (r"outs\s*recorded", "outs"),
    (r"earned\s*runs", "earned_runs"),
    (r"hits\s*allowed", "hits_allowed"),
    (r"walks\s*allowed", "walks_allowed"),
    (r"^walks$|bases\s*on\s*balls", "walks"),
    (r"to\s*record\s*(a\s*)?win|pitcher\s*win", "win"),
    (r"shots?\s*on\s*goal", "shots"),
    (r"^goals?$|anytime\s*goal", "goals"),
    (r"goalie\s*saves|total\s*saves|^saves$", "saves"),
    (r"power\s*play\s*points", "power_play_points"),
    (r"^aces$", "aces"),
    (r"double\s*faults?", "double_faults"),
    (r"total\s*games", "total_games"),
)


def canonical_stat(label: str, sport: str | None = None) -> str | None:
    """Map a provider market key or human label to a canonical stat name."""
    if not label:
        return None
    key = label.strip().lower()
    base = key.replace("_alternate", "")
    if base in ODDS_API_MARKETS:
        return ODDS_API_MARKETS[base]
    if sport == "nhl":
        if base == "player_assists":
            return "assists"
        if base == "player_points":
            return "nhl_points"
    cleaned = re.sub(r"[^a-z0-9+ ]+", " ", key).strip()
    for pattern, stat in LABEL_PATTERNS:
        if re.search(pattern, cleaned):
            if sport and stat not in CANONICAL_STATS.get(sport, ()) :
                continue
            return stat
    return None


def is_alternate(market_key: str) -> bool:
    return "alternate" in (market_key or "").lower()


def stat_family(stat: str) -> str:
    """Grouping used when reconciling overlapping markets."""
    if stat in {"hits", "total_bases", "home_runs", "singles", "doubles", "triples"}:
        return "mlb_hit_type"
    if stat in {"points", "rebounds", "assists", "points_rebounds_assists",
                "points_rebounds", "points_assists", "rebounds_assists"}:
        return "nba_box"
    return stat
