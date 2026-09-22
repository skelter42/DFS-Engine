"""Exposure audit, correlation summary, risk flags, and final QA.

Everything here exists to satisfy the delivery contract in
``schemas/LINEUP_OUTPUT.md`` and the required audit table in
``core/ENGINE.md``: source values and engine values side by side, with the
largest deviations explained rather than merely listed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..models import PlayerProjection, Portfolio


@dataclass
class ExposureRow:
    player_id: str
    name: str
    team: str
    position: str
    salary: int
    vendor_projection: float | None
    market_projection: float | None
    coverage: str
    engine_projection: float
    source_ownership: float | None
    engine_ownership: float
    exposure_pct: float
    difference_pp: float
    reason: str

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def exposure_table(portfolio: Portfolio, projections: Mapping[str, PlayerProjection],
                   ownership: Mapping[str, float]) -> list[ExposureRow]:
    counts = portfolio.exposure_counts()
    n = max(len(portfolio.lineups), 1)
    rows: list[ExposureRow] = []
    for pid, count in counts.items():
        proj = projections.get(pid)
        if proj is None:
            continue
        exposure = 100.0 * count / n
        own = ownership.get(pid, 0.0)
        rows.append(ExposureRow(
            player_id=pid,
            name=proj.player.name,
            team=proj.player.team,
            position="/".join(proj.player.positions),
            salary=proj.player.salary,
            vendor_projection=proj.vendor_projection,
            market_projection=(round(proj.market_projection, 2)
                               if proj.market_projection is not None else None),
            coverage=f"{proj.coverage} ({proj.coverage_label})",
            engine_projection=round(proj.engine_projection, 2),
            source_ownership=(round(proj.source_ownership, 1)
                              if proj.source_ownership is not None else None),
            engine_ownership=round(own, 1),
            exposure_pct=round(exposure, 1),
            difference_pp=round(exposure - own, 1),
            reason=_explain(proj, exposure, own),
        ))
    rows.sort(key=lambda r: -r.exposure_pct)
    return rows


def _explain(proj: PlayerProjection, exposure: float, ownership: float) -> str:
    diff = exposure - ownership
    bits: list[str] = []
    if abs(diff) < 5:
        bits.append("exposure tracks the field")
    elif diff > 0:
        bits.append(f"overweight by {diff:.0f}pp")
    else:
        bits.append(f"underweight by {abs(diff):.0f}pp")
    if proj.coverage in {"A", "B"}:
        bits.append(f"market-derived ({proj.coverage_label}, {proj.n_markets} markets, "
                    f"{proj.n_books} books)")
    else:
        bits.append(f"{proj.coverage_label} projection")
    if proj.vendor_projection is not None:
        delta = proj.engine_projection - proj.vendor_projection
        if abs(delta) >= 1.0:
            bits.append(f"engine {delta:+.1f} vs source")
    if proj.ceiling > proj.engine_projection * 1.6:
        bits.append("high ceiling relative to median")
    return "; ".join(bits)


def largest_deviations(rows: Sequence[ExposureRow], n: int = 10) -> list[ExposureRow]:
    return sorted(rows, key=lambda r: -abs(r.difference_pp))[:n]


def correlation_summary(portfolio: Portfolio) -> dict:
    """Stack structure across the portfolio, in sport-appropriate terms."""
    stacks: dict[str, int] = {}
    game_stacks: dict[str, int] = {}
    sizes: dict[int, int] = {}
    for lu in portfolio.lineups:
        teams = lu.team_counts()
        if teams:
            top_team, size = max(teams.items(), key=lambda kv: kv[1])
            if size >= 2:
                stacks[f"{top_team} x{size}"] = stacks.get(f"{top_team} x{size}", 0) + 1
            sizes[size] = sizes.get(size, 0) + 1
        games = lu.game_counts()
        for gid, count in games.items():
            if count >= 3:
                game_stacks[gid] = game_stacks.get(gid, 0) + 1
    return {
        "primary_stacks": dict(sorted(stacks.items(), key=lambda kv: -kv[1])[:12]),
        "stack_size_distribution": dict(sorted(sizes.items())),
        "game_stacks_3plus": dict(sorted(game_stacks.items(), key=lambda kv: -kv[1])[:10]),
    }


def risk_flags(projections: Mapping[str, PlayerProjection], portfolio: Portfolio,
               snapshot=None) -> list[str]:
    flags: list[str] = []
    used = set(portfolio.exposure_counts())
    fallback = [projections[p].player.name for p in used
                if p in projections and projections[p].coverage == "D"]
    if fallback:
        flags.append(f"{len(fallback)} rostered player(s) have no market coverage "
                     f"(fallback-driven): {', '.join(sorted(fallback)[:6])}"
                     + (" ..." if len(fallback) > 6 else ""))
    thin = [projections[p].player.name for p in used
            if p in projections and projections[p].n_books == 1]
    if thin:
        flags.append(f"{len(thin)} rostered player(s) priced by a single book; "
                     "no cross-book consensus available")
    unconfirmed = [projections[p].player.name for p in used
                   if p in projections and projections[p].player.status.lower()
                   in {"questionable", "probable", "gtd"}]
    if unconfirmed:
        flags.append(f"unconfirmed status: {', '.join(sorted(unconfirmed))}")
    if snapshot is not None and getattr(snapshot, "errors", None):
        flags.append(f"{len(snapshot.errors)} market source error(s) during the sweep; "
                     "coverage may be understated")
    return flags


def final_audit(portfolio: Portfolio, projections: Mapping[str, PlayerProjection],
                rules) -> dict:
    """Pre-delivery QA. Any failure here must be fixed before the file ships."""
    failures: list[str] = []
    checks: list[str] = []

    over_cap = [lu for lu in portfolio.lineups if lu.salary > rules.salary_cap]
    if over_cap:
        failures.append(f"{len(over_cap)} lineup(s) exceed the salary cap")
    else:
        checks.append(f"all lineups within the ${rules.salary_cap:,} cap")

    wrong_size = [lu for lu in portfolio.lineups if len(lu.players) != rules.size]
    if wrong_size:
        failures.append(f"{len(wrong_size)} lineup(s) have the wrong roster size")
    else:
        checks.append(f"all lineups fill {rules.size} roster spots")

    dupes = [lu for lu in portfolio.lineups
             if len({p.player_id for p in lu.players}) != len(lu.players)]
    if dupes:
        failures.append(f"{len(dupes)} lineup(s) roster the same player twice")

    zeroed = []
    for lu in portfolio.lineups:
        for p in lu.players:
            if p.vendor_projection is not None and abs(p.vendor_projection) < 1e-9:
                zeroed.append(p.name)
    if zeroed:
        failures.append("source-zero players present in the lineup file: "
                        + ", ".join(sorted(set(zeroed))))
    else:
        checks.append("zero-projection eligibility gate: no source-zero player rostered")

    inactive = []
    for lu in portfolio.lineups:
        for p in lu.players:
            if p.status.lower() in {"out", "scratched", "inactive", "ir"}:
                inactive.append(p.name)
    if inactive:
        failures.append("inactive players rostered: " + ", ".join(sorted(set(inactive))))
    else:
        checks.append("no confirmed-inactive players rostered")

    sigs = [lu.signature() for lu in portfolio.lineups]
    if len(set(sigs)) != len(sigs):
        failures.append(f"{len(sigs) - len(set(sigs))} duplicate lineup(s) in the portfolio")
    else:
        checks.append("every delivered lineup is unique")

    legal_teams = [lu for lu in portfolio.lineups
                   if len(set(lu.teams)) < rules.min_teams]
    if legal_teams:
        failures.append(f"{len(legal_teams)} lineup(s) below the {rules.min_teams}-team minimum")
    else:
        checks.append(f"all lineups use at least {rules.min_teams} teams")

    return {"passed": not failures, "failures": failures, "checks": checks}
