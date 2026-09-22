"""DFS Engine expected ownership: a forecast of field behaviour.

Ownership is not projection. It is an estimate of what entrants will roster
after seeing salary, projections, value, news and industry content
(``core/MARKET_INPUTS.md``). Two rules shape this module:

* Industry numeric consensus is the preferred anchor when it exists. The
  behavioural model is a sanity check and a gap-filler, never a lever.
* Ownership is **never** adjusted to manufacture leverage. Exposure is the
  decision variable; ownership is a measurement.

The behavioural model fills each roster slot by softmax over the players the
field can see, so slate-wide ownership automatically sums to
``100% x roster size`` -- the constraint real ownership obeys and ad-hoc
player-by-player models usually violate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from ..models import MarketSnapshot, PlayerProjection
from ..optimize.rules import RosterRules


@dataclass
class OwnershipConfig:
    """Field-behaviour weights. Higher temperature == flatter, softer field."""

    value_weight: float = 2.55
    projection_weight: float = 1.35
    ceiling_weight: float = 0.45
    salary_weight: float = -0.28        # sticker shock at equal value
    environment_weight: float = 0.35    # implied team total
    narrative_weight: float = 0.30      # obvious value / clear role
    temperature: float = 2.8
    chalk_ceiling: float = 62.0         # realistic single-player ownership cap
    min_ownership: float = 0.2
    #: weight on industry numbers when they are supplied
    industry_weight_multi: float = 0.85
    industry_weight_single: float = 0.65


def _z(values: np.ndarray) -> np.ndarray:
    if len(values) < 2:
        return np.zeros_like(values)
    sd = float(np.std(values))
    if sd < 1e-9:
        return np.zeros_like(values)
    return (values - float(np.mean(values))) / sd


@dataclass
class OwnershipResult:
    ownership: dict[str, float]
    confidence: dict[str, str]
    diagnostics: dict[str, object] = field(default_factory=dict)
    audit_flags: list[str] = field(default_factory=list)


def behavioral_ownership(projections: Mapping[str, PlayerProjection],
                         rules: RosterRules,
                         snapshot: MarketSnapshot | None = None,
                         config: OwnershipConfig | None = None) -> dict[str, float]:
    """Slot-by-slot softmax field model. Returns percentage points per player."""
    cfg = config or OwnershipConfig()
    players = list(projections.values())
    if not players:
        return {}

    proj = np.array([p.engine_projection for p in players])
    ceil = np.array([p.ceiling for p in players])
    sal = np.array([max(p.player.salary, 1) for p in players], dtype=float)
    value = proj / (sal / 1000.0)

    env = np.zeros(len(players))
    if snapshot is not None:
        for i, p in enumerate(players):
            game = snapshot.game_for_team(p.player.team)
            tt = game.team_total(p.player.team) if game else None
            if tt is not None:
                env[i] = tt

    # "Obvious value": cheap players whose projection outruns their price tier.
    salary_rank = np.argsort(np.argsort(sal)) / max(len(sal) - 1, 1)
    narrative = _z(value) * (1.0 - salary_rank)

    utility = (
        cfg.value_weight * _z(value)
        + cfg.projection_weight * _z(proj)
        + cfg.ceiling_weight * _z(ceil)
        + cfg.salary_weight * _z(sal)
        + cfg.environment_weight * _z(env)
        + cfg.narrative_weight * narrative
    ) / max(cfg.temperature, 1e-3)

    exp_u = np.exp(utility - utility.max())
    own = np.zeros(len(players))
    for slot in rules.slots:
        mask = np.array([any(pos in slot.eligible for pos in p.player.positions)
                         for p in players], dtype=float)
        weighted = exp_u * mask
        total = weighted.sum()
        if total <= 0:
            continue
        own += 100.0 * weighted / total

    # Renormalise to the structural total (100% per roster spot) while honouring
    # the chalk ceiling: water-fill so capped players' excess spreads over the
    # rest instead of silently breaking the total.
    own = _cap_and_normalise(own, 100.0 * rules.size, cfg.min_ownership, cfg.chalk_ceiling)
    return {p.player.player_id: float(o) for p, o in zip(players, own)}


def _cap_and_normalise(own: np.ndarray, target: float, floor: float,
                       ceiling: float, iters: int = 40) -> np.ndarray:
    own = np.clip(own, floor, ceiling)
    for _ in range(iters):
        total = own.sum()
        if total <= 0 or abs(total - target) < 1e-6:
            break
        free = (own < ceiling - 1e-9) & (own > floor + 1e-9)
        if not free.any():
            break
        fixed = own[~free].sum()
        room = target - fixed
        pool = own[free].sum()
        if pool <= 0:
            break
        own[free] = np.clip(own[free] * (room / pool), floor, ceiling)
    return np.clip(own, floor, ceiling)


def blend_ownership(projections: Mapping[str, PlayerProjection],
                    rules: RosterRules,
                    snapshot: MarketSnapshot | None = None,
                    industry: Mapping[str, Sequence[float]] | None = None,
                    config: OwnershipConfig | None = None) -> OwnershipResult:
    """Combine industry numeric consensus (preferred) with the behavioural model.

    ``industry`` maps player_id -> one or more current numeric ownership
    projections for this exact site/slate. Vendor ownership carried on the
    player row is treated as one such source, not as the authority.
    """
    cfg = config or OwnershipConfig()
    model = behavioral_ownership(projections, rules, snapshot, cfg)
    industry = industry or {}

    out: dict[str, float] = {}
    conf: dict[str, str] = {}
    flags: list[str] = []
    n_multi = n_single = n_model = 0

    for pid, proj in projections.items():
        sources = [float(v) for v in industry.get(pid, []) if v is not None]
        if proj.player.vendor_ownership is not None:
            sources.append(float(proj.player.vendor_ownership))
        base = model.get(pid, cfg.min_ownership)

        if len(sources) >= 2:
            anchor = float(np.median(sources))
            weight = cfg.industry_weight_multi
            tier = "A"
            n_multi += 1
        elif len(sources) == 1:
            anchor = sources[0]
            weight = cfg.industry_weight_single
            tier = "B"
            n_single += 1
        else:
            anchor = base
            weight = 0.0
            tier = "C"
            n_model += 1

        blended = weight * anchor + (1.0 - weight) * base
        out[pid] = float(min(max(blended, cfg.min_ownership), cfg.chalk_ceiling))
        conf[pid] = tier

        # Audit failure: a big disagreement between the field model and a
        # supplied number has to be explained, not shipped silently.
        if sources and abs(anchor - base) > 15.0:
            flags.append(
                f"{proj.player.name}: supplied ownership {anchor:.1f}% vs field model "
                f"{base:.1f}% (>15pp disagreement -- verify before lock)")

    total = sum(out.values())
    target = 100.0 * rules.size
    if total > 0:
        scale = target / total
        if abs(scale - 1.0) > 0.02:
            out = {k: v * scale for k, v in out.items()}
            flags.append(f"ownership rescaled by {scale:.2f}x to the structural "
                         f"{target:.0f}% roster total")

    diagnostics = {
        "total_pct": round(sum(out.values()), 1),
        "structural_total_pct": target,
        "multi_source_players": n_multi,
        "single_source_players": n_single,
        "behavioral_only_players": n_model,
        "coverage_label": _coverage_label(n_multi, n_single, n_model),
    }
    return OwnershipResult(ownership=out, confidence=conf, diagnostics=diagnostics,
                           audit_flags=flags)


def _coverage_label(multi: int, single: int, model_only: int) -> str:
    total = max(multi + single + model_only, 1)
    if multi / total >= 0.5:
        return "multi-source industry"
    if (multi + single) / total >= 0.5:
        return "single-source industry supported"
    return "behavioral model (no external ownership supplied)"


def leverage_score(projection: PlayerProjection, ownership: float) -> float:
    """Ceiling relative to the field's commitment. Positive == under-owned upside.

    Deliberately ceiling-based, not median-based: large-field GPP leverage is
    about who wins the tail, not who is efficient at the median.
    """
    own = max(ownership, 0.3)
    expected_own = 4.0 * math.sqrt(max(projection.ceiling, 0.1))
    return float(math.log(max(expected_own, 0.3) / own))


def duplication_proxy(ownerships: Sequence[float], field_size: int) -> float:
    """Expected number of identical entries, ownership-independence proxy."""
    prod = 1.0
    for own in ownerships:
        prod *= max(own, 0.1) / 100.0
    return float(prod * field_size)
