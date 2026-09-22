"""Opposing-field model: who else is in the contest, and did we beat them.

Absolute fantasy score does not pay. Finish position does, so the engine
builds a synthetic field from the expected ownership estimates (the same ones
the ownership layer produced -- ``core/SIMULATION_IMPLEMENTATION.md`` forbids a
second, private ownership model) and ranks candidate lineups inside each
simulated world.

Field entries are sampled ownership-weighted, slot by slot, with the stacking
behaviour real entrants show. A sampled field is a *sample*: results are scaled
to the contest's true entry count, and duplication is reported so a lineup that
splits first place with 40 copies of itself is not mistaken for a winner.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Mapping, Sequence

import numpy as np

from ..models import Contest, PlayerProjection
from ..optimize.rules import RosterRules
from .core import SlateSimulation


@dataclass
class FieldConfig:
    n_entries: int = 3000       # sampled field size (a sample of the real field)
    stack_rate: float = 0.55    # share of entries that deliberately stack
    stack_boost: float = 6.0    # weight multiplier for correlated teammates
    salary_floor_ratio: float = 0.93
    seed: int = 909090
    max_attempts_per_entry: int = 40


@dataclass
class FieldModel:
    """Sampled opposing lineups as an index matrix (entries x roster size)."""

    entries: np.ndarray                       # int32 (F, roster_size)
    player_ids: list[str]
    multipliers: np.ndarray | None = None     # showdown captain multipliers
    config: FieldConfig = dc_field(default_factory=FieldConfig)
    meta: dict = dc_field(default_factory=dict)

    @property
    def size(self) -> int:
        return int(self.entries.shape[0])

    def duplication_counts(self) -> dict[tuple[int, ...], int]:
        counts: dict[tuple[int, ...], int] = {}
        for row in self.entries:
            key = tuple(sorted(int(v) for v in row))
            counts[key] = counts.get(key, 0) + 1
        return counts

    def unique_rate(self) -> float:
        return len(self.duplication_counts()) / max(self.size, 1)


def build_field(projections: Mapping[str, PlayerProjection], rules: RosterRules,
                ownership: Mapping[str, float], sim: SlateSimulation,
                config: FieldConfig | None = None,
                stack_positions: Sequence[str] = ("QB",)) -> FieldModel:
    cfg = config or FieldConfig()
    rng = np.random.default_rng(cfg.seed)
    ids = sim.player_ids
    projs = [projections[pid] for pid in ids]
    salaries = np.array([p.player.salary for p in projs], dtype=float)
    teams = [p.player.team for p in projs]
    positions = [p.player.positions for p in projs]
    games = [p.player.game_id or f"g:{p.player.team}" for p in projs]
    weights = np.array([max(ownership.get(pid, 0.5), 0.05) for pid in ids], dtype=float)

    slot_eligibility = [
        np.array([any(pos in slot.eligible for pos in positions[i]) for i in range(len(ids))])
        for slot in rules.slots
    ]
    cheapest = float(np.min(salaries)) if len(salaries) else 0.0

    entries = np.zeros((cfg.n_entries, rules.size), dtype=np.int32)
    built = 0
    attempts = 0
    while built < cfg.n_entries and attempts < cfg.n_entries * cfg.max_attempts_per_entry:
        attempts += 1
        row = _sample_entry(rng, rules, weights, salaries, teams, games, positions,
                            slot_eligibility, cheapest, cfg, stack_positions)
        if row is None:
            continue
        entries[built] = row
        built += 1
    entries = entries[:built]

    mult = None
    if any(s.multiplier != 1.0 for s in rules.slots):
        mult = np.array([s.multiplier for s in rules.slots], dtype=float)

    return FieldModel(entries=entries, player_ids=list(ids), multipliers=mult, config=cfg,
                      meta={"attempts": attempts, "built": built,
                            "unique_rate": round(len(set(map(lambda r: tuple(sorted(r)),
                                                             entries.tolist()))) /
                                                 max(built, 1), 4)})


def _sample_entry(rng, rules: RosterRules, weights, salaries, teams, games, positions,
                  slot_eligibility, cheapest, cfg: FieldConfig,
                  stack_positions: Sequence[str]) -> np.ndarray | None:
    chosen: list[int] = []
    used: set[int] = set()
    spend = 0.0
    boost = np.ones(len(weights))
    stacking = rng.random() < cfg.stack_rate

    for slot_i, slot in enumerate(rules.slots):
        remaining = rules.size - slot_i - 1
        budget_left = rules.salary_cap - spend - cheapest * remaining
        mask = slot_eligibility[slot_i].copy()
        for i in used:
            mask[i] = False
        mask &= salaries <= budget_left
        if rules.max_per_team:
            excl = {e.upper() for e in rules.max_per_team_excludes}
            counts: dict[str, int] = {}
            for i in chosen:
                if not any(p.upper() in excl for p in positions[i]):
                    counts[teams[i]] = counts.get(teams[i], 0) + 1
            for i in np.nonzero(mask)[0]:
                if counts.get(teams[i], 0) >= rules.max_per_team and \
                        not any(p.upper() in excl for p in positions[i]):
                    mask[i] = False
        if rules.forbid_same_game_opponents:
            taken_games = {games[i] for i in chosen}
            for i in np.nonzero(mask)[0]:
                if games[i] in taken_games:
                    mask[i] = False
        if not mask.any():
            return None

        w = weights * mask * boost
        total = w.sum()
        if total <= 0:
            return None
        pick = int(rng.choice(len(w), p=w / total))
        chosen.append(pick)
        used.add(pick)
        spend += salaries[pick] * slot.multiplier

        if stacking and any(p in stack_positions for p in positions[pick]):
            same_team = np.array([t == teams[pick] for t in teams])
            boost = np.where(same_team, boost * cfg.stack_boost, boost)

    if spend < rules.salary_cap * cfg.salary_floor_ratio and rng.random() < 0.65:
        return None  # real entrants spend most of the cap
    if rules.min_teams > 1 and len({teams[i] for i in chosen}) < rules.min_teams:
        return None
    if rules.min_games > 1 and len({games[i] for i in chosen}) < rules.min_games:
        return None
    return np.array(chosen, dtype=np.int32)


# --------------------------------------------------------------------------
# Payouts
# --------------------------------------------------------------------------


@dataclass
class PayoutCurve:
    """Parametric GPP payout shape: steep at the top, flat at the cash line."""

    paid_fraction: float = 0.2
    top_prize_share: float = 0.15
    decay: float = 0.72

    def prize_fractions(self, field_size: int, places: int = 2000) -> np.ndarray:
        paid = max(1, int(field_size * self.paid_fraction))
        places = min(places, paid)
        ranks = np.arange(1, places + 1)
        raw = ranks ** (-self.decay)
        raw = raw / raw.sum()
        return raw

    def payout_for_rank(self, rank: np.ndarray, field_size: int) -> np.ndarray:
        """Prize as a fraction of the pool for an (array of) finishing ranks."""
        paid = max(1, int(field_size * self.paid_fraction))
        fractions = self.prize_fractions(field_size)
        idx = np.clip(np.asarray(rank, dtype=np.int64) - 1, 0, len(fractions) - 1)
        out = fractions[idx]
        return np.where(np.asarray(rank) <= paid, out, 0.0)


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------

#: Quantile grid used to locate a lineup inside the field's score distribution.
#: Dense at the top because that is the only region that pays in a large GPP.
_GRID = np.concatenate([
    np.linspace(0.0, 0.98, 99),
    np.array([0.985, 0.99, 0.993, 0.995, 0.997, 0.998, 0.999, 0.9995, 0.9999, 1.0]),
])


@dataclass
class LineupSimMetrics:
    mean: float
    median: float
    p90: float
    p95: float
    p99: float
    top20_rate: float
    top10_rate: float
    top1_rate: float
    top01_rate: float
    first_place_proxy: float
    cash_rate: float
    field_overlap: float        # expected contest entries sharing size-1+ players
    expected_payout: float
    dup_estimate: float
    mean_percentile: float

    def as_dict(self) -> dict[str, float]:
        return {k: round(float(v), 6) for k, v in self.__dict__.items()}


def incidence_matrix(field: FieldModel, n_players: int) -> np.ndarray:
    """(entries x players) roster matrix, carrying captain multipliers if any."""
    mat = np.zeros((field.size, n_players), dtype=np.float32)
    mult = field.multipliers
    for r, row in enumerate(field.entries):
        for c, pid_idx in enumerate(row):
            mat[r, int(pid_idx)] += 1.0 if mult is None else float(mult[c])
    return mat


@dataclass
class EvaluationResult:
    """Per-lineup metrics plus the world-by-world matrices the portfolio needs."""

    metrics: list["LineupSimMetrics"]
    scores: np.ndarray          # (n_lineups, n_worlds) fantasy points
    beaten_by: np.ndarray       # (n_lineups, n_worlds) fraction of field above us
    payouts: np.ndarray         # (n_lineups, n_worlds) prize-pool fraction
    contest: Contest

    def __iter__(self):  # keeps ``metrics, scores = evaluate_lineups(...)`` working
        return iter((self.metrics, self.scores))


def evaluate_lineups(sim: SlateSimulation, field: FieldModel,
                     lineups: Sequence[Sequence[str]], contest: Contest,
                     payout: PayoutCurve | None = None,
                     ownership: Mapping[str, float] | None = None,
                     world_chunk: int = 2000,
                     multipliers: Sequence[Sequence[float]] | None = None
                     ) -> EvaluationResult:
    """Rank each lineup against the sampled field in every simulated world.

    Returns per-lineup metrics and the ``(n_lineups, n_worlds)`` score matrix,
    which the portfolio layer needs in order to reason about *joint* outcomes.

    Tail resolution is bounded by the sampled field size: with F sampled
    entries, nothing finer than ``1/F`` is measurable, so ``first_place_proxy``
    is exactly that -- a proxy, extrapolated to the contest's entry count and
    labelled as an approximation per ``core/SIMULATION.md``.
    """
    payout = payout or PayoutCurve(paid_fraction=contest.payout_top_fraction)
    idx = sim.index
    n_w, n_l = sim.n_worlds, len(lineups)
    n_p = len(sim.player_ids)

    incidence = incidence_matrix(field, n_p)
    incidence_bool = (incidence > 0).astype(np.float32)
    lu_cols = [[idx[pid] for pid in lu] for lu in lineups]
    lu_mult = [np.asarray(m, dtype=np.float32) if m is not None else None
               for m in (multipliers or [None] * n_l)]

    lineup_scores = np.zeros((n_l, n_w), dtype=np.float32)
    grid_pos = np.zeros((n_l, n_w), dtype=np.float32)   # approx fraction of field beaten
    max_beat = np.zeros((n_l, n_w), dtype=bool)

    start = 0
    while start < n_w:
        stop = min(start + world_chunk, n_w)
        block = sim.scores[start:stop]                  # (w, players)
        f_tot = block @ incidence.T                     # (w, entries)
        quants = np.quantile(f_tot, _GRID, axis=1)      # (grid, w)
        for i, cols in enumerate(lu_cols):
            sub = block[:, cols]
            if lu_mult[i] is not None:
                sub = sub * lu_mult[i]
            mine = sub.sum(axis=1)
            lineup_scores[i, start:stop] = mine
            above = (mine[None, :] >= quants)           # (grid, w)
            reached = above.sum(axis=0)                 # index into _GRID
            pct = _GRID[np.clip(reached - 1, 0, len(_GRID) - 1)]
            pct = np.where(reached == 0, 0.0, pct)
            grid_pos[i, start:stop] = pct
            max_beat[i, start:stop] = mine >= quants[-1]
        start = stop

    field_n = max(field.size, 1)
    resolution = 1.0 / field_n
    metrics: list[LineupSimMetrics] = []
    beaten_matrix = np.zeros((n_l, n_w), dtype=np.float32)
    payout_matrix = np.zeros((n_l, n_w), dtype=np.float32)
    for i in range(n_l):
        scores = lineup_scores[i]
        pct = grid_pos[i]                       # fraction of the field we are above
        beaten_by = 1.0 - pct                   # fraction of the field above us
        rank = 1.0 + beaten_by * (contest.field_size - 1)
        # Duplication, two ways: an independence product (right for genuinely
        # chalky rosters) and a near-match count measured against the sampled
        # field (right when construction, not raw ownership, drives overlap).
        onehot = np.zeros(n_p, dtype=np.float32)
        for c in lu_cols[i]:
            onehot[c] = 1.0
        overlaps = incidence_bool @ onehot
        roster_size = len(lu_cols[i])
        scale = contest.field_size / field_n
        near_dupes = float((overlaps >= roster_size - 1).sum()) * scale
        exact_dupes = float((overlaps >= roster_size).sum()) * scale
        dup = max(_dup_estimate(lineups[i], ownership, contest.field_size),
                  1.0 + exact_dupes)
        eff_rank = rank + 0.5 * max(dup - 1.0, 0.0)   # ties split prizes
        pay = payout.payout_for_rank(np.round(eff_rank).astype(np.int64), contest.field_size)
        beaten_matrix[i] = beaten_by
        payout_matrix[i] = pay
        # First place in a contest far larger than the sampled field cannot be
        # measured directly; scale the "beat every sampled entry" rate by the
        # ratio of contest size to sample size and divide out duplication.
        beat_all = float(max_beat[i].mean())
        proxy = beat_all * min(1.0, field_n / max(contest.field_size, 1)) / max(dup, 1.0)
        metrics.append(LineupSimMetrics(
            mean=float(scores.mean()),
            median=float(np.median(scores)),
            p90=float(np.percentile(scores, 90)),
            p95=float(np.percentile(scores, 95)),
            p99=float(np.percentile(scores, 99)),
            top20_rate=float((beaten_by <= 0.20).mean()),
            top10_rate=float((beaten_by <= 0.10).mean()),
            top1_rate=float((beaten_by <= 0.01).mean()),
            top01_rate=float((beaten_by <= max(0.001, resolution)).mean()),
            first_place_proxy=float(proxy),
            cash_rate=float((beaten_by <= contest.payout_top_fraction).mean()),
            field_overlap=near_dupes,
            expected_payout=float(pay.mean()),
            dup_estimate=float(dup),
            mean_percentile=float(100.0 * pct.mean()),
        ))
    return EvaluationResult(metrics=metrics, scores=lineup_scores,
                            beaten_by=beaten_matrix, payouts=payout_matrix,
                            contest=contest)


def _dup_estimate(lineup: Sequence[str], ownership: Mapping[str, float] | None,
                  field_size: int) -> float:
    """Expected identical entries. Independence understates this badly.

    Entrants correlate through shared optimizers, shared projections and stack
    conventions, so the independent product is inflated before reporting. It
    remains a proxy, not a measurement.
    """
    if not ownership:
        return 1.0
    prod = 1.0
    for pid in lineup:
        prod *= max(ownership.get(pid, 1.0), 0.15) / 100.0
    return max(1.0, prod * field_size * 12.0)
