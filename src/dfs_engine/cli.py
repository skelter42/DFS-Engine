"""Command line entry point for auditable NFL Market Inputs previews."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from datetime import datetime

from .market_nfl import InsufficientMarket, project_player
from .market_sports import PROJECTORS


def build_import(source: Path, inputs: Path, output: Path, audit: Path) -> None:
    data = json.loads(inputs.read_text())
    sport = data.get("sport")
    if sport not in {"NFL", "MLB", "NHL"} or data.get("site") != "DraftKings":
        raise ValueError("Supported: DraftKings NFL, MLB and NHL")
    for key in ("slate", "as_of_utc", "lock_utc"):
        if not data.get(key):
            raise ValueError(f"Missing input metadata: {key}")
    as_of = datetime.fromisoformat(data["as_of_utc"].replace("Z", "+00:00"))
    lock = datetime.fromisoformat(data["lock_utc"].replace("Z", "+00:00"))
    if as_of.tzinfo is None or lock.tzinfo is None or as_of >= lock:
        raise ValueError("Input snapshot must be timestamped before lock")
    if sport in {"MLB", "NHL"} and not data.get("games"):
        raise ValueError("MLB/NHL inputs must define the exact slate game IDs")
    with source.open(newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames
        if columns is None or not {"DFS ID", "Proj"}.issubset(columns):
            raise ValueError("Savant CSV needs DFS ID and Proj columns")
        rows = list(reader)
    result = []
    seen = set()
    players = data.get("players", {})
    for row in rows:
        player_id = row["DFS ID"]
        # Showdown may have a CPT and a FLEX row for the same athlete.
        source_projection = float(row["Proj"] or 0)
        record = {"dfs_id": player_id, "name": row.get("Name"),
                  "source_projection": source_projection}
        if source_projection <= 0:
            record["status"] = "source_zero_preserved"
        elif player_id not in players:
            record["status"] = "uncovered_source_preserved"
        else:
            try:
                entry = dict(players[player_id], as_of_utc=data["as_of_utc"])
                if sport in {"MLB", "NHL"}:
                    if entry.get("game") not in data["games"]:
                        raise ValueError(f"Player {player_id} has an off-slate or missing game")
                    if entry.get("inactive") is True:
                        row["Proj"] = "0"
                        record["status"] = "confirmed_inactive_zeroed"
                        result.append(record)
                        seen.add(player_id)
                        continue
                    if entry.get("active_role") is not True:
                        raise InsufficientMarket("Active MLB lineup/SP or NHL line/goalie role unverified")
                    kind = entry.get("kind")
                    if (sport, kind) not in PROJECTORS:
                        raise ValueError(f"Unsupported role for {sport}: {kind}")
                    calc = PROJECTORS[sport, kind](entry)
                else:
                    calc = project_player(entry)
                mult = 1.5 if row.get("Roster Position", "").upper() == "CPT" else 1.0
                row["Proj"] = f'{calc["projection"] * mult:.4f}'
                record.update(calc)
                record["status"] = ("market_component_projection"
                                    if any(v not in ("industry_component_prior",)
                                           for v in calc["provenance"].values())
                                    else "industry_component_projection")
                record["captain_multiplier"] = mult
            except InsufficientMarket as exc:
                record["status"] = "uncovered_source_preserved"
                record["reason"] = str(exc)
        result.append(record)
        seen.add(player_id)
    unknown = sorted(set(players) - seen)
    if unknown:
        raise ValueError(f"Market inputs contain unknown DFS IDs: {unknown}")
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row["status"] for row in result)
    positive = sum(row["source_projection"] > 0 for row in result)
    active = [row for row in result if row["source_projection"] > 0 and
              players.get(row["dfs_id"], {}).get("active_role") is True]
    coverage = {"full_positive_pool": positive, "active_role_mapped_pool": len(active),
                "status_counts": dict(counts),
                "market_supported_active": sum(row["status"] == "market_component_projection"
                                               for row in active),
                "source_preserved_active": sum(row["status"] == "uncovered_source_preserved"
                                               for row in active)}
    audit.write_text(json.dumps({"sport": sport, "site": "DraftKings",
                                 "slate": data["slate"], "as_of_utc": data["as_of_utc"],
                                 "coverage": coverage, "rows": result}, indent=2) + "\n")


build_nfl_import = build_import


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditable DK NFL/MLB/NHL prop conversion (preview)")
    parser.add_argument("--source", type=Path, required=True, help="Original Savant CSV")
    parser.add_argument("--inputs", type=Path, required=True, help="Structured market JSON")
    parser.add_argument("--output", type=Path, required=True, help="New Savant CSV")
    parser.add_argument("--audit", type=Path, required=True, help="Per-player provenance JSON")
    args = parser.parse_args()
    build_import(args.source, args.inputs, args.output, args.audit)


if __name__ == "__main__":
    main()
