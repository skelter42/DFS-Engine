"""Command line entry point.

    dfs-engine demo         end-to-end run on a synthetic slate (no network, no keys)
    dfs-engine fetch-props  sweep sportsbooks and save a market snapshot
    dfs-engine inspect      summarise a snapshot's coverage
    dfs-engine project      market snapshot + player pool -> projections.csv
    dfs-engine build        full build: projections, simulation, portfolio, reports
    dfs-engine scoring      print the site scoring rules in use
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Sequence

from .config import EngineConfig
from .models import Contest


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sport", default="nfl",
                        choices=["nfl", "ncaaf", "nba", "mlb", "nhl", "tennis"])
    parser.add_argument("--site", default="dk", choices=["dk", "fd"])
    parser.add_argument("-v", "--verbose", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dfs-engine", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run the whole pipeline on a synthetic slate")
    _add_common(demo)
    demo.add_argument("--out", default="slates/demo")
    demo.add_argument("--lineups", type=int, default=20)
    demo.add_argument("--candidates", type=int, default=200)
    demo.add_argument("--worlds", type=int, default=20000)
    demo.add_argument("--field", type=int, default=3000)
    demo.add_argument("--seed", type=int, default=20260101)

    fetch = sub.add_parser("fetch-props", help="sweep sportsbooks for props and game lines")
    _add_common(fetch)
    fetch.add_argument("--out", required=True, help="snapshot JSON to write")
    fetch.add_argument("--csv", help="also ingest a flat prop CSV from any aggregator")
    fetch.add_argument("--games-csv", help="game lines CSV to merge with --csv")
    fetch.add_argument("--max-events", type=int, help="cap events (saves API credits)")
    fetch.add_argument("--books", help="comma-separated bookmaker keys")
    fetch.add_argument("--no-live", action="store_true", help="files only, no HTTP")

    inspect = sub.add_parser("inspect", help="summarise a saved market snapshot")
    inspect.add_argument("--markets", required=True)
    inspect.add_argument("-v", "--verbose", action="store_true")

    project = sub.add_parser("project", help="build projections only")
    _add_common(project)
    project.add_argument("--players", required=True, help="site salary export CSV")
    project.add_argument("--vendor", help="vendor projection/ownership CSV")
    project.add_argument("--markets", required=True, help="snapshot JSON from fetch-props")
    project.add_argument("--out", default="projections.csv")

    build = sub.add_parser("build", help="full build from a player pool and a snapshot")
    _add_common(build)
    build.add_argument("--players", required=True)
    build.add_argument("--vendor")
    build.add_argument("--markets", required=True)
    build.add_argument("--contests", help="contests JSON")
    build.add_argument("--out", default="slates/latest")
    build.add_argument("--lineups", type=int, default=20)
    build.add_argument("--candidates", type=int, default=200)
    build.add_argument("--worlds", type=int, default=20000)
    build.add_argument("--field", type=int, default=3000)
    build.add_argument("--min-uniques", type=int, default=2)
    build.add_argument("--profile", default="large_field_gpp")
    build.add_argument("--variant", default="classic", choices=["classic", "showdown"])
    build.add_argument("--selection", default="marginal_value",
                       choices=["marginal_value", "uniqueness_ladder"],
                       help="portfolio selection strategy")
    build.add_argument("--seed", type=int, default=20260101)

    scoring = sub.add_parser("scoring", help="print site scoring rules")
    _add_common(scoring)

    return parser


def _progress(stage: str, message: str) -> None:
    print(f"  [{stage:<10}] {message}", file=sys.stderr)


def _load_contests(path: str | None, default_entries: int) -> list[Contest]:
    if not path:
        return []
    data = json.loads(Path(path).read_text())
    contests = []
    for i, row in enumerate(data, start=1):
        contests.append(Contest(
            name=row.get("name", f"Contest {i}"),
            entries=int(row.get("entries", 1)),
            field_size=int(row.get("field_size", 10000)),
            entry_fee=float(row.get("entry_fee", 0.0)),
            profile=row.get("profile", "large_field_gpp"),
            payout_top_fraction=float(row.get("payout_top_fraction", 0.2)),
            priority=int(row.get("priority", i)),
            max_entries_per_user=row.get("max_entries_per_user"),
        ))
    return contests


def _report(result, out_dir: str) -> None:
    from .report.writers import write_all

    paths = write_all(result, out_dir)
    pm = result.portfolio.metrics
    fa = result.portfolio.diagnostics.get("final_audit", {})
    print()
    print(f"Portfolio: {len(result.portfolio.lineups)} lineups | "
          f"any-top-1% {pm.get('any_top1_rate', 0):.1%} | "
          f"any-top-0.1% {pm.get('any_top01_rate', 0):.2%} | "
          f"effective lineups {pm.get('effective_lineups', 0):.1f}")
    print(f"Final audit: {'PASSED' if fa.get('passed') else 'FAILED'}")
    for failure in fa.get("failures", []):
        print(f"  ! {failure}")
    print()
    for name, path in paths.items():
        print(f"  {name:16s} {path}")


def cmd_demo(args) -> int:
    from .data.synthetic import build_demo_slate
    from .pipeline import BuildRequest, run_build

    slate = build_demo_slate(args.sport)
    contests = [
        Contest(name="Large-field GPP", entries=max(args.lineups - args.lineups // 3, 1),
                field_size=150000, entry_fee=20, profile="large_field_gpp",
                priority=1, payout_top_fraction=0.20),
        Contest(name="Small-field GPP", entries=args.lineups // 3, field_size=5000,
                entry_fee=10, profile="small_field_gpp", priority=2,
                payout_top_fraction=0.25),
    ]
    contests = [c for c in contests if c.entries > 0]
    request = BuildRequest(
        sport=args.sport, players=slate.players, snapshot=slate.snapshot,
        contests=contests, site=args.site, n_lineups=args.lineups,
        n_candidates=args.candidates, n_worlds=args.worlds, field_entries=args.field,
        seed=args.seed, synthetic=True, label="synthetic demo")
    result = run_build(request, progress=_progress)
    _report(result, args.out)
    print("\nNOTE: synthetic market data. Do not enter these lineups anywhere.")
    return 0


def cmd_fetch_props(args) -> int:
    from .markets import (CsvPropSource, DraftKingsSource, TheOddsApiSource,
                          save_snapshot, sweep)

    sources = []
    if not args.no_live:
        books = tuple(b.strip() for b in args.books.split(",")) if args.books else None
        odds = TheOddsApiSource(books=books) if books else TheOddsApiSource()
        sources.append(odds)
        sources.append(DraftKingsSource())
    if args.csv:
        sources.append(CsvPropSource(path=args.csv, games_path=args.games_csv))
    if not sources:
        print("nothing to fetch: pass --csv or drop --no-live", file=sys.stderr)
        return 2

    kwargs = {}
    if args.max_events:
        kwargs["max_events"] = args.max_events
    snapshot = sweep(args.sport, sources, **kwargs)
    save_snapshot(snapshot, args.out)
    summary = snapshot.summary()
    print(json.dumps(summary, indent=2))
    if snapshot.errors:
        print("\nSource errors (coverage may be understated):", file=sys.stderr)
        for err in snapshot.errors:
            print(f"  - {err}", file=sys.stderr)
    if not snapshot.props:
        print("\nNo markets were collected. Set ODDS_API_KEY for multi-book coverage, "
              "or supply --csv with an aggregator export.", file=sys.stderr)
        return 1
    return 0


def cmd_inspect(args) -> int:
    from .markets import consensus_by_player, load_snapshot

    snapshot = load_snapshot(args.markets)
    print(json.dumps(snapshot.summary(), indent=2))
    consensus = consensus_by_player(snapshot)
    print(f"\nplayers with usable consensus: {len(consensus)}")
    if args.verbose:
        for pkey, stats in sorted(consensus.items())[:25]:
            detail = ", ".join(f"{s}({c.n_lines}L/{c.n_books}B)" for s, c in stats.items())
            print(f"  {pkey:28s} {detail}")
    return 0


def cmd_project(args) -> int:
    from .ingest import apply_game_markets, load_player_pool, load_vendor_file
    from .markets import load_snapshot
    from .projections.engine import ProjectionConfig, coverage_summary, project_slate

    vendor = load_vendor_file(args.vendor) if args.vendor else None
    players, games = load_player_pool(args.players, args.sport, args.site, vendor)
    snapshot = load_snapshot(args.markets)
    if not snapshot.games:
        snapshot.games.extend(games)
    apply_game_markets(players, snapshot.games)
    projections = project_slate([p for p in players if p.eligible], snapshot,
                                ProjectionConfig(site=args.site))
    print(json.dumps(coverage_summary(projections), indent=2))

    import csv as _csv

    with Path(args.out).open("w", newline="", encoding="utf-8") as fh:
        writer = _csv.writer(fh)
        writer.writerow(["Name", "DFS ID", "Team", "Pos", "Salary", "Vendor", "Market",
                         "Coverage", "Weight", "Engine", "Ceiling", "SD", "Notes"])
        for proj in sorted(projections.values(), key=lambda p: -p.engine_projection):
            p = proj.player
            writer.writerow([
                p.name, p.dfs_id, p.team, "/".join(p.positions), p.salary,
                "" if proj.vendor_projection is None else round(proj.vendor_projection, 2),
                "" if proj.market_projection is None else round(proj.market_projection, 2),
                proj.coverage, round(proj.market_weight, 3),
                round(proj.engine_projection, 2), round(proj.ceiling, 2),
                round(proj.sd, 2), "; ".join(proj.notes),
            ])
    print(f"\nwrote {args.out}")
    return 0


def cmd_build(args) -> int:
    from .ingest import apply_game_markets, load_player_pool, load_vendor_file
    from .markets import load_snapshot
    from .pipeline import BuildRequest, run_build

    vendor = load_vendor_file(args.vendor) if args.vendor else None
    players, games = load_player_pool(args.players, args.sport, args.site, vendor)
    snapshot = load_snapshot(args.markets)
    if not snapshot.games:
        snapshot.games.extend(games)
    apply_game_markets(players, snapshot.games)

    contests = _load_contests(args.contests, args.lineups)
    request = BuildRequest(
        sport=args.sport, players=players, snapshot=snapshot, contests=contests,
        site=args.site, variant=args.variant, n_lineups=args.lineups,
        n_candidates=args.candidates, n_worlds=args.worlds, field_entries=args.field,
        seed=args.seed, min_uniques=args.min_uniques, contest_profile=args.profile,
        selection_strategy=args.selection, config=EngineConfig.load())
    result = run_build(request, progress=_progress)
    _report(result, args.out)
    return 0 if result.portfolio.diagnostics["final_audit"]["passed"] else 1


def cmd_scoring(args) -> int:
    from .projections.scoring import RULES

    for (site, sport, slot), rule in sorted(RULES.items()):
        if site != args.site or sport != args.sport:
            continue
        print(f"\n{site.upper()} {sport.upper()} [{slot}] - {rule.notes}")
        for stat, coef in sorted(rule.linear.items()):
            print(f"  {stat:22s} {coef:+.2f}")
        for bonus in rule.bonuses:
            print(f"  bonus: {bonus.stat} >= {bonus.threshold} -> {bonus.points:+.1f}")
        if rule.specials:
            print(f"  specials: {len(rule.specials)} threshold/tier rule(s)")
    return 0


COMMANDS = {
    "demo": cmd_demo,
    "fetch-props": cmd_fetch_props,
    "inspect": cmd_inspect,
    "project": cmd_project,
    "build": cmd_build,
    "scoring": cmd_scoring,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if getattr(args, "verbose", False) else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")
    try:
        return COMMANDS[args.command](args)
    except KeyboardInterrupt:  # pragma: no cover
        return 130
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
