"""Site scoring rules: stat components -> fantasy points.

Scoring is applied to *sampled component arrays*, never to point estimates
alone. That matters because most sites pay threshold bonuses (DK's 100-yard
game, 3+ blocks, double-double), and a bonus is a tail probability: you cannot
recover ``E[bonus]`` from ``E[yards]``.

Verify against the live site rules before a real slate -- sites do change them
(``sports/mlb.md``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

import numpy as np

Components = Mapping[str, np.ndarray]


@dataclass(frozen=True)
class ThresholdBonus:
    """``points`` awarded when ``stat >= threshold`` (DK-style yardage bonus)."""

    stat: str
    threshold: float
    points: float

    def apply(self, comps: Components, n: int) -> np.ndarray:
        arr = comps.get(self.stat)
        if arr is None:
            return np.zeros(n)
        return (np.asarray(arr) >= self.threshold) * self.points


@dataclass(frozen=True)
class ScoringRule:
    site: str
    sport: str
    slot: str  # "skater", "goalie", "hitter", "pitcher", "all"
    linear: Mapping[str, float]
    bonuses: tuple[ThresholdBonus, ...] = ()
    specials: tuple[Callable[[Components, int], np.ndarray], ...] = ()
    notes: str = ""

    def score(self, comps: Components) -> np.ndarray:
        n = _n_samples(comps)
        total = np.zeros(n, dtype=float)
        for stat, coef in self.linear.items():
            arr = comps.get(stat)
            if arr is not None:
                total = total + coef * np.asarray(arr, dtype=float)
        for bonus in self.bonuses:
            total = total + bonus.apply(comps, n)
        for fn in self.specials:
            total = total + fn(comps, n)
        return total

    def score_expectation(self, means: Mapping[str, float]) -> float:
        """Linear-only expectation. Ignores bonuses -- use :meth:`score` for those."""
        return float(sum(coef * float(means.get(stat, 0.0)) for stat, coef in self.linear.items()))

    @property
    def stats(self) -> tuple[str, ...]:
        keys = set(self.linear) | {b.stat for b in self.bonuses}
        return tuple(sorted(keys))


def _n_samples(comps: Components) -> int:
    for arr in comps.values():
        a = np.asarray(arr)
        if a.ndim > 0:
            return int(a.shape[0])
    return 1


# --------------------------------------------------------------------------
# NBA specials
# --------------------------------------------------------------------------


def _dk_nba_double_bonus(comps: Components, n: int) -> np.ndarray:
    cats = [np.asarray(comps.get(k, np.zeros(n)), dtype=float)
            for k in ("points", "rebounds", "assists", "steals", "blocks")]
    doubles = np.sum([c >= 10 for c in cats], axis=0)
    return 1.5 * (doubles >= 2) + 1.5 * (doubles >= 3)  # DD +1.5, TD +3 total


def _dk_dst_points_allowed(comps: Components, n: int) -> np.ndarray:
    """DraftKings defense points-allowed tiers."""
    pa = np.asarray(comps.get("points_allowed", np.full(n, 21.0)), dtype=float)
    out = np.full(n, -4.0)
    out = np.where(pa <= 34, -1.0, out)
    out = np.where(pa <= 27, 0.0, out)
    out = np.where(pa <= 20, 1.0, out)
    out = np.where(pa <= 13, 4.0, out)
    out = np.where(pa <= 6, 7.0, out)
    out = np.where(pa <= 0, 10.0, out)
    return out


# --------------------------------------------------------------------------
# Rule tables
# --------------------------------------------------------------------------


DK_NFL = ScoringRule(
    site="dk", sport="nfl", slot="all",
    linear={
        "pass_yards": 0.04, "pass_td": 4.0, "interception": -1.0,
        "rush_yards": 0.1, "rush_td": 6.0,
        "receptions": 1.0, "rec_yards": 0.1, "rec_td": 6.0,
        "fumble_lost": -1.0, "two_point": 2.0, "return_td": 6.0,
        "pass_2pt": 2.0,
    },
    bonuses=(
        ThresholdBonus("pass_yards", 300, 3.0),
        ThresholdBonus("rush_yards", 100, 3.0),
        ThresholdBonus("rec_yards", 100, 3.0),
    ),
    notes="DraftKings NFL classic, full PPR with 100/300-yard bonuses.",
)

FD_NFL = ScoringRule(
    site="fd", sport="nfl", slot="all",
    linear={
        "pass_yards": 0.04, "pass_td": 4.0, "interception": -1.0,
        "rush_yards": 0.1, "rush_td": 6.0,
        "receptions": 0.5, "rec_yards": 0.1, "rec_td": 6.0,
        "fumble_lost": -2.0, "two_point": 2.0, "return_td": 6.0,
    },
    notes="FanDuel NFL, half PPR, no yardage bonuses.",
)

DK_NFL_DST = ScoringRule(
    site="dk", sport="nfl", slot="dst",
    linear={
        "sacks": 1.0, "def_interceptions": 2.0, "fumble_recoveries": 2.0,
        "def_td": 6.0, "special_teams_td": 6.0, "safeties": 2.0, "blocked_kicks": 2.0,
    },
    specials=(_dk_dst_points_allowed,),
    notes="DraftKings NFL defense: event scoring plus points-allowed tiers.",
)

DK_NBA = ScoringRule(
    site="dk", sport="nba", slot="all",
    linear={
        "points": 1.0, "threes": 0.5, "rebounds": 1.25, "assists": 1.5,
        "steals": 2.0, "blocks": 2.0, "turnovers": -0.5,
    },
    specials=(_dk_nba_double_bonus,),
    notes="DraftKings NBA classic; double-double +1.5, triple-double +3 total.",
)

FD_NBA = ScoringRule(
    site="fd", sport="nba", slot="all",
    linear={
        "points": 1.0, "rebounds": 1.2, "assists": 1.5,
        "steals": 3.0, "blocks": 3.0, "turnovers": -1.0,
    },
    notes="FanDuel NBA, no double-double bonuses.",
)

DK_MLB_HITTER = ScoringRule(
    site="dk", sport="mlb", slot="hitter",
    linear={
        "singles": 3.0, "doubles": 5.0, "triples": 8.0, "home_runs": 10.0,
        "rbi": 2.0, "runs": 2.0, "walks": 2.0, "hbp": 2.0, "stolen_bases": 5.0,
    },
    notes="DraftKings MLB classic hitter.",
)

DK_MLB_PITCHER = ScoringRule(
    site="dk", sport="mlb", slot="pitcher",
    linear={
        "outs": 0.75, "strikeouts": 2.0, "win": 4.0, "earned_runs": -2.0,
        "hits_allowed": -0.6, "walks_allowed": -0.6, "hbp_allowed": -0.6,
        "complete_game": 2.5, "cg_shutout": 2.5, "no_hitter": 5.0,
    },
    notes="DraftKings MLB classic pitcher (0.75/out == 2.25/IP).",
)

FD_MLB_HITTER = ScoringRule(
    site="fd", sport="mlb", slot="hitter",
    linear={
        "singles": 3.0, "doubles": 6.0, "triples": 9.0, "home_runs": 12.0,
        "rbi": 3.5, "runs": 3.2, "walks": 3.0, "hbp": 3.0, "stolen_bases": 6.0,
    },
)

FD_MLB_PITCHER = ScoringRule(
    site="fd", sport="mlb", slot="pitcher",
    linear={
        "outs": 1.0, "strikeouts": 3.0, "win": 6.0, "earned_runs": -3.0,
    },
)

DK_NHL_SKATER = ScoringRule(
    site="dk", sport="nhl", slot="skater",
    linear={
        "goals": 8.5, "assists": 5.0, "shots": 1.5, "blocks": 1.3,
        "short_handed_points": 2.0, "shootout_goals": 1.5,
    },
    bonuses=(
        ThresholdBonus("goals", 3, 3.0),
        ThresholdBonus("shots", 5, 3.0),
        ThresholdBonus("blocks", 3, 3.0),
    ),
    notes="DraftKings NHL skater; 3+ point bonus handled as a special.",
)

DK_NHL_GOALIE = ScoringRule(
    site="dk", sport="nhl", slot="goalie",
    linear={"win": 6.0, "saves": 0.7, "goals_against": -3.5, "shutout": 4.0},
    bonuses=(ThresholdBonus("saves", 35, 3.0),),
)

DK_TENNIS_BO3 = ScoringRule(
    site="dk", sport="tennis", slot="all",
    linear={
        "match_played": 30.0, "games_won": 2.5, "games_lost": -2.0,
        "sets_won": 6.0, "sets_lost": -3.0, "match_won": 6.0,
        "aces": 0.4, "double_faults": -1.0, "breaks": 0.75,
    },
    bonuses=(
        ThresholdBonus("clean_sets", 1, 4.0),
        ThresholdBonus("straight_sets", 1, 6.0),
        ThresholdBonus("aces", 10, 2.0),
    ),
    notes="DraftKings tennis best-of-3. Confirm per-tournament before a build.",
)


RULES: dict[tuple[str, str, str], ScoringRule] = {
    ("dk", "nfl", "all"): DK_NFL,
    ("dk", "nfl", "dst"): DK_NFL_DST,
    ("dk", "ncaaf", "all"): DK_NFL,
    ("fd", "nfl", "all"): FD_NFL,
    ("dk", "nba", "all"): DK_NBA,
    ("fd", "nba", "all"): FD_NBA,
    ("dk", "mlb", "hitter"): DK_MLB_HITTER,
    ("dk", "mlb", "pitcher"): DK_MLB_PITCHER,
    ("fd", "mlb", "hitter"): FD_MLB_HITTER,
    ("fd", "mlb", "pitcher"): FD_MLB_PITCHER,
    ("dk", "nhl", "skater"): DK_NHL_SKATER,
    ("dk", "nhl", "goalie"): DK_NHL_GOALIE,
    ("dk", "tennis", "all"): DK_TENNIS_BO3,
}


def get_rule(site: str, sport: str, slot: str = "all") -> ScoringRule:
    key = (site.lower(), sport.lower(), slot.lower())
    if key in RULES:
        return RULES[key]
    fallback = (site.lower(), sport.lower(), "all")
    if fallback in RULES:
        return RULES[fallback]
    raise KeyError(f"No scoring rule for site={site} sport={sport} slot={slot}")


def _nhl_three_point_bonus(comps: Components, n: int) -> np.ndarray:
    pts = (np.asarray(comps.get("goals", np.zeros(n)), dtype=float)
           + np.asarray(comps.get("assists", np.zeros(n)), dtype=float))
    return 3.0 * (pts >= 3)


object.__setattr__(DK_NHL_SKATER, "specials", (_nhl_three_point_bonus,))
