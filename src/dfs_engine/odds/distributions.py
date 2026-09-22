"""Turn de-vigged prop probabilities into stat distributions.

A prop is a probability statement about a *distribution*, not a point
estimate: ``Over 5.5 K @ -120`` says ``P(K >= 6) = 0.55``. This module inverts
that statement into a full distribution per stat, so the engine gets an
expectation, a shape, and the tail behaviour that DFS ceilings depend on --
including scoring bonuses, which are pure tail events.

Alternate/ladder lines are fitted jointly by weighted least squares in
probability space, which is how ``core/MARKET_PROJECTIONS.md`` asks for them
to be used.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

SQRT2 = math.sqrt(2.0)


def norm_cdf(x: float | np.ndarray) -> float | np.ndarray:
    if isinstance(x, np.ndarray):
        from numpy import vectorize  # local import keeps module import cheap

        return 0.5 * (1.0 + vectorize(math.erf)(x / SQRT2))
    return 0.5 * (1.0 + math.erf(x / SQRT2))


def norm_ppf(p: float) -> float:
    """Acklam's rational approximation to the standard normal quantile."""
    if not 0.0 < p < 1.0:
        raise ValueError("norm_ppf requires 0 < p < 1")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


# --------------------------------------------------------------------------
# Incomplete gamma (no SciPy dependency)
# --------------------------------------------------------------------------


