"""Build DFS Engine projections: market-first, vendor prior only where earned.

The output per player is not a number but a *distribution*: components are
sampled jointly (a receiver's yards, catches and touchdowns move together),
scored with the site's rules including threshold bonuses, and kept as an
empirical sample. Those samples are the marginals the slate simulator draws
from, so the ceiling the optimizer sees is the one the market implies.

Coverage grading and the coverage-weighted shrink toward the vendor prior
follow ``core/MARKET_PROJECTIONS.md``: no fixed universal blend, weight moves
with the quality of the evidence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import numpy as np

from ..markets.aggregate import MarketConsensus, consensus_by_player
from ..markets.catalog import ONE_SIDED_MULTIPLIER
from ..odds.conversions import DEFAULT_ONE_SIDED_MULTIPLIER
from ..models import COVERAGE_LABELS, GameEnvironment, MarketSnapshot, Player, PlayerProjection
from ..odds.distributions import norm_cdf_vec
from .components import ComponentBuilder, ComponentResult, get_builder
from .reconcile import reconcile_slate
from .reconcile import validate as reconcile_validate
from .team_units import build_team_units
from .scoring import ScoringRule, get_rule

DEFAULT_SAMPLES = 4096

#: How many distinct priced markets constitutes "full" coverage for a role.
TARGET_MARKETS: dict[str, int] = {
    "nfl": 4, "ncaaf": 4, "mlb": 4, "nba": 5, "nhl": 3, "tennis": 2,
}

#: Archetype volatility used only when a player has no usable market at all.
FALLBACK_CV: dict[str, float] = {
    "nfl": 0.72, "ncaaf": 0.78, "mlb": 0.95, "nba": 0.33, "nhl": 0.85, "tennis": 0.45,
}


@dataclass
class ProjectionConfig:
    site: str = "dk"
    n_samples: int = DEFAULT_SAMPLES
    seed: int = 20260101
    devig_method: str = "multiplicative"
    consensus_mode: str = "book_median"   # book_median | pooled
    one_sided_multiplier: float | None = None  # None -> the sport default
    trim: float = 0.0
    min_books: int = 1
    #: hard ceiling on how far the engine projection may sit from the vendor prior
    max_vendor_deviation: float | None = None
    #: reconcile receiving production to the quarterback (football only)
    reconcile_teams: bool = True
    fallback_cv: dict[str, float] = field(default_factory=lambda: dict(FALLBACK_CV))


# --------------------------------------------------------------------------
# Correlated component sampling
# --------------------------------------------------------------------------


def correlation_matrix(stats: Sequence[str],
                       pairs: Iterable[tuple[str, str, float]]) -> np.ndarray:
    n = len(stats)
    idx = {s: i for i, s in enumerate(stats)}
    mat = np.eye(n)
    for a, b, rho in pairs:
        if a in idx and b in idx:
            mat[idx[a], idx[b]] = mat[idx[b], idx[a]] = float(rho)
    return nearest_psd(mat)


def nearest_psd(mat: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Project a hand-specified correlation matrix onto the PSD cone."""
    sym = 0.5 * (mat + mat.T)
    vals, vecs = np.linalg.eigh(sym)
    vals = np.clip(vals, eps, None)
    out = vecs @ np.diag(vals) @ vecs.T
    d = np.sqrt(np.clip(np.diag(out), eps, None))
    out = out / np.outer(d, d)
    np.fill_diagonal(out, 1.0)
    return out


