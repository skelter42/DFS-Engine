import math

import numpy as np
import pytest

from dfs_engine.odds.distributions import (
    LognormalDistribution,
    ProbPoint,
    fit_count,
    fit_lognormal,
    make_count,
    norm_cdf,
    norm_cdf_vec,
    norm_ppf,
)


def test_norm_helpers_agree():
    for p in (0.01, 0.25, 0.5, 0.84, 0.999):
        assert norm_cdf(norm_ppf(p)) == pytest.approx(p, abs=1e-6)
    z = np.linspace(-5, 5, 101)
    assert np.allclose(norm_cdf_vec(z), [norm_cdf(float(v)) for v in z], atol=1e-8)


def test_single_line_fit_reproduces_the_quoted_probability():
    dist = fit_count([ProbPoint(5.5, 0.58)], dispersion=12.0)
    assert dist.sf(5.5) == pytest.approx(0.58, abs=1e-3)
    assert dist.mean > 5.5  # over is favoured, so the mean must sit above the line


def test_ladder_fit_beats_a_single_line_on_a_true_distribution():
    truth = make_count(6.2, dispersion=10.0)
    lines = [3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
    points = [ProbPoint(l, truth.sf(l)) for l in lines]
    fitted = fit_count(points, dispersion=10.0)
    assert fitted.mean == pytest.approx(truth.mean, rel=0.05)
    # tail behaviour, not just the mean, should line up
    assert fitted.sf(9.5) == pytest.approx(truth.sf(9.5), abs=0.02)


def test_lognormal_fit_recovers_mean_and_tail():
    sigma = math.sqrt(math.log(1 + 0.68 ** 2))
    truth = LognormalDistribution(mu=math.log(72) - 0.5 * sigma ** 2, sigma=sigma)
    points = [ProbPoint(l, truth.sf(l)) for l in (45.5, 60.5, 75.5, 90.5)]
    fitted = fit_lognormal(points, cv=0.68)
    assert fitted.mean == pytest.approx(truth.mean, rel=0.03)
    assert fitted.sf(100) == pytest.approx(truth.sf(100), abs=0.02)


def test_sampling_matches_the_fitted_survival_function():
    dist = fit_count([ProbPoint(4.5, 0.62)], dispersion=12.0)
    u = np.random.default_rng(3).random(200_000)
    draws = dist.ppf(u)
    assert float((draws > 4.5).mean()) == pytest.approx(dist.sf(4.5), abs=0.005)
    assert float(draws.mean()) == pytest.approx(dist.mean, rel=0.01)


def test_negative_binomial_is_wider_than_poisson():
    poisson = make_count(6.0, dispersion=None)
    negbin = make_count(6.0, dispersion=3.0)
    assert negbin.var > poisson.var
    assert negbin.sf(12.5) > poisson.sf(12.5)   # fatter tail


def test_zero_inflation_adds_mass_at_zero():
    plain = make_count(1.2)
    inflated = make_count(1.2, zero_inflation=0.3)
    assert inflated.pmf[0] > plain.pmf[0]
    assert inflated.mean < plain.mean
