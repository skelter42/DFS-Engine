"""DraftKings Sportsbook public content API.

A free, key-less second touch point for the sweep. It is a single book, so it
cannot satisfy the multi-book consensus rule on its own -- its role is to widen
coverage (DK posts deep alternate ladders) and to sanity-check the aggregator.

DraftKings reshapes these endpoints periodically. The parser is deliberately
defensive and tolerates both the ``sportscontent`` v1 payload and the older
``eventgroups`` v5 payload; anything it cannot read is reported as a source
error rather than silently dropped.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..models import GameEnvironment, MarketSnapshot, PropMarket, normalize_name
from ..odds.conversions import BookQuote
from .base import HttpClient, MarketSource, MarketSourceError, SnapshotCache
from .catalog import DK_LEAGUE_IDS, canonical_stat

log = logging.getLogger("dfs_engine.markets.draftkings")

CONTENT_BASE = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1"
LEGACY_BASE = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups"

_OVER_LABELS = {"over", "o", "yes", "more"}
_UNDER_LABELS = {"under", "u", "no", "less"}


@dataclass
class DraftKingsSource(MarketSource):
    """Single-book source: DraftKings' own posted markets."""

    cache_ttl: int = 180
    client: HttpClient | None = None
    name: str = "draftkings"
    books: tuple[str, ...] = ("draftkings",)
    category_ids: dict[str, tuple[int, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = HttpClient(cache=SnapshotCache())

    def fetch(self, sport: str, **kwargs: Any) -> MarketSnapshot:
        snap = MarketSnapshot(sport=sport, sources=[self.name])
        league = DK_LEAGUE_IDS.get(sport.lower())
        if not league:
            snap.errors.append(f"{self.name}: no DK league id for {sport}")
            return snap
        assert self.client is not None
        urls = [f"{CONTENT_BASE}/leagues/{league}"]
        for cat in self.category_ids.get(sport.lower(), ()):  # optional prop categories
            urls.append(f"{CONTENT_BASE}/leagues/{league}/categories/{cat}")
        got_any = False
        for url in urls:
            try:
                data = self.client.get_json(url, cache_ttl=self.cache_ttl)
            except MarketSourceError as exc:
                snap.errors.append(f"{self.name}: {url} failed ({exc})")
                continue
            try:
                parse_dk_payload(data, snap, sport=sport, source=self.name)
                got_any = True
            except Exception as exc:  # noqa: BLE001 - payload shape drifts
                snap.errors.append(f"{self.name}: parse failed for {url} ({exc})")
        if not got_any:
            snap.errors.append(f"{self.name}: no readable payload")
        return snap


def parse_dk_payload(data: dict, snap: MarketSnapshot, sport: str, source: str = "draftkings") -> int:
    """Parse a DK payload (either known shape) into games and prop markets."""
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    if "eventGroup" in data:
        return _parse_legacy(data["eventGroup"], snap, sport, source)
    return _parse_content_v1(data, snap, sport, source)


def _parse_content_v1(data: dict, snap: MarketSnapshot, sport: str, source: str) -> int:
    events = {str(e.get("id")): e for e in data.get("events", []) or []}
    for ev in events.values():
        game = _game_from_content_event(ev, source)
        if game is not None and not any(g.game_id == game.game_id for g in snap.games):
            snap.games.append(game)

    markets = {str(m.get("id")): m for m in data.get("markets", []) or []}
    bucket: dict[tuple[str, str, float], dict[str, float | str | None]] = {}
    names: dict[str, str] = {}
    games: dict[tuple[str, str, float], str | None] = {}

    for sel in data.get("selections", []) or []:
        market = markets.get(str(sel.get("marketId")))
        if not market:
            continue
        label = market.get("name") or (market.get("marketType") or {}).get("name") or ""
        stat = canonical_stat(label, sport=sport)
        if stat is None:
            continue
        player = _player_from_selection(sel, market)
        if not player:
            continue
        price = _american_from_selection(sel)
        if price is None:
            continue
        side = _side_from_label(sel.get("label") or sel.get("outcomeType") or "")
        if side is None:
            continue
        point = sel.get("points")
        if point is None:
            point = market.get("line")
        line = float(point) if point is not None else 0.5
        key = (normalize_name(player), stat, round(line, 2))
        names.setdefault(key[0], player)
        games[key] = str(market.get("eventId") or "") or None
        bucket.setdefault(key, {})[side] = price

    return _flush(bucket, names, games, snap, source)


def _parse_legacy(group: dict, snap: MarketSnapshot, sport: str, source: str) -> int:
    bucket: dict[tuple[str, str, float], dict[str, float | str | None]] = {}
    names: dict[str, str] = {}
    games: dict[tuple[str, str, float], str | None] = {}
    for cat in group.get("offerCategories", []) or []:
        for sub in cat.get("offerSubcategoryDescriptors", []) or []:
            stat = canonical_stat(sub.get("name", ""), sport=sport)
            subcat = sub.get("offerSubcategory") or {}
            for offers in subcat.get("offers", []) or []:
                for offer in offers or []:
                    offer_stat = stat or canonical_stat(offer.get("label", ""), sport=sport)
                    if offer_stat is None:
                        continue
                    event_id = str(offer.get("eventId") or "") or None
                    for out in offer.get("outcomes", []) or []:
                        player = out.get("participant") or out.get("label")
                        price = out.get("oddsAmerican")
                        if not player or price in (None, ""):
                            continue
                        side = _side_from_label(out.get("label", ""))
                        if side is None:
                            continue
                        line = float(out.get("line", 0.5) or 0.5)
                        key = (normalize_name(player), offer_stat, round(line, 2))
                        names.setdefault(key[0], player)
                        games[key] = event_id
                        bucket.setdefault(key, {})[side] = float(str(price).replace("+", ""))
    return _flush(bucket, names, games, snap, source)


def _flush(bucket, names, games, snap: MarketSnapshot, source: str) -> int:
    added = 0
    for (pkey, stat, line), sides in bucket.items():
        over = sides.get("over")
        under = sides.get("under")
        if over is None and under is None:
            continue
        snap.add_prop(PropMarket(
            player_key=pkey, player_name=names.get(pkey, pkey), stat=stat,
            quotes=[BookQuote(book="draftkings", line=line,
                              over=over if over is None else float(over),
                              under=under if under is None else float(under))],
            sources={source}, game_id=games.get((pkey, stat, line)),
        ))
        added += 1
    return added


def _game_from_content_event(ev: dict, source: str) -> GameEnvironment | None:
    parts = ev.get("participants") or []
    home = away = None
    for p in parts:
        role = (p.get("venueRole") or "").lower()
        if role == "home":
            home = p.get("name")
        elif role == "away":
            away = p.get("name")
    if not home or not away:
        name = ev.get("name") or ""
        if " at " in name:
            away, home = [s.strip() for s in name.split(" at ", 1)]
        elif " @ " in name:
            away, home = [s.strip() for s in name.split(" @ ", 1)]
    if not home or not away:
        return None
    return GameEnvironment(
        game_id=str(ev.get("id") or f"{away}@{home}"),
        home_team=home, away_team=away,
        start_time=ev.get("startEventDate") or ev.get("startDate"),
        source=source,
    )


def _player_from_selection(sel: dict, market: dict) -> str | None:
    for p in sel.get("participants", []) or []:
        if (p.get("type") or "").lower() in {"player", "athlete"} and p.get("name"):
            return p["name"]
    for p in market.get("participants", []) or []:
        if (p.get("type") or "").lower() in {"player", "athlete"} and p.get("name"):
            return p["name"]
    return market.get("playerName") or sel.get("participant")


def _american_from_selection(sel: dict) -> float | None:
    odds = sel.get("displayOdds") or {}
    raw = odds.get("american") if isinstance(odds, dict) else None
    raw = raw if raw not in (None, "") else sel.get("oddsAmerican")
    if raw in (None, ""):
        return None
    try:
        return float(str(raw).replace("+", "").replace("−", "-"))
    except ValueError:
        return None


def _side_from_label(label: str) -> str | None:
    txt = (label or "").strip().lower()
    if txt in _OVER_LABELS or txt.startswith("over"):
        return "over"
    if txt in _UNDER_LABELS or txt.startswith("under"):
        return "under"
    return None
