"""Tennis dependence: opponents are close to mutually exclusive outcomes."""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from .base import FactorLoadings, SportAdapter, game_key


class TennisAdapter(SportAdapter):
    sport = "tennis"

    match_factor = 0.78  # sign flips between the two sides of a match

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:
        loads = FactorLoadings()
        sides: dict[str, int] = {}
        for i, p in enumerate(projections):
            match = game_key(p, snapshot)
            side = sides.setdefault(f"{match}:{p.player.team}", len(
                [k for k in sides if k.startswith(f"{match}:")]))
            sign = 1.0 if side % 2 == 0 else -1.0
            loads.add(i, f"match:{match}", sign * self.match_factor)
        return loads

    def describe(self) -> str:
        return "Tennis: strong negative correlation between the two sides of a match"
