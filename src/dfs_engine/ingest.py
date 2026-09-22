"""Read the site player pool and the vendor baseline.

The vendor file is an immutable baseline (``core/ENGINE.md``): its projections
and ownership are preserved exactly as supplied for later comparison, and its
player identity text is never rewritten -- normalisation happens only in the
matching key, never in ``name`` or ``dfs_id``.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .models import GameEnvironment, Player, normalize_name, positions_from_string, safe_float

#: column aliases seen across DraftKings exports, FanDuel exports and vendor files
ALIASES: dict[str, tuple[str, ...]] = {
    "name": ("name", "player", "nickname", "player name", "full name"),
    "id": ("id", "dfs id", "player id", "playerid", "dfs_id", "name + id"),
    "position": ("roster position", "position", "pos"),
    "base_position": ("position", "pos"),
    "salary": ("salary", "sal", "cost"),
    "team": ("teamabbrev", "team", "team abbrev", "tm"),
    "opponent": ("opponent", "opp", "opp team"),
    "game": ("game info", "game", "gameinfo", "matchup"),
    "projection": ("proj", "projection", "fpts", "points", "avgpointspergame",
                   "avg points per game", "my proj", "projected points"),
    "ownership": ("own", "ownership", "proj own", "projected ownership", "own%"),
    "status": ("status", "injury", "injury status", "inj"),
    "order": ("batting order", "order", "lineup order"),
}


def normalize_header(name: str) -> str:
    """Header matching ignores case, spaces and punctuation ("Name + ID" -> name_id)."""
    return re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")


def _resolve(headers: Iterable[str]) -> dict[str, str]:
    lookup = {normalize_header(h): h for h in headers}
    out: dict[str, str] = {}
    for key, aliases in ALIASES.items():
        for alias in aliases:
            alias_key = normalize_header(alias)
            if alias_key in lookup:
                out[key] = lookup[alias_key]
                break
    return out


GAME_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9.]{1,4})\s*@\s*([A-Za-z][A-Za-z0-9.]{1,4})\b")


def parse_game_info(raw: str) -> tuple[str | None, str | None]:
    """``"KC@BUF 09/22/2026 01:00PM ET"`` -> ``("KC", "BUF")`` (away, home)."""
    if not raw:
        return None, None
    match = GAME_RE.search(raw)
    if not match:
        return None, None
    return match.group(1).strip().upper(), match.group(2).strip().upper()


def _roster_role(sport: str, positions: Sequence[str]) -> str:
    pos = {p.upper() for p in positions}
    sport = sport.lower()
    if sport == "mlb":
        return "pitcher" if pos & {"P", "SP", "RP"} else "hitter"
    if sport == "nhl":
        return "goalie" if "G" in pos else "skater"
    if sport in {"nfl", "ncaaf"} and pos & {"DST", "DEF", "D"}:
        return "dst"
    return "all"


def load_player_pool(path: str | Path, sport: str, site: str = "dk",
                     vendor: Mapping[str, Mapping[str, float]] | None = None
                     ) -> tuple[list[Player], list[GameEnvironment]]:
    """Load a site salary export (optionally merged with a vendor projection file)."""
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8-sig")))
    if not rows:
        raise ValueError(f"{path} contains no rows")
    cols = _resolve(rows[0].keys())
    if "name" not in cols or "salary" not in cols:
        raise ValueError(f"{path} needs at least name and salary columns; found "
                         f"{sorted(rows[0].keys())}")

    players: list[Player] = []
    games: dict[str, GameEnvironment] = {}
    seen_ids: set[str] = set()

    for i, row in enumerate(rows):
        # Identity text is copied verbatim -- no trimming, case folding or accent
        # normalisation (player-identity rule, core/MARKET_INPUTS.md).
        name = row.get(cols["name"]) or ""
        if not name.strip():
            continue
        salary = safe_float(row.get(cols["salary"]), 0.0) or 0.0
        raw_id = (row.get(cols.get("id", "")) or "").strip()
        pid = raw_id or f"{sport}-{i}-{normalize_name(name).replace(' ', '_')}"
        if pid in seen_ids:
            pid = f"{pid}-{i}"
        seen_ids.add(pid)

        positions = positions_from_string(row.get(cols.get("position", ""), "")) or \
            positions_from_string(row.get(cols.get("base_position", ""), ""))
        team = (row.get(cols.get("team", "")) or "").strip().upper()
        away, home = parse_game_info(row.get(cols.get("game", "")) or "")
        opponent = (row.get(cols.get("opponent", "")) or "").strip().upper() or None
        game_id = None
        if away and home:
            game_id = f"{away}@{home}"
            if game_id not in games:
                games[game_id] = GameEnvironment(game_id=game_id, home_team=home,
                                                 away_team=away, source="player_pool")
            if not opponent and team:
                opponent = home if team == away else away

        vendor_row = (vendor or {}).get(normalize_name(name), {})
        projection = vendor_row.get("projection")
        if projection is None and "projection" in cols:
            projection = safe_float(row.get(cols["projection"]))
        ownership = vendor_row.get("ownership")
        if ownership is None and "ownership" in cols:
            ownership = safe_float(row.get(cols["ownership"]))

        players.append(Player(
            player_id=pid,
            name=name,
            dfs_id=raw_id,
            team=team or "?",
            positions=positions or ("UTIL",),
            salary=int(salary),
            sport=sport.lower(),
            site=site.lower(),
            opponent=opponent,
            game_id=game_id,
            home=(team == home) if (team and home) else None,
            roster_role=_roster_role(sport, positions),
            vendor_projection=projection,
            vendor_ownership=ownership,
            status=(row.get(cols.get("status", "")) or "active").strip() or "active",
            batting_order=int(safe_float(row.get(cols.get("order", "")), 0) or 0) or None,
        ))
    return players, list(games.values())


def load_vendor_file(path: str | Path) -> dict[str, dict[str, float]]:
    """Vendor baseline keyed by the matching key; original text is not modified."""
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8-sig")))
    if not rows:
        return {}
    cols = _resolve(rows[0].keys())
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        name = row.get(cols.get("name", "")) or ""
        if not name.strip():
            continue
        entry: dict[str, float] = {}
        proj = safe_float(row.get(cols.get("projection", "")))
        own = safe_float(row.get(cols.get("ownership", "")))
        if proj is not None:
            entry["projection"] = proj
        if own is not None:
            entry["ownership"] = own
        if entry:
            out[normalize_name(name)] = entry
    return out


def apply_game_markets(players: Sequence[Player], games: Sequence[GameEnvironment]) -> None:
    """Fill each player's opponent/home flag from the resolved game list."""
    by_team: dict[str, GameEnvironment] = {}
    for g in games:
        by_team[g.home_team] = g
        by_team[g.away_team] = g
    for p in players:
        game = by_team.get(p.team)
        if game is None:
            continue
        p.game_id = p.game_id or game.game_id
        p.opponent = p.opponent or game.opponent_of(p.team)
        if p.home is None:
            p.home = p.team == game.home_team
