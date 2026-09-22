"""Portfolio-level simulation metrics.

A set of lineups is not the sum of its lineups. Nine differently-spelled
rosters can all be betting on the same underlying world, and
``core/SIMULATION.md`` asks specifically for that failure to be measured:
aggregate first-place equity, the frequency at least one lineup reaches the
tail, overlap between lineups' *winning worlds*, and hidden concentration by
latent outcome rather than by player name.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Mapping, Sequence

import numpy as np

from ..models import Lineup
from .field import EvaluationResult


@dataclass
class PortfolioMetrics:
    n_lineups: int
    total_expected_payout: float
    any_top1_rate: float
    any_top01_rate: float
    any_first_proxy: float
    best_rank_mean_percentile: float
    world_overlap: float          # mean pairwise correlation of lineup scores
    winning_world_overlap: float  # share of tail worlds won by more than one lineup
    effective_lineups: float      # diversity-adjusted count
    concentration: dict[str, float] = dc_field(default_factory=dict)
    notes: list[str] = dc_field(default_factory=list)

    def as_dict(self) -> dict:
        out = {k: v for k, v in self.__dict__.items()}
        for k, v in list(out.items()):
            if isinstance(v, float):
                out[k] = round(v, 6)
        return out


def portfolio_metrics(evaluation: EvaluationResult, lineups: Sequence[Lineup],
                      tail: float = 0.01) -> PortfolioMetrics:
    beaten = evaluation.beaten_by
    scores = evaluation.scores
    payouts = evaluation.payouts
    n_l, n_w = beaten.shape
    if n_l == 0:
        return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)

    in_tail = beaten <= tail
    in_deep = beaten <= max(tail / 10.0, 1e-4)
    any_tail = in_tail.any(axis=0)
    any_deep = in_deep.any(axis=0)
    best_pct = 1.0 - beaten.min(axis=0)

    corr = _mean_pairwise_corr(scores)
    multi_win = in_tail.sum(axis=0)
    overlap = float((multi_win[any_tail] > 1).mean()) if any_tail.any() else 0.0

    # Effective lineup count: how many *independent* shots the portfolio really
    # has. Perfectly correlated lineups collapse toward 1.
    eff = n_l / (1.0 + (n_l - 1) * max(corr, 0.0)) if n_l > 1 else 1.0

    return PortfolioMetrics(
        n_lineups=n_l,
        total_expected_payout=float(payouts.sum(axis=0).mean()),
        any_top1_rate=float(any_tail.mean()),
        any_top01_rate=float(any_deep.mean()),
        any_first_proxy=float(np.mean([m.first_place_proxy for m in evaluation.metrics])) * n_l,
        best_rank_mean_percentile=float(100.0 * best_pct.mean()),
        world_overlap=float(corr),
        winning_world_overlap=overlap,
        effective_lineups=float(eff),
        concentration=concentration_report(lineups),
    )


def _mean_pairwise_corr(scores: np.ndarray) -> float:
    n = scores.shape[0]
    if n < 2:
        return 0.0
    mat = np.corrcoef(scores)
    iu = np.triu_indices(n, k=1)
    vals = mat[iu]
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return 0.0
    return float(vals.mean())


def concentration_report(lineups: Sequence[Lineup]) -> dict[str, float]:
    """Herfindahl indices over players, teams and games. 1.0 == one story only."""
    def hhi(counts: Mapping[str, int]) -> float:
        total = sum(counts.values())
        if total <= 0:
            return 0.0
        return float(sum((c / total) ** 2 for c in counts.values()))

    players: dict[str, int] = {}
    teams: dict[str, int] = {}
    games: dict[str, int] = {}
    for lu in lineups:
        for p in lu.players:
            players[p.player_id] = players.get(p.player_id, 0) + 1
            teams[p.team] = teams.get(p.team, 0) + 1
            gid = p.game_id or f"g:{p.team}"
            games[gid] = games.get(gid, 0) + 1
    return {
        "player_hhi": round(hhi(players), 4),
        "team_hhi": round(hhi(teams), 4),
        "game_hhi": round(hhi(games), 4),
        "distinct_players": float(len(players)),
        "distinct_teams": float(len(teams)),
        "distinct_games": float(len(games)),
    }


def hidden_world_concentration(evaluation: EvaluationResult, lineups: Sequence[Lineup],
                               tail: float = 0.01, top_n: int = 6) -> dict:
    """Which teams/games actually carry the portfolio in the worlds where it wins.

    This is the check that catches a portfolio of visually different lineups
    all depending on the same script.
    """
    beaten = evaluation.beaten_by
    in_tail = beaten <= tail
    n_l, n_w = beaten.shape
    team_hits: dict[str, int] = {}
    game_hits: dict[str, int] = {}
    tail_worlds = int(in_tail.any(axis=0).sum())
    for i in range(n_l):
        hits = int(in_tail[i].sum())
        if hits == 0:
            continue
        for p in lineups[i].players:
            team_hits[p.team] = team_hits.get(p.team, 0) + hits
            gid = p.game_id or f"g:{p.team}"
            game_hits[gid] = game_hits.get(gid, 0) + hits
    total_team = max(sum(team_hits.values()), 1)
    total_game = max(sum(game_hits.values()), 1)
    return {
        "tail_worlds": tail_worlds,
        "tail_world_pct": round(100.0 * tail_worlds / max(n_w, 1), 2),
        "top_teams": [
            {"team": t, "share_pct": round(100.0 * c / total_team, 1)}
            for t, c in sorted(team_hits.items(), key=lambda kv: -kv[1])[:top_n]
        ],
        "top_games": [
            {"game": g, "share_pct": round(100.0 * c / total_game, 1)}
            for g, c in sorted(game_hits.items(), key=lambda kv: -kv[1])[:top_n]
        ],
    }


def marginal_values(evaluation: EvaluationResult) -> list[float]:
    """Each lineup's marginal contribution to the portfolio's best-world payout."""
    payouts = evaluation.payouts
    n_l = payouts.shape[0]
    if n_l == 0:
        return []
    best = payouts.max(axis=0)
    out = []
    for i in range(n_l):
        others = np.delete(payouts, i, axis=0)
        without = others.max(axis=0) if others.shape[0] else np.zeros_like(best)
        out.append(float((best - without).mean()))
    return out


def champion_challenger(champion: EvaluationResult, challenger: EvaluationResult,
                        champion_lineups: Sequence[Lineup],
                        challenger_lineups: Sequence[Lineup]) -> dict:
    """The gate from ``core/ENGINE.md``: a rebuild must earn its replacement.

    Returns the side-by-side comparison plus a verdict. The challenger wins only
    with a documented portfolio-level reason -- more tail equity or better
    risk-adjusted contest fit -- not merely because it used engine numbers.
    """
    champ = portfolio_metrics(champion, champion_lineups)
    chal = portfolio_metrics(challenger, challenger_lineups)

    tail_gain = chal.any_top1_rate - champ.any_top1_rate
    deep_gain = chal.any_top01_rate - champ.any_top01_rate
    ev_gain = chal.total_expected_payout - champ.total_expected_payout
    concentration_added = (chal.concentration.get("team_hhi", 0)
                           - champ.concentration.get("team_hhi", 0))
    diversity_lost = champ.effective_lineups - chal.effective_lineups

    reasons: list[str] = []
    if tail_gain > 0:
        reasons.append(f"top-1% rate +{tail_gain:.2%}")
    if deep_gain > 0:
        reasons.append(f"top-0.1% rate +{deep_gain:.3%}")
    if ev_gain > 0:
        reasons.append(f"expected payout +{ev_gain:.5f} of pool")
    blockers: list[str] = []
    if concentration_added > 0.03:
        blockers.append(f"team concentration +{concentration_added:.3f} HHI")
    if diversity_lost > 0.5:
        blockers.append(f"effective lineups {champ.effective_lineups:.1f} -> "
                        f"{chal.effective_lineups:.1f}")

    improves = (deep_gain > 0 or tail_gain > 0 or ev_gain > 0)
    verdict = "replace" if improves and not blockers else (
        "blend" if improves else "retain_champion")
    return {
        "champion": champ.as_dict(),
        "challenger": chal.as_dict(),
        "verdict": verdict,
        "reasons": reasons,
        "blockers": blockers,
    }
