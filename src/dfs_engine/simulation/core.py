"""The shared slate simulator.

One runtime, four layers (``core/SIMULATION_IMPLEMENTATION.md``): slate state,
sport adapter, field evaluator, portfolio evaluator. Sports supply dependence
structure and nothing else -- there is no MLB simulator and a separate NFL
simulator.

Design:

* A world is one internally coherent version of the whole slate. Every player's
  score in world *w* comes from the same latent game and team outcomes.
* Marginals are the market-implied fantasy-point distributions from the
  projection layer -- skewed, zero-heavy, bonus-aware -- not
  ``projection + normal noise``, which ``core/SIMULATION.md`` explicitly rules
  out.
* Dependence is a linear factor model over latent game/team/role factors, so
  the correlation any pair of players ends up with is the dot product of their
  loadings: inspectable, testable, and cheap at 100k worlds.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from ..models import MarketSnapshot, PlayerProjection
from ..odds.distributions import norm_cdf_vec


@dataclass
class SimConfig:
    n_worlds: int = 20000
    seed: int = 20260101
    #: "native" once calibrated marginals exist; recorded in output metadata
    mode: str = "native_monte_carlo"
    chunk: int = 4096


@dataclass
class FactorLoadings:
    """Sparse factor loadings: ``corr(i, j) = L_i . L_j`` for i != j."""

    factor_names: list[str] = field(default_factory=list)
    _index: dict[str, int] = field(default_factory=dict)
    _entries: list[tuple[int, int, float]] = field(default_factory=list)

    def factor(self, name: str) -> int:
        if name not in self._index:
            self._index[name] = len(self.factor_names)
            self.factor_names.append(name)
        return self._index[name]

    def add(self, player_idx: int, factor_name: str, loading: float) -> None:
        if abs(loading) < 1e-9:
            return
        self._entries.append((player_idx, self.factor(factor_name), float(loading)))

    def matrix(self, n_players: int) -> np.ndarray:
        mat = np.zeros((n_players, len(self.factor_names)))
        for i, f, v in self._entries:
            mat[i, f] += v
        return mat


@dataclass
class SlateSimulation:
    """Simulated fantasy points: ``scores`` is ``(n_worlds, n_players)``."""

    player_ids: list[str]
    scores: np.ndarray
    config: SimConfig
    factor_names: list[str]
    loadings: np.ndarray
    factor_draws: np.ndarray | None = None
    meta: dict = field(default_factory=dict)

    @property
    def n_worlds(self) -> int:
        return int(self.scores.shape[0])

    @property
    def index(self) -> dict[str, int]:
        if not hasattr(self, "_idx"):
            self._idx = {pid: i for i, pid in enumerate(self.player_ids)}
        return self._idx

    def column(self, player_id: str) -> np.ndarray:
        return self.scores[:, self.index[player_id]]

    def lineup_scores(self, player_ids: Sequence[str],
                      multipliers: Sequence[float] | None = None) -> np.ndarray:
        cols = [self.index[p] for p in player_ids]
        sub = self.scores[:, cols]
        if multipliers is not None:
            sub = sub * np.asarray(multipliers, dtype=float)
        return sub.sum(axis=1)

    def implied_correlation(self, a: str, b: str) -> float:
        la = self.loadings[self.index[a]]
        lb = self.loadings[self.index[b]]
        return float(np.dot(la, lb))

    def empirical_correlation(self, a: str, b: str) -> float:
        return float(np.corrcoef(self.column(a), self.column(b))[0, 1])


class SportAdapter:
    """Supplies sport-specific dependence. Owns no iteration or scoring logic."""

    sport = "base"

    def build_loadings(self, projections: Sequence[PlayerProjection],
                       snapshot: MarketSnapshot | None) -> FactorLoadings:  # pragma: no cover
        raise NotImplementedError

    def describe(self) -> str:
        return f"{self.sport} adapter"


def _normalise_loadings(mat: np.ndarray, max_systematic: float = 0.94) -> np.ndarray:
    """Keep total systematic variance below 1 so idiosyncratic variance stays positive."""
    norms = np.sqrt((mat ** 2).sum(axis=1))
    scale = np.where(norms > max_systematic, max_systematic / np.maximum(norms, 1e-12), 1.0)
    return mat * scale[:, None]


def simulate_slate(projections: Mapping[str, PlayerProjection],
                   adapter: SportAdapter,
                   snapshot: MarketSnapshot | None = None,
                   config: SimConfig | None = None) -> SlateSimulation:
    """Run correlated slate worlds and return per-player fantasy points."""
    cfg = config or SimConfig()
    projs = list(projections.values())
    if not projs:
        raise ValueError("simulate_slate requires at least one projection")
    ids = [p.player.player_id for p in projs]

    loadings = adapter.build_loadings(projs, snapshot)
    mat = _normalise_loadings(loadings.matrix(len(projs)))
    idio = np.sqrt(np.clip(1.0 - (mat ** 2).sum(axis=1), 1e-6, None))

    rng = np.random.default_rng(cfg.seed)
    n_w, n_p, n_f = cfg.n_worlds, len(projs), mat.shape[1]
    scores = np.empty((n_w, n_p), dtype=np.float32)

    # Pre-sort each player's market-implied sample so the copula maps uniforms
    # straight onto the empirical quantile function.
    marginals = []
    for p in projs:
        s = p.samples
        if s is None or len(s) == 0:
            s = np.full(256, p.engine_projection)
        marginals.append(np.sort(np.asarray(s, dtype=np.float64)))

    start = 0
    while start < n_w:
        n = min(cfg.chunk, n_w - start)
        f = rng.standard_normal((n, n_f)) if n_f else np.zeros((n, 0))
        z = (f @ mat.T) + rng.standard_normal((n, n_p)) * idio
        u = norm_cdf_vec(z)
        for j, quantiles in enumerate(marginals):
            pos = u[:, j] * (len(quantiles) - 1)
            lo = np.floor(pos).astype(np.int64)
            hi = np.minimum(lo + 1, len(quantiles) - 1)
            frac = pos - lo
            scores[start:start + n, j] = (quantiles[lo] * (1 - frac)
                                          + quantiles[hi] * frac).astype(np.float32)
        start += n

    meta = {
        "mode": cfg.mode,
        "iterations": cfg.n_worlds,
        "adapter": adapter.describe(),
        "factors": len(loadings.factor_names),
        "players": n_p,
        "seed": cfg.seed,
        "fallback_marginals": sum(1 for p in projs if p.coverage == "D"),
    }
    return SlateSimulation(player_ids=ids, scores=scores, config=cfg,
                           factor_names=list(loadings.factor_names), loadings=mat,
                           meta=meta)


def percentile_table(sim: SlateSimulation, player_id: str,
                     qs: Sequence[float] = (10, 25, 50, 75, 90, 99)) -> dict[str, float]:
    col = sim.column(player_id)
    return {f"p{int(q)}": float(np.percentile(col, q)) for q in qs}


def correlation_audit(sim: SlateSimulation, pairs: Sequence[tuple[str, str]]) -> list[dict]:
    """Implied vs realised correlation -- the sanity check the brain requires."""
    out = []
    for a, b in pairs:
        out.append({
            "a": a, "b": b,
            "implied": round(sim.implied_correlation(a, b), 3),
            "empirical": round(sim.empirical_correlation(a, b), 3),
        })
    return out


def effective_sample_note(n_worlds: int) -> str:
    """Honest labelling of tail precision at the chosen iteration count."""
    top1 = n_worlds * 0.01
    top01 = n_worlds * 0.001
    return (f"{n_worlds:,} worlds -> ~{top1:,.0f} observations in the top 1% and "
            f"~{top01:,.0f} in the top 0.1%; "
            + ("tail estimates are stable." if top01 >= 50 else
               "top-0.1% estimates are noisy at this iteration count."))


def relative_std_error(rate: float, n: int) -> float:
    if rate <= 0 or n <= 0:
        return float("inf")
    return math.sqrt((1 - rate) / (rate * n))
