"""Turn a Python pull into one Proj.

Industry leaders and sportsbook props are co-primary. Neither is a fallback
for the other. Savant is the file skeleton and the last resort, not a third
equal vote. Savant 0 stays 0. Own is not touched.
"""

from __future__ import annotations

import math
from statistics import median


def american_to_implied(odds: float) -> float:
    odds = float(odds)
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return (-odds) / ((-odds) + 100.0)


def devig(over_odds: float, under_odds: float) -> float:
    po = american_to_implied(over_odds)
    pu = american_to_implied(under_odds)
    return po / (po + pu)


def poisson_count(p_one_plus: float) -> float:
    p = min(max(float(p_one_plus), 1e-9), 1 - 1e-9)
    return -math.log(1.0 - p)


def one_number(industry: list[float], vegas: float | None, savant: float) -> tuple[float, str]:
    """Return (proj, source_label)."""
    if savant == 0:
        return 0.0, "zero"
    ind = median(industry) if industry else None
    if ind is not None and vegas is not None:
        return (ind + vegas) / 2.0, "both"
    if vegas is not None:
        return float(vegas), "vegas"
    if ind is not None:
        return float(ind), "industry"
    return float(savant), "savant"


def blend_frame(rows: list[dict]) -> list[dict]:
    """rows need name, dfs_id, own, savant, industry (list), vegas (float|None)."""
    out = []
    for row in rows:
        proj, label = one_number(row.get("industry") or [], row.get("vegas"), float(row["savant"]))
        out.append(
            {
                "Name": row["name"],
                "DFS ID": row["dfs_id"],
                "Proj": f"{proj:.2f}",
                "Own": row["own"],
                "source": label,
                "industry_median": None if not row.get("industry") else round(median(row["industry"]), 2),
                "vegas": None if row.get("vegas") is None else round(float(row["vegas"]), 2),
                "savant": row["savant"],
            }
        )
    return out
