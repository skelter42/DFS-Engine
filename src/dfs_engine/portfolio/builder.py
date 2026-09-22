"""Select the delivered portfolio from the candidate pool.

Candidate ranking is not portfolio construction. Taking the top N lineups by
any single metric produces a set that wins the same world nine times. The
selection here is greedy on the *marginal* value a lineup adds: new tail worlds
covered, payout added where the portfolio is currently weak, minus the
correlation it brings with what is already in.

This is the mathematical half of the process. ``core/ENGINE.md`` then requires
an explicit strategic review of the result -- which is what the diagnostics and
audit outputs exist to support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from ..models import Contest, Lineup, PlayerProjection, Portfolio
from ..simulation.field import EvaluationResult, LineupSimMetrics


@dataclass
class SelectionConfig:
    #: "marginal_value" ranks by what a lineup adds to the portfolio's tail
    #: coverage; "uniqueness_ladder" is the documented pregame flow (high-
    #: projection pool -> maximise pairwise uniqueness -> recover projection).
    strategy: str = "marginal_value"
    #: uniqueness_ladder: share of the candidate pool retained on projection
    pool_fraction: float = 0.10
    #: uniqueness_ladder: fraction of peak average uniqueness that must survive
    uniqueness_retention: float = 0.90
    n_lineups: int = 20
    tail: float = 0.01
    ev_weight: float = 1.0
    tail_weight: float = 6.0
    marginal_payout_weight: float = 2.0
    correlation_penalty: float = 0.35
    min_uniques: int = 2
    #: soft ceiling on a single player's share of the portfolio; exceeded only
    #: when the evidence keeps saying so (no arbitrary hard caps, per ENGINE.md)
    exposure_soft_cap: float = 0.70
    exposure_penalty: float = 0.6


@dataclass
class SelectionResult:
    lineups: list[Lineup]
    indices: list[int]
    trace: list[dict] = field(default_factory=list)


def select_portfolio(candidates: Sequence[Lineup], evaluation: EvaluationResult,
                     config: SelectionConfig | None = None) -> SelectionResult:
    cfg = config or SelectionConfig()
    if cfg.strategy == "uniqueness_ladder":
        return select_by_uniqueness_ladder(candidates, evaluation, cfg)
    payouts = evaluation.payouts
    beaten = evaluation.beaten_by
    scores = evaluation.scores
    n_c, n_w = payouts.shape
    if n_c == 0:
        return SelectionResult([], [])

    in_tail = beaten <= cfg.tail
    ev = payouts.mean(axis=1)
    norm_scores = _standardise(scores)

    chosen: list[int] = []
    best_payout = np.zeros(n_w, dtype=np.float32)
    covered = np.zeros(n_w, dtype=bool)
    exposure: dict[str, int] = {}
    trace: list[dict] = []

    target = min(cfg.n_lineups, n_c)
    while len(chosen) < target:
        best_gain = -np.inf
        best_i = -1
        best_parts: dict[str, float] = {}
        for i in range(n_c):
            if i in chosen:
                continue
            if not _passes_uniqueness(candidates[i], chosen, candidates, cfg.min_uniques):
                continue
            new_tail = float((in_tail[i] & ~covered).mean())
            marginal_pay = float(np.maximum(payouts[i], best_payout).mean()
                                 - best_payout.mean())
            corr = _max_corr(norm_scores, i, chosen)
            over = _exposure_penalty(candidates[i], exposure, len(chosen) + 1, cfg)
            gain = (cfg.ev_weight * ev[i]
                    + cfg.tail_weight * new_tail * ev.mean()
                    + cfg.marginal_payout_weight * marginal_pay
                    - cfg.correlation_penalty * corr * ev.mean()
                    - over * ev.mean())
            if gain > best_gain:
                best_gain = gain
                best_i = i
                best_parts = {"ev": float(ev[i]), "new_tail_worlds": new_tail,
                              "marginal_payout": marginal_pay, "max_corr": corr,
                              "exposure_penalty": over}
        if best_i < 0:
            break
        chosen.append(best_i)
        best_payout = np.maximum(best_payout, payouts[best_i])
        covered |= in_tail[best_i]
        for p in candidates[best_i].players:
            exposure[p.player_id] = exposure.get(p.player_id, 0) + 1
        trace.append({"pick": len(chosen), "candidate": best_i,
                      "gain": round(float(best_gain), 8), **{
                          k: round(float(v), 6) for k, v in best_parts.items()}})

    lineups = []
    for rank, i in enumerate(chosen, start=1):
        lu = candidates[i]
        lu.index = rank
        lu.metrics.update(evaluation.metrics[i].as_dict())
        lineups.append(lu)
    return SelectionResult(lineups=lineups, indices=chosen, trace=trace)


def select_by_uniqueness_ladder(candidates: Sequence[Lineup],
                                evaluation: EvaluationResult,
                                config: SelectionConfig | None = None
                                ) -> SelectionResult:
    """The documented pregame portfolio flow.

    Retain the high-projection pool, maximise average pairwise uniqueness inside
    it, keep at least ``uniqueness_retention`` of that peak, then recover as much
    projection as that constraint allows. Projections are consumed here, never
    modified -- correlation and exposure preferences belong to lineup
    construction, not to player means.
    """
    cfg = config or SelectionConfig()
    n = min(cfg.n_lineups, len(candidates))
    if n == 0:
        return SelectionResult([], [])

    ranked = sorted(range(len(candidates)), key=lambda i: -candidates[i].projection)
    keep = max(n, int(round(len(candidates) * cfg.pool_fraction)))
    pool = ranked[:min(keep, len(ranked))]

    roster = len(candidates[pool[0]].players)
    uniq = np.zeros((len(pool), len(pool)))
    for a, i in enumerate(pool):
        for b, j in enumerate(pool):
            if a < b:
                value = roster - candidates[i].overlap(candidates[j])
                uniq[a, b] = uniq[b, a] = value

    best_uniqueness = _greedy_uniqueness(uniq, n)
    floor = cfg.uniqueness_retention * best_uniqueness

    # Second pass: take projection wherever the uniqueness floor still holds.
    order = sorted(range(len(pool)), key=lambda a: -candidates[pool[a]].projection)
    chosen: list[int] = []
    for a in order:
        if len(chosen) >= n:
            break
        trial = chosen + [a]
        if len(trial) < 2 or _average_uniqueness(uniq, trial) >= floor:
            chosen = trial
    for a in order:                      # top up if the floor was too tight
        if len(chosen) >= n:
            break
        if a not in chosen:
            chosen.append(a)

    indices = [pool[a] for a in chosen]
    lineups = []
    trace = []
    for rank, i in enumerate(indices, start=1):
        lu = candidates[i]
        lu.index = rank
        lu.metrics.update(evaluation.metrics[i].as_dict())
        lineups.append(lu)
        trace.append({"pick": rank, "candidate": i,
                      "projection": round(lu.projection, 3)})
    achieved = _average_uniqueness(uniq, chosen) if len(chosen) > 1 else 0.0
    trace.append({"strategy": "uniqueness_ladder",
                  "pool_size": len(pool),
                  "peak_average_uniqueness": round(best_uniqueness, 3),
                  "achieved_average_uniqueness": round(achieved, 3),
                  "retention": round(achieved / best_uniqueness, 3)
                  if best_uniqueness else None})
    return SelectionResult(lineups=lineups, indices=indices, trace=trace)


def _average_uniqueness(uniq: np.ndarray, members: Sequence[int]) -> float:
    if len(members) < 2:
        return 0.0
    idx = np.array(members)
    sub = uniq[np.ix_(idx, idx)]
    pairs = len(members) * (len(members) - 1) / 2
    return float(sub.sum() / 2.0 / pairs)


def _greedy_uniqueness(uniq: np.ndarray, n: int) -> float:
    """Greedy estimate of the most mutually-different set of ``n`` lineups."""
    size = uniq.shape[0]
    if size <= 1 or n <= 1:
        return 0.0
    a, b = np.unravel_index(int(np.argmax(uniq)), uniq.shape)
    chosen = [int(a), int(b)]
    while len(chosen) < min(n, size):
        remaining = [i for i in range(size) if i not in chosen]
        if not remaining:
            break
        best = max(remaining, key=lambda i: float(uniq[i, chosen].sum()))
        chosen.append(best)
    return _average_uniqueness(uniq, chosen)


def _standardise(scores: np.ndarray) -> np.ndarray:
    mean = scores.mean(axis=1, keepdims=True)
    sd = scores.std(axis=1, keepdims=True)
    return (scores - mean) / np.maximum(sd, 1e-6)


def _max_corr(norm_scores: np.ndarray, i: int, chosen: Sequence[int]) -> float:
    if not chosen:
        return 0.0
    n_w = norm_scores.shape[1]
    corrs = norm_scores[list(chosen)] @ norm_scores[i] / n_w
    return float(np.max(corrs))


def _passes_uniqueness(candidate: Lineup, chosen: Sequence[int],
                       pool: Sequence[Lineup], min_uniques: int) -> bool:
    if min_uniques <= 0:
        return True
    limit = len(candidate.players) - min_uniques
    return all(candidate.overlap(pool[j]) <= limit for j in chosen)


def _exposure_penalty(candidate: Lineup, exposure: Mapping[str, int], n_total: int,
                      cfg: SelectionConfig) -> float:
    penalty = 0.0
    for p in candidate.players:
        share = (exposure.get(p.player_id, 0) + 1) / max(n_total, 1)
        if share > cfg.exposure_soft_cap:
            penalty += cfg.exposure_penalty * (share - cfg.exposure_soft_cap)
    return penalty


# --------------------------------------------------------------------------
# Script labelling
# --------------------------------------------------------------------------


def label_lineups(lineups: Sequence[Lineup], projections: Mapping[str, PlayerProjection],
                  ownership: Mapping[str, float],
                  metrics: Sequence[LineupSimMetrics] | None = None) -> None:
    """Tag each lineup with the script family, anchor and risk tier it expresses.

    Multi-contest allocation is only meaningful once lineups carry these labels
    (``core/ENGINE.md``): a contest needs a spread of *stories*, not a spread of
    projection ranks.
    """
    if not lineups:
        return
    own_totals = []
    ceilings = []
    for lu in lineups:
        own_totals.append(sum(ownership.get(p.player_id, 0.0) for p in lu.players))
        ceilings.append(sum(projections[p.player_id].ceiling
                            for p in lu.players if p.player_id in projections))
    own_arr = np.array(own_totals)
    ceil_arr = np.array(ceilings)
    own_med = float(np.median(own_arr)) if len(own_arr) else 0.0
    ceil_med = float(np.median(ceil_arr)) if len(ceil_arr) else 0.0

    for i, lu in enumerate(lineups):
        teams = lu.team_counts()
        games = lu.game_counts()
        anchor_team = max(teams.items(), key=lambda kv: (kv[1], kv[0]))[0] if teams else "?"
        anchor_game = max(games.items(), key=lambda kv: (kv[1], kv[0]))[0] if games else "?"
        stack_size = max(teams.values()) if teams else 0
        if own_arr[i] >= own_med * 1.12:
            risk = "chalk-leaning"
        elif own_arr[i] <= own_med * 0.88:
            risk = "leverage"
        else:
            risk = "balanced"
        ceiling_tier = "high-ceiling" if ceil_arr[i] >= ceil_med else "stable"
        lu.labels.update({
            "anchor_team": anchor_team,
            "anchor_game": anchor_game,
            "stack": f"{anchor_team} x{stack_size}",
            "risk": risk,
            "ceiling_tier": ceiling_tier,
            "script": f"{anchor_game}|{anchor_team}x{stack_size}|{risk}",
            "family": f"{anchor_game}:{risk}",
        })
        lu.metrics.setdefault("total_ownership", float(own_arr[i]))
        lu.metrics.setdefault("ceiling_sum", float(ceil_arr[i]))
        if metrics is not None and i < len(metrics):
            lu.metrics.update(metrics[i].as_dict())


def build_portfolio(lineups: Sequence[Lineup], contests: Sequence[Contest]) -> Portfolio:
    return Portfolio(lineups=list(lineups), contests=list(contests))
