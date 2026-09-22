"""Core data model shared by every stage of the engine.

Layer separation is a hard rule in ``core/ENGINE.md``: vendor/source values are
immutable baselines, market-derived values are separate, and the final engine
value is a third column. The dataclasses here keep all three side by side so
the audit trail is a property of the data, not of a report generator.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Sequence

import numpy as np

from .odds.conversions import BookQuote

# --------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def normalize_name(name: str) -> str:
    """Matching key for joining sportsbook names to the source player pool.

    Used for *research matching only*. ``Player.name`` and ``Player.dfs_id``
    stay character-for-character as supplied -- see the player-identity rule in
    ``core/MARKET_INPUTS.md``.
    """
    txt = unicodedata.normalize("NFKD", name or "")
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.lower().replace("&", "and")
    txt = re.sub(r"[.'`’]", "", txt)
    txt = re.sub(r"[^a-z0-9]+", " ", txt).strip()
    parts = [p for p in txt.split() if p not in _SUFFIXES]
    return " ".join(parts)


# --------------------------------------------------------------------------
# Slate inputs
# --------------------------------------------------------------------------


@dataclass
class GameEnvironment:
    """Game-level market state: the anchor every player projection reconciles to."""

    game_id: str
    home_team: str
    away_team: str
    start_time: str | None = None
    total: float | None = None
    spread_home: float | None = None  # negative when home is favoured
    home_moneyline: float | None = None
    away_moneyline: float | None = None
    home_team_total: float | None = None
    away_team_total: float | None = None
    weather: str | None = None
    source: str | None = None

    def team_total(self, team: str) -> float | None:
        if team == self.home_team:
            if self.home_team_total is not None:
                return self.home_team_total
        elif team == self.away_team:
            if self.away_team_total is not None:
                return self.away_team_total
        else:
            return None
        if self.total is None or self.spread_home is None:
            return None
        half = self.total / 2.0
        edge = -self.spread_home / 2.0  # favourite scores more
        return half + edge if team == self.home_team else half - edge

    def opponent_of(self, team: str) -> str | None:
        if team == self.home_team:
            return self.away_team
        if team == self.away_team:
            return self.home_team
        return None

    @property
    def teams(self) -> tuple[str, str]:
        return (self.away_team, self.home_team)


@dataclass
class Player:
    """One row of the site player pool plus the vendor baseline."""

    player_id: str
    name: str
    team: str
    positions: tuple[str, ...]
    salary: int
    sport: str
    site: str = "dk"
    dfs_id: str = ""
    opponent: str | None = None
    game_id: str | None = None
    home: bool | None = None
    roster_role: str = "all"  # hitter/pitcher/skater/goalie/all -> selects scoring rule
    vendor_projection: float | None = None
    vendor_ownership: float | None = None
    status: str = "active"  # active | questionable | out
    batting_order: int | None = None
    depth_note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return normalize_name(self.name)

    @property
    def eligible(self) -> bool:
        """Source Projection Eligibility Gate (``core/ENGINE.md``).

        A current vendor projection of exactly zero excludes the player, as does
        a confirmed OUT. Missing vendor data is *not* an exclusion -- prebuilds
        before lineup confirmation are expected.
        """
        if self.status.lower() in {"out", "scratched", "inactive", "ir"}:
            return False
        if self.vendor_projection is not None and abs(self.vendor_projection) < 1e-9:
            return False
        return True

    @property
    def ineligible_reason(self) -> str | None:
        if self.status.lower() in {"out", "scratched", "inactive", "ir"}:
            return f"status={self.status}"
        if self.vendor_projection is not None and abs(self.vendor_projection) < 1e-9:
            return "source projection is zero (eligibility gate)"
        return None


@dataclass
class PropMarket:
    """Every book quote collected for one player/stat, across lines and sources."""

    player_key: str
    player_name: str
    stat: str
    quotes: list[BookQuote] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    team: str | None = None
    game_id: str | None = None

    def lines(self) -> dict[float, list[BookQuote]]:
        out: dict[float, list[BookQuote]] = {}
        for q in self.quotes:
            out.setdefault(round(q.line, 2), []).append(q)
        return out

    @property
    def books(self) -> set[str]:
        return {q.book for q in self.quotes}

    def merge(self, other: "PropMarket") -> None:
        self.quotes.extend(other.quotes)
        self.sources |= other.sources


@dataclass
class MarketSnapshot:
    """The result of a sportsbook sweep: games + player props + provenance."""

    sport: str
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    games: list[GameEnvironment] = field(default_factory=list)
    props: dict[tuple[str, str], PropMarket] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_prop(self, market: PropMarket) -> None:
        key = (market.player_key, market.stat)
        if key in self.props:
            self.props[key].merge(market)
        else:
            self.props[key] = market

    def for_player(self, player_key: str) -> dict[str, PropMarket]:
        return {stat: m for (pkey, stat), m in self.props.items() if pkey == player_key}

    def game_for_team(self, team: str) -> GameEnvironment | None:
        for g in self.games:
            if team in g.teams:
                return g
        return None

    @property
    def books(self) -> set[str]:
        out: set[str] = set()
        for m in self.props.values():
            out |= m.books
        return out

    def summary(self) -> dict:
        return {
            "sport": self.sport,
            "fetched_at": self.fetched_at,
            "games": len(self.games),
            "players_with_props": len({k[0] for k in self.props}),
            "prop_markets": len(self.props),
            "quotes": sum(len(m.quotes) for m in self.props.values()),
            "books": sorted(self.books),
            "sources": self.sources,
            "errors": self.errors,
        }


# --------------------------------------------------------------------------
# Engine outputs
# --------------------------------------------------------------------------

COVERAGE_TIERS = ("A", "B", "C", "D")
COVERAGE_LABELS = {
    "A": "Vegas-rich",
    "B": "Vegas-supported",
    "C": "Industry-supported",
    "D": "Fallback-heavy",
}


@dataclass
class PlayerProjection:
    """Vendor baseline, market projection, and the engine's blended output.

    ``samples`` is the player's market-implied fantasy-point distribution: the
    empirical marginal the slate simulator draws from.
    """

    player: Player
    components: dict[str, Any] = field(default_factory=dict)  # stat -> FittedStat
    samples: np.ndarray | None = None
    market_projection: float | None = None
    vendor_projection: float | None = None
    engine_projection: float = 0.0
    coverage: str = "D"
    coverage_score: float = 0.0
    market_weight: float = 0.0
    n_markets: int = 0
    n_books: int = 0
    notes: list[str] = field(default_factory=list)
    engine_ownership: float | None = None
    source_ownership: float | None = None
    ownership_confidence: str = "D"

    @property
    def coverage_label(self) -> str:
        return COVERAGE_LABELS.get(self.coverage, "unknown")

    @property
    def sd(self) -> float:
        if self.samples is None or len(self.samples) < 2:
            return 0.0
        return float(np.std(self.samples))

    @property
    def ceiling(self) -> float:
        """85th percentile: the ceiling metric used in candidate scoring."""
        if self.samples is None or len(self.samples) == 0:
            return self.engine_projection
        return float(np.percentile(self.samples, 85))

    @property
    def floor(self) -> float:
        if self.samples is None or len(self.samples) == 0:
            return self.engine_projection
        return float(np.percentile(self.samples, 15))

    def percentile(self, q: float) -> float:
        if self.samples is None or len(self.samples) == 0:
            return self.engine_projection
        return float(np.percentile(self.samples, q))

    @property
    def value(self) -> float:
        """Points per $1000 of salary."""
        if self.player.salary <= 0:
            return 0.0
        return self.engine_projection / (self.player.salary / 1000.0)

    @property
    def projection_delta(self) -> float | None:
        if self.vendor_projection is None:
            return None
        return self.engine_projection - self.vendor_projection

    def scaled_samples(self, n: int, rng: np.random.Generator) -> np.ndarray:
        if self.samples is None or len(self.samples) == 0:
            return np.full(n, self.engine_projection)
        return rng.choice(self.samples, size=n, replace=True)


@dataclass
class Lineup:
    """A roster in site slot order, with simulation and ownership metrics."""

    players: tuple[Player, ...]
    slots: tuple[str, ...] = ()
    salary: int = 0
    projection: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    contest: str | None = None
    index: int | None = None

    @property
    def player_ids(self) -> frozenset[str]:
        return frozenset(p.player_id for p in self.players)

    def overlap(self, other: "Lineup") -> int:
        return len(self.player_ids & other.player_ids)

    @property
    def teams(self) -> list[str]:
        return [p.team for p in self.players]

    def team_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self.players:
            out[p.team] = out.get(p.team, 0) + 1
        return out

    def game_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self.players:
            if p.game_id:
                out[p.game_id] = out.get(p.game_id, 0) + 1
        return out

    def signature(self) -> str:
        return "|".join(sorted(p.player_id for p in self.players))


@dataclass
class Contest:
    """Contest metadata driving allocation and field modelling."""

    name: str
    entries: int = 1
    field_size: int = 10000
    entry_fee: float = 0.0
    profile: str = "large_field_gpp"
    payout_top_fraction: float = 0.2
    priority: int = 1
    max_entries_per_user: int | None = None

    @property
    def is_single_entry(self) -> bool:
        return self.max_entries_per_user == 1 or self.profile == "single_entry"


@dataclass
class Portfolio:
    """The delivered lineup set plus portfolio-level diagnostics."""

    lineups: list[Lineup] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    exposures: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    contests: list[Contest] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lineups)

    def exposure_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for lu in self.lineups:
            for p in lu.players:
                out[p.player_id] = out.get(p.player_id, 0) + 1
        return out

    def exposure_pct(self) -> dict[str, float]:
        n = max(len(self.lineups), 1)
        return {pid: 100.0 * c / n for pid, c in self.exposure_counts().items()}

    def for_contest(self, name: str) -> list[Lineup]:
        return [lu for lu in self.lineups if lu.contest == name]


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        out = float(value)
        if math.isnan(out):
            return default
        return out
    except (TypeError, ValueError):
        return default


def dedupe_preserving(seq: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def positions_from_string(raw: str) -> tuple[str, ...]:
    parts: Sequence[str] = re.split(r"[\/,;|]", raw or "")
    return tuple(dedupe_preserving(p.strip().upper() for p in parts if p.strip()))
