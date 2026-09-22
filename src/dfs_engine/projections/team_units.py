"""Kickers and defenses: projected from the game market, not from player props.

Neither position has prop coverage worth building on. What they do have is the
game line, which is exactly what drives them: a kicker's scoring is the part of
his team's implied points that touchdowns do not explain, and a defense is a
function of the opponent's implied total and how far ahead its own team is
expected to be.

Both models are the documented NFL pregame-process fallbacks. They run after the
offensive pass and after team reconciliation, because both depend on the team's
final touchdown means.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from ..models import GameEnvironment, MarketSnapshot, PlayerProjection
from ..odds.distributions import FittedStat, NormalDistribution
from .components import ComponentResult, counted

# -- kicker ----------------------------------------------------------------

XP_CONVERSION_RATE = 0.96
#: Field-goal distance mix: under 40, 40-49, 50+. DK pays 3, 4 and 5 points.
FG_DISTANCE_MIX = (0.55, 0.30, 0.15)
FG_POINTS = (3.0, 4.0, 5.0)

# -- defense ---------------------------------------------------------------

DROPBACK_RATE = 0.93          # pass attempts per dropback (the rest are sacks)
SACK_RATE = 0.07
LEAGUE_INT_PER_ATTEMPT = 0.023
FUMBLE_RECOVERIES = 0.40
SAFETIES = 0.035
BLOCKED_KICKS = 0.035
DEFENSIVE_TD_BASE = 0.12
DEFENSIVE_TD_PER_POINT = 0.005
POINTS_ALLOWED_SD = 10.0
DEFAULT_PASS_ATTEMPTS = 33.0


@dataclass
class TeamUnitInputs:
    """Everything the kicker and defense models need from the offensive pass."""

    team: str
    implied_points: float
    opponent: str | None = None
    opponent_implied_points: float | None = None
    offensive_td_mean: float = 0.0        # rushing + receiving TDs, not passing
    opponent_pass_attempts: float | None = None
    opponent_interceptions: float | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def advantage(self) -> float:
        if self.opponent_implied_points is None:
            return 0.0
        return self.implied_points - self.opponent_implied_points


def collect_team_inputs(projections: Mapping[str, PlayerProjection],
                        snapshot: MarketSnapshot | None) -> dict[str, TeamUnitInputs]:
    """Aggregate per-team offensive means and game-market context."""
    by_team: dict[str, list[PlayerProjection]] = {}
    for proj in projections.values():
        by_team.setdefault(proj.player.team, []).append(proj)

    out: dict[str, TeamUnitInputs] = {}
    for team, players in by_team.items():
        game: GameEnvironment | None = None
        if snapshot is not None:
            game = snapshot.game_for_team(team)
        opponent = game.opponent_of(team) if game else (players[0].player.opponent)
        implied = game.team_total(team) if game else None
        opp_implied = game.team_total(opponent or "") if game else None
        if implied is None:
            implied = 22.0
        # Offensive touchdowns: rushing plus receiving, including QB rushing
        # scores. Passing TDs are excluded -- they are the same scores as the
        # receiving TDs already counted.
        td_mean = 0.0
        for p in players:
            for stat in ("rush_td", "rec_td"):
                fitted = p.components.get(stat)
                if fitted is not None:
                    td_mean += float(fitted.mean)
        out[team] = TeamUnitInputs(
            team=team, implied_points=float(implied), opponent=opponent,
            opponent_implied_points=None if opp_implied is None else float(opp_implied),
            offensive_td_mean=td_mean,
        )

    # Opponent passing volume and interception means feed the defense model.
    for team, inputs in out.items():
        opp = inputs.opponent
        if not opp or opp not in by_team:
            continue
        passers = [p for p in by_team[opp] if "pass_attempts" in p.components
                   or "pass_yards" in p.components]
        if passers:
            qb = max(passers, key=lambda p: p.engine_projection or 0.0)
            att = qb.components.get("pass_attempts")
            ints = qb.components.get("interception")
            if att is not None:
                inputs.opponent_pass_attempts = float(att.mean)
            if ints is not None:
                inputs.opponent_interceptions = float(ints.mean)
    return out


def kicker_components(inputs: TeamUnitInputs) -> ComponentResult:
    """Residual scoring model: points the offense's touchdowns do not explain.

    A negative residual means the team's touchdown means already account for
    more than its implied total. The field-goal mean is floored at zero and the
    inconsistency is flagged rather than hidden.
    """
    res = ComponentResult()
    xp_made = XP_CONVERSION_RATE * inputs.offensive_td_mean
    residual = inputs.implied_points - 6.0 * inputs.offensive_td_mean - xp_made
    fg_made = max(0.0, residual / 3.0)

    res.add(counted("extra_points", xp_made, note="0.96 x team offensive TDs"))
    for share, stat in zip(FG_DISTANCE_MIX, ("fg_0_39", "fg_40_49", "fg_50_plus")):
        res.add(counted(stat, fg_made * share, note="residual points / 3, distance mix"))
    res.note(f"residual scoring model: implied {inputs.implied_points:.1f} points, "
             f"{inputs.offensive_td_mean:.2f} offensive TDs -> {fg_made:.2f} FGs")
    if residual < 0:
        res.note("WARNING: negative scoring residual -- projected touchdowns "
                 "exceed the team's implied total; field goals floored at zero")
    return res


def defense_components(inputs: TeamUnitInputs) -> ComponentResult:
    """Sacks, turnovers and points allowed from the game line."""
    res = ComponentResult()
    opp_points = (inputs.opponent_implied_points
                  if inputs.opponent_implied_points is not None else 22.0)
    advantage = inputs.advantage
    attempts = inputs.opponent_pass_attempts
    if attempts is None:
        attempts = DEFAULT_PASS_ATTEMPTS
        res.note("opponent passing volume unavailable; league-average attempts used")

    # Trailing teams throw more, which creates sacks; the floor stops a big
    # underdog's sack mean from collapsing.
    dropbacks = attempts / DROPBACK_RATE
    sacks = dropbacks * SACK_RATE * max(0.75, 1.0 + 0.04 * advantage)
    res.add(counted("sacks", sacks, dispersion=6.0,
                    note="opponent dropbacks x sack rate x game script"))

    interceptions = inputs.opponent_interceptions
    if interceptions is None:
        interceptions = LEAGUE_INT_PER_ATTEMPT * attempts
        res.note("no opponent interception market; league rate used")
    res.add(counted("def_interceptions", interceptions, note="opponent QB INT mean"))
    res.add(counted("fumble_recoveries", FUMBLE_RECOVERIES, note="league rate"))
    res.add(counted("safeties", SAFETIES, note="league rate"))
    res.add(counted("blocked_kicks", BLOCKED_KICKS, note="league rate"))
    res.add(counted("def_td", DEFENSIVE_TD_BASE + DEFENSIVE_TD_PER_POINT * max(advantage, 0.0),
                    note="league rate scaled by game script"))

    res.add(FittedStat(
        "points_allowed",
        NormalDistribution(mu=opp_points, sigma=POINTS_ALLOWED_SD, floor=0.0),
        inferred=True, sources=["opponent implied total, SD 10"]))
    res.note(f"defense derived from the game market: opponent implied "
             f"{opp_points:.1f}, advantage {advantage:+.1f}")
    return res


def build_team_units(projections: Mapping[str, PlayerProjection],
                     snapshot: MarketSnapshot | None) -> dict[str, ComponentResult]:
    """Fill components for every kicker and defense in the pool."""
    inputs = collect_team_inputs(projections, snapshot)
    out: dict[str, ComponentResult] = {}
    for pid, proj in projections.items():
        pos = (proj.player.positions[0] if proj.player.positions else "").upper()
        role = proj.player.roster_role
        team_input = inputs.get(proj.player.team)
        if team_input is None:
            continue
        if role == "dst" or pos in {"DST", "DEF", "D"}:
            out[pid] = defense_components(team_input)
        elif role == "k" or pos == "K":
            out[pid] = kicker_components(team_input)
    return out


def expected_dk_points(components: Sequence[tuple[str, float]],
                       weights: Mapping[str, float]) -> float:
    """Linear scoring check used by the validation step."""
    return sum(weights.get(stat, 0.0) * mean for stat, mean in components)