def _gammainc_series(a: float, x: float, iters: int = 400, tol: float = 1e-14) -> float:
    """Regularized lower incomplete gamma P(a, x) by series. Converges for x < a+1."""
    if x <= 0:
        return 0.0
    ap = a
    total = delta = 1.0 / a
    for _ in range(iters):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * tol:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gammainc_cf(a: float, x: float, iters: int = 400, tol: float = 1e-14) -> float:
    """Regularized upper incomplete gamma Q(a, x) by continued fraction (x > a+1)."""
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, iters + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < tol:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def gammainc_p(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x) = Gamma(a, scale=1).cdf(x)."""
    if x <= 0:
        return 0.0
    if a <= 0:
        raise ValueError("shape must be positive")
    if x < a + 1.0:
        return min(1.0, _gammainc_series(a, x))
    return max(0.0, 1.0 - _gammainc_cf(a, x))


def gamma_sf(x: float, shape: float, scale: float = 1.0) -> float:
    """P(X > x) for a Gamma(shape, scale) variable."""
    if x <= 0:
        return 1.0
    return max(0.0, 1.0 - gammainc_p(shape, x / scale))


def gamma_ppf(q: float, shape: float, scale: float = 1.0) -> float:
    """Gamma quantile by bracketed bisection on the regularized CDF."""
    if not 0.0 < q < 1.0:
        raise ValueError("gamma_ppf requires 0 < q < 1")
    lo, hi = 0.0, max(shape, 1.0)
    while gammainc_p(shape, hi) < q and hi < 1e6:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gammainc_p(shape, mid) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12 * max(hi, 1.0):
            break
    return 0.5 * (lo + hi) * scale


#: Quantile grid: dense in both tails so bonus thresholds stay accurate.
_GAMMA_U_GRID = np.concatenate([
    np.logspace(-5, -2, 120),
    np.linspace(0.0105, 0.9895, 760),
    1.0 - np.logspace(-2, -5, 120),
])
_GAMMA_QUANTILE_CACHE: dict[float, np.ndarray] = {}


def _standard_gamma_quantiles(shape: float) -> np.ndarray:
    """Cached Gamma(shape, 1) quantiles; scale is a pure multiplier."""
    key = round(float(shape), 6)
    cached = _GAMMA_QUANTILE_CACHE.get(key)
    if cached is None:
        cached = np.array([gamma_ppf(float(u), key) for u in _GAMMA_U_GRID])
        _GAMMA_QUANTILE_CACHE[key] = cached
    return cached


# --------------------------------------------------------------------------
# Observations
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbPoint:
    """``P(stat > line) = prob``, with an evidence weight."""

    line: float
    prob_over: float
    weight: float = 1.0


# --------------------------------------------------------------------------
# Distribution objects
# --------------------------------------------------------------------------


class StatDistribution:
    """Common surface: expectation, survival, and inverse-CDF sampling."""

    name: str = "base"

    @property
    def mean(self) -> float:  # pragma: no cover - interface
        raise NotImplementedError

    def sf(self, line: float) -> float:  # pragma: no cover - interface
        """P(X > line)."""
        raise NotImplementedError

    def ppf(self, u: np.ndarray) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> dict:  # pragma: no cover - trivial
        return {"family": self.name, "mean": round(self.mean, 4)}


@dataclass
class DiscreteDistribution(StatDistribution):
    """Poisson / negative-binomial counts, held as an explicit pmf vector."""

    pmf: np.ndarray
    name: str = "poisson"
    inflation_zero: float = 0.0

    def __post_init__(self) -> None:
        self.pmf = np.asarray(self.pmf, dtype=float)
        total = self.pmf.sum()
        if total <= 0:
            raise ValueError("pmf must have positive mass")
        self.pmf = self.pmf / total
        self._cdf = np.cumsum(self.pmf)
        self._support = np.arange(len(self.pmf), dtype=float)

    @property
    def mean(self) -> float:
        return float(np.dot(self._support, self.pmf))

    @property
    def var(self) -> float:
        m = self.mean
        return float(np.dot((self._support - m) ** 2, self.pmf))

    def sf(self, line: float) -> float:
        k = math.floor(line) + 1  # "over 5.5" and "over 5" both mean X >= 6
        if k <= 0:
            return 1.0
        if k >= len(self.pmf):
            return 0.0
        return float(1.0 - self._cdf[k - 1])

    def pr_at_least(self, k: int) -> float:
        if k <= 0:
            return 1.0
        if k >= len(self.pmf):
            return 0.0
        return float(1.0 - self._cdf[k - 1])

    def ppf(self, u: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(self._cdf, np.clip(u, 0.0, 1.0 - 1e-12), side="left")
        return np.minimum(idx, len(self.pmf) - 1).astype(float)


@dataclass
class LognormalDistribution(StatDistribution):
    """Right-skewed non-negative continuous stat (yardage, minutes, time-on-ice)."""

    mu: float
    sigma: float
    name: str = "lognormal"
    zero_prob: float = 0.0

    @property
    def mean(self) -> float:
        return float((1.0 - self.zero_prob) * math.exp(self.mu + 0.5 * self.sigma ** 2))

    def sf(self, line: float) -> float:
        if line <= 0:
            return 1.0 - self.zero_prob
        z = (math.log(line) - self.mu) / self.sigma
        return float((1.0 - self.zero_prob) * (1.0 - norm_cdf(z)))

    def ppf(self, u: np.ndarray) -> np.ndarray:
        u = np.clip(u, 1e-9, 1 - 1e-9)
        out = np.zeros_like(u, dtype=float)
        live = u > self.zero_prob
        if self.zero_prob > 0:
            scaled = (u[live] - self.zero_prob) / (1.0 - self.zero_prob)
        else:
            scaled = u[live]
        scaled = np.clip(scaled, 1e-9, 1 - 1e-9)
        z = np.array([norm_ppf(float(v)) for v in scaled]) if scaled.size < 64 else _norm_ppf_vec(scaled)
        out[live] = np.exp(self.mu + self.sigma * z)
        return out


@dataclass
class GammaDistribution(StatDistribution):
    """Right-skewed non-negative continuous stat, parameterised by mean and CV.

    This is the yardage model in the NFL pregame process: ``shape = 1/CV**2``
    and ``scale = mean * CV**2``. Its mean sits above its median, which is why a
    balanced-price yardage line implies an expectation above the line.
    """

    shape: float
    scale: float
    name: str = "gamma"

    @classmethod
    def from_mean_cv(cls, mean: float, cv: float) -> "GammaDistribution":
        shape = 1.0 / (cv * cv)
        return cls(shape=shape, scale=max(mean, 1e-9) * cv * cv)

    @classmethod
    def from_line(cls, line: float, prob_over: float, cv: float) -> "GammaDistribution":
        """Fit so that ``P(X > line) == prob_over`` at the supplied CV."""
        shape = 1.0 / (cv * cv)
        scale = line / gamma_ppf(1.0 - prob_over, shape)
        return cls(shape=shape, scale=scale)

    @property
    def mean(self) -> float:
        return float(self.shape * self.scale)

    @property
    def cv(self) -> float:
        return float(1.0 / math.sqrt(self.shape))

    def sf(self, line: float) -> float:
        return gamma_sf(line, self.shape, self.scale)

    def ppf(self, u: np.ndarray) -> np.ndarray:
        grid = _standard_gamma_quantiles(self.shape)
        return np.interp(np.clip(u, 1e-9, 1 - 1e-9), _GAMMA_U_GRID, grid) * self.scale


@dataclass
class NormalDistribution(StatDistribution):
    """Symmetric continuous stat (team points allowed in the DST model)."""

    mu: float
    sigma: float
    name: str = "normal"
    floor: float | None = None

    @property
    def mean(self) -> float:
        return float(self.mu)

    def sf(self, line: float) -> float:
        return float(1.0 - norm_cdf((line - self.mu) / self.sigma))

    def ppf(self, u: np.ndarray) -> np.ndarray:
        out = self.mu + self.sigma * _norm_ppf_vec(np.clip(u, 1e-9, 1 - 1e-9))
        if self.floor is not None:
            out = np.maximum(out, self.floor)
        return out


@dataclass
class BernoulliDistribution(StatDistribution):
    """Binary market (anytime TD, pitcher win, shutout)."""

    p: float
    name: str = "bernoulli"

    @property
    def mean(self) -> float:
        return float(self.p)

    def sf(self, line: float) -> float:
        return float(self.p) if line < 1 else 0.0

    def ppf(self, u: np.ndarray) -> np.ndarray:
        return (u > (1.0 - self.p)).astype(float)


@dataclass
class ConstantDistribution(StatDistribution):
    """A stat we know only as an expectation (no market shape available)."""

    value: float
    name: str = "constant"

    @property
    def mean(self) -> float:
        return float(self.value)

    def sf(self, line: float) -> float:
        return 1.0 if self.value > line else 0.0

    def ppf(self, u: np.ndarray) -> np.ndarray:
        return np.full(u.shape, float(self.value))


_NORM_CDF_GRID = None


def norm_cdf_vec(z: np.ndarray) -> np.ndarray:
    """Vectorised standard-normal CDF via a cached interpolation table.

    Fast enough to map millions of copula draws to uniforms without SciPy.
    """
    global _NORM_CDF_GRID
    if _NORM_CDF_GRID is None:
        grid_z = np.linspace(-8.0, 8.0, 160001)
        grid_p = np.array([0.5 * (1.0 + math.erf(float(v) / SQRT2)) for v in grid_z])
        _NORM_CDF_GRID = (grid_z, grid_p)
    gz, gp = _NORM_CDF_GRID
    return np.interp(np.clip(z, -8.0, 8.0), gz, gp)


_NORM_PPF_GRID = None


def _norm_ppf_vec(u: np.ndarray) -> np.ndarray:
    """Vectorised normal quantile via a cached interpolation grid."""
    global _NORM_PPF_GRID
    if _NORM_PPF_GRID is None:
        grid_p = np.linspace(1e-6, 1 - 1e-6, 20001)
        grid_z = np.array([norm_ppf(float(p)) for p in grid_p])
        _NORM_PPF_GRID = (grid_p, grid_z)
    grid_p, grid_z = _NORM_PPF_GRID
    return np.interp(np.clip(u, 1e-6, 1 - 1e-6), grid_p, grid_z)


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------


_LOG_FACTORIAL_CACHE: np.ndarray = np.array([0.0])


def _log_factorial(max_k: int) -> np.ndarray:
    """Cached log(k!) table; rebuilding it per pmf dominated the fitting loop."""
    global _LOG_FACTORIAL_CACHE
    if len(_LOG_FACTORIAL_CACHE) <= max_k:
        size = max(max_k + 1, 2 * len(_LOG_FACTORIAL_CACHE))
        _LOG_FACTORIAL_CACHE = np.concatenate(
            [[0.0], np.cumsum(np.log(np.arange(1, size)))])
    return _LOG_FACTORIAL_CACHE[:max_k + 1]


def poisson_pmf(mean: float, max_k: int) -> np.ndarray:
    mean = max(mean, 1e-6)
    ks = np.arange(max_k + 1)
    return np.exp(-mean + ks * math.log(mean) - _log_factorial(max_k))


def negbin_pmf(mean: float, dispersion: float, max_k: int) -> np.ndarray:
    """NB parameterised by mean and dispersion r (var = mean + mean^2 / r)."""
    mean = max(mean, 1e-6)
    r = max(dispersion, 1e-3)
    p = r / (r + mean)
    ks = np.arange(max_k + 1)
    log_binom = (np.array([math.lgamma(k + r) for k in ks]) - math.lgamma(r)
                 - _log_factorial(max_k))
    return np.exp(log_binom + r * math.log(p) + ks * math.log1p(-p))


def make_count(mean: float, dispersion: float | None = None, max_k: int | None = None,
               zero_inflation: float = 0.0) -> DiscreteDistribution:
    """Count distribution; ``dispersion=None`` gives Poisson, else negative binomial."""
    mean = max(float(mean), 1e-6)
    if max_k is None:
        max_k = int(max(8, math.ceil(mean + 10 * math.sqrt(mean + 1) + 4)))
    if dispersion is None:
        pmf = poisson_pmf(mean, max_k)
        name = "poisson"
    else:
        pmf = negbin_pmf(mean, dispersion, max_k)
        name = "negbin"
    if zero_inflation > 0:
        pmf = pmf * (1.0 - zero_inflation)
        pmf[0] += zero_inflation
    return DiscreteDistribution(pmf=pmf, name=name)


def _count_sf(mean: float, line: float, dispersion: float | None, max_k: int) -> float:
    return make_count(mean, dispersion, max_k).sf(line)


#: Dispersion grid scanned when a ladder is rich enough to identify shape.
#: ``None`` is Poisson (var = mean); small r means heavy over-dispersion.
DISPERSION_GRID: tuple[float | None, ...] = (1.5, 3.0, 6.0, 12.0, 25.0, 60.0, 150.0, None)


def fit_count(points: Sequence[ProbPoint], dispersion: float | None = None,
              bounds: tuple[float, float] = (0.01, 60.0),
              fit_dispersion: bool = True) -> DiscreteDistribution:
    """Fit a count distribution to one or many ``P(X > line)`` observations.

    Single observation -> exact bisection on the mean at the adapter's prior
    dispersion. Ladder of three or more lines -> the shape is identifiable, so
    mean and dispersion are fitted jointly by weighted least squares in
    probability space (``core/MARKET_PROJECTIONS.md``: use alternate/ladder
    markets to estimate tail probabilities).
    """
    pts = [p for p in points if 0.0 < p.prob_over < 1.0]
    if not pts:
        raise ValueError("fit_count needs at least one usable probability point")
    max_k = int(max(12, math.ceil(max(p.line for p in pts) * 3 + 20)))
    lo, hi = bounds

    def loss_for(disp: float | None):
        def loss(mean: float) -> float:
            d = make_count(mean, disp, max_k)
            return sum(p.weight * (d.sf(p.line) - p.prob_over) ** 2 for p in pts)

        return loss

    if len(pts) == 1:
        target = pts[0].prob_over
        line = pts[0].line
        k = math.floor(line) + 1
        if dispersion is None and k >= 1:
            # Exact: for X ~ Poisson(mean), P(X >= k) is the regularized lower
            # incomplete gamma P(k, mean), so inverting it solves the fit in one
            # bracketed search instead of rebuilding a pmf per bisection step.
            return make_count(gamma_ppf(target, float(k)), None, max_k)
        a, b = lo, hi
        for _ in range(80):
            mid = 0.5 * (a + b)
            if _count_sf(mid, line, dispersion, max_k) < target:
                a = mid
            else:
                b = mid
        return make_count(0.5 * (a + b), dispersion, max_k)

    candidates: list[float | None]
    if fit_dispersion and len(pts) >= 3:
        candidates = list(DISPERSION_GRID)
        if dispersion is not None and dispersion not in candidates:
            candidates.append(dispersion)
    else:
        candidates = [dispersion]

    best = None
    for disp in candidates:
        f = loss_for(disp)
        mean = _golden(f, lo, hi)
        score = f(mean)
        if best is None or score < best[0]:
            best = (score, mean, disp)
    assert best is not None
    return make_count(best[1], best[2], max_k)


def fit_lognormal(points: Sequence[ProbPoint], cv: float = 0.55,
                  bounds: tuple[float, float] = (0.05, 600.0)) -> LognormalDistribution:
    """Fit a lognormal mean (coefficient of variation supplied by the sport adapter)."""
    pts = [p for p in points if 0.0 < p.prob_over < 1.0 and p.line > 0]
    if not pts:
        raise ValueError("fit_lognormal needs at least one usable probability point")
    sigma = math.sqrt(math.log(1.0 + cv * cv))

    if len(pts) == 1:
        p = pts[0]
        mu = math.log(p.line) + sigma * norm_ppf(p.prob_over)
        return LognormalDistribution(mu=mu, sigma=sigma)

    def loss(mean: float) -> float:
        mu = math.log(max(mean, 1e-6)) - 0.5 * sigma ** 2
        d = LognormalDistribution(mu=mu, sigma=sigma)
        return sum(p.weight * (d.sf(p.line) - p.prob_over) ** 2 for p in pts)

    mean = _golden(loss, *bounds)
    return LognormalDistribution(mu=math.log(mean) - 0.5 * sigma ** 2, sigma=sigma)


def fit_gamma(points: Sequence[ProbPoint], cv: float) -> GammaDistribution:
    """Fit a Gamma yardage distribution to one or many ``P(X > line)`` points.

    A single line is an exact solve (the NFL process's ``yardage_mean``); a
    ladder is fitted by weighted least squares on the mean at the supplied CV.
    """
    pts = [p for p in points if 0.0 < p.prob_over < 1.0 and p.line > 0]
    if not pts:
        raise ValueError("fit_gamma needs at least one usable probability point")
    if len(pts) == 1:
        return GammaDistribution.from_line(pts[0].line, pts[0].prob_over, cv)

    def loss(mean: float) -> float:
        dist = GammaDistribution.from_mean_cv(mean, cv)
        return sum(p.weight * (dist.sf(p.line) - p.prob_over) ** 2 for p in pts)

    mean = _golden(loss, 0.05, 700.0)
    return GammaDistribution.from_mean_cv(mean, cv)


def _golden(f, lo: float, hi: float, iters: int = 60) -> float:
    invphi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c = b - invphi * (b - a)
    d = a + invphi * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - invphi * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + invphi * (b - a)
            fd = f(d)
        if abs(b - a) < 1e-7:
            break
    return 0.5 * (a + b)


@dataclass
class FittedStat:
    """A market-derived stat distribution plus the evidence behind it."""

    stat: str
    dist: StatDistribution
    n_points: int = 0
    n_books: int = 0
    sources: list[str] = field(default_factory=list)
    inferred: bool = False  # True when derived from context, not a direct prop

    @property
    def mean(self) -> float:
        return self.dist.mean

    def describe(self) -> dict:
        return {
            "stat": self.stat,
            "mean": round(self.mean, 3),
            "family": self.dist.name,
            "points": self.n_points,
            "books": self.n_books,
            "inferred": self.inferred,
        }
