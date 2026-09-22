"""Lineup construction: exact MILP with a greedy fallback.

Candidate generation is deliberately optimizer-heavy -- it is not the final
decision stage (``core/ENGINE.md``). The interesting part is *what* gets
optimized. The default generator samples a simulated world and solves for the
lineup that wins **that** world, so the candidate pool is a set of coherent
slate stories rather than N perturbations of the same median lineup.

Hard constraints are restricted to roster legality, contest rules, and
explicit user requirements. Exposure and diversity enter through the
objective, never as arbitrary caps.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from ..models import Lineup, PlayerProjection
from .rules import RosterRules, lineup_is_legal

log = logging.getLogger("dfs_engine.optimize")

try:  # pragma: no cover - availability differs per environment
    import pulp

    HAVE_PULP = True
except ImportError:  # pragma: no cover
    pulp = None
    HAVE_PULP = False


@dataclass
class ObjectiveWeights:
    """Mirrors ``config/engine.json:score_weights`` with contest multipliers applied."""

    projection: float = 1.0
    ceiling: float = 0.22
    leverage: float = 0.18
    correlation: float = 0.12
    value: float = 0.08
    volatility_penalty: float = 0.05

    def scaled(self, profile: Mapping[str, float]) -> "ObjectiveWeights":
        return ObjectiveWeights(
            projection=self.projection * profile.get("projection_multiplier", 1.0),
            ceiling=self.ceiling * profile.get("ceiling_multiplier", 1.0),
            leverage=self.leverage * profile.get("leverage_multiplier", 1.0),
            correlation=self.correlation * profile.get("correlation_multiplier", 1.0),
            value=self.value,
            volatility_penalty=self.volatility_penalty,
        )


@dataclass
class SolverConfig:
    mode: str = "world"          # world | noise | chalk
    randomness: float = 0.28     # noise mode: sd as a fraction of projection
    min_uniques: int = 2
    max_overlap: int | None = None
    exposure_penalty: float = 0.9   # points subtracted per unit of over-exposure
    locked: tuple[str, ...] = ()
    banned: tuple[str, ...] = ()
    max_exposure: Mapping[str, float] | None = None  # hard cap only if user asks
    time_limit: int = 10
    seed: int = 20260101


@dataclass
class SolveResult:
    lineup: Lineup | None
    status: str
    objective: float = 0.0


def _player_score(proj: PlayerProjection, weights: ObjectiveWeights,
                  ownership: Mapping[str, float], base: float | None = None) -> float:
    from ..projections.ownership import leverage_score

    own = ownership.get(proj.player.player_id, 5.0)
    value = proj.value
    core = base if base is not None else proj.engine_projection
    return (
        weights.projection * core
        + weights.ceiling * (proj.ceiling - proj.engine_projection)
        + weights.leverage * leverage_score(proj, own) * max(proj.engine_projection, 1.0) * 0.25
        + weights.value * value
        - weights.volatility_penalty * proj.sd
    )


def build_objective(projections: Sequence[PlayerProjection], weights: ObjectiveWeights,
                    ownership: Mapping[str, float], config: SolverConfig,
                    world_scores: np.ndarray | None = None,
                    rng: random.Random | None = None,
                    exposure_counts: Mapping[str, int] | None = None,
                    lineups_built: int = 0) -> dict[str, float]:
    """Per-player objective coefficients for one solve."""
    rng = rng or random.Random(config.seed)
    out: dict[str, float] = {}
    for i, proj in enumerate(projections):
        if config.mode == "world" and world_scores is not None:
            base = float(world_scores[i])
        elif config.mode == "noise":
            base = proj.engine_projection + rng.gauss(
                0.0, config.randomness * proj.engine_projection)
        else:
            base = proj.engine_projection
        score = _player_score(proj, weights, ownership, base=base)
        if exposure_counts and lineups_built > 0 and config.exposure_penalty:
            used = exposure_counts.get(proj.player.player_id, 0) / lineups_built
            score -= config.exposure_penalty * used ** 2 * max(proj.engine_projection, 1.0) * 0.1
        out[proj.player.player_id] = score
    return out


# --------------------------------------------------------------------------
# MILP
# --------------------------------------------------------------------------


def solve_lineup(projections: Sequence[PlayerProjection], rules: RosterRules,
                 objective: Mapping[str, float], config: SolverConfig,
                 previous: Sequence[Lineup] = ()) -> SolveResult:
    if not HAVE_PULP:
        return _greedy_lineup(projections, rules, objective, config, previous)

    pool = [p for p in projections if p.player.player_id not in set(config.banned)]
    if not pool:
        return SolveResult(None, "no eligible players")
    slot_counts = rules.slot_counts()
    slot_eligible = {name: [s for s in rules.slots if s.name == name][0].eligible
                     for name in slot_counts}
    slot_mult = {name: [s for s in rules.slots if s.name == name][0].multiplier
                 for name in slot_counts}

    prob = pulp.LpProblem("dfs_lineup", pulp.LpMaximize)
    x: dict[tuple[str, str], object] = {}
    for proj in pool:
        pid = proj.player.player_id
        for name, eligible in slot_eligible.items():
            if any(pos in eligible for pos in proj.player.positions):
                x[(pid, name)] = pulp.LpVariable(f"x_{pid}_{name}", cat="Binary")
    if not x:
        return SolveResult(None, "no player fits any roster slot")

    used = {}
    for proj in pool:
        pid = proj.player.player_id
        vars_for = [v for (p, _), v in x.items() if p == pid]
        if not vars_for:
            continue
        used[pid] = pulp.lpSum(vars_for)
        prob += used[pid] <= 1, f"once_{pid}"

    prob += pulp.lpSum(
        objective.get(pid, 0.0) * slot_mult[name] * var for (pid, name), var in x.items()
    )

    for name, count in slot_counts.items():
        prob += pulp.lpSum(v for (_, n), v in x.items() if n == name) == count, f"slot_{name}"

    salary = {p.player.player_id: p.player.salary for p in pool}
    prob += pulp.lpSum(salary[pid] * slot_mult[name] * v
                       for (pid, name), v in x.items()) <= rules.salary_cap, "cap"
    if rules.min_salary:
        prob += pulp.lpSum(salary[pid] * slot_mult[name] * v
                           for (pid, name), v in x.items()) >= rules.min_salary, "min_cap"

    by_team: dict[str, list[str]] = {}
    by_game: dict[str, list[str]] = {}
    for proj in pool:
        pid = proj.player.player_id
        if pid not in used:
            continue
        by_team.setdefault(proj.player.team, []).append(pid)
        by_game.setdefault(proj.player.game_id or f"g:{proj.player.team}", []).append(pid)

    if rules.max_per_team:
        excl = {e.upper() for e in rules.max_per_team_excludes}
        for team, pids in by_team.items():
            capped = [pid for pid in pids
                      if not any(pos.upper() in excl
                                 for pos in _positions(pool, pid))]
            if capped:
                prob += pulp.lpSum(used[pid] for pid in capped) <= rules.max_per_team, \
                    f"team_cap_{team}"

    _min_group(prob, used, by_team, rules.min_teams, "team")
    _min_group(prob, used, by_game, rules.min_games, "game")

    if rules.forbid_same_game_opponents:
        for game, pids in by_game.items():
            if len(pids) > 1:
                prob += pulp.lpSum(used[pid] for pid in pids) <= 1, f"one_side_{game}"

    for pid in config.locked:
        if pid in used:
            prob += used[pid] == 1, f"lock_{pid}"

    if config.max_exposure:
        for pid, cap in config.max_exposure.items():
            if cap <= 0 and pid in used:
                prob += used[pid] == 0, f"excl_{pid}"

    max_overlap = config.max_overlap
    if max_overlap is None:
        max_overlap = rules.size - max(config.min_uniques, 0)
    for i, lu in enumerate(previous):
        pids = [pid for pid in (p.player_id for p in lu.players) if pid in used]
        if pids:
            prob += pulp.lpSum(used[pid] for pid in pids) <= max_overlap, f"uniq_{i}"

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=config.time_limit)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        return SolveResult(None, status)

    chosen: list[tuple[str, str]] = [(pid, name) for (pid, name), v in x.items()
                                     if v.value() and v.value() > 0.5]
    lookup = {p.player.player_id: p for p in pool}
    order = {name: i for i, name in enumerate(dict.fromkeys(rules.slot_names))}
    chosen.sort(key=lambda t: (order.get(t[1], 99), -lookup[t[0]].player.salary))
    players = tuple(lookup[pid].player for pid, _ in chosen)
    slots = tuple(name for _, name in chosen)
    total_salary = sum(lookup[pid].player.salary * slot_mult[name] for pid, name in chosen)
    proj_total = sum(lookup[pid].engine_projection * slot_mult[name] for pid, name in chosen)
    lineup = Lineup(players=players, slots=slots, salary=int(round(total_salary)),
                    projection=float(proj_total))
    return SolveResult(lineup, "Optimal", float(pulp.value(prob.objective) or 0.0))


def _positions(pool: Sequence[PlayerProjection], pid: str) -> tuple[str, ...]:
    for p in pool:
        if p.player.player_id == pid:
            return p.player.positions
    return ()


def _min_group(prob, used, groups: Mapping[str, list[str]], minimum: int, label: str) -> None:
    """Force at least ``minimum`` distinct teams/games to appear in the roster."""
    if minimum <= 1 or len(groups) <= 1:
        return
    indicators = {}
    # Sorted keys and positional names keep the model byte-identical between
    # runs; Python's string hash is salted per process, so hashing keys here
    # would silently make builds non-reproducible.
    for i, key in enumerate(sorted(groups)):
        pids = groups[key]
        var = pulp.LpVariable(f"{label}_{i}", cat="Binary")
        indicators[key] = var
        prob += var <= pulp.lpSum(used[pid] for pid in pids if pid in used)
    prob += pulp.lpSum(indicators.values()) >= minimum, f"min_{label}s"


# --------------------------------------------------------------------------
# Greedy fallback (used when PuLP/CBC is unavailable)
# --------------------------------------------------------------------------


def _greedy_lineup(projections: Sequence[PlayerProjection], rules: RosterRules,
                   objective: Mapping[str, float], config: SolverConfig,
                   previous: Sequence[Lineup] = ()) -> SolveResult:
    """Value-ordered slot fill. Legal output is checked, not assumed."""
    banned = set(config.banned)
    pool = sorted((p for p in projections if p.player.player_id not in banned),
                  key=lambda p: -objective.get(p.player.player_id, 0.0))
    slots = list(rules.slots)
    chosen: list[tuple[PlayerProjection, str]] = []
    used_ids: set[str] = set()
    salary = 0
    for slot in slots:
        remaining = len(slots) - len(chosen) - 1
        for proj in pool:
            pid = proj.player.player_id
            if pid in used_ids or not any(pos in slot.eligible for pos in proj.player.positions):
                continue
            cost = proj.player.salary * slot.multiplier
            if salary + cost > rules.salary_cap - 2800 * remaining:
                continue
            chosen.append((proj, slot.name))
            used_ids.add(pid)
            salary += cost
            break
        else:
            return SolveResult(None, "greedy: no feasible player for slot " + slot.name)
    lineup = Lineup(
        players=tuple(p.player for p, _ in chosen),
        slots=tuple(n for _, n in chosen),
        salary=int(salary),
        projection=float(sum(p.engine_projection for p, _ in chosen)),
    )
    # The greedy pass fills slots by value and cannot reason about team/game
    # minimums, so its output is verified rather than trusted.
    ok, reason = lineup_is_legal(lineup, rules)
    if not ok:
        return SolveResult(None, f"greedy: {reason}")
    return SolveResult(lineup, "Greedy", 0.0)


# --------------------------------------------------------------------------
# Candidate pool
# --------------------------------------------------------------------------


@dataclass
class CandidatePool:
    lineups: list[Lineup] = field(default_factory=list)
    attempts: int = 0
    failures: dict[str, int] = field(default_factory=dict)

    def add(self, lineup: Lineup) -> bool:
        sig = lineup.signature()
        if any(l.signature() == sig for l in self.lineups):
            return False
        self.lineups.append(lineup)
        return True


def generate_candidates(projections: Mapping[str, PlayerProjection], rules: RosterRules,
                        ownership: Mapping[str, float], weights: ObjectiveWeights,
                        config: SolverConfig, n: int = 150,
                        sim=None, progress=None) -> CandidatePool:
    """Build a broad pool of legal, coherent lineups.

    ``mode="world"`` draws a simulated slate outcome and solves it exactly, so
    every candidate is the best lineup for some world the market says is
    possible.
    """
    projs = list(projections.values())
    pool = CandidatePool()
    rng = random.Random(config.seed)
    nprng = np.random.default_rng(config.seed)
    exposure: dict[str, int] = {}

    order = [p.player.player_id for p in projs]
    sim_index = {pid: sim.index[pid] for pid in order if sim and pid in sim.index} if sim else {}

    stall = 0
    while len(pool.lineups) < n and stall < max(40, n):
        pool.attempts += 1
        world_scores = None
        if config.mode == "world" and sim is not None:
            w = int(nprng.integers(0, sim.n_worlds))
            world_scores = np.array([sim.scores[w, sim_index[pid]] if pid in sim_index
                                     else projections[pid].engine_projection for pid in order])
        objective = build_objective(projs, weights, ownership, config, world_scores,
                                    rng, exposure, len(pool.lineups))
        # Uniqueness is enforced against a recent window: forcing global
        # uniqueness across hundreds of solves degrades every later lineup.
        result = solve_lineup(projs, rules, objective, config, previous=pool.lineups[-25:])
        if result.lineup is None:
            pool.failures[result.status] = pool.failures.get(result.status, 0) + 1
            stall += 1
            continue
        if pool.add(result.lineup):
            for p in result.lineup.players:
                exposure[p.player_id] = exposure.get(p.player_id, 0) + 1
            stall = 0
            if progress:
                progress(len(pool.lineups), n)
        else:
            stall += 1
    return pool
