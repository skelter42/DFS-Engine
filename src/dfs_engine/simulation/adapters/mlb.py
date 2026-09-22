"""MLB dependence structure.

The defining MLB features: a team's offense either happens or it does not
(so its hitters move together), batting-order neighbours share innings more
tightly than the top and bottom of the order do, and a starting pitcher is
strongly negatively tied to the offense he is facing.
"""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from .base import FactorLoadings, SportAdapter, game_key


class MLBAdapter(SportAdapter):
    sport = "mlb"

    hitter_team = 0.50
    hitter_game = 0.16          # both offenses share park/weather/umpire
    hitter_order_block = 0.22   # batting-order neighbourhood
    pitcher_opp_offense = -0.52
    pitcher_own_team = 0.10     # run support helps the win
    pitcher_game = -0.12

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:
        loads = FactorLoadings()
        for i, p in enumerate(projections):
            team = p.player.team
            opp = p.player.opponent
            g = game_key(p, snapshot)
            is_pitcher = p.player.roster_role == "pitcher" or "P" in p.player.positions
            if is_pitcher:
                if opp:
                    loads.add(i, f"offense:{opp}", self.pitcher_opp_offense)
                loads.add(i, f"offense:{team}", self.pitcher_own_team)
                loads.add(i, f"game:{g}", self.pitcher_game)
                continue
            loads.add(i, f"offense:{team}", self.hitter_team)
            loads.add(i, f"game:{g}", self.hitter_game)
            order = p.player.batting_order
            if order:
                block = (order - 1) // 3  # top / middle / bottom of the order
                loads.add(i, f"order:{team}:{block}", self.hitter_order_block)
        return loads

    def describe(self) -> str:
        return "MLB: correlated team offenses, batting-order blocks, pitcher-vs-opposing-lineup"
