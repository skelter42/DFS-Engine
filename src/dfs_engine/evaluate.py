"""Paired, pre-lock projection scorecard against completed DK results."""

from __future__ import annotations

import argparse
import csv
import json
from math import sqrt
from pathlib import Path


def score_snapshot(audit: Path, actuals: Path) -> dict:
    snapshot = json.loads(audit.read_text())
    with actuals.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"DFS ID", "DK Points"}.issubset(reader.fieldnames or []):
            raise ValueError("Results need DFS ID and DK Points columns")
        actual = {}
        for row in reader:
            if row["DFS ID"] in actual:
                raise ValueError(f'Duplicate actual DFS ID: {row["DFS ID"]}')
            actual[row["DFS ID"]] = float(row["DK Points"])
    paired = []
    seen = set()
    for row in snapshot["rows"]:
        if row["status"] not in {"market_component_projection",
                                  "industry_component_projection"}:
            continue
        player_id = row["dfs_id"]
        if player_id not in actual or player_id in seen:
            continue
        # Evaluate one unmultiplied player projection per athlete, even if
        # Showdown CSV includes both CPT and FLEX rows for that DFS ID.
        multiplier = row.get("captain_multiplier", 1)
        baseline = row["source_projection"] / multiplier
        candidate = row["projection"]
        paired.append({"dfs_id": player_id, "source": baseline,
                       "engine": candidate, "actual": actual[player_id],
                       "status": row["status"]})
        seen.add(player_id)
    if not paired:
        raise ValueError("No paired projected players with actual results")

    def metrics(key: str) -> dict:
        errors = [r[key] - r["actual"] for r in paired]
        n = len(errors)
        return {"mae": sum(abs(x) for x in errors)/n,
                "rmse": sqrt(sum(x*x for x in errors)/n),
                "bias": sum(errors)/n}

    source = metrics("source")
    engine = metrics("engine")
    return {"sport": snapshot["sport"], "slate": snapshot["slate"],
            "as_of_utc": snapshot["as_of_utc"], "paired_count": len(paired),
            "source": source, "engine": engine,
            "engine_mae_minus_source": engine["mae"] - source["mae"],
            "rows": paired}


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade frozen DK projections")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--actuals", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    args.report.write_text(json.dumps(score_snapshot(args.audit, args.actuals), indent=2) + "\n")


if __name__ == "__main__":
    main()
