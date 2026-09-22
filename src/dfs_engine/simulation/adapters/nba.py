"""NBA dependence structure: pace and usage, not scoreboard correlation.

NBA teammates are only weakly positively correlated through pace and game
environment, and negatively correlated through usage -- shots taken by one are
shots not taken by another. Blowout risk links a whole game together.
"""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from .base import FactorLoadings, SportAdapter, add_share_competition, game_key


class NBAAdapter(SportAdapter):
    sport = "nba"

    game_pace = 0.26
    team_env = 0.14
    usage_competition = 0.40

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:
        loads = FactorLoadings()
        depth: dict[str, list[int]] = {}
        for i, p in enumerate(projections):
            depth.setdefault(p.player.team, []).append(i)
        for idxs in depth.values():
            idxs.sort(key=lambda i: -projections[i].engine_projection)

        for i, p in enumerate(projections):
            team = p.player.team
            loads.add(i, f"game:{game_key(p, snapshot)}", self.game_pace)
            loads.add(i, f"team:{team}", self.team_env)
        for team, idxs in depth.items():
            add_share_competition(loads, idxs, f"usage:{team}", self.usage_competition)
        return loads

    def describe(self) -> str:
        return "NBA: game pace/blowout factor, team environment, intra-team usage competition"
