"""Synthetic slates for demos, tests, and CI.

EVERYTHING THIS MODULE PRODUCES IS FAKE. It is a generator of *plausibly
shaped* player pools and sportsbook quotes so the pipeline can be exercised,
benchmarked, and regression-tested without a live sweep or a paid API key. It
is never a substitute for real market data, and the engine labels any build
made from it as synthetic.

The generator works the way the real world does -- it picks latent "true"
player rates, then posts lines around them at several books with realistic
juice and cross-book noise -- so fitting the props back into projections is a
genuine test of the odds math rather than a lookup.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from ..models import GameEnvironment, MarketSnapshot, Player, PropMarket, normalize_name
from ..odds.conversions import BookQuote, prob_to_american

SYNTHETIC_BOOKS = ("draftkings", "fanduel", "betmgm", "caesars", "espnbet")

NFL_TEAMS = ["KC", "BUF", "PHI", "DAL", "SF", "DET", "BAL", "MIA",
             "CIN", "GB", "HOU", "LAR"]
MLB_TEAMS = ["LAD", "ATL", "NYY", "HOU", "BAL", "PHI", "SD", "TEX",
             "MIN", "SEA", "CHC", "BOS"]

FIRST = ["Avery", "Brooks", "Carter", "Dax", "Elliot", "Foster", "Gideon", "Hayes",
         "Isaiah", "Jonah", "Kai", "Lennox", "Micah", "Nash", "Owen", "Preston",
         "Quinn", "Reece", "Silas", "Tobias", "Uriah", "Vance", "Wilder", "Xavier",
         "Yusuf", "Zane", "Ander", "Bexley", "Colt", "Dorian"]
LAST = ["Abbott", "Beckham", "Calloway", "Dunphy", "Easton", "Fairchild", "Granger",
        "Holloway", "Ibarra", "Jennings", "Kingsley", "Lachance", "Marbury", "Northrup",
        "Okafor", "Pemberton", "Quintero", "Ridgeway", "Stapleton", "Thorne", "Ulrich",
        "Vandermeer", "Whitlock", "Yarborough", "Zimmerman", "Ashford", "Brennan",
        "Castellan", "Delacroix", "Ellsworth"]


def _name(rng: np.random.Generator, used: set[str]) -> str:
    for _ in range(200):
        nm = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        if nm not in used:
            used.add(nm)
            return nm
    nm = f"{rng.choice(FIRST)} {rng.choice(LAST)} {len(used)}"
    used.add(nm)
    return nm


@dataclass
class SyntheticSlate:
    sport: str
    players: list[Player]
    snapshot: MarketSnapshot
    truth: dict[str, dict[str, float]]  # player_id -> latent true component means

    @property
    def synthetic(self) -> bool:
        return True


# --------------------------------------------------------------------------
# Quote posting
# --------------------------------------------------------------------------


def _post_count_market(snap: MarketSnapshot, name: str, stat: str, mean: float,
                       rng: np.random.Generator, team: str, game_id: str,
                       dispersion: float | None = None, n_books: int = 4,
                       ladder: int = 0, hold: float = 0.045) -> None:
    """Post over/under quotes around a latent Poisson/NB mean."""
    from ..odds.distributions import make_count

    dist = make_count(mean, dispersion)
    lines = [_natural_line(mean)]
    for step in range(1, ladder + 1):
        lines.extend([lines[0] + step, lines[0] - step])
    books = list(SYNTHETIC_BOOKS[:max(1, min(n_books, len(SYNTHETIC_BOOKS)))])
    for line in sorted({round(l, 1) for l in lines if l > 0}):
        true_p = dist.sf(line)
        if not 0.04 < true_p < 0.96:
            continue
        quotes = []
        for book in books:
            p = float(np.clip(true_p + rng.normal(0, 0.012), 0.02, 0.98))
            over = prob_to_american(min(0.97, p * (1 + hold / 2)))
            under = prob_to_american(min(0.97, (1 - p) * (1 + hold / 2)))
            quotes.append(BookQuote(book=book, line=line, over=round(over),
                                    under=round(under)))
        snap.add_prop(PropMarket(player_key=normalize_name(name), player_name=name,
                                 stat=stat, quotes=quotes, sources={"synthetic"},
                                 team=team, game_id=game_id))


def _post_continuous_market(snap: MarketSnapshot, name: str, stat: str, mean: float,
                            cv: float, rng: np.random.Generator, team: str, game_id: str,
                            n_books: int = 4, ladder: int = 0, hold: float = 0.045) -> None:
    sigma = math.sqrt(math.log(1 + cv * cv))
    mu = math.log(max(mean, 1e-3)) - 0.5 * sigma ** 2
    from ..odds.distributions import LognormalDistribution

    dist = LognormalDistribution(mu=mu, sigma=sigma)
    base = round(mean * 2) / 2 - 0.5
    lines = [base] + [base + 5 * s for s in range(1, ladder + 1)] + \
            [base - 5 * s for s in range(1, ladder + 1)]
    books = list(SYNTHETIC_BOOKS[:max(1, min(n_books, len(SYNTHETIC_BOOKS)))])
    for line in sorted({round(l, 1) for l in lines if l > 0}):
        true_p = dist.sf(line)
        if not 0.05 < true_p < 0.95:
            continue
        quotes = []
        for book in books:
            p = float(np.clip(true_p + rng.normal(0, 0.012), 0.02, 0.98))
            quotes.append(BookQuote(book=book, line=line,
                                    over=round(prob_to_american(min(0.97, p * (1 + hold / 2)))),
                                    under=round(prob_to_american(min(0.97, (1 - p) * (1 + hold / 2))))))
        snap.add_prop(PropMarket(player_key=normalize_name(name), player_name=name,
                                 stat=stat, quotes=quotes, sources={"synthetic"},
                                 team=team, game_id=game_id))


def _post_binary_market(snap: MarketSnapshot, name: str, stat: str, prob: float,
                        rng: np.random.Generator, team: str, game_id: str,
                        n_books: int = 4, hold: float = 0.06) -> None:
    quotes = []
    for book in SYNTHETIC_BOOKS[:n_books]:
        p = float(np.clip(prob + rng.normal(0, 0.015), 0.02, 0.95))
        quotes.append(BookQuote(book=book, line=0.5,
                                over=round(prob_to_american(min(0.95, p * (1 + hold / 2)))),
                                under=round(prob_to_american(min(0.97, (1 - p) * (1 + hold / 2))))))
    snap.add_prop(PropMarket(player_key=normalize_name(name), player_name=name, stat=stat,
                             quotes=quotes, sources={"synthetic"}, team=team, game_id=game_id))


def _natural_line(mean: float) -> float:
    return max(0.5, round(mean - 0.5) + 0.5)


# --------------------------------------------------------------------------
# NFL
# --------------------------------------------------------------------------

NFL_ROSTER = (
    ("QB", 1), ("RB", 3), ("WR", 5), ("TE", 2), ("DST", 1),
)


def build_nfl_slate(seed: int = 7, n_games: int = 6, coverage: float = 0.82) -> SyntheticSlate:
    rng = np.random.default_rng(seed)
    snap = MarketSnapshot(sport="nfl", sources=["synthetic"])
    players: list[Player] = []
    truth: dict[str, dict[str, float]] = {}
    used: set[str] = set()
    teams = NFL_TEAMS[: n_games * 2]

    for g in range(n_games):
        away, home = teams[2 * g], teams[2 * g + 1]
        total = float(np.round(rng.normal(45.5, 4.5) * 2) / 2)
        spread = float(np.round(rng.normal(0, 5.0) * 2) / 2)
        game = GameEnvironment(
            game_id=f"NFL-G{g+1}", home_team=home, away_team=away,
            total=total, spread_home=spread, source="synthetic",
            home_moneyline=round(_spread_to_ml(spread)),
            away_moneyline=round(_spread_to_ml(-spread)),
        )
        snap.games.append(game)

        for team in (away, home):
            tt = game.team_total(team) or total / 2
            pass_share = float(np.clip(rng.normal(0.60, 0.05), 0.45, 0.72))
            team_plays = float(np.clip(rng.normal(63, 4), 54, 72))
            _build_nfl_team(snap, players, truth, rng, team, game, tt, pass_share,
                            team_plays, used, coverage)
    return SyntheticSlate("nfl", players, snap, truth)


def _spread_to_ml(spread_home: float) -> float:
    p = 1.0 / (1.0 + math.exp(spread_home / 3.6))
    p = min(max(p, 0.05), 0.95)
    return prob_to_american(p * 1.02)


def _build_nfl_team(snap, players, truth, rng, team, game, team_total, pass_share,
                    plays, used, coverage) -> None:
    pass_att = plays * pass_share
    rush_att = plays * (1 - pass_share)
    target_shares = _dirichlet(rng, [0.22, 0.17, 0.13, 0.08, 0.05, 0.14, 0.06, 0.06, 0.05, 0.04])
    rush_shares = _dirichlet(rng, [0.55, 0.28, 0.12, 0.05])
    idx = 0
    skill: list[tuple[Player, dict]] = []

    for pos, count in NFL_ROSTER:
        for i in range(count):
            name = _name(rng, used)
            pid = f"NFL-{team}-{pos}{i+1}"
            comps: dict[str, float] = {}
            if pos == "QB":
                ypa = float(np.clip(rng.normal(7.1, 0.7), 5.6, 8.8))
                comps = {
                    "pass_attempts": pass_att,
                    "pass_completions": pass_att * float(np.clip(rng.normal(0.65, 0.04), 0.55, 0.74)),
                    "pass_yards": pass_att * ypa,
                    "pass_td": max(0.4, team_total * 0.085),
                    "interception": 0.024 * pass_att,
                    "rush_attempts": float(np.clip(rng.normal(4.0, 2.5), 0.5, 11)),
                }
                comps["rush_yards"] = comps["rush_attempts"] * float(np.clip(rng.normal(4.4, 1.2), 1.5, 7.5))
                comps["rush_td"] = 0.035 * comps["rush_attempts"] + 0.06
                salary = int(np.clip(4800 + comps["pass_yards"] * 8 + comps["rush_yards"] * 12, 4600, 9000) // 100 * 100)
            elif pos in {"RB", "WR", "TE"}:
                t_idx = {"RB": 0, "WR": 3, "TE": 8}[pos] + i
                tshare = target_shares[min(t_idx, len(target_shares) - 1)]
                targets = pass_att * tshare
                catch = 0.72 if pos == "RB" else (0.64 if pos == "WR" else 0.70)
                ypr = 7.6 if pos == "RB" else (12.9 if pos == "WR" else 10.8)
                comps = {
                    "receptions": targets * catch,
                    "rec_yards": targets * catch * float(np.clip(rng.normal(ypr, 1.6), 4, 19)),
                }
                comps["rec_td"] = 0.055 * comps["receptions"] * (team_total / 23.0)
                if pos == "RB":
                    share = rush_shares[min(i, len(rush_shares) - 1)]
                    comps["rush_attempts"] = rush_att * share
                    comps["rush_yards"] = comps["rush_attempts"] * float(np.clip(rng.normal(4.4, 0.8), 2.6, 6.4))
                    comps["rush_td"] = comps["rush_attempts"] * 0.035 * (team_total / 23.0)
                salary = int(np.clip(3000 + comps.get("rec_yards", 0) * 22 +
                                     comps.get("rush_yards", 0) * 26 +
                                     comps["receptions"] * 180, 3000, 9200) // 100 * 100)
            else:  # DST
                comps = {}
                salary = int(np.clip(4400 - (team_total - 23) * 120, 2200, 4200) // 100 * 100)

            player = Player(
                player_id=pid, name=name, dfs_id=pid, team=team,
                positions=(pos,), salary=salary, sport="nfl", site="dk",
                opponent=game.opponent_of(team), game_id=game.game_id,
                home=(team == game.home_team),
                vendor_projection=None, vendor_ownership=None,
            )
            players.append(player)
            truth[pid] = comps
            if comps:
                skill.append((player, comps))
            idx += 1

    # Keep the synthetic slate internally coherent: a team's receiving
    # touchdowns should sum to its quarterback's passing touchdowns, the same
    # identity the reconciliation stage enforces on real markets.
    qb_comps = next((c for _, c in skill if "pass_td" in c), None)
    if qb_comps is not None:
        receivers = [(pl, c) for pl, c in skill if c.get("receptions", 0) > 0]
        raw_rec_td = sum(c["rec_td"] for _, c in receivers)
        if raw_rec_td > 0:
            scale = qb_comps["pass_td"] / raw_rec_td
            for _, c in receivers:
                c["rec_td"] *= scale

    for player, comps in skill:
        if rng.random() > coverage:
            continue  # some players genuinely have no posted market
        n_books = int(rng.integers(3, 6))
        if "pass_yards" in comps:
            _post_continuous_market(snap, player.name, "pass_yards", comps["pass_yards"],
                                    0.30, rng, player.team, game.game_id, n_books, ladder=2)
            _post_count_market(snap, player.name, "pass_td", comps["pass_td"], rng,
                               player.team, game.game_id, None, n_books, ladder=1)
            _post_count_market(snap, player.name, "pass_attempts", comps["pass_attempts"],
                               rng, player.team, game.game_id, 40.0, n_books)
            _post_count_market(snap, player.name, "interception", comps["interception"],
                               rng, player.team, game.game_id, None, n_books)
        if comps.get("receptions", 0) > 0.6:
            _post_count_market(snap, player.name, "receptions", comps["receptions"], rng,
                               player.team, game.game_id, None, n_books, ladder=1)
            _post_continuous_market(snap, player.name, "rec_yards", comps["rec_yards"],
                                    0.65, rng, player.team, game.game_id, n_books, ladder=1)
        if comps.get("rush_attempts", 0) > 2:
            _post_count_market(snap, player.name, "rush_attempts", comps["rush_attempts"],
                               rng, player.team, game.game_id, 20.0, n_books)
            _post_continuous_market(snap, player.name, "rush_yards", comps["rush_yards"],
                                    0.55, rng, player.team, game.game_id, n_books, ladder=1)
        td_rate = comps.get("rush_td", 0) + comps.get("rec_td", 0)
        if td_rate > 0.03 and "pass_yards" not in comps:
            _post_binary_market(snap, player.name, "anytime_td", 1 - math.exp(-td_rate),
                                rng, player.team, game.game_id, n_books)


def _dirichlet(rng: np.random.Generator, alphas: Sequence[float]) -> list[float]:
    draw = rng.dirichlet(np.array(alphas) * 30)
    return [float(x) for x in draw]


# --------------------------------------------------------------------------
# MLB
# --------------------------------------------------------------------------


def build_mlb_slate(seed: int = 11, n_games: int = 6, coverage: float = 0.85) -> SyntheticSlate:
    rng = np.random.default_rng(seed)
    snap = MarketSnapshot(sport="mlb", sources=["synthetic"])
    players: list[Player] = []
    truth: dict[str, dict[str, float]] = {}
    used: set[str] = set()
    teams = MLB_TEAMS[: n_games * 2]
    lineup_slots = ["OF", "1B", "SS", "3B", "OF", "2B", "C", "OF", "1B"]

    for g in range(n_games):
        away, home = teams[2 * g], teams[2 * g + 1]
        total = float(np.round(rng.normal(8.6, 1.3) * 2) / 2)
        spread = float(np.round(rng.normal(0, 0.8) * 2) / 2)
        game = GameEnvironment(
            game_id=f"MLB-G{g+1}", home_team=home, away_team=away, total=total,
            spread_home=spread, source="synthetic",
            home_moneyline=round(_spread_to_ml(spread * 3)),
            away_moneyline=round(_spread_to_ml(-spread * 3)),
        )
        snap.games.append(game)

        for team in (away, home):
            tt = game.team_total(team) or total / 2
            # Starting pitcher
            name = _name(rng, used)
            pid = f"MLB-{team}-SP"
            opp_tt = game.team_total(game.opponent_of(team) or "") or total / 2
            outs = float(np.clip(rng.normal(17.5, 2.5), 11, 22))
            k9 = float(np.clip(rng.normal(9.2, 2.0), 5.0, 13.5))
            comps = {
                "outs": outs,
                "strikeouts": outs / 3.0 * k9 / 9.0,
                "earned_runs": opp_tt * (outs / 27.0) * 0.86,
                "hits_allowed": 0.95 * outs / 3.0,
                "walks_allowed": 0.3 * outs / 3.0,
            }
            sal = int(np.clip(5000 + comps["strikeouts"] * 700 - comps["earned_runs"] * 300,
                              5000, 11500) // 100 * 100)
            p = Player(player_id=pid, name=name, dfs_id=pid, team=team, positions=("P",),
                       salary=sal, sport="mlb", site="dk", roster_role="pitcher",
                       opponent=game.opponent_of(team), game_id=game.game_id,
                       home=(team == game.home_team))
            players.append(p)
            truth[pid] = comps
            if rng.random() < coverage:
                nb = int(rng.integers(3, 6))
                _post_count_market(snap, name, "strikeouts", comps["strikeouts"], rng, team,
                                   game.game_id, 12.0, nb, ladder=2)
                _post_count_market(snap, name, "outs", comps["outs"], rng, team,
                                   game.game_id, 25.0, nb, ladder=1)
                _post_count_market(snap, name, "earned_runs", comps["earned_runs"], rng, team,
                                   game.game_id, 3.0, nb, ladder=1)
                _post_count_market(snap, name, "hits_allowed", comps["hits_allowed"], rng,
                                   team, game.game_id, 8.0, nb)

            # Lineup
            for order, pos in enumerate(lineup_slots, start=1):
                name = _name(rng, used)
                pid = f"MLB-{team}-B{order}"
                pa = 4.6 - 0.11 * (order - 1)
                obp = float(np.clip(rng.normal(0.325, 0.035), 0.24, 0.42))
                iso = float(np.clip(rng.normal(0.170, 0.055), 0.06, 0.32))
                hits = pa * float(np.clip(obp - 0.075, 0.14, 0.33))
                hr = pa * iso * 0.22
                comps = {
                    "hits": hits,
                    "home_runs": hr,
                    "total_bases": hits + 0.30 * hits + 2.2 * hr,
                    "runs": tt * (0.135 - 0.006 * (order - 1)),
                    "rbi": tt * (0.105 + 0.004 * (order - 1)),
                    "walks": pa * float(np.clip(obp - 0.245, 0.03, 0.16)),
                    "stolen_bases": float(np.clip(rng.gamma(1.2, 0.06), 0, 0.5)),
                }
                sal = int(np.clip(1900 + (comps["total_bases"] - 1.2) * 2400
                                  + comps["runs"] * 1400, 2000, 6600) // 100 * 100)
                pl = Player(player_id=pid, name=name, dfs_id=pid, team=team,
                            positions=(pos,), salary=sal, sport="mlb", site="dk",
                            roster_role="hitter", opponent=game.opponent_of(team),
                            game_id=game.game_id, home=(team == game.home_team),
                            batting_order=order)
                players.append(pl)
                truth[pid] = comps
                if rng.random() < coverage:
                    nb = int(rng.integers(3, 6))
                    _post_count_market(snap, name, "hits", comps["hits"], rng, team,
                                       game.game_id, None, nb, ladder=1)
                    _post_count_market(snap, name, "total_bases", comps["total_bases"], rng,
                                       team, game.game_id, 3.0, nb, ladder=1)
                    _post_binary_market(snap, name, "home_runs", 1 - math.exp(-comps["home_runs"]),
                                        rng, team, game.game_id, nb)
                    _post_count_market(snap, name, "runs", comps["runs"], rng, team,
                                       game.game_id, None, nb)
                    _post_count_market(snap, name, "rbi", comps["rbi"], rng, team,
                                       game.game_id, 2.0, nb)
    return SyntheticSlate("mlb", players, snap, truth)


BUILDERS = {"nfl": build_nfl_slate, "mlb": build_mlb_slate}


def build_demo_slate(sport: str = "nfl", **kwargs) -> SyntheticSlate:
    fn = BUILDERS.get(sport.lower())
    if fn is None:
        raise KeyError(f"No synthetic slate generator for {sport!r}; have {sorted(BUILDERS)}")
    return fn(**kwargs)
