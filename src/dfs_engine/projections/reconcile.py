"""Team reconciliation: make receiver production add up to the quarterback.

Props are priced player by player. Nothing in a sportsbook guarantees that a
team's receiving-yard props sum to its quarterback's passing-yard prop, and in
practice they rarely do -- books post the markets that get bet, not a coherent
box score. Projecting both sets straight from the market therefore ships an
internally contradictory slate, which ``core/MARKET_INPUTS.md`` calls out
directly: individual projections must not collectively imply a different game
than the betting market.

The NFL pregame process fixes this with one pass over each team's active
receiving pool:

    yard_factor = QB passing yards / sum(raw receiving yards)
    TD_factor   = QB passing TDs   / sum(raw receiving TDs)

Two rules matter for correctness. Factors are always computed from **raw**
market means, so re-running the build cannot compound the scaling. And only the
receiving share of a player's touchdown mean is rescaled -- a running back's
rushing touchdowns have nothing to do with his quarterback's passing volume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from ..models import PlayerProjection
from ..odds.distributions import FittedStat

#: Fallback share of a player's total TD mean that is a *receiving* touchdown.
#: Explicit assumptions; replace with player-specific shares where they exist.
RECEIVING_TD_SHARE: dict[str, float] = {"WR": 1.0, "TE": 1.0, "RB": 0.12, "QB": 0.0}

RECEIVING_POSITIONS = ("RB", "WR", "TE")

#: Relative receiving weight per dollar of salary, used only to allocate the
#: part of a quarterback's passing production that no posted market explains.
UNCOVERED_RECEIVING_WEIGHT: dict[str, float] = {"WR": 1.0, "TE": 0.7, "RB": 0.35}

#: Yards per reception by position, used to turn modeled receiving yards into a
#: catch total. Receptions are a full point each on DraftKings, so projecting
#: yardage without them would understate a modeled receiver badly.
YARDS_PER_RECEPTION: dict[str, float] = {"WR": 12.9, "TE": 10.8, "RB": 7.6}

#: League-average team rushing yards, and how much a point of spread moves it.
#: Favourites run more; trailing teams abandon the run. Used only to give a
#: back with no posted rushing market something better than zero.
TEAM_RUSH_YARDS_BASE = 112.0
TEAM_RUSH_YARDS_PER_POINT = 2.0
TEAM_RUSH_YARDS_BOUNDS = (70.0, 165.0)
RUSH_TD_PER_YARD = 0.0075
YARDS_PER_CARRY = 4.3

#: Guardrail on the reconciliation factor. A factor outside this band means the
#: receiving pool and the quarterback's market disagree badly enough that
#: silently scaling would do more harm than good.
FACTOR_BOUNDS = (0.65, 1.55)


@dataclass
class TeamReconciliation:
    team: str
    quarterback: str | None
    yard_factor: float | None = None
    td_factor: float | None = None
    yard_factor_clamped: bool = False
    td_factor_clamped: bool = False
    raw_receiving_yards: float = 0.0
    raw_receiving_tds: float = 0.0
    qb_passing_yards: float = 0.0
    qb_passing_tds: float = 0.0
    receivers: int = 0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "team": self.team,
            "quarterback": self.quarterback,
            "receivers": self.receivers,
            "qb_passing_yards": round(self.qb_passing_yards, 2),
            "raw_receiving_yards": round(self.raw_receiving_yards, 2),
            "yard_factor": None if self.yard_factor is None else round(self.yard_factor, 4),
            "qb_passing_tds": round(self.qb_passing_tds, 3),
            "raw_receiving_tds": round(self.raw_receiving_tds, 3),
            "td_factor": None if self.td_factor is None else round(self.td_factor, 4),
            "yard_factor_clamped": self.yard_factor_clamped,
            "td_factor_clamped": self.td_factor_clamped,
            "notes": self.notes,
        }


def _position(proj: PlayerProjection) -> str:
    return (proj.player.positions[0] if proj.player.positions else "").upper()


def _mean(proj: PlayerProjection, stat: str) -> float:
    fitted = proj.components.get(stat)
    return float(fitted.mean) if fitted is not None else 0.0


def _set_mean(proj: PlayerProjection, stat: str, mean: float, note: str) -> None:
    """Rebuild a component at a new mean, preserving its distribution family."""
    from ..markets.catalog import CONTINUOUS_CV, dispersion_for
    from ..odds.distributions import GammaDistribution, make_count

    mean = max(float(mean), 0.0)
    if stat in CONTINUOUS_CV:
        dist = GammaDistribution.from_mean_cv(max(mean, 1e-6), CONTINUOUS_CV[stat])
    else:
        dist = make_count(max(mean, 1e-6), dispersion_for(stat, proj.player.sport))
    existing = proj.components.get(stat)
    proj.components[stat] = FittedStat(
        stat=stat, dist=dist,
        n_points=existing.n_points if existing else 0,
        n_books=existing.n_books if existing else 0,
        sources=(existing.sources if existing else []) + [note],
        inferred=existing.inferred if existing else True,
    )


def allocate_uncovered_rushing(projections: Sequence[PlayerProjection],
                               favoured_by: float = 0.0) -> int:
    """Give backs with no rushing market a share of the team's expected carries.

    Unlike receiving, there is no single market that pins a team's rushing
    total, so the anchor is a league prior scaled by game script. That makes
    this the weakest inference in the projection layer -- it is labelled
    modeled, it shrinks toward the vendor prior like any low-coverage
    component, and it exists because leaving an every-down back at zero rushing
    production is worse than an explicitly-assumed estimate.
    """
    backs = [p for p in projections if _position(p) in {"RB", "QB"}]
    rushers = [p for p in backs if _position(p) == "RB"]
    if not rushers:
        return 0

    team_yards = TEAM_RUSH_YARDS_BASE + TEAM_RUSH_YARDS_PER_POINT * favoured_by
    team_yards = min(max(team_yards, TEAM_RUSH_YARDS_BOUNDS[0]), TEAM_RUSH_YARDS_BOUNDS[1])
    covered = sum(_mean(p, "rush_yards") for p in backs)
    gap = team_yards - covered
    uncovered = [p for p in rushers if _mean(p, "rush_yards") <= 0]
    if gap <= 0 or not uncovered:
        return 0

    weights = [max(p.player.salary, 100) for p in uncovered]
    total = sum(weights)
    for p, weight in zip(uncovered, weights):
        yards = gap * weight / total
        _set_mean(p, "rush_yards", yards, "modeled share of team rushing")
        if "rush_attempts" not in p.components:
            _set_mean(p, "rush_attempts", yards / YARDS_PER_CARRY,
                      "modeled yards / yards-per-carry")
        if "rush_td" not in p.components:
            _set_mean(p, "rush_td", yards * RUSH_TD_PER_YARD, "modeled rushing TD rate")
        p.notes.append("rushing production modeled from the team rushing prior "
                       "(no posted rushing market)")
        p.modeled_from_team = True
    return len(uncovered)


def reconcile_team(projections: Sequence[PlayerProjection],
                   shares: Mapping[str, float] | None = None,
                   favoured_by: float = 0.0) -> TeamReconciliation:
    """Scale one team's receiving production to its projected starting QB."""
    shares = dict(RECEIVING_TD_SHARE if shares is None else shares)
    team = projections[0].player.team if projections else "?"

    quarterbacks = [p for p in projections if _position(p) == "QB"]
    receivers = [p for p in projections if _position(p) in RECEIVING_POSITIONS]
    result = TeamReconciliation(team=team, quarterback=None, receivers=len(receivers))

    if not quarterbacks:
        result.notes.append("no quarterback in the pool; receiving left unreconciled")
        return result
    # The projected starter is the highest-projected QB on the roster.
    qb = max(quarterbacks, key=lambda p: p.engine_projection)
    result.quarterback = qb.player.name
    result.qb_passing_yards = _mean(qb, "pass_yards")
    result.qb_passing_tds = _mean(qb, "pass_td")

    rushing_filled = allocate_uncovered_rushing(projections, favoured_by)
    if rushing_filled:
        result.notes.append(
            f"{rushing_filled} back(s) without a posted rushing market were given a "
            "salary-weighted share of the team rushing prior (modeled)")

    if not receivers:
        result.notes.append("no active receiving pool; nothing to reconcile")
        return result

    # Snapshot raw market means once, so reruns rescale from the same base.
    for p in receivers:
        p.extra_raw = getattr(p, "extra_raw", {})
        p.extra_raw.setdefault("rec_yards", _mean(p, "rec_yards"))
        p.extra_raw.setdefault("rush_td", _mean(p, "rush_td"))
        p.extra_raw.setdefault("rec_td", _mean(p, "rec_td"))

    # Players with no posted receiving market contribute nothing to the raw sum,
    # which would otherwise hand their production to whoever *is* covered. Give
    # them an explicit modeled share of the unexplained gap first.
    allocated = allocate_uncovered_receiving(receivers, result.qb_passing_yards,
                                             result.qb_passing_tds)
    if allocated:
        result.notes.append(
            f"{allocated} receiver(s) without a posted market were given a "
            "salary-weighted share of the unexplained passing production (modeled)")

    raw_yards = sum(p.extra_raw["rec_yards"] for p in receivers)
    result.raw_receiving_yards = raw_yards

    if result.qb_passing_yards > 0 and raw_yards > 0:
        factor = result.qb_passing_yards / raw_yards
        clamped = min(max(factor, FACTOR_BOUNDS[0]), FACTOR_BOUNDS[1])
        if abs(clamped - factor) > 1e-9:
            result.yard_factor_clamped = True
            result.notes.append(
                f"yard factor {factor:.2f} clamped to {clamped:.2f}: the receiving "
                "pool and the QB market disagree beyond the guardrail")
        result.yard_factor = clamped
        for p in receivers:
            if p.extra_raw["rec_yards"] <= 0:
                continue   # no receiving production: do not invent a component
            _set_mean(p, "rec_yards", p.extra_raw["rec_yards"] * clamped,
                      "team reconciliation")
    elif raw_yards <= 0:
        result.notes.append("receiving yards unavailable; yard reconciliation skipped")
    else:
        result.notes.append("no QB passing-yard market; yard reconciliation skipped")

    raw_rec_td = 0.0
    for p in receivers:
        share = shares.get(_position(p), 0.5)
        total_td = p.extra_raw["rec_td"] + p.extra_raw["rush_td"]
        raw_rec_td += total_td * share if p.extra_raw["rec_td"] <= 0 else p.extra_raw["rec_td"]
    result.raw_receiving_tds = raw_rec_td

    if result.qb_passing_tds > 0 and raw_rec_td > 0:
        factor = result.qb_passing_tds / raw_rec_td
        clamped = min(max(factor, FACTOR_BOUNDS[0]), FACTOR_BOUNDS[1])
        if abs(clamped - factor) > 1e-9:
            result.td_factor_clamped = True
            result.notes.append(
                f"receiving TD factor {factor:.2f} clamped to {clamped:.2f}")
        result.td_factor = clamped
        for p in receivers:
            share = shares.get(_position(p), 0.5)
            total_td = p.extra_raw["rec_td"] + p.extra_raw["rush_td"]
            rec_td = p.extra_raw["rec_td"] if p.extra_raw["rec_td"] > 0 else total_td * share
            if rec_td <= 0:
                continue
            _set_mean(p, "rec_td", rec_td * clamped, "team reconciliation")
    elif raw_rec_td <= 0:
        result.notes.append("receiving TD means unavailable; TD reconciliation skipped")
    else:
        result.notes.append("no QB passing-TD market; TD reconciliation skipped")

    return result


