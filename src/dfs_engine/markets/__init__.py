"""Market sweep: fetch Vegas props and game lines from multiple sites."""

from .aggregate import (
    MarketConsensus,
    consensus_by_player,
    consensus_for_market,
    coverage_report,
    merge_snapshots,
    sweep,
)
from .base import HttpClient, MarketSource, MarketSourceError, SnapshotCache
from .catalog import CANONICAL_STATS, canonical_stat
from .draftkings import DraftKingsSource
from .fileset import CsvPropSource, JsonSnapshotSource, load_snapshot, save_snapshot
from .the_odds_api import TheOddsApiSource

__all__ = [
    "CANONICAL_STATS", "CsvPropSource", "DraftKingsSource", "HttpClient",
    "JsonSnapshotSource", "MarketConsensus", "MarketSource", "MarketSourceError",
    "SnapshotCache", "TheOddsApiSource", "canonical_stat", "consensus_by_player",
    "consensus_for_market", "coverage_report", "load_snapshot", "merge_snapshots",
    "save_snapshot", "sweep", "default_sources",
]


def default_sources(sport: str, snapshot_path: str | None = None,
                    csv_path: str | None = None, use_live: bool = True) -> list[MarketSource]:
    """Standard sweep order: multi-book aggregator, then DK direct, then files."""
    sources: list[MarketSource] = []
    if use_live:
        sources.append(TheOddsApiSource())
        sources.append(DraftKingsSource())
    if csv_path:
        sources.append(CsvPropSource(path=csv_path))
    if snapshot_path:
        sources.append(JsonSnapshotSource(path=snapshot_path))
    return sources
