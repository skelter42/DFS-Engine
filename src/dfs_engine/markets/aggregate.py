"""Run the sportsbook sweep across sources and reconcile it into one snapshot.

``core/MARKET_INPUTS.md`` is explicit that one book is not a market: this module
merges every source, de-duplicates the same book arriving by two paths, and
produces per-line cross-book consensus probabilities with a dispersion measure
that the projection layer uses to grade confidence.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from ..models import MarketSnapshot, PropMarket
from ..odds.conversions import (
    DEFAULT_ONE_SIDED_MULTIPLIER,
    BookQuote,
    ConsensusPoint,
    consensus_over_prob,
)
from .base import MarketSource

log = logging.getLogger("dfs_engine.markets.aggregate")


def _quote_rank(q: BookQuote) -> tuple[int, str]:
    """Prefer two-sided quotes, then the most recent timestamp."""
    return (1 if q.two_sided else 0, q.timestamp or "")


def dedupe_quotes(quotes: Sequence[BookQuote]) -> list[BookQuote]:
    """One quote per (book, line): the same book can arrive from several sources."""
    best: dict[tuple[str, float], BookQuote] = {}
    for q in quotes:
        key = (q.book.lower(), round(q.line, 2))
        current = best.get(key)
        if current is None or _quote_rank(q) > _quote_rank(current):
            best[key] = q
    return list(best.values())


def merge_snapshots(snapshots: Iterable[MarketSnapshot], sport: str | None = None) -> MarketSnapshot:
    snaps = [s for s in snapshots if s is not None]
    if not snaps:
        return MarketSnapshot(sport=sport or "unknown")
    out = MarketSnapshot(sport=sport or snaps[0].sport)
    seen_games: set[tuple[str, str]] = set()
    for snap in snaps:
        out.sources.extend(s for s in snap.sources if s not in out.sources)
        out.errors.extend(snap.errors)
        for g in snap.games:
            key = (g.home_team.lower(), g.away_team.lower())
            if key in seen_games:
                existing = next(x for x in out.games
                                if (x.home_team.lower(), x.away_team.lower()) == key)
                for fld in ("total", "spread_home", "home_moneyline", "away_moneyline",
                            "home_team_total", "away_team_total", "start_time", "weather"):
                    if getattr(existing, fld) is None and getattr(g, fld) is not None:
                        setattr(existing, fld, getattr(g, fld))
                continue
            seen_games.add(key)
            out.games.append(g)
        for market in snap.props.values():
            out.add_prop(PropMarket(
                player_key=market.player_key, player_name=market.player_name,
                stat=market.stat, quotes=list(market.quotes),
                sources=set(market.sources), team=market.team, game_id=market.game_id,
            ))
    for market in out.props.values():
        market.quotes = dedupe_quotes(market.quotes)
    return out


def sweep(sport: str, sources: Sequence[MarketSource], **kwargs) -> MarketSnapshot:
    """Fetch from every configured source; a failing source is logged, not fatal."""
    snaps: list[MarketSnapshot] = []
    for src in sources:
        ok, reason = src.available()
        if not ok:
            log.info("skipping source %s: %s", src.name, reason)
            skipped = MarketSnapshot(sport=sport)
            skipped.errors.append(f"{src.name}: skipped ({reason})")
            snaps.append(skipped)
            continue
        try:
            snaps.append(src.fetch(sport, **kwargs))
        except Exception as exc:  # noqa: BLE001 - one bad source must not kill the sweep
            log.warning("source %s failed: %s", src.name, exc)
            failed = MarketSnapshot(sport=sport)
            failed.errors.append(f"{src.name}: {exc}")
            snaps.append(failed)
    return merge_snapshots(snaps, sport=sport)


@dataclass
class MarketConsensus:
    """De-vigged market state for one player/stat.

    ``points`` collapses every book at each line (probability-space consensus).
    ``by_book`` keeps each book's own ladder intact so the projection layer can
    instead fit a mean per book and take the median of those means -- the
    documented consensus rule in ``sports/nfl.md``.
    """

    stat: str
    points: list[ConsensusPoint]
    books: set[str]
    sources: set[str]
    by_book: dict[str, list[ConsensusPoint]] = field(default_factory=dict)

    @property
    def n_books(self) -> int:
        return len(self.books)

    @property
    def n_lines(self) -> int:
        return len(self.points)

    @property
    def two_sided_lines(self) -> int:
        return sum(1 for p in self.points if p.two_sided_books > 0)

    @property
    def dispersion(self) -> float:
        if not self.points:
            return 0.0
        return sum(p.dispersion for p in self.points) / len(self.points)


def consensus_for_market(market: PropMarket, method: str = "multiplicative",
                         trim: float = 0.0, min_books: int = 1,
                         one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER
                         ) -> MarketConsensus | None:
    """Collapse one player/stat into robust per-line fair probabilities."""
    points: list[ConsensusPoint] = []
    for line, quotes in sorted(market.lines().items()):
        point = consensus_over_prob(quotes, method=method, trim=trim,
                                    one_sided_multiplier=one_sided_multiplier)
        if point is None or point.n_books < min_books:
            continue
        if not 0.001 < point.prob_over < 0.999:
            continue  # a pinned market carries no information about the mean
        points.append(point)
    if not points:
        return None

    by_book: dict[str, list[ConsensusPoint]] = {}
    for quote in market.quotes:
        fair = quote.fair_over(method, one_sided_multiplier)
        if fair is None or not 0.001 < fair < 0.999:
            continue
        by_book.setdefault(quote.book.lower(), []).append(ConsensusPoint(
            line=quote.line, prob_over=fair, n_books=1, books=[quote.book],
            two_sided_books=int(quote.two_sided)))

    return MarketConsensus(stat=market.stat, points=points, books=market.books,
                           sources=set(market.sources), by_book=by_book)


def consensus_by_player(snapshot: MarketSnapshot, method: str = "multiplicative",
                        trim: float = 0.0, min_books: int = 1,
                        one_sided_multiplier: float = DEFAULT_ONE_SIDED_MULTIPLIER
                        ) -> dict[str, dict[str, MarketConsensus]]:
    """``{player_key: {stat: MarketConsensus}}`` for the whole slate."""
    out: dict[str, dict[str, MarketConsensus]] = {}
    for (pkey, stat), market in snapshot.props.items():
        cons = consensus_for_market(market, method=method, trim=trim, min_books=min_books,
                                    one_sided_multiplier=one_sided_multiplier)
        if cons is not None:
            out.setdefault(pkey, {})[stat] = cons
    return out


def coverage_report(snapshot: MarketSnapshot, player_keys: Iterable[str]) -> dict:
    """Sweep coverage against the *likely active pool*, per the market-inputs audit."""
    keys = list(player_keys)
    by_player = {k[0] for k in snapshot.props}
    covered = [k for k in keys if k in by_player]
    market_counts = {}
    for k in covered:
        market_counts[k] = len(snapshot.for_player(k))
    rich = sum(1 for v in market_counts.values() if v >= 3)
    supported = sum(1 for v in market_counts.values() if 1 <= v < 3)
    return {
        "pool_size": len(keys),
        "players_with_any_market": len(covered),
        "coverage_pct": round(100.0 * len(covered) / max(len(keys), 1), 1),
        "multi_market_players": rich,
        "single_or_double_market_players": supported,
        "uncovered": sorted(set(keys) - set(covered)),
        "books": sorted(snapshot.books),
        "sources": snapshot.sources,
        "errors": snapshot.errors,
    }