def allocate_uncovered_receiving(receivers: Sequence[PlayerProjection],
                                 qb_passing_yards: float,
                                 qb_passing_tds: float) -> int:
    """Give market-less receivers a modeled share of the unexplained passing total.

    This is a modeling decision, not a market observation, and every affected
    component is labelled ``inferred``. The alternative -- leaving them at zero
    -- is worse: it both projects an active player at nothing and inflates every
    covered teammate when the reconciliation factor is applied.

    The split is salary-weighted with a per-position receiving multiplier, since
    salary is the one role signal always present in a site player pool.
    """
    covered_yards = sum(p.extra_raw["rec_yards"] for p in receivers
                        if p.extra_raw["rec_yards"] > 0)
    gap = qb_passing_yards - covered_yards
    uncovered = [p for p in receivers if p.extra_raw["rec_yards"] <= 0]
    if gap <= 0 or not uncovered:
        return 0

    weights = []
    positions = []
    for p in uncovered:
        pos = _position(p)
        positions.append(pos)
        weights.append(max(p.player.salary, 100) *
                       UNCOVERED_RECEIVING_WEIGHT.get(pos, 0.5))
    total_weight = sum(weights)
    if total_weight <= 0:
        return 0

    covered_td = sum(p.extra_raw["rec_td"] for p in receivers
                     if p.extra_raw["rec_td"] > 0)
    td_gap = max(0.0, qb_passing_tds - covered_td)

    for p, pos, weight in zip(uncovered, positions, weights):
        share = weight / total_weight
        p.extra_raw["rec_yards"] = gap * share
        _set_mean(p, "rec_yards", p.extra_raw["rec_yards"],
                  "modeled share of unexplained passing yards")
        if td_gap > 0:
            p.extra_raw["rec_td"] = td_gap * share
            _set_mean(p, "rec_td", p.extra_raw["rec_td"],
                      "modeled share of unexplained passing TDs")
        if "receptions" not in p.components:
            ypr = YARDS_PER_RECEPTION.get(pos, 10.5)
            _set_mean(p, "receptions", p.extra_raw["rec_yards"] / ypr,
                      "modeled yards / position yards-per-reception")
        p.notes.append("receiving production modeled from the team passing total "
                       "(no posted receiving market)")
        p.modeled_from_team = True
    return len(uncovered)


