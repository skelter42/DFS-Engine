"""NHL dependence structure: lines, power-play units, and goalie opposition."""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from .base import FactorLoadings, SportAdapter, game_key


class NHLAdapter(SportAdapter):
    sport = "nhl"

    line_factor = 0.46
    team_factor = 0.22
    pp_factor = 0.26
    game_factor = 0.12
    goalie_opp_offense = -0.60
    goalie_team = 0.18

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:
        loads = FactorLoadings()
        for i, p in enumerate(projections):
            team = p.player.team
            opp = p.player.opponent
            is_goalie = p.player.roster_role == "goalie" or "G" in p.player.positions
            if is_goalie:
                if opp:
                    loads.add(i, f"offense:{opp}", self.goalie_opp_offense)
                loads.add(i, f"team:{team}", self.goalie_team)
                continue
            loads.add(i, f"offense:{team}", self.team_factor)
            loads.add(i, f"game:{game_key(p, snapshot)}", self.game_factor)
            line = p.player.extra.get("line") or p.player.depth_note or "L?"
            loads.add(i, f"line:{team}:{line}", self.line_factor)
            pp = p.player.extra.get("pp_unit")
            if pp:
                loads.add(i, f"pp:{team}:{pp}", self.pp_factor)
        return loads

    def describe(self) -> str:
        return "NHL: line stacks, power-play units, goalie-vs-opposing-skaters"
