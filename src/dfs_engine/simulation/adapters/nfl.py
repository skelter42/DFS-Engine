"""NFL / NCAAF dependence structure.

Captures what actually drives football DFS correlation: a shared game
environment, a team passing game that lifts the QB and his pass catchers
together, target competition that pushes those pass catchers apart, running
backs tied to positive game script, and defenses negatively tied to the
opposing offense.
"""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from .base import FactorLoadings, SportAdapter, add_share_competition, game_key

PASS_CATCHERS = {"WR", "TE"}


class NFLAdapter(SportAdapter):
    sport = "nfl"

    # Loadings are tuned so the implied pairwise correlations land near the
    # historically observed values asserted in tests/test_simulation.py.
    game_env = {"QB": 0.28, "WR": 0.26, "TE": 0.24, "RB": 0.16, "DST": -0.10, "K": 0.20}
    team_off = {"QB": 0.30, "WR": 0.20, "TE": 0.20, "RB": 0.26, "DST": 0.05, "K": 0.30}
    team_pass = {"QB": 0.52, "WR": 0.32, "TE": 0.30, "RB": 0.10, "DST": 0.0, "K": 0.0}
    team_rush = {"QB": 0.10, "WR": 0.0, "TE": 0.02, "RB": 0.46, "DST": 0.0, "K": 0.0}
    opp_off = {"DST": -0.62, "RB": -0.14, "QB": 0.04, "WR": 0.04, "TE": 0.04, "K": -0.05}
    #: strength of target competition among a team's pass catchers
    target_competition = 0.55
    #: QB-to-individual-receiver link, on top of the shared team passing factor.
    #: Per-receiver so it lifts each QB/pass-catcher pair without also pulling
    #: the receivers toward each other.
    qb_pair_qb = 0.20
    qb_pair_receiver = 0.36

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:
        loads = FactorLoadings()
        depth: dict[str, list[int]] = {}
        for i, p in enumerate(projections):
            if (p.player.positions[0] if p.player.positions else "") in PASS_CATCHERS:
                depth.setdefault(p.player.team, []).append(i)
        for team, idxs in depth.items():
            idxs.sort(key=lambda i: -projections[i].engine_projection)

        for i, p in enumerate(projections):
            pos = (p.player.positions[0] if p.player.positions else "WR").upper()
            team = p.player.team
            opp = p.player.opponent
            g = game_key(p, snapshot)
            loads.add(i, f"game:{g}", self.game_env.get(pos, 0.2))
            loads.add(i, f"off:{team}", self.team_off.get(pos, 0.2))
            loads.add(i, f"pass:{team}", self.team_pass.get(pos, 0.3))
            loads.add(i, f"rush:{team}", self.team_rush.get(pos, 0.05))
            if opp:
                loads.add(i, f"off:{opp}", self.opp_off.get(pos, 0.0))
                loads.add(i, f"pass:{opp}", -0.30 if pos == "DST" else 0.0)
            if pos in PASS_CATCHERS and i in depth.get(team, []):
                rank = depth[team].index(i)
                loads.add(i, f"qbpair:{team}:{rank}", self.qb_pair_receiver)
            elif pos == "QB":
                for rank in range(len(depth.get(team, []))):
                    loads.add(i, f"qbpair:{team}:{rank}", self.qb_pair_qb)

        for team, idxs in depth.items():
            add_share_competition(loads, idxs, f"targets:{team}", self.target_competition)
        return loads

    def describe(self) -> str:
        return "NFL: game environment, team pass/rush volume, target competition, DST-vs-offense"
