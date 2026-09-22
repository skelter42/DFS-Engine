"""Market consensus -> expected stat components, per sport.

This is where "Vegas tells us what is likely to happen" becomes numbers. Each
sport adapter knows which prop families exist, how overlapping markets
reconcile (hits/total bases/home runs describe the *same* hit-type
distribution, so they are solved together rather than added), and what can be
inferred from game/team markets when a direct prop is missing.

Nothing here invents a market. A component with no evidence is either derived
from an explicitly-labelled contextual rule or left out, and the omission
lowers the player's coverage grade.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import median
from typing import Mapping

from ..markets.aggregate import MarketConsensus
from ..markets.catalog import BINARY_STATS, CONTINUOUS_CV, dispersion_for
from ..models import GameEnvironment, Player
from ..odds.distributions import (
    BernoulliDistribution,
    ConstantDistribution,
    FittedStat,
    GammaDistribution,
    ProbPoint,
    fit_count,
    fit_gamma,
    make_count,
)


def _points(points) -> list[ProbPoint]:
    return [ProbPoint(line=p.line, prob_over=p.prob_over, weight=max(p.weight, 1e-3))
            for p in points]


def _usable_count_points(points: list[ProbPoint]) -> list[ProbPoint]:
    """Drop integer lines from count markets.

    An integer line can push, so ``P(X > L)`` from a two-way price is not the
    quantity a no-push fit assumes. The NFL process rejects these outright
    rather than silently treating them as half-integer lines.
    """
    return [p for p in points if abs(p.line % 1 - 0.5) < 1e-9]


def _fit_family(stat: str, points: list[ProbPoint], sport: str | None):
    """Fit the distribution family appropriate to ``stat``."""
    if stat in CONTINUOUS_CV:
        return fit_gamma(points, cv=CONTINUOUS_CV[stat])
    counts = _usable_count_points(points) or points
    return fit_count(counts, dispersion=dispersion_for(stat, sport))


def _rebuild_at_mean(stat: str, mean: float, sport: str | None):
    """Rebuild a distribution of the same family at a consensus mean."""
    if stat in CONTINUOUS_CV:
        return GammaDistribution.from_mean_cv(mean, CONTINUOUS_CV[stat])
    return make_count(max(mean, 1e-6), dispersion_for(stat, sport))


def fit_stat(stat: str, cons: MarketConsensus, sport: str | None = None,
             mode: str = "book_median") -> FittedStat:
    """Fit a stat distribution from its de-vigged market state.

    ``mode="book_median"`` follows the documented consensus rule: fit an
    expected value per independent book, then take the median of those fitted
    means. It is robust to one book hanging a different line, which a
    probability-space average is not. ``mode="pooled"`` fits every book's points
    jointly instead, which is preferable when books post partial ladders.
    """
    if stat in BINARY_STATS:
        prob = max(0.001, min(0.999, cons.points[0].prob_over))
        return FittedStat(stat=stat, dist=BernoulliDistribution(p=prob),
                          n_points=len(cons.points), n_books=cons.n_books,
                          sources=sorted(cons.sources))

    pooled = _points(cons.points)
    dist = None
    if mode == "book_median" and len(cons.by_book) >= 2:
        means: list[float] = []
        for book_points in cons.by_book.values():
            book_pts = _points(book_points)
            if stat not in CONTINUOUS_CV:
                book_pts = _usable_count_points(book_pts)
            if not book_pts:
                continue
            try:
                means.append(_fit_family(stat, book_pts, sport).mean)
            except ValueError:
                continue
        if len(means) >= 2:
            dist = _rebuild_at_mean(stat, float(median(means)), sport)
    if dist is None:
        dist = _fit_family(stat, pooled, sport)

    return FittedStat(stat=stat, dist=dist, n_points=len(pooled), n_books=cons.n_books,
                      sources=sorted(cons.sources))


def constant(stat: str, value: float, note: str = "") -> FittedStat:
    return FittedStat(stat=stat, dist=ConstantDistribution(value=max(0.0, value)),
                      inferred=True, sources=[note] if note else [])


def counted(stat: str, mean: float, dispersion: float | None = None,
            note: str = "") -> FittedStat:
    return FittedStat(stat=stat, dist=make_count(max(mean, 1e-6), dispersion),
                      inferred=True, sources=[note] if note else [])


def poisson_rate_from_prob(prob_at_least_one: float) -> float:
    """``P(X >= 1) = p`` under a Poisson count implies ``lambda = -ln(1 - p)``."""
    p = min(max(prob_at_least_one, 1e-6), 0.999)
    return -math.log(1.0 - p)


@dataclass
class ComponentResult:
    components: dict[str, FittedStat] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    direct_markets: int = 0
    inferred_markets: int = 0

    def add(self, fitted: FittedStat) -> None:
        self.components[fitted.stat] = fitted
        if fitted.inferred:
            self.inferred_markets += 1
        else:
            self.direct_markets += 1

    def note(self, msg: str) -> None:
        if msg not in self.notes:
            self.notes.append(msg)

    def mean(self, stat: str, default: float = 0.0) -> float:
        f = self.components.get(stat)
        return f.mean if f is not None else default

    def has(self, *stats: str) -> bool:
        return all(s in self.components for s in stats)


class ComponentBuilder:
    """Per-sport reconciliation of prop markets into scoring components."""

    sport = "base"
    #: within-player dependence used when sampling components together
    correlations: tuple[tuple[str, str, float], ...] = ()

    def build(self, player: Player, cons: Mapping[str, MarketConsensus],
              game: GameEnvironment | None) -> ComponentResult:  # pragma: no cover
        raise NotImplementedError

    def _direct(self, res: ComponentResult, cons: Mapping[str, MarketConsensus],
                *stats: str) -> None:
        for stat in stats:
            c = cons.get(stat)
            if c is not None:
                res.add(fit_stat(stat, c, self.sport))


# --------------------------------------------------------------------------
# NFL / NCAAF
# --------------------------------------------------------------------------


class FootballComponents(ComponentBuilder):
    """NFL / NCAAF components, following the documented pregame process.

    Yardage is Gamma with explicit CVs, counts are Poisson fitted off
    half-integer lines, and an anytime-TD market becomes an expected *count*
    via a Poisson scoring model rather than a single-score probability.

    Kickers and defenses have no per-player props worth speaking of; they are
    built from the game market in ``projections/team_units.py`` once team
    touchdown means exist.
    """

    sport = "nfl"
    correlations = (
        ("pass_yards", "pass_td", 0.52), ("pass_yards", "pass_attempts", 0.55),
        ("pass_yards", "pass_completions", 0.72), ("pass_yards", "interception", 0.05),
        ("rush_yards", "rush_attempts", 0.78), ("rush_yards", "rush_td", 0.45),
        ("rec_yards", "receptions", 0.74), ("rec_yards", "rec_td", 0.50),
        ("receptions", "rec_td", 0.35), ("rush_yards", "rec_yards", 0.10),
    )
    #: Share of a player's anytime-TD mean that is a *receiving* score. These
    #: match projections/reconcile.py so the two stages cannot disagree.
    RECEIVING_TD_SHARE = {"QB": 0.0, "RB": 0.12, "WR": 1.0, "TE": 1.0}
    #: League fumble rates. The skill-position form is a workload proxy.
    SKILL_FUMBLE_RECEPTION_RATE = 0.0035
    SKILL_FUMBLE_RUSH_YARD_RATE = 0.0035 * 0.22
    QB_LOST_FUMBLE_DEFAULT = 0.055
    LEAGUE_INT_RATE = 0.024

    def build(self, player: Player, cons, game):
        pos0 = (player.positions[0] if player.positions else "").upper()
        if player.roster_role in {"dst", "k"} or pos0 in {"DST", "DEF", "D", "K"}:
            # Team units are derived from the game market after the offensive
            # pass; see projections/team_units.py.
            return ComponentResult()

        res = ComponentResult()
        self._direct(res, cons, "pass_yards", "pass_td", "pass_attempts",
                     "pass_completions", "interception", "rush_yards", "rush_attempts",
                     "rush_td", "receptions", "rec_yards", "rec_td")

        pos = pos0 or "WR"
        self._touchdowns(res, cons, pos)

        # A passer with yardage but no TD market: anchor TDs to the team total.
        if res.has("pass_yards") and "pass_td" not in res.components and game:
            team_total = game.team_total(player.team)
            if team_total:
                res.add(counted("pass_td", max(0.4, 0.62 * team_total / 7.0),
                                note="team total -> pass TD"))
                res.note("passing TDs inferred from the implied team total")
        if res.has("pass_attempts") and "interception" not in res.components:
            res.add(counted("interception",
                            self.LEAGUE_INT_RATE * res.mean("pass_attempts"),
                            note="league INT rate x attempts"))

        self._fumbles(res, pos)
        return res

    def _touchdowns(self, res: ComponentResult, cons, pos: str) -> None:
        """Turn an anytime-TD price into an expected rushing/receiving TD count.

        ``P(at least one) = p`` under a Poisson scoring model implies
        ``lambda = -ln(1 - p)``. Using ``6 x p`` instead would cap the player at
        one score and understate multi-TD games.
        """
        atd = cons.get("anytime_td")
        if atd is None or res.has("rush_td", "rec_td"):
            return
        prob = atd.points[0].prob_over
        lam = poisson_rate_from_prob(prob)
        rec_share = self.RECEIVING_TD_SHARE.get(pos, 0.7)
        rush_share = 1.0 - rec_share
        if "rec_td" not in res.components and rec_share > 0:
            res.add(counted("rec_td", lam * rec_share, note="anytime TD x receiving share"))
        if "rush_td" not in res.components and rush_share > 0:
            res.add(counted("rush_td", lam * rush_share, note="anytime TD x rushing share"))
        res.note(f"anytime TD {prob:.0%} -> {lam:.3f} expected scores, "
                 f"{rec_share:.0%} receiving")

    def _fumbles(self, res: ComponentResult, pos: str) -> None:
        if pos == "QB":
            res.add(constant("fumble_lost", self.QB_LOST_FUMBLE_DEFAULT,
                             note="QB lost-fumble default"))
            return
        touches = (self.SKILL_FUMBLE_RECEPTION_RATE * res.mean("receptions")
                   + self.SKILL_FUMBLE_RUSH_YARD_RATE * res.mean("rush_yards"))
        if touches > 0:
            res.add(constant("fumble_lost", touches, note="workload fumble proxy"))


# --------------------------------------------------------------------------
# MLB
# --------------------------------------------------------------------------


class BaseballComponents(ComponentBuilder):
    sport = "mlb"
    correlations = (
        ("hits", "total_bases", 0.80), ("hits", "runs", 0.45), ("hits", "rbi", 0.35),
        ("total_bases", "home_runs", 0.62), ("total_bases", "rbi", 0.55),
        ("total_bases", "runs", 0.50), ("home_runs", "rbi", 0.55),
        ("home_runs", "runs", 0.45), ("walks", "runs", 0.25),
        ("strikeouts", "outs", 0.55), ("earned_runs", "outs", -0.35),
        ("earned_runs", "hits_allowed", 0.55), ("hits_allowed", "outs", -0.20),
        ("win", "outs", 0.30), ("win", "earned_runs", -0.45),
    )
    LEAGUE_TRIPLE_RATE = 0.021  # triples as a share of hits

    def build(self, player: Player, cons, game):
        if player.roster_role == "pitcher" or "P" in player.positions or "SP" in player.positions:
            return self._pitcher(player, cons, game)
        return self._hitter(player, cons, game)

    # -- hitters -----------------------------------------------------------

    def _hitter(self, player: Player, cons, game) -> ComponentResult:
        res = ComponentResult()
        self._direct(res, cons, "hits", "total_bases", "home_runs", "rbi", "runs",
                     "walks", "stolen_bases", "doubles", "triples", "singles")

        # Overlapping hit-type markets describe one distribution: solve, never add.
        hits = res.mean("hits") if res.has("hits") else None
        tb = res.mean("total_bases") if res.has("total_bases") else None
        hr = res.mean("home_runs") if res.has("home_runs") else None
        if hits is None and res.has("hits_runs_rbis"):
            hits = 0.45 * res.mean("hits_runs_rbis")
            res.note("hits inferred from H+R+RBI combo market")
        if hits is not None:
            triples = res.mean("triples") if res.has("triples") else self.LEAGUE_TRIPLE_RATE * hits
            if hr is None:
                hr = 0.11 * hits  # league-typical HR share of hits
                res.note("home runs inferred from league hit-type mix")
            if tb is None:
                tb = hits + 0.32 * hits + 2.0 * hr  # typical extra-base mix
                res.note("total bases inferred from league hit-type mix")
            doubles = res.mean("doubles") if res.has("doubles") else \
                max(0.0, tb - hits - 3.0 * hr - 2.0 * triples)
            singles = max(0.0, hits - hr - triples - doubles)
            for stat, val, disp in (("singles", singles, None), ("doubles", doubles, None),
                                    ("triples", triples, None), ("home_runs", hr, None)):
                if stat not in res.components or stat in {"singles", "doubles", "triples"}:
                    res.components[stat] = counted(stat, val, disp,
                                                   note="hit-type reconciliation")
            res.note("hit types reconciled from hits/total bases/HR")

        if "runs" not in res.components and game:
            tt = game.team_total(player.team)
            if tt:
                res.add(counted("runs", 0.11 * tt, note="team total -> runs"))
        if "rbi" not in res.components and game:
            tt = game.team_total(player.team)
            if tt:
                res.add(counted("rbi", 0.11 * tt, note="team total -> RBI"))
        if "walks" not in res.components:
            res.add(counted("walks", 0.32, note="league walk rate per game"))
        res.add(constant("hbp", 0.012 * 4.2, note="league HBP rate"))
        return res

    # -- pitchers ----------------------------------------------------------

    def _pitcher(self, player: Player, cons, game) -> ComponentResult:
        res = ComponentResult()
        self._direct(res, cons, "strikeouts", "outs", "earned_runs", "hits_allowed",
                     "walks_allowed", "win")

        if "outs" not in res.components:
            res.add(counted("outs", 16.5, dispersion=25.0, note="typical SP workload"))
            res.note("outs not priced; typical starter workload used")
        outs = max(res.mean("outs"), 1.0)
        ip = outs / 3.0

        if "win" not in res.components and game:
            ml = game.home_moneyline if player.team == game.home_team else game.away_moneyline
            if ml is not None:
                from ..odds.conversions import american_to_prob
                team_win = american_to_prob(ml)
                other = game.away_moneyline if player.team == game.home_team else game.home_moneyline
                if other is not None:
                    total = team_win + american_to_prob(other)
                    team_win = team_win / total
                qualify = min(1.0, max(0.0, (ip - 4.0) / 2.0)) * 0.85
                res.add(FittedStat("win", BernoulliDistribution(p=team_win * qualify),
                                   inferred=True, sources=["moneyline x qualify rate"]))
                res.note("pitcher win probability derived from de-vigged moneyline")
        if "earned_runs" not in res.components and game and game.opponent_of(player.team):
            opp_total = game.team_total(game.opponent_of(player.team) or "")
            if opp_total:
                res.add(counted("earned_runs", opp_total * (ip / 9.0) * 0.86, dispersion=3.0,
                                note="opponent implied total -> ER"))
        if "hits_allowed" not in res.components:
            res.add(counted("hits_allowed", 0.95 * ip, dispersion=8.0,
                            note="league hits-per-inning"))
        if "walks_allowed" not in res.components:
            res.add(counted("walks_allowed", 0.32 * ip, note="league walks-per-inning"))
        res.add(constant("hbp_allowed", 0.04 * ip, note="league HBP rate"))
        return res


# --------------------------------------------------------------------------
# NBA
# --------------------------------------------------------------------------


class BasketballComponents(ComponentBuilder):
    sport = "nba"
    correlations = (
        ("points", "threes", 0.45), ("points", "rebounds", 0.18),
        ("points", "assists", 0.22), ("points", "turnovers", 0.28),
        ("rebounds", "blocks", 0.28), ("assists", "turnovers", 0.35),
        ("steals", "blocks", 0.05), ("rebounds", "assists", 0.05),
    )

    def build(self, player: Player, cons, game):
        res = ComponentResult()
        self._direct(res, cons, "points", "rebounds", "assists", "threes",
                     "steals", "blocks", "turnovers")

        # Combo markets fill a missing leg by subtraction.
        combos = (("points_rebounds_assists", ("points", "rebounds", "assists")),
                  ("points_rebounds", ("points", "rebounds")),
                  ("points_assists", ("points", "assists")),
                  ("rebounds_assists", ("rebounds", "assists")))
        for combo, legs in combos:
            c = cons.get(combo)
            if c is None:
                continue
            total = fit_stat(combo, c, self.sport).mean
            missing = [s for s in legs if s not in res.components]
            if len(missing) == 1:
                known = sum(res.mean(s) for s in legs if s != missing[0])
                res.add(counted(missing[0], max(0.0, total - known),
                                dispersion=dispersion_for(missing[0], self.sport),
                                note=f"{combo} minus priced legs"))
                res.note(f"{missing[0]} inferred from {combo}")

        if "turnovers" not in res.components:
            res.add(counted("turnovers", 0.14 * res.mean("points") + 0.22 * res.mean("assists"),
                            dispersion=8.0, note="usage-scaled turnover rate"))
        for stat, coef, base in (("steals", 0.02, 0.35), ("blocks", 0.02, 0.25)):
            if stat not in res.components:
                res.add(counted(stat, base + coef * res.mean("points"),
                                note="role-scaled default"))
        if "threes" not in res.components:
            res.add(counted("threes", 0.09 * res.mean("points"), dispersion=6.0,
                            note="scoring-scaled 3PM default"))
        return res


# --------------------------------------------------------------------------
# NHL
# --------------------------------------------------------------------------


class HockeyComponents(ComponentBuilder):
    sport = "nhl"
    correlations = (
        ("goals", "shots", 0.45), ("goals", "assists", 0.10),
        ("shots", "blocks", -0.10), ("saves", "goals_against", 0.25),
        ("win", "goals_against", -0.55), ("win", "saves", 0.05),
    )

    def build(self, player: Player, cons, game):
        res = ComponentResult()
        is_goalie = player.roster_role == "goalie" or "G" in player.positions
        if is_goalie:
            self._direct(res, cons, "saves", "goals_against", "win")
            if "goals_against" not in res.components and game:
                opp = game.opponent_of(player.team)
                tt = game.team_total(opp or "")
                if tt:
                    res.add(counted("goals_against", tt, dispersion=4.0,
                                    note="opponent implied total"))
            if "saves" not in res.components:
                res.add(counted("saves", 26.0, dispersion=20.0, note="league save volume"))
            if "win" not in res.components and game:
                ml = game.home_moneyline if player.team == game.home_team else game.away_moneyline
                if ml is not None:
                    from ..odds.conversions import american_to_prob
                    res.add(FittedStat("win", BernoulliDistribution(p=american_to_prob(ml)),
                                       inferred=True, sources=["moneyline"]))
            ga = res.mean("goals_against")
            res.add(FittedStat("shutout", BernoulliDistribution(p=math.exp(-max(ga, 0.05))),
                               inferred=True, sources=["Poisson GA -> shutout"]))
            return res

        self._direct(res, cons, "goals", "assists", "shots", "blocks", "power_play_points")
        pts = cons.get("nhl_points")
        if pts is not None and "assists" not in res.components:
            total = fit_stat("nhl_points", pts, self.sport).mean
            res.add(counted("assists", max(0.0, total - res.mean("goals")),
                            note="points minus goals"))
            res.note("assists inferred from points market")
        if "goals" not in res.components and game:
            tt = game.team_total(player.team)
            if tt:
                res.add(counted("goals", 0.16 * tt, note="team total -> goals"))
        if "assists" not in res.components:
            res.add(counted("assists", 1.35 * res.mean("goals"), note="league A:G ratio"))
        if "shots" not in res.components:
            res.add(counted("shots", max(1.0, 8.0 * res.mean("goals")), dispersion=8.0,
                            note="league shooting percentage"))
        if "blocks" not in res.components:
            default = 1.6 if "D" in player.positions else 0.6
            res.add(counted("blocks", default, note="position default"))
        res.add(constant("short_handed_points", 0.03, note="league SH rate"))
        return res


# --------------------------------------------------------------------------
# Tennis
# --------------------------------------------------------------------------


class TennisComponents(ComponentBuilder):
    sport = "tennis"
    correlations = (("match_won", "sets_won", 0.85), ("match_won", "games_won", 0.55),
                    ("aces", "games_won", 0.20))

    def build(self, player: Player, cons, game):
        res = ComponentResult()
        self._direct(res, cons, "aces", "double_faults")
        win_p = None
        if game:
            ml = game.home_moneyline if player.team == game.home_team else game.away_moneyline
            other = game.away_moneyline if player.team == game.home_team else game.home_moneyline
            if ml is not None:
                from ..odds.conversions import american_to_prob, devig
                raw = [american_to_prob(ml)]
                if other is not None:
                    raw.append(american_to_prob(other))
                win_p = devig(raw)[0]
        if win_p is None:
            win_p = 0.5
            res.note("no moneyline available; 50% win probability assumed")
        res.add(FittedStat("match_won", BernoulliDistribution(p=win_p), inferred=True,
                           sources=["de-vigged moneyline"]))
        res.add(constant("match_played", 1.0, note="assumes the match is played"))
        # Expected games/sets scale with win probability (best-of-three).
        total_games = cons.get("total_games")
        exp_games = fit_stat("total_games", total_games, self.sport).mean \
            if total_games else 21.0
        share = 0.5 + 0.22 * (win_p - 0.5) * 2
        res.add(constant("games_won", exp_games * share, note="match length x win share"))
        res.add(constant("games_lost", exp_games * (1 - share), note="match length x win share"))
        res.add(constant("sets_won", 2 * win_p + 0.65 * (1 - win_p), note="best-of-three model"))
        res.add(constant("sets_lost", 0.65 * win_p + 2 * (1 - win_p), note="best-of-three model"))
        res.add(constant("breaks", 2.4 * share, note="break model"))
        if "aces" not in res.components:
            res.add(counted("aces", 6.0, dispersion=8.0, note="tour-average ace rate"))
        if "double_faults" not in res.components:
            res.add(counted("double_faults", 2.6, dispersion=6.0, note="tour-average DF rate"))
        return res


BUILDERS: dict[str, ComponentBuilder] = {
    "nfl": FootballComponents(),
    "ncaaf": FootballComponents(),
    "mlb": BaseballComponents(),
    "nba": BasketballComponents(),
    "nhl": HockeyComponents(),
    "tennis": TennisComponents(),
}


def get_builder(sport: str) -> ComponentBuilder:
    builder = BUILDERS.get(sport.lower())
    if builder is None:
        raise KeyError(f"No component builder for sport {sport!r}")
    return builder
