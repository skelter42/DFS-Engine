"""Auditable, pre-lock NFL prop-to-DraftKings mean projection.

This module deliberately refuses to infer a mean from an unpriced line.  A
single paired yards quote also needs an externally calibrated standard
deviation; alternate thresholds can identify the spread from market prices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import erf, exp, isfinite, pi, sqrt
from statistics import NormalDist, median


NORMAL = NormalDist()
STATS = ("pass_yds", "pass_tds", "interceptions", "rush_yds",
         "receptions", "rec_yds", "offensive_tds", "fumbles_lost")
YARDS = {"pass_yds", "rush_yds", "rec_yds"}
COUNTS = set(STATS) - YARDS


class InsufficientMarket(ValueError):
    """The quotes do not identify a defensible stat expectation."""


def american_probability(odds: int | float) -> float:
    if not isfinite(odds) or odds == 0 or -100 < odds < 100:
        raise ValueError("Invalid American odds")
    return 100 / (odds + 100) if odds > 0 else -odds / (100 - odds)


def fair_over(over: int | float, under: int | float) -> float:
    a, b = american_probability(over), american_probability(under)
    if a + b < 0.98 or a + b > 1.35:
        raise ValueError("Implausible paired quote / mismatched strike")
    return a / (a + b)


def _utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Market timestamps must include timezone")
    return dt.astimezone(timezone.utc)


def _normal_cdf(x: float) -> float:
    return (1 + erf(x / sqrt(2))) / 2


def _count_tail(k: int, lam: float) -> float:
    if k <= 0:
        return 1.0
    mass = exp(-lam)
    cdf = mass
    for j in range(1, k):
        mass *= lam / j
        cdf += mass
    return max(0.0, min(1.0, 1 - cdf))


@dataclass(frozen=True)
class StatEstimate:
    mean: float
    method: str
    sigma: float | None = None
    fit_error: float = 0.0

    def at_least(self, threshold: int) -> float:
        if self.sigma is None:
            raise ValueError("Yardage threshold requires a fitted spread")
        # Yards are integer-valued.  The continuity correction is negligible
        # at large lines but matters for low-yardage players.
        return 1 - _normal_cdf((threshold - 0.5 - self._latent_mean()) / self.sigma)

    def _latent_mean(self) -> float:
        # 'mean' is E[max(0, X)], so store the latent mean separately below.
        raise NotImplementedError


@dataclass(frozen=True)
class YardEstimate(StatEstimate):
    latent_mean: float = 0.0

    def _latent_mean(self) -> float:
        return self.latent_mean


def estimate_stat(kind: str, quotes: list[dict], sigma_prior: float | None = None,
                  as_of_utc: str | None = None) -> StatEstimate:
    """Fit a censored normal (yards) or Poisson (counts) to paired quotes.

    Each quote is {threshold, over, under}; count thresholds mean >= k,
    yard thresholds mean > line. Independent books at one strike are combined
    by median fair probability. One-sided odds are intentionally rejected.
    """
    if kind not in STATS:
        raise ValueError(f"Unknown stat: {kind}")
    grouped: dict[float, list[float]] = {}
    for q in quotes:
        if as_of_utc is not None:
            if not q.get("book") or not q.get("captured_at_utc"):
                raise ValueError("Each quote needs book and captured_at_utc")
            quote_time = _utc(q["captured_at_utc"])
            run_time = _utc(as_of_utc)
            if quote_time > run_time or (run_time - quote_time).total_seconds() > 7200:
                raise InsufficientMarket("Quote is future-dated or over two hours old")
        t = float(q["threshold"])
        if not isfinite(t) or t < 0:
            raise ValueError("Invalid threshold")
        grouped.setdefault(t, []).append(fair_over(q["over"], q["under"]))
    if not grouped:
        raise InsufficientMarket("No paired prices")
    points = sorted((t, median(ps)) for t, ps in grouped.items())
    if kind in YARDS:
        if len(points) == 1:
            if sigma_prior is None or not isfinite(sigma_prior) or sigma_prior <= 0:
                raise InsufficientMarket("One yard line requires calibrated sigma_prior")
            sigma = sigma_prior
            t, p = points[0]
            mu = t - sigma * NORMAL.inv_cdf(1 - p)
            method = "one_line_plus_external_sigma"
        else:
            zs = [NORMAL.inv_cdf(1 - p) for _, p in points]
            mt = sum(t for t, _ in points) / len(points)
            mz = sum(zs) / len(zs)
            cov = sum((t - mt) * (z - mz) for (t, _), z in zip(points, zs))
            var = sum((t - mt) ** 2 for t, _ in points)
            slope = cov / var
            if slope <= 0:
                raise InsufficientMarket("Inconsistent alternate yard lines")
            sigma = 1 / slope
            mu = mt - mz * sigma
            method = "priced_alternate_yards"
        if not isfinite(sigma) or sigma <= 0 or not isfinite(mu):
            raise InsufficientMarket("Unstable yard fit")
        fit_error = max(abs(1 - _normal_cdf((t - mu) / sigma) - p) for t, p in points)
        if fit_error > 0.10:
            raise InsufficientMarket("Yard quotes disagree beyond 10 probability points")
        z = mu / sigma
        mean = mu * _normal_cdf(z) + sigma * exp(-z * z / 2) / sqrt(2 * pi)
        return YardEstimate(mean, method, sigma, fit_error, mu)

    for t, _ in points:
        if t < 1 or not t.is_integer():
            raise ValueError("Count thresholds must be integers >= 1")
    # Market fit is a working Poisson model, not a claim of true Poisson
    # scoring.  Preserve disagreement so it can be calibrated by role.
    def loss(lam: float) -> float:
        return sum((_count_tail(int(t), lam) - p) ** 2 for t, p in points)
    lo, hi = 0.0, 30.0
    for _ in range(100):
        left = lo + (hi - lo) / 3
        right = hi - (hi - lo) / 3
        if loss(left) < loss(right):
            hi = right
        else:
            lo = left
    lam = (lo + hi) / 2
    error = max(abs(_count_tail(int(t), lam) - p) for t, p in points)
    if error > 0.10:
        raise InsufficientMarket("Count quotes disagree beyond 10 probability points")
    return StatEstimate(lam, "paired_count_poisson", fit_error=error)


def project_player(player: dict) -> dict:
    """Return DK mean and provenance; fail closed on unfilled components.

    player has `prior_stats` for every absent market component, optionally
    `bonus_probs` for yards supplied only as prior stats, and `markets` by
    stat. Explicit prior zero is permitted; missing is never silently zero.
    """
    prior = player.get("prior_stats", {})
    markets = player.get("markets", {})
    sigma = player.get("sigma_prior", {})
    values: dict[str, float] = {}
    fitted: dict[str, StatEstimate] = {}
    provenance: dict[str, str] = {}
    for stat in STATS:
        if stat in markets:
            try:
                fit = estimate_stat(stat, markets[stat], sigma.get(stat),
                                    player.get("as_of_utc"))
                values[stat] = fit.mean
                fitted[stat] = fit
                provenance[stat] = fit.method
                continue
            except InsufficientMarket:
                pass
        if stat not in prior:
            raise InsufficientMarket(f"Missing market and prior: {stat}")
        v = float(prior[stat])
        if not isfinite(v) or v < 0:
            raise ValueError(f"Invalid prior for {stat}")
        values[stat] = v
        provenance[stat] = "industry_component_prior"

    bonuses: dict[str, float] = {}
    for stat, threshold in (("pass_yds", 300), ("rush_yds", 100), ("rec_yds", 100)):
        if stat in fitted:
            bonuses[stat] = fitted[stat].at_least(threshold)
        else:
            if stat not in player.get("bonus_probs", {}):
                raise InsufficientMarket(f"Missing market distribution / prior bonus probability: {stat}")
            p = float(player["bonus_probs"][stat])
            if not isfinite(p) or not 0 <= p <= 1:
                raise ValueError(f"Invalid bonus probability for {stat}")
            bonuses[stat] = p
    points = (0.04 * values["pass_yds"] + 4 * values["pass_tds"]
              - values["interceptions"] + 0.1 * values["rush_yds"]
              + values["receptions"] + 0.1 * values["rec_yds"]
              + 6 * values["offensive_tds"] - values["fumbles_lost"]
              + 3 * sum(bonuses.values()))
    return {"projection": round(points, 4), "stats": values,
            "bonus_probs": bonuses, "provenance": provenance,
            "fit_errors": {k: v.fit_error for k, v in fitted.items()}}
