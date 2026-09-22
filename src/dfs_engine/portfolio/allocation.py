"""Multi-contest allocation: a scenario-stratified quality ladder.

``core/ENGINE.md`` is blunt about the failure mode this avoids: sorting every
lineup by projection and dropping the top block into the biggest contest. That
leaves the other contests as leftovers and gives the big one a single script.

Instead every contest is dealt from within each script family in turn, in
priority order, so each contest ends up a complete mini-portfolio with its own
credible path to first while the higher-priority contest still gets a modest
quality tilt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..models import Contest, Lineup


@dataclass
class AllocationConfig:
    quality_key: str = "expected_payout"
    allow_repeats: bool = False     # a lineup may appear in more than one contest
    priority_tilt: bool = True      # higher-priority contests pick first each round


def allocate(lineups: Sequence[Lineup], contests: Sequence[Contest],
             config: AllocationConfig | None = None) -> dict[str, list[Lineup]]:
    cfg = config or AllocationConfig()
    if not contests:
        return {}
    if len(contests) == 1:
        for lu in lineups:
            lu.contest = contests[0].name
        return {contests[0].name: list(lineups)}

    order = sorted(contests, key=lambda c: (c.priority, -c.entry_fee))
    need = {c.name: c.entries for c in order}
    out: dict[str, list[Lineup]] = {c.name: [] for c in order}

    families: dict[str, list[Lineup]] = {}
    for lu in lineups:
        families.setdefault(lu.labels.get("family", "unlabelled"), []).append(lu)
    for fam in families.values():
        fam.sort(key=lambda lu: -float(lu.metrics.get(cfg.quality_key, lu.projection)))

    # Deal one lineup per (family, contest) per pass. Every contest therefore
    # sees every script family before any contest gets a second lineup from the
    # same family, and the priority order inside a pass gives the top contest
    # the modest quality tilt ENGINE.md allows.
    family_names = sorted(families, key=lambda f: (-len(families[f]), f))
    cursor = {f: 0 for f in family_names}
    remaining = sum(need.values())

    while remaining > 0:
        progressed = False
        for fam in family_names:
            pool = families[fam]
            for contest in order:
                if need[contest.name] <= 0 or cursor[fam] >= len(pool):
                    continue
                lu = pool[cursor[fam]]
                cursor[fam] += 1
                lu.contest = contest.name
                out[contest.name].append(lu)
                need[contest.name] -= 1
                remaining -= 1
                progressed = True
        if not progressed:
            break
    return out


def allocation_audit(allocation: Mapping[str, Sequence[Lineup]],
                     contests: Sequence[Contest],
                     ownership: Mapping[str, float] | None = None) -> list[dict]:
    """Per-contest report required by ``schemas/LINEUP_OUTPUT.md``."""
    by_name = {c.name: c for c in contests}
    rows: list[dict] = []
    for name, lus in allocation.items():
        contest = by_name.get(name)
        if not lus:
            rows.append({"contest": name, "lineups": 0,
                         "flags": ["contest received no lineups"]})
            continue
        families: dict[str, int] = {}
        risks: dict[str, int] = {}
        teams: dict[str, int] = {}
        for lu in lus:
            families[lu.labels.get("family", "?")] = families.get(lu.labels.get("family", "?"), 0) + 1
            risks[lu.labels.get("risk", "?")] = risks.get(lu.labels.get("risk", "?"), 0) + 1
            for p in lu.players:
                teams[p.team] = teams.get(p.team, 0) + 1
        sigs = {lu.signature() for lu in lus}
        avg = lambda key: sum(float(lu.metrics.get(key, 0.0)) for lu in lus) / len(lus)
        own_avg = None
        if ownership:
            own_avg = sum(sum(ownership.get(p.player_id, 0.0) for p in lu.players)
                          for lu in lus) / len(lus)
        flags: list[str] = []
        if len(risks) < 2 and len(lus) >= 3:
            flags.append("only one risk family present in this contest")
        if len(sigs) < len(lus):
            flags.append(f"{len(lus) - len(sigs)} duplicated lineups within the contest")
        top_team_share = max(teams.values()) / max(sum(teams.values()), 1) if teams else 0
        if top_team_share > 0.35:
            flags.append(f"one team holds {top_team_share:.0%} of roster spots")
        rows.append({
            "contest": name,
            "entries": contest.entries if contest else len(lus),
            "field_size": contest.field_size if contest else None,
            "profile": contest.profile if contest else None,
            "lineups": len(lus),
            "unique_lineups": len(sigs),
            "avg_projection": round(sum(lu.projection for lu in lus) / len(lus), 2),
            "avg_top1_rate": round(avg("top1_rate"), 5),
            "avg_expected_payout": round(avg("expected_payout"), 6),
            "avg_total_ownership": round(own_avg, 1) if own_avg is not None else None,
            "avg_duplication": round(avg("dup_estimate"), 2),
            "script_families": dict(sorted(families.items(), key=lambda kv: -kv[1])),
            "risk_families": dict(sorted(risks.items(), key=lambda kv: -kv[1])),
            "top_teams": dict(sorted(teams.items(), key=lambda kv: -kv[1])[:5]),
            "flags": flags,
        })
    rows.sort(key=lambda r: (by_name[r["contest"]].priority if r["contest"] in by_name else 99))
    return rows
