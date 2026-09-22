import numpy as np
import pytest

from dfs_engine.markets.aggregate import consensus_by_player
from dfs_engine.models import MarketSnapshot, Player
from dfs_engine.projections.engine import (
    ProjectionConfig,
    coverage_summary,
    market_weight,
    nearest_psd,
    project_player,
    project_slate,
)
from dfs_engine.projections.ownership import (
    behavioral_ownership,
    blend_ownership,
    leverage_score,
)


def test_market_components_recover_the_latent_truth(mlb_slate):
    """Props are posted around latent rates; fitting them back must recover those rates."""
    projections = project_slate(mlb_slate.players, mlb_slate.snapshot,
                                ProjectionConfig(site="dk", n_samples=2048))
    errors = []
    for pid, proj in projections.items():
        truth = mlb_slate.truth.get(pid) or {}
        for stat in ("hits", "total_bases", "home_runs", "strikeouts", "outs"):
            if stat in truth and stat in proj.components and truth[stat] > 0.1:
                fitted = proj.components[stat]
                if not fitted.inferred:
                    errors.append(abs(fitted.mean - truth[stat]) / truth[stat])
    assert len(errors) > 100
    assert float(np.mean(errors)) < 0.08


def test_nfl_projection_recovers_fantasy_points(nfl_slate, nfl_projections):
    """Market-covered players must come back close to the truth the props encode.

    The synthetic slate posts yardage quotes from a lognormal while the engine
    fits a Gamma, so this measures robustness to a misspecified family, not the
    engine inverting its own assumption.
    """
    from dfs_engine.projections.scoring import get_rule

    errors = []
    for pid, proj in nfl_projections.items():
        truth = nfl_slate.truth.get(pid)
        if not truth or proj.coverage not in {"A", "B"} or proj.modeled_from_team:
            continue
        rule = get_rule("dk", "nfl", proj.player.roster_role)
        expected = rule.score_expectation(truth)
        if expected > 5:
            errors.append((proj.engine_projection - expected) / expected)
    errors = np.array(errors)
    assert len(errors) > 40
    assert abs(float(errors.mean())) < 0.04          # no systematic bias
    assert float(np.abs(errors).mean()) < 0.06


def test_players_modeled_from_team_markets_are_labelled_and_looser(
        nfl_slate, nfl_projections):
    """A player with no props of his own is modeled, and says so.

    His production is derived from a teammate's market (the QB's passing total,
    the team rushing prior), which is a real basis but a much weaker one. He is
    graded tier C rather than D, and in a real build the vendor prior carries
    most of his weight.
    """
    from dfs_engine.projections.scoring import get_rule

    modeled = [p for p in nfl_projections.values() if p.modeled_from_team]
    assert modeled, "the synthetic slate should leave some players uncovered"
    for proj in modeled:
        assert proj.coverage in {"A", "B", "C"}
        assert any("modeled" in note or "no posted" in note for note in proj.notes)

    errors = []
    for proj in modeled:
        truth = nfl_slate.truth.get(proj.player.player_id)
        if not truth:
            continue
        expected = get_rule("dk", "nfl", proj.player.roster_role).score_expectation(truth)
        if expected > 5:
            errors.append(abs(proj.engine_projection - expected) / expected)
    if errors:
        # Much looser than the market-covered population, and that gap is the
        # point of the coverage grade.
        assert float(np.mean(errors)) < 0.45


def test_samples_carry_skew_not_symmetric_noise(nfl_projections):
    skewed = 0
    for proj in nfl_projections.values():
        if proj.coverage in {"A", "B"} and proj.engine_projection > 8:
            upside = proj.percentile(90) - proj.engine_projection
            downside = proj.engine_projection - proj.percentile(10)
            if upside > downside * 1.15:
                skewed += 1
    assert skewed >= 10, "market-derived distributions should be right-skewed"


