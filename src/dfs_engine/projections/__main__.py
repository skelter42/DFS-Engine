"""python -m dfs_engine.projections --sport mlb --savant slate.csv --vegas vegas.csv --industry industry.csv --out upload.csv

Pulls are Python. A chat summary of a prop page is not an input.
This does not write an upload from Savant alone. A blend needs a pulled board.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from dfs_engine.projections.blend import blend_frame
from dfs_engine.projections.pull import MLB_PROP_MARKETS, NHL_PROP_MARKETS, pull_odds_api, write_rows


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def index_numbers(path: Path, value_field: str) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in read_csv(path):
        name = row.get("Name") or row.get("player") or row.get("Player")
        if not name or row.get(value_field) in (None, ""):
            continue
        grouped[name].append(float(row[value_field]))
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull industry + books in Python and blend to one Proj.")
    parser.add_argument("--sport", required=True, choices=["mlb", "nhl", "nfl", "nba"])
    parser.add_argument("--savant", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--vegas", type=Path, help="CSV with Name and Vegas columns. Vegas is already site points.")
    parser.add_argument("--industry", type=Path, help="CSV with Name and Proj columns, one row per site.")
    parser.add_argument("--pull", action="store_true", help="Hit The Odds API. Requires ODDS_API_KEY.")
    parser.add_argument("--raw", type=Path, help="Where the raw prop rows are written.")
    args = parser.parse_args()

    if args.pull:
        markets = MLB_PROP_MARKETS if args.sport == "mlb" else NHL_PROP_MARKETS
        raw_rows = pull_odds_api(args.sport, markets)
        dest = args.raw or Path(f"{args.sport}-props-raw.csv")
        n = write_rows(dest, raw_rows)
        print(f"prop rows pulled: {n} -> {dest}")
        if n < 100:
            raise SystemExit("prop pull is too small to be a board. Do not blend a summarized fetch.")

    if args.out is None:
        return
    if args.vegas is None and args.industry is None:
        raise SystemExit("refusing to write Proj from Savant alone. Pass --vegas and/or --industry from a Python pull.")

    vegas = {}
    if args.vegas:
        for name, values in index_numbers(args.vegas, "Vegas").items():
            vegas[name] = values[0]
    industry = index_numbers(args.industry, "Proj") if args.industry else {}

    rows = []
    for raw in read_csv(args.savant):
        name = raw["Name"]
        rows.append(
            {
                "name": name,
                "dfs_id": raw.get("DFS ID") or raw.get("DFS_ID"),
                "own": raw["Own"],
                "savant": float(raw["Proj"]),
                "industry": industry.get(name, []),
                "vegas": vegas.get(name),
            }
        )
    blended = blend_frame(rows)
    counts = Counter(row["source"] for row in blended)
    print("source mix:", dict(counts))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Name", "DFS ID", "Proj", "Own"])
        writer.writeheader()
        for row in blended:
            writer.writerow({k: row[k] for k in writer.fieldnames})
    if args.audit:
        with args.audit.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(blended[0].keys()))
            writer.writeheader()
            writer.writerows(blended)


if __name__ == "__main__":
    main()
