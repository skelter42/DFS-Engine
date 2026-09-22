"""The Odds API (v4) source: one request path, many sportsbooks.

This is the workhorse for the multi-book sweep ``core/MARKET_INPUTS.md``
requires -- DraftKings, FanDuel, BetMGM, Caesars, bet365, Fanatics and others
come back from the same event call, with both sides priced, so markets can be
de-vigged and consensused rather than read off one book.

Set ``ODDS_API_KEY`` in the environment. Player props are per-event on this API,
so a slate costs roughly one request per game per market group; the snapshot
cache keeps repeated sweeps cheap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

from ..models import GameEnvironment, MarketSnapshot, PropMarket, normalize_name
from ..odds.conversions import BookQuote
from .base import HttpClient, MarketSource, MarketSourceError, SnapshotCache, env_key
from .catalog import (
    ODDS_API_SPORT_KEYS,
    ODDS_API_SPORT_MARKETS,
    canonical_stat,
)

log = logging.getLogger("dfs_engine.markets.the_odds_api")

BASE = "https://api.the-odds-api.com/v4"

DEFAULT_BOOKS = (
    "draftkings", "fanduel", "betmgm", "caesars", "betrivers",
    "williamhill_us", "bovada", "espnbet", "fanatics", "hardrockbet",
)


@dataclass
class TheOddsApiSource(MarketSource):
    """Multi-book player props + game lines."""

    api_key: str | None = None
    regions: str = "us,us2"
    books: tuple[str, ...] = DEFAULT_BOOKS
    include_alternates: bool = True
    cache_ttl: int = 300
    client: HttpClient | None = None
    name: str = "the_odds_api"

    def __post_init__(self) -> None:
        self.api_key = self.api_key or env_key("ODDS_API_KEY", "THE_ODDS_API_KEY")
        if self.client is None:
            self.client = HttpClient(cache=SnapshotCache())

    def available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "ODDS_API_KEY is not set"
        return True, ""

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def fetch(self, sport: str, markets: Iterable[str] | None = None,
              max_events: int | None = None, **kwargs: Any) -> MarketSnapshot:
        snap = MarketSnapshot(sport=sport, sources=[self.name])
        ok, reason = self.available()
        if not ok:
            snap.errors.append(f"{self.name}: {reason}")
            return snap

        sport_key = ODDS_API_SPORT_KEYS.get(sport.lower())
        if not sport_key:
            snap.errors.append(f"{self.name}: no API sport key for {sport}")
            return snap

        try:
            events = self._game_lines(sport_key, snap)
        except MarketSourceError as exc:
            snap.errors.append(f"{self.name}: game lines failed ({exc})")
            return snap

        wanted = tuple(markets) if markets else ODDS_API_SPORT_MARKETS.get(sport.lower(), ())
        if self.include_alternates:
            wanted = wanted + tuple(f"{m}_alternate" for m in wanted
                                    if m.startswith("player_") or m.startswith("batter_")
                                    or m.startswith("pitcher_"))
        if not wanted:
            snap.errors.append(f"{self.name}: no prop markets configured for {sport}")
            return snap

        for i, event in enumerate(events):
            if max_events is not None and i >= max_events:
                break
            try:
                self._event_props(sport_key, event, wanted, snap)
            except MarketSourceError as exc:
                snap.errors.append(f"{self.name}: props for {event.get('id')} failed ({exc})")
        return snap

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _game_lines(self, sport_key: str, snap: MarketSnapshot) -> list[dict]:
        assert self.client is not None
        data = self.client.get_json(
            f"{BASE}/sports/{sport_key}/odds",
            params={
                "apiKey": self.api_key,
                "regions": self.regions,
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "bookmakers": ",".join(self.books) if self.books else None,
            },
            cache_ttl=self.cache_ttl,
        )
        events: list[dict] = []
        for ev in data or []:
            game = _game_from_event(ev, source=self.name)
            if game is not None:
                snap.games.append(game)
            events.append(ev)
        return events

    def _event_props(self, sport_key: str, event: dict, markets: tuple[str, ...],
                     snap: MarketSnapshot) -> None:
        assert self.client is not None
        event_id = event.get("id")
        if not event_id:
            return
        data = self.client.get_json(
            f"{BASE}/sports/{sport_key}/events/{event_id}/odds",
            params={
                "apiKey": self.api_key,
                "regions": self.regions,
                "markets": ",".join(markets),
                "oddsFormat": "american",
                "bookmakers": ",".join(self.books) if self.books else None,
            },
            cache_ttl=self.cache_ttl,
        )
        parse_event_props(data, snap, sport=snap.sport, source=self.name, game_id=event_id)


def _game_from_event(ev: dict, source: str) -> GameEnvironment | None:
    home, away = ev.get("home_team"), ev.get("away_team")
    if not home or not away:
        return None
    total, spread_home, ml_home, ml_away = _consensus_game_lines(ev, home, away)
    return GameEnvironment(
        game_id=str(ev.get("id") or f"{away}@{home}"),
        home_team=home,
        away_team=away,
        start_time=ev.get("commence_time"),
        total=total,
        spread_home=spread_home,
        home_moneyline=ml_home,
        away_moneyline=ml_away,
        source=source,
    )


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def _consensus_game_lines(ev: dict, home: str, away: str):
    totals: list[float] = []
    spreads: list[float] = []
    ml_home: list[float] = []
    ml_away: list[float] = []
    for bk in ev.get("bookmakers", []) or []:
        for mkt in bk.get("markets", []) or []:
            key = mkt.get("key")
            for out in mkt.get("outcomes", []) or []:
                name, point, price = out.get("name"), out.get("point"), out.get("price")
                if key == "totals" and name == "Over" and point is not None:
                    totals.append(float(point))
                elif key == "spreads" and name == home and point is not None:
                    spreads.append(float(point))
                elif key == "h2h" and price is not None:
                    if name == home:
                        ml_home.append(float(price))
                    elif name == away:
                        ml_away.append(float(price))
    return _median(totals), _median(spreads), _median(ml_home), _median(ml_away)


def parse_event_props(data: dict, snap: MarketSnapshot, sport: str, source: str,
                      game_id: str | None = None) -> int:
    """Parse one event-odds payload into :class:`PropMarket` objects.

    Split out from the client so recorded fixtures can exercise the parser
    without network access.
    """
    if not data:
        return 0
    game_id = str(data.get("id") or game_id or "")
    added = 0
    # (player, stat, line) -> {book: {"over": price, "under": price}}
    bucket: dict[tuple[str, str, float], dict[str, dict[str, float]]] = {}
    names: dict[str, str] = {}

    for bk in data.get("bookmakers", []) or []:
        book = bk.get("key") or bk.get("title") or "unknown"
        for mkt in bk.get("markets", []) or []:
            stat = canonical_stat(mkt.get("key", ""), sport=sport)
            if stat is None:
                continue
            updated = mkt.get("last_update")
            for out in mkt.get("outcomes", []) or []:
                player = out.get("description") or out.get("participant")
                price = out.get("price")
                if not player or price is None:
                    continue
                side = (out.get("name") or "").strip().lower()
                point = out.get("point")
                if side in {"yes", "no"}:
                    line = 0.5
                    side = "over" if side == "yes" else "under"
                elif side in {"over", "under"} and point is not None:
                    line = float(point)
                else:
                    continue
                key = (normalize_name(player), stat, round(line, 2))
                names.setdefault(key[0], player)
                entry = bucket.setdefault(key, {}).setdefault(book, {})
                entry[side] = float(price)
                entry["_ts"] = updated  # type: ignore[assignment]

    for (pkey, stat, line), by_book in bucket.items():
        quotes = [
            BookQuote(book=book, line=line, over=vals.get("over"),
                      under=vals.get("under"), timestamp=vals.get("_ts"))
            for book, vals in by_book.items()
            if vals.get("over") is not None or vals.get("under") is not None
        ]
        if not quotes:
            continue
        snap.add_prop(PropMarket(
            player_key=pkey, player_name=names.get(pkey, pkey), stat=stat,
            quotes=quotes, sources={source}, game_id=game_id or None,
        ))
        added += 1
    return added
