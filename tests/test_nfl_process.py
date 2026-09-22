"""Regression tests for the documented NFL pregame projection process.

The worked example in the source methodology gives exact expected values, so
these are equality tests rather than sanity checks: if the odds math, the
distribution choices or the scoring table drift, these fail.
"""

import math

import numpy as np
import pytest

from dfs_engine.markets.catalog import CONTINUOUS_CV
from dfs_engine.models import GameEnvironment, Player, PlayerProjection
from dfs_engine.odds.conversions import american_to_prob, devig, devig_two_way
from dfs_engine.odds.distributions import (
    GammaDistribution,
    ProbPoint,
    fit_count,
    gamma_ppf,
    gamma_sf,
    gammainc_p,
)
from dfs_engine.projections.components import poisson_rate_from_prob
from dfs_engine.projections.reconcile import (
    RECEIVING_TD_SHARE,
    reconcile_team,
    validate,
)
from dfs_engine.projections.scoring import DK_NFL, DK_NFL_DST, DK_NFL_KICKER
from dfs_engine.projections.team_units import (
    TeamUnitInputs,
    defense_components,
    kicker_components,
)

# --- worked example ------------------------------------------------------
# A receiver with receiving yards 50.5 (-110/-110), receptions 4.5 (-110/-110)
# and anytime TD +200, before any team reconciliation.

EXPECTED_REC_YARDS = 58.500543
EXPECTED_RECEPTIONS = 4.670909
EXPECTED_TD_COUNT = 0.366244
EXPECTED_DK_POINTS = 13.100113


def test_worked_example_receiving_yards():
    p_over = devig_two_way(-110, -110)
    dist = GammaDistribution.from_line(50.5, p_over, CONTINUOUS_CV["rec_yards"])
    assert dist.mean == pytest.approx(EXPECTED_REC_YARDS, abs=1e-6)
    # The Gamma mean exceeds a balanced-price line because the median is lower.
    assert dist.mean > 50.5


def test_worked_example_receptions():
    p_over = devig_two_way(-110, -110)
    dist = fit_count([ProbPoint(4.5, p_over)])
    assert dist.mean == pytest.approx(EXPECTED_RECEPTIONS, abs=1e-6)


def test_worked_example_anytime_td_count():
    prob = devig([american_to_prob(200)], one_sided_multiplier=0.92)[0]
    assert prob == pytest.approx(0.306667, abs=1e-6)
    assert poisson_rate_from_prob(prob) == pytest.approx(EXPECTED_TD_COUNT, abs=1e-6)


def test_worked_example_dk_points():
    """Full scoring reproduction, including the modeled bonus and lost fumbles."""
    p_over = devig_two_way(-110, -110)
    yards = GammaDistribution.from_line(50.5, p_over, CONTINUOUS_CV["rec_yards"])
    catches = fit_count([ProbPoint(4.5, p_over)]).mean
    tds = poisson_rate_from_prob(devig([american_to_prob(200)],
                                       one_sided_multiplier=0.92)[0])
    lost_fumbles = 0.0035 * (catches + 0.22 * 0.0)

    linear = (0.1 * yards.mean + catches + 6 * tds - lost_fumbles)
    bonus = 3 * yards.sf(100)
    assert linear + bonus == pytest.approx(EXPECTED_DK_POINTS, abs=1e-5)


def test_sampled_scoring_matches_the_analytic_bonus():
    """The engine scores sampled components; that must agree with the closed form."""
    p_over = devig_two_way(-110, -110)
    yards = GammaDistribution.from_line(50.5, p_over, CONTINUOUS_CV["rec_yards"])
    u = np.random.default_rng(11).random(400_000)
    comps = {"rec_yards": yards.ppf(u), "receptions": np.full(400_000, EXPECTED_RECEPTIONS),
             "rec_td": np.full(400_000, EXPECTED_TD_COUNT),
             "fumble_lost": np.full(400_000, 0.0035 * EXPECTED_RECEPTIONS)}
    sampled = float(DK_NFL.score(comps).mean())
    assert sampled == pytest.approx(EXPECTED_DK_POINTS, rel=0.004)


# --- distribution machinery ---------------------------------------------


def test_incomplete_gamma_matches_known_values():
    # P(1, x) = 1 - exp(-x) exactly.
    for x in (0.25, 1.0, 3.5, 12.0):
        assert gammainc_p(1.0, x) == pytest.approx(1 - math.exp(-x), abs=1e-12)
    # Chi-square with 2 df: P(1, x/2); median is 2*ln(2).
    assert gamma_ppf(0.5, 1.0) == pytest.approx(math.log(2), abs=1e-9)
    assert gamma_sf(0.0, 2.0) == 1.0


