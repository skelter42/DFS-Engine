"""Delivery artifacts: upload files, audit tables, and the written build report.

The set of outputs is fixed by ``schemas/LINEUP_OUTPUT.md`` -- slate summary,
thesis, portfolio, exposure table with percentage-point differences, stack
summary, multi-contest allocation audit, risk flags, and final audit. If a
number is missing it is reported as missing, never filled in.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ..pipeline import BuildResult


def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_upload_csv(result: BuildResult, path: Path) -> Path:
    """Site-ready upload file: one row per lineup, columns in roster-slot order."""
    slots = list(result.rules.slot_names)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(slots)
        for lu in result.portfolio.lineups:
            by_slot: dict[str, list[str]] = {}
            for player, slot in zip(lu.players, lu.slots or slots):
                by_slot.setdefault(slot, []).append(player.dfs_id or player.name)
            row = []
            used: dict[str, int] = {}
            for slot in slots:
                i = used.get(slot, 0)
                values = by_slot.get(slot, [])
                row.append(values[i] if i < len(values) else "")
                used[slot] = i + 1
            writer.writerow(row)
    return path


def write_lineups_detail(result: BuildResult, path: Path) -> Path:
    fields = ["lineup", "contest", "salary", "projection", "ceiling_sum", "total_ownership",
              "mean", "p99", "top1_rate", "top01_rate", "first_place_proxy",
              "expected_payout", "dup_estimate", "marginal_value", "script", "risk",
              "stack", "players"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i, lu in enumerate(result.portfolio.lineups, start=1):
            writer.writerow({
                "lineup": i,
                "contest": lu.contest or "",
                "salary": lu.salary,
                "projection": round(lu.projection, 2),
                "ceiling_sum": round(float(lu.metrics.get("ceiling_sum", 0.0)), 2),
                "total_ownership": round(float(lu.metrics.get("total_ownership", 0.0)), 1),
                "mean": round(float(lu.metrics.get("mean", 0.0)), 2),
                "p99": round(float(lu.metrics.get("p99", 0.0)), 2),
                "top1_rate": round(float(lu.metrics.get("top1_rate", 0.0)), 5),
                "top01_rate": round(float(lu.metrics.get("top01_rate", 0.0)), 5),
                "first_place_proxy": round(float(lu.metrics.get("first_place_proxy", 0.0)), 7),
                "expected_payout": round(float(lu.metrics.get("expected_payout", 0.0)), 7),
                "dup_estimate": round(float(lu.metrics.get("dup_estimate", 0.0)), 2),
                "marginal_value": round(float(lu.metrics.get("marginal_value", 0.0)), 7),
                "script": lu.labels.get("script", ""),
                "risk": lu.labels.get("risk", ""),
                "stack": lu.labels.get("stack", ""),
                "players": " | ".join(f"{s}:{p.name}" for p, s in zip(lu.players, lu.slots)),
            })
    return path


def write_exposures_csv(result: BuildResult, path: Path) -> Path:
    rows = result.portfolio.diagnostics.get("exposure_table", [])
    if not rows:
        path.write_text("")
        return path
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_projections_csv(result: BuildResult, path: Path) -> Path:
    """The full audit table: vendor vs market vs engine, ownership, exposure."""
    exposure = result.portfolio.exposure_pct()
    fields = ["player_id", "dfs_id", "name", "team", "opponent", "position", "salary",
              "vendor_projection", "market_projection", "market_coverage",
              "market_weight", "engine_projection", "projection_delta", "ceiling",
              "floor", "sd", "value", "n_markets", "n_books",
              "source_ownership", "engine_ownership", "exposure_pct", "notes"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for pid, proj in sorted(result.projections.items(),
                                key=lambda kv: -kv[1].engine_projection):
            p = proj.player
            writer.writerow({
                "player_id": pid, "dfs_id": p.dfs_id, "name": p.name, "team": p.team,
                "opponent": p.opponent or "", "position": "/".join(p.positions),
                "salary": p.salary,
                "vendor_projection": _num(proj.vendor_projection),
                "market_projection": _num(proj.market_projection),
                "market_coverage": f"{proj.coverage} ({proj.coverage_label})",
                "market_weight": round(proj.market_weight, 3),
                "engine_projection": round(proj.engine_projection, 3),
                "projection_delta": _num(proj.projection_delta),
                "ceiling": round(proj.ceiling, 2), "floor": round(proj.floor, 2),
                "sd": round(proj.sd, 2), "value": round(proj.value, 3),
                "n_markets": proj.n_markets, "n_books": proj.n_books,
                "source_ownership": _num(proj.source_ownership),
                "engine_ownership": round(result.ownership.get(pid, 0.0), 2),
                "exposure_pct": round(exposure.get(pid, 0.0), 1),
                "notes": "; ".join(proj.notes),
            })
    return path


def _num(value: float | None, digits: int = 3) -> str:
    return "" if value is None else str(round(float(value), digits))


def write_build_json(result: BuildResult, path: Path) -> Path:
    payload = {
        "meta": result.meta,
        "portfolio_metrics": result.portfolio.metrics,
        "diagnostics": result.portfolio.diagnostics,
        "lineups": [
            {
                "index": i,
                "contest": lu.contest,
                "salary": lu.salary,
                "projection": round(lu.projection, 3),
                "labels": lu.labels,
                "metrics": {k: round(float(v), 7) for k, v in lu.metrics.items()},
                "players": [
                    {"slot": slot, "name": p.name, "dfs_id": p.dfs_id, "team": p.team,
                     "position": "/".join(p.positions), "salary": p.salary,
                     "engine_projection": round(
                         result.projections[p.player_id].engine_projection, 2)
                     if p.player_id in result.projections else None,
                     "engine_ownership": round(result.ownership.get(p.player_id, 0.0), 1)}
                    for p, slot in zip(lu.players, lu.slots)
                ],
            }
            for i, lu in enumerate(result.portfolio.lineups, start=1)
        ],
    }
    path.write_text(json.dumps(payload, indent=2, default=_json_default))
    return path


def _json_default(obj: Any):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, set):
        return sorted(obj)
    return str(obj)


# --------------------------------------------------------------------------
# Written report
# --------------------------------------------------------------------------


def slate_thesis(result: BuildResult) -> list[str]:
    """Derive the thesis from what the market and the simulation actually said."""
    lines: list[str] = []
    envs = []
    for lu in result.portfolio.lineups:
        envs.append(lu.labels.get("anchor_game", "?"))
    top_games = sorted({g: envs.count(g) for g in envs}.items(), key=lambda kv: -kv[1])[:3]
    if top_games:
        lines.append("Portfolio concentrates its primary correlation in "
                     + ", ".join(f"`{g}` ({c} lineups)" for g, c in top_games) + ".")

    cov = result.portfolio.diagnostics.get("coverage", {})
    lines.append(f"Projection basis: {cov.get('vegas_backed_pct', 0)}% of the eligible pool "
                 f"is Vegas-rich or Vegas-supported; mean market weight "
                 f"{cov.get('mean_market_weight', 0)}.")

    hidden = result.portfolio.diagnostics.get("hidden_concentration", {})
    teams = hidden.get("top_teams", [])[:3]
    if teams:
        lines.append("In the worlds where this portfolio reaches the top 1%, the leading "
                     "teams are " + ", ".join(f"{t['team']} ({t['share_pct']}%)"
                                              for t in teams) + ".")
    pm = result.portfolio.metrics
    lines.append(f"Aggregate tail coverage: at least one lineup reaches the top 1% in "
                 f"{pm.get('any_top1_rate', 0):.1%} of simulated worlds and the top 0.1% in "
                 f"{pm.get('any_top01_rate', 0):.2%}; effective independent lineups "
                 f"{pm.get('effective_lineups', 0):.1f} of {pm.get('n_lineups', 0)}.")
    return lines


def write_audit_markdown(result: BuildResult, path: Path) -> Path:
    meta = result.meta
    d = result.portfolio.diagnostics
    pm = result.portfolio.metrics
    out: list[str] = []
    a = out.append

    a(f"# DFS Engine build - {meta.get('sport', '?').upper()} "
      f"{meta.get('site', '').upper()} {meta.get('variant', '')}")
    a("")
    if meta.get("synthetic"):
        a(f"> **{meta.get('warning')}**")
        a("")

    a("## Slate summary")
    a("")
    a(f"- Generated: {meta.get('generated_at')}")
    a(f"- Engine version: {meta.get('engine_version')}")
    a(f"- Player pool: {meta.get('players_in_pool')} rows, "
      f"{meta.get('players_eligible')} eligible after the source-zero gate")
    a(f"- Market sources: {', '.join(meta.get('market_sources') or ['none'])}")
    mc = d.get("market_coverage", {})
    a(f"- Sweep coverage: {mc.get('players_with_any_market', 0)}/{mc.get('pool_size', 0)} "
      f"players with at least one posted market ({mc.get('coverage_pct', 0)}%), "
      f"books: {', '.join(mc.get('books') or ['none'])}")
    a(f"- Simulation: {meta.get('simulation', {}).get('mode')} , "
      f"{meta.get('simulation', {}).get('iterations'):,} worlds, "
      f"{meta.get('simulation', {}).get('factors')} latent factors")
    a(f"- {meta.get('iteration_note')}")
    if meta.get("market_errors"):
        a("- Source errors during the sweep:")
        for err in meta["market_errors"]:
            a(f"    - {err}")
    a("")

    a("## Projection confidence")
    a("")
    cov = d.get("coverage", {})
    a("| Tier | Meaning | Players | Share |")
    a("|---|---|---:|---:|")
    for tier, info in (cov.get("tiers") or {}).items():
        a(f"| {tier} | {info['label']} | {info['count']} | {info['pct']}% |")
    a("")

    a("## Slate thesis")
    a("")
    for line in slate_thesis(result):
        a(f"- {line}")
    a("")

    a("## Portfolio")
    a("")
    a("| # | Contest | Salary | Proj | Ceiling | Own sum | Top 1% | Top 0.1% | Dup | Script |")
    a("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for i, lu in enumerate(result.portfolio.lineups, start=1):
        m = lu.metrics
        a(f"| {i} | {lu.contest or '-'} | ${lu.salary:,} | {lu.projection:.1f} | "
          f"{float(m.get('ceiling_sum', 0)):.1f} | {float(m.get('total_ownership', 0)):.0f}% | "
          f"{float(m.get('top1_rate', 0)):.2%} | {float(m.get('top01_rate', 0)):.3%} | "
          f"{float(m.get('dup_estimate', 0)):.1f} | {lu.labels.get('script', '')} |")
    a("")

    a("### Rosters")
    a("")
    for i, lu in enumerate(result.portfolio.lineups, start=1):
        names = ", ".join(f"{slot} {p.name}" for p, slot in zip(lu.players, lu.slots))
        a(f"{i}. ({lu.contest or '-'}) {names}")
    a("")

    a("## Source ownership vs engine exposure")
    a("")
    a("| Player | Team | Pos | Coverage | Engine proj | Source own % | Engine own % | "
      "Exposure % | Diff (pp) | Reason |")
    a("|---|---|---|---|---:|---:|---:|---:|---:|---|")
    for row in d.get("exposure_table", []):
        a(f"| {row['name']} | {row['team']} | {row['position']} | {row['coverage']} | "
          f"{row['engine_projection']} | {row['source_ownership'] if row['source_ownership'] is not None else '-'} | "
          f"{row['engine_ownership']} | {row['exposure_pct']} | {row['difference_pp']:+.1f} | "
          f"{row['reason']} |")
    a("")

    a("### Largest exposure deviations")
    a("")
    for row in d.get("largest_deviations", []):
        a(f"- **{row['name']}** ({row['team']} {row['position']}): "
          f"{row['exposure_pct']}% exposure vs {row['engine_ownership']}% expected ownership "
          f"({row['difference_pp']:+.1f}pp) - {row['reason']}")
    a("")

    a("## Correlation / stack summary")
    a("")
    corr = d.get("correlation", {})
    a(f"- Primary stacks: {corr.get('primary_stacks')}")
    a(f"- Stack size distribution: {corr.get('stack_size_distribution')}")
    a(f"- Games with 3+ players: {corr.get('game_stacks_3plus')}")
    a("")

    a("## Portfolio simulation")
    a("")
    a(f"- At least one lineup top 1%: **{pm.get('any_top1_rate', 0):.2%}** of worlds")
    a(f"- At least one lineup top 0.1%: **{pm.get('any_top01_rate', 0):.3%}** of worlds")
    a(f"- Mean best-lineup percentile: {pm.get('best_rank_mean_percentile', 0):.2f}")
    a(f"- Total expected payout (share of prize pool): "
      f"{pm.get('total_expected_payout', 0):.6f}")
    a(f"- Mean pairwise lineup correlation: {pm.get('world_overlap', 0):.3f}")
    a(f"- Effective independent lineups: {pm.get('effective_lineups', 0):.1f} of "
      f"{pm.get('n_lineups', 0)}")
    a(f"- Tail worlds won by more than one lineup: "
      f"{pm.get('winning_world_overlap', 0):.1%}")
    a(f"- Concentration (HHI): {pm.get('concentration')}")
    a("")
    hc = d.get("hidden_concentration", {})
    a(f"- Hidden concentration in tail worlds -- teams: {hc.get('top_teams')}")
    a(f"- Hidden concentration in tail worlds -- games: {hc.get('top_games')}")
    a("")

    a("## Multi-contest allocation audit")
    a("")
    for row in d.get("allocation_audit", []):
        a(f"### {row['contest']}")
        a("")
        a(f"- Lineups: {row.get('lineups')} ({row.get('unique_lineups')} unique) of "
          f"{row.get('entries')} entries; field size {row.get('field_size')}")
        a(f"- Avg projection {row.get('avg_projection')}, avg top-1% rate "
          f"{float(row.get('avg_top1_rate') or 0):.2%}, avg duplication "
          f"{row.get('avg_duplication')}")
        a(f"- Avg total ownership: {row.get('avg_total_ownership')}%")
        a(f"- Script families: {row.get('script_families')}")
        a(f"- Risk families: {row.get('risk_families')}")
        a(f"- Top teams: {row.get('top_teams')}")
        for flag in row.get("flags", []):
            a(f"- **Flag:** {flag}")
        a("")

    a("## Risk flags")
    a("")
    flags = d.get("risk_flags", []) + d.get("ownership_flags", [])
    if flags:
        for flag in flags:
            a(f"- {flag}")
    else:
        a("- None raised by the automated checks. Re-run closer to lock for late news.")
    a("")

    a("## Final audit")
    a("")
    fa = d.get("final_audit", {})
    a(f"- **Status: {'PASSED' if fa.get('passed') else 'FAILED'}**")
    for check in fa.get("checks", []):
        a(f"- [x] {check}")
    for failure in fa.get("failures", []):
        a(f"- [ ] **{failure}**")
    excluded = d.get("excluded_players", [])
    if excluded:
        a("")
        a(f"- Excluded from the pool ({len(excluded)}): "
          + ", ".join(f"{e['name']} ({e['reason']})" for e in excluded[:20])
          + (" ..." if len(excluded) > 20 else ""))
    a("")
    a("---")
    a("")
    a("_Mathematical output only. `core/ENGINE.md` requires an explicit strategic "
      "review of this portfolio -- check that the exposures above express intended "
      "slate theses rather than optimizer repetition -- before these lineups are entered._")
    a("")
    path.write_text("\n".join(out))
    return path


def write_all(result: BuildResult, out_dir: str | Path,
              dk_template: str | Path | None = None) -> dict[str, Path]:
    out = _ensure(Path(out_dir))
    paths = {
        "upload": write_upload_csv(result, out / "lineups.csv"),
        "lineups_detail": write_lineups_detail(result, out / "lineups_detail.csv"),
        "exposures": write_exposures_csv(result, out / "exposures.csv"),
        "projections": write_projections_csv(result, out / "projections.csv"),
        "build_json": write_build_json(result, out / "build.json"),
        "audit": write_audit_markdown(result, out / "audit.md"),
        "html": _write_html(result, out / "report.html"),
    }
    if dk_template:
        from .dk_upload import fill_dk_template

        fill = fill_dk_template(result.portfolio.lineups, result.rules.slot_names,
                                dk_template, out / "dk_entries.csv")
        result.meta["dk_template_fill"] = {
            "rows_filled": fill.rows_filled,
            "rows_in_template": fill.rows_in_template,
            "warnings": fill.warnings,
        }
        paths["dk_entries"] = fill.path
    return paths


def _write_html(result: BuildResult, path: Path) -> Path:
    from .html import write_html

    return write_html(result, path)
