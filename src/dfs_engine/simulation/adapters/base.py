"""Adapter helpers shared across sports."""

from __future__ import annotations

from typing import Sequence

from ...models import MarketSnapshot, PlayerProjection
from ..core import FactorLoadings, SportAdapter


def game_key(proj: PlayerProjection, snapshot: MarketSnapshot | None) -> str:
    if proj.player.game_id:
        return str(proj.player.game_id)
    if snapshot is not None:
        game = snapshot.game_for_team(proj.player.team)
        if game is not None:
            return game.game_id
    opp = proj.player.opponent or "?"
    return "-".join(sorted([proj.player.team, opp]))


def team_ranks(projections: Sequence[PlayerProjection], position_filter=None
               ) -> dict[str, list[str]]:
    """Players per team ordered by projection -- used for role-depth loadings."""
    buckets: dict[str, list[PlayerProjection]] = {}
    for p in projections:
        if position_filter is not None and not position_filter(p):
            continue
        buckets.setdefault(p.player.team, []).append(p)
    return {team: [p.player.player_id for p in sorted(ps, key=lambda x: -x.engine_projection)]
            for team, ps in buckets.items()}


def add_share_competition(loads: FactorLoadings, indices: list[int], prefix: str,
                          strength: float) -> None:
    """Make a group of players compete for one finite pool (targets, usage).

    A single shared factor with negative loadings would make the *losers*
    positively correlated with each other, which is wrong. Instead each member
    gets its own share factor: +strength on its own, and an offsetting negative
    on everyone else's. Every pair in the group then ends up negatively
    correlated, which is what a simplex constraint actually implies.
    """
    n = len(indices)
    if n < 2 or strength <= 0:
        return
    off = strength / (n - 1)
    for own, i in enumerate(indices):
        for other, _ in enumerate(indices):
            loads.add(i, f"{prefix}:{other}", strength if own == other else -off)


__all__ = ["FactorLoadings", "SportAdapter", "add_share_competition", "game_key",
           "team_ranks"]