def test_gamma_sampling_reproduces_the_analytic_tail():
    dist = GammaDistribution.from_mean_cv(72.0, 0.65)
    u = np.random.default_rng(5).random(300_000)
    draws = dist.ppf(u)
    assert float(draws.mean()) == pytest.approx(dist.mean, rel=0.01)
    assert float((draws > 100).mean()) == pytest.approx(dist.sf(100), abs=0.004)


def test_integer_count_lines_are_rejected_not_silently_reinterpreted():
    from dfs_engine.projections.components import _usable_count_points

    points = [ProbPoint(4.0, 0.5), ProbPoint(4.5, 0.5), ProbPoint(5.0, 0.4)]
    usable = _usable_count_points(points)
    assert [p.line for p in usable] == [4.5]


def test_one_sided_haircut_is_explicit_and_configurable():
    raw = american_to_prob(200)
    assert devig([raw], one_sided_multiplier=0.92)[0] == pytest.approx(0.92 * raw)
    assert devig([raw])[0] != pytest.approx(0.92 * raw)


# --- team reconciliation -------------------------------------------------


def _player(pid, name, pos, salary=5000, team="KC"):
    return Player(player_id=pid, name=name, team=team, positions=(pos,),
                  salary=salary, sport="nfl", opponent="BUF", game_id="KC@BUF")


def _with_components(player, **means):
    from dfs_engine.odds.distributions import make_count
    from dfs_engine.projections.components import counted

    proj = PlayerProjection(player=player)
    for stat, mean in means.items():
        if stat in CONTINUOUS_CV:
            from dfs_engine.odds.distributions import FittedStat

            proj.components[stat] = FittedStat(
                stat, GammaDistribution.from_mean_cv(mean, CONTINUOUS_CV[stat]))
        else:
            proj.components[stat] = counted(stat, mean)
    proj.engine_projection = sum(means.values())
    return proj


def test_reconciliation_makes_receiving_add_up_to_the_quarterback():
    qb = _with_components(_player("qb", "Passer", "QB", 7800),
                          pass_yards=280.0, pass_td=2.0)
    wr1 = _with_components(_player("wr1", "Alpha", "WR", 8000), rec_yards=80.0, rec_td=0.6)
    wr2 = _with_components(_player("wr2", "Beta", "WR", 5000), rec_yards=55.0, rec_td=0.4)
    te = _with_components(_player("te", "Tight", "TE", 4000), rec_yards=35.0, rec_td=0.3)
    rb = _with_components(_player("rb", "Back", "RB", 6000),
                          rec_yards=30.0, rec_td=0.1, rush_td=0.7)
    players = [qb, wr1, wr2, te, rb]

    result = reconcile_team(players)
    assert result.quarterback == "Passer"
    total_yards = sum(p.components["rec_yards"].mean for p in (wr1, wr2, te, rb))
    assert total_yards == pytest.approx(280.0, rel=1e-6)
    total_rec_td = sum(p.components["rec_td"].mean for p in (wr1, wr2, te, rb))
    assert total_rec_td == pytest.approx(2.0, rel=1e-6)
    # A running back's rushing touchdowns are untouched by passing volume.
    assert rb.components["rush_td"].mean == pytest.approx(0.7, rel=1e-9)

    report = validate([result], {p.player.player_id: p for p in players})
    assert report["passed"], report["failures"]


def test_reconciliation_is_idempotent():
    """Factors come from raw means, so re-running must not compound the scaling."""
    def build():
        qb = _with_components(_player("qb", "Passer", "QB"), pass_yards=300.0, pass_td=2.0)
        wr = _with_components(_player("wr", "Alpha", "WR"), rec_yards=100.0, rec_td=1.0)
        te = _with_components(_player("te", "Tight", "TE"), rec_yards=60.0, rec_td=0.5)
        return [qb, wr, te]

    players = build()
    reconcile_team(players)
    once = [p.components["rec_yards"].mean for p in players[1:]]
    reconcile_team(players)
    twice = [p.components["rec_yards"].mean for p in players[1:]]
    assert once == pytest.approx(twice, rel=1e-9)


def test_uncovered_receivers_get_a_labelled_share_not_zero():
    qb = _with_components(_player("qb", "Passer", "QB"), pass_yards=300.0, pass_td=2.0)
    covered = _with_components(_player("wr1", "Alpha", "WR", 8000),
                               rec_yards=100.0, rec_td=1.0)
    bare = PlayerProjection(player=_player("wr2", "Bench", "WR", 3600))
    result = reconcile_team([qb, covered, bare])
    assert "rec_yards" in bare.components
    assert bare.components["rec_yards"].mean > 0
    assert any("no posted receiving market" in n for n in bare.notes)
    assert result.yard_factor == pytest.approx(1.0, abs=0.01)


def test_receiving_share_constants_match_the_component_builder():
    from dfs_engine.projections.components import FootballComponents

    assert FootballComponents.RECEIVING_TD_SHARE == RECEIVING_TD_SHARE


# --- team units ----------------------------------------------------------


