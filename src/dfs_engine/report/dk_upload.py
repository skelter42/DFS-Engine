"""Fill DraftKings' own bulk-entry template with the built lineups.

DraftKings does not accept an arbitrary lineup file. You download a template
from the contest lobby -- one row per entry you already own, carrying Entry ID,
Contest Name, Contest ID and Entry Fee -- and fill in the roster columns. Those
first four columns identify the entry and must survive untouched; only the
roster slots get written.

This keeps the last mile from being a manual copy-paste, which is where a
correct portfolio most easily turns into a wrong upload.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from ..models import Lineup

ENTRY_ID_HEADERS = {"entry id", "entryid"}
CONTEST_NAME_HEADERS = {"contest name", "contestname"}
PASSTHROUGH_HEADERS = {"entry id", "entryid", "contest name", "contestname",
                       "contest id", "contestid", "entry fee", "entryfee"}


@dataclass
class TemplateFill:
    path: Path
    rows_filled: int = 0
    rows_in_template: int = 0
    lineups_used: int = 0
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (f"{self.rows_filled} of {self.rows_in_template} template rows filled "
                f"from {self.lineups_used} lineups")


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def player_cell(player) -> str:
    """DraftKings' own ``Name (ID)`` form; falls back to the name alone."""
    return f"{player.name} ({player.dfs_id})" if player.dfs_id else player.name


def fill_dk_template(lineups: Sequence[Lineup], slot_names: Sequence[str],
                     template_path: str | Path, out_path: str | Path) -> TemplateFill:
    """Write the lineups into a copy of DraftKings' entry template.

    Entries are matched to lineups by contest name where the template provides
    one, so a multi-contest portfolio lands in the contests it was allocated to
    rather than in template order.
    """
    template_path, out_path = Path(template_path), Path(out_path)
    rows = list(csv.reader(template_path.open(newline="", encoding="utf-8-sig")))
    if not rows:
        raise ValueError(f"{template_path} is empty")

    header_idx = next((i for i, row in enumerate(rows)
                       if any(_norm(c) in ENTRY_ID_HEADERS for c in row)), None)
    if header_idx is None:
        raise ValueError(
            f"{template_path} has no 'Entry ID' column -- this should be the entry "
            "template downloaded from the DraftKings contest lobby, not the salary file")
    header = rows[header_idx]
    lookup = {_norm(c): i for i, c in enumerate(header)}

    # Roster columns are the template's own slot headers, in order. Duplicated
    # slot names (RB, RB) are matched positionally.
    wanted = [s.upper() for s in slot_names]
    roster_cols: list[int] = []
    used: set[int] = set()
    for slot in wanted:
        for i, cell in enumerate(header):
            if i in used or i in roster_cols:
                continue
            if _norm(cell) == _norm(slot) and _norm(cell) not in PASSTHROUGH_HEADERS:
                roster_cols.append(i)
                break
    if len(roster_cols) != len(wanted):
        missing = set(wanted) - {header[i].upper() for i in roster_cols}
        raise ValueError(
            f"template roster columns {sorted(missing)} not found; expected "
            f"{wanted} to match the contest's roster format")

    contest_col = next((i for name, i in lookup.items() if name in CONTEST_NAME_HEADERS), None)

    by_contest: dict[str, list[Lineup]] = {}
    pool: list[Lineup] = []
    for lu in lineups:
        if lu.contest:
            by_contest.setdefault(lu.contest, []).append(lu)
        else:
            pool.append(lu)

    result = TemplateFill(path=out_path)
    entry_col = next(i for name, i in lookup.items() if name in ENTRY_ID_HEADERS)

    for row in rows[header_idx + 1:]:
        if len(row) <= entry_col or not row[entry_col].strip():
            continue
        result.rows_in_template += 1
        lineup = None
        if contest_col is not None and len(row) > contest_col:
            name = row[contest_col].strip()
            for key, queue in by_contest.items():
                if queue and (key == name or _norm(key) in _norm(name)
                              or _norm(name) in _norm(key)):
                    lineup = queue.pop(0)
                    break
        if lineup is None:
            for queue in by_contest.values():
                if queue:
                    lineup = queue.pop(0)
                    break
        if lineup is None and pool:
            lineup = pool.pop(0)
        if lineup is None:
            continue

        by_slot: dict[str, list[str]] = {}
        for player, slot in zip(lineup.players, lineup.slots or wanted):
            by_slot.setdefault(slot.upper(), []).append(player_cell(player))
        taken: dict[str, int] = {}
        while len(row) < len(header):
            row.append("")
        for slot, col in zip(wanted, roster_cols):
            i = taken.get(slot, 0)
            values = by_slot.get(slot, [])
            row[col] = values[i] if i < len(values) else ""
            taken[slot] = i + 1
        result.rows_filled += 1
        result.lineups_used += 1

    leftover = sum(len(q) for q in by_contest.values()) + len(pool)
    if leftover:
        result.warnings.append(
            f"{leftover} lineup(s) had no template row to go in -- the template has "
            f"{result.rows_in_template} entries; enter more in the contest or build fewer")
    if result.rows_filled < result.rows_in_template:
        result.warnings.append(
            f"{result.rows_in_template - result.rows_filled} template row(s) left blank -- "
            "you have more entries than lineups built")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)
    return result
