"""Sport adapters: dependence structure only, no separate simulators."""

from ..core import SportAdapter
from .mlb import MLBAdapter
from .nba import NBAAdapter
from .nfl import NFLAdapter
from .nhl import NHLAdapter
from .tennis import TennisAdapter

ADAPTERS: dict[str, SportAdapter] = {
    "nfl": NFLAdapter(),
    "ncaaf": NFLAdapter(),
    "mlb": MLBAdapter(),
    "nba": NBAAdapter(),
    "nhl": NHLAdapter(),
    "tennis": TennisAdapter(),
}


def get_adapter(sport: str) -> SportAdapter:
    adapter = ADAPTERS.get(sport.lower())
    if adapter is None:
        raise KeyError(f"No simulation adapter for sport {sport!r}")
    return adapter


__all__ = ["ADAPTERS", "MLBAdapter", "NBAAdapter", "NFLAdapter", "NHLAdapter",
           "SportAdapter", "TennisAdapter", "get_adapter"]