def test_kicker_residual_model():
    inputs = TeamUnitInputs(team="KC", implied_points=27.5, opponent="BUF",
                            opponent_implied_points=21.0, offensive_td_mean=2.6)
    res = kicker_components(inputs)
    xp = 0.96 * 2.6
    residual = 27.5 - 6 * 2.6 - xp
    fg = residual / 3
    assert res.mean("extra_points") == pytest.approx(xp, rel=1e-6)
    total_fg = sum(res.mean(s) for s in ("fg_0_39", "fg_40_49", "fg_50_plus"))
    assert total_fg == pytest.approx(fg, rel=1e-6)
    points = DK_NFL_KICKER.score_expectation({s: f.mean for s, f in res.components.items()})
    assert points == pytest.approx(xp + 3.60 * fg, rel=1e-6)


def test_kicker_flags_a_negative_residual_instead_of_hiding_it():
    res = kicker_components(TeamUnitInputs(team="X", implied_points=14.0,
                                           offensive_td_mean=2.6))
    total = sum(res.mean(s) for s in ("fg_0_39", "fg_40_49", "fg_50_plus"))
    assert total == pytest.approx(0.0, abs=1e-5)   # floored, up to the count-mean epsilon
    assert any("negative scoring residual" in n for n in res.notes)


def test_defense_scales_with_game_script():
    favoured = defense_components(TeamUnitInputs(
        team="KC", implied_points=28.0, opponent="X", opponent_implied_points=17.0,
        opponent_pass_attempts=34.0, opponent_interceptions=0.8))
    underdog = defense_components(TeamUnitInputs(
        team="Y", implied_points=17.0, opponent="Z", opponent_implied_points=28.0,
        opponent_pass_attempts=34.0, opponent_interceptions=0.8))
    assert favoured.mean("sacks") > underdog.mean("sacks")
    assert favoured.mean("def_td") > underdog.mean("def_td")
    assert favoured.components["points_allowed"].mean == 17.0


def test_dst_points_allowed_bands_use_half_point_boundaries():
    pa = np.array([0.0, 0.4, 0.6, 6.4, 6.6, 13.4, 20.4, 27.4, 34.4, 34.6])
    scores = DK_NFL_DST.score({"points_allowed": pa})
    assert list(scores) == [10.0, 10.0, 7.0, 7.0, 4.0, 4.0, 1.0, 0.0, -1.0, -4.0]


def test_defense_expectation_matches_the_documented_formula():
    inputs = TeamUnitInputs(team="KC", implied_points=27.0, opponent="BUF",
                            opponent_implied_points=20.0,
                            opponent_pass_attempts=35.0, opponent_interceptions=0.75)
    res = defense_components(inputs)
    advantage = 7.0
    expected_sacks = 35.0 / 0.93 * 0.07 * max(0.75, 1 + 0.04 * advantage)
    assert res.mean("sacks") == pytest.approx(expected_sacks, rel=1e-6)
    assert res.mean("def_td") == pytest.approx(0.12 + 0.005 * advantage, rel=1e-6)
    assert res.mean("def_interceptions") == pytest.approx(0.75, rel=1e-9)


# --- selection strategy --------------------------------------------------


def test_uniqueness_ladder_trades_tail_coverage_for_projection(
        nfl_projections, nfl_rules, nfl_ownership, nfl_sim):
    from dfs_engine.models import Contest
    from dfs_engine.optimize.solver import (ObjectiveWeights, SolverConfig,
                                            generate_candidates)
    from dfs_engine.portfolio.builder import SelectionConfig, select_portfolio
    from dfs_engine.simulation.field import FieldConfig, build_field, evaluate_lineups

    field = build_field(nfl_projections, nfl_rules, nfl_ownership, nfl_sim,
                        FieldConfig(n_entries=400, seed=21))
    pool = generate_candidates(nfl_projections, nfl_rules, nfl_ownership,
                               ObjectiveWeights(), SolverConfig(mode="world", seed=8),
                               n=30, sim=nfl_sim)
    evaluation = evaluate_lineups(
        nfl_sim, field, [[p.player_id for p in lu.players] for lu in pool.lineups],
        Contest(name="c", field_size=50000), ownership=nfl_ownership)

    ladder = select_portfolio(pool.lineups, evaluation,
                              SelectionConfig(n_lineups=8, strategy="uniqueness_ladder"))
    assert len(ladder.lineups) == 8
    assert ladder.trace[-1]["strategy"] == "uniqueness_ladder"
    assert ladder.trace[-1]["retention"] >= 0.85
    # The ladder optimises projection subject to uniqueness, so it should not
    # lose to a projection-blind selection on average projection.
    marginal = select_portfolio(pool.lineups, evaluation, SelectionConfig(n_lineups=8))
    ladder_proj = sum(lu.projection for lu in ladder.lineups) / 8
    marginal_proj = sum(lu.projection for lu in marginal.lineups) / 8
    assert ladder_proj >= marginal_proj * 0.97
