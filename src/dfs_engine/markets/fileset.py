"""Offline market sources: engine snapshots and generic CSV prop exports.

Two jobs:

1. Persist a sweep so a build is reproducible and auditable after lock.
2. Accept prop data from anywhere else -- an Action Network export, a
   PropCruncher pull, a hand-built CSV -- without needing a bespoke scraper.
   Any aggregator the user can get a table out of is one CSV away from the
   sweep, which is what keeps the "escalate to another source" rule in
   ``core/MARKET_INPUTS.md`` practical.

Expected CSV columns (header names are matched case-insensitively, extras
ignored)::

    player, stat, line, book, over, under[, team, game_id, timestamp]

``stat`` may be a canonical name or any recognisable book label
("Passing Yards", "player_pass_yds", "Total Bases").
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ..models import GameEnvironment, MarketSnapshot, PropMarket, normalize_name, safe_float
from ..odds.conversions import BookQuote
from .base import MarketSource
from .catalog import canonical_stat


def normalize_header(name: str) -> str:
    """Header matching ignores case, spaces and punctuation ("Over Odds" -> over_odds)."""
    return re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")


# --------------------------------------------------------------------------
# Serialisation
# --------------------------------------------------------------------------


def snapshot_to_dict(snap: MarketSnapshot) -> dict:
    return {
        "sport": snap.sport,
        "fetched_at": snap.fetched_at,
        "sources": snap.sources,
        "errors": snap.errors,
        "games": [
            {
                "game_id": g.game_id, "home_team": g.home_team, "away_team": g.away_team,
                "start_time": g.start_time, "total": g.total, "spread_home": g.spread_home,
                "home_moneyline": g.home_moneyline, "away_moneyline": g.away_moneyline,
                "home_team_total": g.home_team_total, "away_team_total": g.away_team_total,
                "weather": g.weather, "source": g.source,
            }
            for g in snap.games
        ],
        "props": [
            {
                "player_key": m.player_key, "player_name": m.player_name, "stat": m.stat,
                "team": m.team, "game_id": m.game_id, "sources": sorted(m.sources),
                "quotes": [
                    {"book": q.book, "line": q.line, "over": q.over,
                     "under": q.under, "timestamp": q.timestamp}
                    for q in m.quotes
                ],
            }
            for m in snap.props.values()
        ],
    }


def snapshot_from_dict(data: dict) -> MarketSnapshot:
    snap = MarketSnapshot(
        sport=data.get("sport", "unknown"),
        fetched_at=data.get("fetched_at", ""),
        sources=list(data.get("sources", [])),
        errors=list(data.get("errors", [])),
    )
    for g in data.get("games", []) or []:
        snap.games.append(GameEnvironment(**{k: g.get(k) for k in (
            "game_id", "home_team", "away_team", "start_time", "total", "spread_home",
            "home_moneyline", "away_moneyline", "home_team_total", "away_team_total",
            "weather", "source")}))
    for m in data.get("props", []) or []:
        snap.add_prop(PropMarket(
            player_key=m.get("player_key") or normalize_name(m.get("player_name", "")),
            player_name=m.get("player_name", ""),
            stat=m["stat"],
            team=m.get("team"),
            game_id=m.get("game_id"),
            sources=set(m.get("sources", [])),
            quotes=[BookQuote(book=q["book"], line=float(q["line"]),
                              over=safe_float(q.get("over")), under=safe_float(q.get("under")),
                              timestamp=q.get("timestamp"))
                    for q in m.get("quotes", [])],
        ))
    return snap


def save_snapshot(snap: MarketSnapshot, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot_to_dict(snap), indent=2))
    return path


def load_snapshot(path: str | Path) -> MarketSnapshot:
    return snapshot_from_dict(json.loads(Path(path).read_text()))


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------


@dataclass
class JsonSnapshotSource(MarketSource):
    """Replay a saved sweep. Makes builds reproducible and tests offline."""

    path: str | Path = ""
    name: str = "snapshot_file"

    def available(self) -> tuple[bool, str]:
        return (Path(self.path).exists(), f"{self.path} not found")

    def fetch(self, sport: str, **kwargs: Any) -> MarketSnapshot:
        snap = load_snapshot(self.path)
        if snap.sport != sport:
            snap.errors.append(f"snapshot sport {snap.sport!r} != requested {sport!r}")
        if self.name not in snap.sources:
            snap.sources.append(self.name)
        return snap


@dataclass
class CsvPropSource(MarketSource):
    """Ingest a flat prop table exported from any aggregator or book."""

    path: str | Path = ""
    source_label: str = "csv"
    name: str = "csv_props"
    games_path: str | Path | None = None
    default_book: str = "consensus"
    _aliases: dict[str, tuple[str, ...]] = field(default_factory=lambda: {
        "player": ("player", "player_name", "name", "athlete", "participant"),
        "stat": ("stat", "market", "prop", "market_name", "category"),
        "line": ("line", "point", "points", "handicap", "total"),
        "book": ("book", "sportsbook", "bookmaker", "site"),
        "over": ("over", "over_odds", "over_price", "odds_over", "yes"),
        "under": ("under", "under_odds", "under_price", "odds_under", "no"),
        "team": ("team", "team_abbr"),
        "game_id": ("game_id", "event_id", "game"),
        "timestamp": ("timestamp", "updated", "last_update"),
    })

    def available(self) -> tuple[bool, str]:
        return (Path(self.path).exists(), f"{self.path} not found")

    def fetch(self, sport: str, **kwargs: Any) -> MarketSnapshot:
        snap = MarketSnapshot(sport=sport, sources=[self.source_label])
        rows = list(csv.DictReader(Path(self.path).open(newline="", encoding="utf-8-sig")))
        if not rows:
            snap.errors.append(f"{self.name}: {self.path} has no rows")
            return snap
        colmap = self._resolve_columns(rows[0].keys())
        missing = [k for k in ("player", "stat", "line") if k not in colmap]
        if missing:
            snap.errors.append(f"{self.name}: missing columns {missing}")
            return snap

        bucket: dict[tuple[str, str, float], list[BookQuote]] = {}
        names: dict[str, str] = {}
        meta: dict[tuple[str, str, float], tuple[str | None, str | None]] = {}
        for row in rows:
            player = (row.get(colmap["player"]) or "").strip()
            stat = canonical_stat(row.get(colmap["stat"], ""), sport=sport)
            line = safe_float(row.get(colmap["line"]))
            if not player or stat is None or line is None:
                continue
            over = safe_float(row.get(colmap.get("over", ""), None))
            under = safe_float(row.get(colmap.get("under", ""), None))
            if over is None and under is None:
                continue
            book = (row.get(colmap.get("book", ""), "") or self.default_book).strip().lower()
            key = (normalize_name(player), stat, round(float(line), 2))
            names.setdefault(key[0], player)
            meta[key] = (
                (row.get(colmap.get("team", "")) or None),
                (row.get(colmap.get("game_id", "")) or None),
            )
            bucket.setdefault(key, []).append(BookQuote(
                book=book or self.default_book, line=float(line), over=over, under=under,
                timestamp=row.get(colmap.get("timestamp", "")) or None,
            ))

        for (pkey, stat, _line), quotes in bucket.items():
            team, game_id = meta.get((pkey, stat, _line), (None, None))
            snap.add_prop(PropMarket(player_key=pkey, player_name=names[pkey], stat=stat,
                                     quotes=quotes, sources={self.source_label},
                                     team=team, game_id=game_id))
        if self.games_path:
            self._load_games(snap)
        return snap

    def _resolve_columns(self, headers: Iterable[str]) -> dict[str, str]:
        lookup = {normalize_header(h): h for h in headers if h}
        out: dict[str, str] = {}
        for canonical, aliases in self._aliases.items():
            for alias in aliases:
                key = normalize_header(alias)
                if key in lookup:
                    out[canonical] = lookup[key]
                    break
        return out

    def _load_games(self, snap: MarketSnapshot) -> None:
        path = Path(str(self.games_path))
        if not path.exists():
            snap.errors.append(f"{self.name}: games file {path} not found")
            return
        for row in csv.DictReader(path.open(newline="", encoding="utf-8-sig")):
            low = {(k or "").strip().lower(): v for k, v in row.items()}
            home, away = low.get("home_team"), low.get("away_team")
            if not home or not away:
                continue
            snap.games.append(GameEnvironment(
                game_id=low.get("game_id") or f"{away}@{home}",
                home_team=home, away_team=away,
                start_time=low.get("start_time"),
                total=safe_float(low.get("total")),
                spread_home=safe_float(low.get("spread_home")),
                home_moneyline=safe_float(low.get("home_moneyline")),
                away_moneyline=safe_float(low.get("away_moneyline")),
                home_team_total=safe_float(low.get("home_team_total")),
                away_team_total=safe_float(low.get("away_team_total")),
                weather=low.get("weather"),
                source=self.source_label,
            ))
