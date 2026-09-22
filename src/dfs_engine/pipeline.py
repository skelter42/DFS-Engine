"""End-to-end slate build: the canonical workflow from ``core/ENGINE.md``.

    raw slate/site data
      -> multi-book market sweep
      -> de-vig + consensus
      -> market-derived projections (+ coverage grade)
      -> confidence-weighted blend with the vendor prior
      -> engine expected ownership
      -> correlated slate simulation
      -> candidate generation
      -> portfolio selection and multi-contest allocation
      -> exposure audit and final QA

Each stage is independently usable; this module just wires them together and
keeps the provenance needed for the delivery contract.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .config import EngineConfig
from .markets.aggregate import coverage_report
from .models import Contest, MarketSnapshot, Player, PlayerProjection, Portfolio
from .optimize.rules import RosterRules, get_rules
from .optimize.solver import ObjectiveWeights, SolverConfig, generate_candidates
from .portfolio.allocation import AllocationConfig, allocate, allocation_audit
from .portfolio.builder import SelectionConfig, label_lineups, select_portfolio
from .portfolio.diagnostics import (
    correlation_summary,
    exposure_table,
    final_audit,
    largest_deviations,
    risk_flags,
)
from .projections.engine import ProjectionConfig, coverage_summary, project_slate
from .projections.ownership import OwnershipConfig, blend_ownership
from .simulation.adapters import get_adapter
from .simulation.core import SimConfig, effective_sample_note, simulate_slate
from .simulation.field import EvaluationResult, FieldConfig, PayoutCurve, build_field, evaluate_lineups
from .simulation.portfolio import (
    hidden_world_concentration,
    marginal_values,
    portfolio_metrics,
)

log = logging.getLogger("dfs_engine.pipeline")


@dataclass
class BuildRequest:
    sport: str
    players: Sequence[Player]
    snapshot: MarketSnapshot
    contests: Sequence[Contest] = field(default_factory=list)
    site: str = "dk"
    variant: str = "classic"
    n_lineups: int = 20
    n_candidates: int = 200
    n_worlds: int = 20000
    field_entries: int = 3000
    seed: int = 20260101
    min_uniques: int = 2
    contest_profile: str = "large_field_gpp"
    industry_ownership: Mapping[str, Sequence[float]] | None = None
    synthetic: bool = False
    label: str = ""
    config: EngineConfig | None = None

    def resolved_contests(self) -> list[Contest]:
        if self.contests:
            return list(self.contests)
        return [Contest(name="Primary GPP", entries=self.n_lineups, field_size=50000,
                        profile=self.contest_profile, priority=1)]


@dataclass
class BuildResult:
    portfolio: Portfolio
    projections: dict[str, PlayerProjection]
    ownership: dict[str, float]
    rules: RosterRules
    simulation: object
    field_model: object
    evaluation: EvaluationResult
    allocation: dict[str, list]
    meta: dict = field(default_factory=dict)

    @property
    def lineups(self):
        return self.portfolio.lineups


def run_build(request: BuildRequest, progress=None) -> BuildResult:
    cfg = request.config or EngineConfig.load()
    rules = get_rules(request.site, request.sport, request.variant)
    contests = request.resolved_contests()
    profile = cfg.profile(request.contest_profile)
    timings: dict[str, float] = {}

    def step(name: str, msg: str):
        if progress:
            progress(name, msg)
        return time.time()

    # 1-2. Eligibility gate and market state ------------------------------
    t = step("ingest", f"{len(request.players)} players, "
                       f"{len(request.snapshot.games)} games, "
                       f"{len(request.snapshot.props)} prop markets")
    eligible = [p for p in request.players if p.eligible]
    excluded = [(p.name, p.ineligible_reason) for p in request.players if not p.eligible]
    timings["ingest"] = time.time() - t

    # 3-7. Market-derived projections -------------------------------------
    t = step("project", "de-vigging markets and building projections")
    proj_cfg = ProjectionConfig(site=request.site, seed=request.seed)
    projections = project_slate(eligible, request.snapshot, proj_cfg)
    if not projections:
        raise ValueError("no eligible players survived the projection stage")
    timings["project"] = time.time() - t

    # 8. Engine expected ownership ----------------------------------------
    t = step("ownership", "modelling expected field ownership")
    own_result = blend_ownership(projections, rules, request.snapshot,
                                 industry=request.industry_ownership,
                                 config=OwnershipConfig())
    ownership = own_result.ownership
    timings["ownership"] = time.time() - t

    # 9. Correlated slate simulation --------------------------------------
    t = step("simulate", f"{request.n_worlds:,} correlated slate worlds")
    sim = simulate_slate(projections, get_adapter(request.sport), request.snapshot,
                         SimConfig(n_worlds=request.n_worlds, seed=request.seed))
    timings["simulate"] = time.time() - t

    t = step("field", f"sampling {request.field_entries:,} opposing entries")
    field_model = build_field(projections, rules, ownership, sim,
                              FieldConfig(n_entries=request.field_entries,
                                          seed=request.seed + 7),
                              stack_positions=_stack_positions(request.sport))
    timings["field"] = time.time() - t

    # 10. Candidate generation --------------------------------------------
    t = step("candidates", f"solving up to {request.n_candidates} candidate lineups")
    weights = ObjectiveWeights(**{k: v for k, v in cfg.score_weights.items()
                                  if k in ObjectiveWeights.__dataclass_fields__}).scaled(profile)
    solver_cfg = SolverConfig(mode="world", seed=request.seed,
                              min_uniques=max(1, request.min_uniques - 1))
    pool = generate_candidates(projections, rules, ownership, weights, solver_cfg,
                               n=request.n_candidates, sim=sim)
    if not pool.lineups:
        raise ValueError(f"candidate generation produced no legal lineups: {pool.failures}")
    timings["candidates"] = time.time() - t

    # 11-12. Evaluate and select ------------------------------------------
    t = step("evaluate", f"ranking {len(pool.lineups)} candidates against the field")
    primary = max(contests, key=lambda c: c.field_size)
    evaluation = evaluate_lineups(
        sim, field_model, [[p.player_id for p in lu.players] for lu in pool.lineups],
        primary, payout=PayoutCurve(paid_fraction=primary.payout_top_fraction),
        ownership=ownership, multipliers=_slot_multipliers(pool.lineups, rules))
    label_lineups(pool.lineups, projections, ownership, evaluation.metrics)
    timings["evaluate"] = time.time() - t

    t = step("select", f"selecting {request.n_lineups} lineups by marginal portfolio value")
    total_entries = sum(c.entries for c in contests) or request.n_lineups
    selection = select_portfolio(pool.lineups, evaluation,
                                 SelectionConfig(n_lineups=total_entries,
                                                 min_uniques=request.min_uniques))
    portfolio = Portfolio(lineups=selection.lineups, contests=contests)
    timings["select"] = time.time() - t

    # Re-evaluate the *selected* set so portfolio metrics describe what ships.
    selected_eval = evaluate_lineups(
        sim, field_model, [[p.player_id for p in lu.players] for lu in portfolio.lineups],
        primary, payout=PayoutCurve(paid_fraction=primary.payout_top_fraction),
        ownership=ownership, multipliers=_slot_multipliers(portfolio.lineups, rules))
    label_lineups(portfolio.lineups, projections, ownership, selected_eval.metrics)
    for lu, mv in zip(portfolio.lineups, marginal_values(selected_eval)):
        lu.metrics["marginal_value"] = mv

    # 13. Allocation and audits -------------------------------------------
    t = step("allocate", f"allocating across {len(contests)} contest(s)")
    allocation = allocate(portfolio.lineups, contests, AllocationConfig())
    timings["allocate"] = time.time() - t

    pmetrics = portfolio_metrics(selected_eval, portfolio.lineups)
    exposures = exposure_table(portfolio, projections, ownership)
    portfolio.exposures = {r.player_id: r.exposure_pct for r in exposures}
    portfolio.metrics = pmetrics.as_dict()
    portfolio.diagnostics = {
        "coverage": coverage_summary(projections),
        "market_coverage": coverage_report(request.snapshot,
                                           [p.player.key for p in projections.values()]),
        "ownership": own_result.diagnostics,
        "ownership_flags": own_result.audit_flags,
        "exposure_table": [r.as_dict() for r in exposures],
        "largest_deviations": [r.as_dict() for r in largest_deviations(exposures)],
        "correlation": correlation_summary(portfolio),
        "hidden_concentration": hidden_world_concentration(selected_eval, portfolio.lineups),
        "allocation_audit": allocation_audit(allocation, contests, ownership),
        "risk_flags": risk_flags(projections, portfolio, request.snapshot),
        "final_audit": final_audit(portfolio, projections, rules),
        "excluded_players": [{"name": n, "reason": r} for n, r in excluded],
        "selection_trace": selection.trace,
    }

    meta = {
        "sport": request.sport,
        "site": request.site,
        "variant": request.variant,
        "label": request.label,
        "synthetic": request.synthetic,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_version": cfg.engine.get("version", "unknown"),
        "players_in_pool": len(request.players),
        "players_eligible": len(eligible),
        "candidates_generated": len(pool.lineups),
        "candidate_failures": pool.failures,
        "simulation": sim.meta,
        "iteration_note": effective_sample_note(request.n_worlds),
        "field": field_model.meta,
        "contests": [c.__dict__ for c in contests],
        "market_sources": request.snapshot.sources,
        "market_errors": request.snapshot.errors,
        "timings_sec": {k: round(v, 2) for k, v in timings.items()},
    }
    if request.synthetic:
        meta["warning"] = ("SYNTHETIC SLATE: generated market data, not real odds. "
                           "Do not use these lineups for a live contest.")

    return BuildResult(portfolio=portfolio, projections=projections, ownership=ownership,
                       rules=rules, simulation=sim, field_model=field_model,
                       evaluation=selected_eval, allocation=allocation, meta=meta)


def _slot_multipliers(lineups, rules: RosterRules):
    """Per-slot scoring multipliers (showdown captains); ``None`` for classic."""
    by_slot = {s.name: s.multiplier for s in rules.slots}
    if all(abs(m - 1.0) < 1e-9 for m in by_slot.values()):
        return None
    return [[by_slot.get(slot, 1.0) for slot in lu.slots] for lu in lineups]


def _stack_positions(sport: str) -> tuple[str, ...]:
    return {"nfl": ("QB",), "ncaaf": ("QB",), "mlb": ("C", "1B", "2B", "3B", "SS", "OF"),
            "nhl": ("C", "W"), "nba": (), "tennis": ()}.get(sport.lower(), ("QB",))
