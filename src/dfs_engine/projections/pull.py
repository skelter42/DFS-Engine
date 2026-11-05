"""Pull posted sportsbook props for any slate.

Inputs are sport and date. Nothing in this module is a player, a game, or a slate.
A summarized page fetch is not a source. Reject a feed whose lines do not vary.
"""

from __future__ import annotations

import csv
from pathlib import Path

import requests

DK_BOOK = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1"


def _get(url: str, params: dict | None = None, timeout: int = 60) -> requests.Response:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response


def lines_vary(rows: list[dict]) -> bool:
    lines = {row.get("line") for row in rows if row.get("line") is not None}
    return len(lines) > 1


def pull_dk_category(league_id: int, category_id: int, subcategory_id: int) -> list[dict]:
    """DraftKings sportsbook JSON for a league category. Ids come from the sport module."""
    url = f"{DK_BOOK}/leagues/{league_id}/categories/{category_id}/subcategories/{subcategory_id}"
    payload = _get(url).json()
    return list(payload.get("markets", []) or payload.get("selections", []) or [])


def write_rows(path: str | Path, rows: list[dict]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return 0
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames and not isinstance(row[key], (dict, list)):
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