def test_coverage_tiers_track_market_breadth(nfl_projections):
    summary = coverage_summary(nfl_projections)
    assert summary["players"] == len(nfl_projections)
    tiers = summary["tiers"]
    assert tiers["A"]["count"] > 0 and tiers["D"]["count"] > 0
    for proj in nfl_projections.values():
        if proj.coverage == "A":
            assert proj.n_markets >= 3 and proj.n_books >= 3
        if proj.coverage == "D":
            assert proj.market_projection is None


def test_market_weight_shrinks_toward_the_vendor_prior_as_coverage_falls():
    assert market_weight("A", 0.9, True) > market_weight("B", 0.6, True)
    assert market_weight("B", 0.6, True) > market_weight("C", 0.3, True)
    assert market_weight("D", 0.0, True) == 0.0
    assert market_weight("C", 0.1, False) == 1.0     # no prior to shrink toward


def test_eligibility_gate_excludes_source_zero_players():
    players = [
        Player("a", "Zeroed Out", "KC", ("WR",), 5000, "nfl", vendor_projection=0.0),
        Player("b", "Playing", "KC", ("WR",), 5000, "nfl", vendor_projection=12.0),
        Player("c", "Ruled Out", "KC", ("WR",), 5000, "nfl", vendor_projection=9.0,
               status="OUT"),
        Player("d", "No Vendor Data", "KC", ("WR",), 5000, "nfl"),
    ]
    result = project_slate(players, MarketSnapshot(sport="nfl"), ProjectionConfig())
    assert set(result) == {"b", "d"}


def test_blend_respects_the_vendor_prior_when_coverage_is_thin(nfl_slate):
    player = next(p for p in nfl_slate.players if p.positions[0] == "WR")
    player.vendor_projection = 40.0                   # deliberately extreme prior
    snapshot = nfl_slate.snapshot
    consensus = consensus_by_player(snapshot)
    rng = np.random.default_rng(1)
    proj = project_player(player, snapshot, consensus, ProjectionConfig(), rng)
    if proj.coverage in {"C", "D"}:
        assert proj.engine_projection > 20            # prior dominates
    else:
        assert proj.engine_projection < 30            # market dominates
    player.vendor_projection = None


def test_ownership_sums_to_the_structural_roster_total(nfl_projections, nfl_rules,
                                                       nfl_slate):
    own = behavioral_ownership(nfl_projections, nfl_rules, nfl_slate.snapshot)
    assert sum(own.values()) == pytest.approx(100.0 * nfl_rules.size, rel=0.02)
    assert max(own.values()) < 70                     # no one is on 70% of rosters
    assert min(own.values()) >= 0


def test_ownership_prefers_supplied_industry_numbers(nfl_projections, nfl_rules,
                                                     nfl_slate):
    pid = next(iter(nfl_projections))
    industry = {pid: [30.0, 32.0, 31.0]}
    result = blend_ownership(nfl_projections, nfl_rules, nfl_slate.snapshot,
                             industry=industry)
    assert result.ownership[pid] > 20                 # the anchor carries most of the weight
    assert result.confidence[pid] == "A"
    assert result.diagnostics["multi_source_players"] == 1


def test_ownership_flags_large_disagreement_with_the_field_model(nfl_projections,
                                                                 nfl_rules, nfl_slate):
    pid = min(nfl_projections, key=lambda k: nfl_projections[k].engine_projection)
    result = blend_ownership(nfl_projections, nfl_rules, nfl_slate.snapshot,
                             industry={pid: [55.0, 56.0]})
    assert any("disagreement" in flag for flag in result.audit_flags)


def test_leverage_rewards_ceiling_over_ownership():
    class _P:
        ceiling = 30.0
    assert leverage_score(_P(), 5.0) > leverage_score(_P(), 30.0)


def test_nearest_psd_fixes_an_impossible_correlation_matrix():
    bad = np.array([[1.0, 0.95, 0.95], [0.95, 1.0, -0.95], [0.95, -0.95, 1.0]])
    fixed = nearest_psd(bad)
    assert np.all(np.linalg.eigvalsh(fixed) > -1e-8)
    assert np.allclose(np.diag(fixed), 1.0)