def reconcile_slate(projections: Mapping[str, PlayerProjection],
                    shares: Mapping[str, float] | None = None,
                    snapshot=None) -> list[TeamReconciliation]:
    """Reconcile every team, then note the adjustment on each affected player."""
    by_team: dict[str, list[PlayerProjection]] = {}
    for proj in projections.values():
        if proj.player.sport not in {"nfl", "ncaaf"}:
            continue
        by_team.setdefault(proj.player.team, []).append(proj)

    results: list[TeamReconciliation] = []
    for team, players in sorted(by_team.items()):
        favoured_by = 0.0
        if snapshot is not None:
            game = snapshot.game_for_team(team)
            if game is not None and game.spread_home is not None:
                favoured_by = (-game.spread_home if team == game.home_team
                               else game.spread_home)
        result = reconcile_team(players, shares, favoured_by)
        results.append(result)
        if result.yard_factor is not None and abs(result.yard_factor - 1.0) > 0.02:
            for p in players:
                if _position(p) in RECEIVING_POSITIONS and "rec_yards" in p.components:
                    p.notes.append(
                        f"receiving reconciled to {result.quarterback} "
                        f"(x{result.yard_factor:.2f} yards"
                        + (f", x{result.td_factor:.2f} receiving TDs)"
                           if result.td_factor else ")"))
    return results