def sample_components(result: ComponentResult, builder: ComponentBuilder,
                      n: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Draw ``n`` jointly-consistent component vectors via a Gaussian copula."""
    stats = [s for s in result.components]
    if not stats:
        return {}
    corr = correlation_matrix(stats, builder.correlations)
    chol = np.linalg.cholesky(corr)
    z = rng.standard_normal((n, len(stats))) @ chol.T
    u = norm_cdf_vec(z)
    return {stat: result.components[stat].dist.ppf(u[:, i]) for i, stat in enumerate(stats)}


# --------------------------------------------------------------------------
# Coverage grading
# --------------------------------------------------------------------------


def grade_coverage(result: ComponentResult, cons: Mapping[str, MarketConsensus],
                   sport: str) -> tuple[str, float]:
    """Return (tier, score in [0,1]) per the market-confidence tiers in the brain."""
    direct = result.direct_markets
    if direct == 0:
        return ("C" if result.inferred_markets else "D"), 0.0

    books = set()
    two_sided = 0
    points = 0
    dispersion: list[float] = []
    for c in cons.values():
        books |= c.books
        two_sided += c.two_sided_lines
        points += c.n_lines
        dispersion.append(c.dispersion)

    target = TARGET_MARKETS.get(sport.lower(), 4)
    breadth = min(1.0, direct / target)
    depth = min(1.0, math.log1p(len(books)) / math.log1p(4))
    sided = min(1.0, two_sided / max(points, 1))
    spread = sum(dispersion) / max(len(dispersion), 1)
    agreement = 1.0 / (1.0 + 8.0 * spread)
    score = 0.45 * breadth + 0.25 * depth + 0.15 * sided + 0.15 * agreement

    if score >= 0.72 and direct >= max(3, target - 1) and len(books) >= 3:
        tier = "A"
    elif score >= 0.40 and direct >= 1:
        tier = "B"
    else:
        tier = "C"
    return tier, float(score)


def market_weight(tier: str, score: float, has_vendor: bool) -> float:
    """Coverage-weighted fallback: Vegas dominates when the evidence is there."""
    if not has_vendor:
        return 1.0
    if tier == "A":
        return min(1.0, 0.88 + 0.12 * score)
    if tier == "B":
        return 0.45 + 0.40 * score
    if tier == "C":
        return 0.15 + 0.25 * score
    return 0.0


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------


def _scoring_rule(player: Player, site: str) -> ScoringRule:
    role = player.roster_role
    if role == "all" and player.positions:
        pos = player.positions[0].upper()
        if pos in {"DST", "DEF", "D"}:
            role = "dst"
        elif pos == "K":
            role = "k"
    return get_rule(site, player.sport, role)


def build_projection(player: Player, snapshot: MarketSnapshot,
                     consensus: Mapping[str, Mapping[str, MarketConsensus]],
                     config: ProjectionConfig,
                     game: GameEnvironment | None = None) -> PlayerProjection:
    """Stage one: market components and a coverage grade. No sampling yet.

    Sampling waits until after team reconciliation, because reconciliation moves
    component means and the yardage bonuses must be computed from the final
    ones.
    """
    builder = get_builder(player.sport)
    cons = dict(consensus.get(player.key, {}))
    game = game or (snapshot.game_for_team(player.team) if snapshot else None)

    result = builder.build(player, cons, game)
    tier, score = grade_coverage(result, cons, player.sport)

    proj = PlayerProjection(
        player=player,
        components=dict(result.components),
        vendor_projection=player.vendor_projection,
        source_ownership=player.vendor_ownership,
        coverage=tier,
        coverage_score=score,
        n_markets=result.direct_markets,
        n_books=len({b for c in cons.values() for b in c.books}),
        notes=list(result.notes),
    )
    # Provisional level so the reconciliation stage can identify the starting
    # quarterback and aggregate team touchdowns before anything is sampled.
    rule = _scoring_rule(player, config.site)
    proj.engine_projection = rule.score_expectation(
        {stat: fitted.mean for stat, fitted in proj.components.items()})
    return proj


def finalize_projection(proj: PlayerProjection, config: ProjectionConfig,
                        rng: np.random.Generator) -> PlayerProjection:
    """Stage two: sample the components jointly, score them, blend with the prior."""
    player = proj.player
    builder = get_builder(player.sport)
    rule = _scoring_rule(player, config.site)

    samples = None
    if proj.components:
        result = ComponentResult(components=dict(proj.components))
        comps = sample_components(result, builder, config.n_samples, rng)
        samples = rule.score(comps)
        proj.market_projection = float(np.mean(samples))

    has_vendor = player.vendor_projection is not None
    weight = (market_weight(proj.coverage, proj.coverage_score, has_vendor)
              if proj.market_projection is not None else 0.0)
    proj.market_weight = weight

    if proj.market_projection is None:
        proj.engine_projection = float(player.vendor_projection or 0.0)
        proj.coverage = "D"
        proj.notes.append("no usable market; vendor prior carried unchanged "
                          "(fallback-driven)")
        samples = fallback_samples(proj.engine_projection, player.sport, config, rng)
    else:
        vendor = float(player.vendor_projection) if has_vendor else proj.market_projection
        blended = weight * proj.market_projection + (1.0 - weight) * vendor
        if config.max_vendor_deviation is not None and has_vendor:
            lo = vendor - config.max_vendor_deviation
            hi = vendor + config.max_vendor_deviation
            blended = min(max(blended, lo), hi)
        proj.engine_projection = float(blended)
        samples = rescale(samples, proj.engine_projection)

    proj.samples = samples
    return proj


def project_player(player: Player, snapshot: MarketSnapshot,
                   consensus: Mapping[str, Mapping[str, MarketConsensus]],
                   config: ProjectionConfig, rng: np.random.Generator,
                   game: GameEnvironment | None = None) -> PlayerProjection:
    """Single-player convenience wrapper (no team reconciliation)."""
    proj = build_projection(player, snapshot, consensus, config, game)
    return finalize_projection(proj, config, rng)


def rescale(samples: np.ndarray, target_mean: float) -> np.ndarray:
    """Shift the distribution's level to the blended projection, preserving shape."""
    current = float(np.mean(samples))
    if target_mean <= 0:
        return np.zeros_like(samples)
    if current <= 1e-9:
        return np.full_like(samples, target_mean)
    return samples * (target_mean / current)


def fallback_samples(mean: float, sport: str, config: ProjectionConfig,
                     rng: np.random.Generator) -> np.ndarray:
    """Labelled archetype distribution for a player with no market coverage."""
    mean = max(float(mean), 0.0)
    if mean <= 0:
        return np.zeros(config.n_samples)
    cv = config.fallback_cv.get(sport.lower(), 0.7)
    sigma = math.sqrt(math.log(1.0 + cv * cv))
    mu = math.log(mean) - 0.5 * sigma ** 2
    return rng.lognormal(mu, sigma, config.n_samples)


def project_slate(players: Sequence[Player], snapshot: MarketSnapshot,
                  config: ProjectionConfig | None = None,
                  diagnostics: MutableMapping[str, Any] | None = None
                  ) -> dict[str, PlayerProjection]:
    """Project every eligible player. Ineligible rows are excluded, not zeroed.

    Ordering matters here. Components are built first, then the team pass
    reconciles receiving production to each quarterback and derives kickers and
    defenses from the game market, and only then is anything sampled -- so
    yardage bonuses and simulated marginals reflect the *final* means.

    Pass ``diagnostics`` to receive the reconciliation report; it is written
    into that mapping rather than held in module state.
    """
    config = config or ProjectionConfig()
    rng = np.random.default_rng(config.seed)
    sport = players[0].sport if players else snapshot.sport
    multiplier = config.one_sided_multiplier
    if multiplier is None:
        multiplier = ONE_SIDED_MULTIPLIER.get(str(sport).lower(),
                                              DEFAULT_ONE_SIDED_MULTIPLIER)
    consensus = consensus_by_player(snapshot, method=config.devig_method,
                                    trim=config.trim, min_books=config.min_books,
                                    one_sided_multiplier=multiplier)

    out: dict[str, PlayerProjection] = {}
    for player in players:
        if not player.eligible:
            continue
        out[player.player_id] = build_projection(player, snapshot, consensus, config)

    if config.reconcile_teams and str(sport).lower() in {"nfl", "ncaaf"}:
        reconciliations = reconcile_slate(out, snapshot=snapshot)
        _apply_team_units(out, snapshot, config)
        for proj in out.values():
            # Production derived from a teammate's market is modeled, not
            # fallback: it has a market basis, just not the player's own.
            if proj.modeled_from_team and proj.coverage == "D":
                proj.coverage = "C"
                proj.coverage_score = max(proj.coverage_score, 0.2)
        if diagnostics is not None:
            diagnostics["reconciliation"] = reconcile_validate(reconciliations, out)

    for proj in out.values():
        finalize_projection(proj, config, rng)
    return out


def _apply_team_units(projections: dict[str, PlayerProjection],
                      snapshot: MarketSnapshot, config: ProjectionConfig) -> None:
    """Attach kicker and defense components derived from the game market."""
    for pid, result in build_team_units(projections, snapshot).items():
        proj = projections[pid]
        if not result.components:
            continue
        proj.components.update(result.components)
        proj.notes.extend(n for n in result.notes if n not in proj.notes)
        # Game-market-derived, not prop-derived: industry-supported, not
        # Vegas-rich, and not a fallback either.
        proj.coverage = "C"
        proj.coverage_score = max(proj.coverage_score, 0.25)
        proj.engine_projection = _scoring_rule(proj.player, config.site) \
            .score_expectation({s: f.mean for s, f in proj.components.items()})


def coverage_summary(projections: Mapping[str, PlayerProjection]) -> dict:
    """Confidence-tier counts, as the mandatory market-inputs audit requires."""
    tiers = {t: 0 for t in COVERAGE_LABELS}
    for proj in projections.values():
        tiers[proj.coverage] = tiers.get(proj.coverage, 0) + 1
    total = max(len(projections), 1)
    return {
        "players": len(projections),
        "tiers": {t: {"label": COVERAGE_LABELS[t], "count": c,
                      "pct": round(100.0 * c / total, 1)} for t, c in tiers.items()},
        "vegas_backed_pct": round(100.0 * (tiers.get("A", 0) + tiers.get("B", 0)) / total, 1),
        "mean_market_weight": round(
            sum(p.market_weight for p in projections.values()) / total, 3),
    }