def validate(results: Sequence[TeamReconciliation],
             projections: Mapping[str, PlayerProjection],
             tolerance: float = 0.01) -> dict:
    """Post-reconciliation checks from the freeze-and-validate step.

    Reconciled team receiving yards must equal projected QB passing yards, and
    allocated receiving touchdowns must equal projected QB passing touchdowns.
    """
    failures: list[str] = []
    checks: list[str] = []
    flags: list[str] = []
    by_team: dict[str, list[PlayerProjection]] = {}
    for proj in projections.values():
        by_team.setdefault(proj.player.team, []).append(proj)

    for result in results:
        if result.yard_factor is None:
            continue
        receivers = [p for p in by_team.get(result.team, [])
                     if _position(p) in RECEIVING_POSITIONS]
        total = sum(_mean(p, "rec_yards") for p in receivers)
        if result.yard_factor_clamped:
            flags.append(
                f"{result.team}: receiving yards left at {total:.0f} vs QB "
                f"{result.qb_passing_yards:.0f} -- factor hit the guardrail")
        elif abs(total - result.qb_passing_yards) > max(tolerance * max(total, 1.0), 0.5):
            failures.append(
                f"{result.team}: receiving yards {total:.1f} != QB passing yards "
                f"{result.qb_passing_yards:.1f}")
        else:
            checks.append(f"{result.team}: receiving yards reconciled to the QB "
                          f"({total:.0f})")
        if result.td_factor is not None:
            td_total = sum(_mean(p, "rec_td") for p in receivers)
            if result.td_factor_clamped:
                flags.append(
                    f"{result.team}: receiving TDs left at {td_total:.2f} vs QB "
                    f"{result.qb_passing_tds:.2f} -- factor hit the guardrail")
            elif abs(td_total - result.qb_passing_tds) > max(tolerance * max(td_total, 1.0), 0.02):
                failures.append(
                    f"{result.team}: receiving TDs {td_total:.2f} != QB passing TDs "
                    f"{result.qb_passing_tds:.2f}")
    return {
        "passed": not failures,
        "failures": failures,
        "flags": flags,
        "checks": checks,
        "teams_reconciled": sum(1 for r in results if r.yard_factor is not None),
        "teams": [r.as_dict() for r in results],
    }
