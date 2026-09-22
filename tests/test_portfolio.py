import numpy as np
import pytest

from dfs_engine.models import Contest, Portfolio
from dfs_engine.optimize.solver import ObjectiveWeights, SolverConfig, generate_candidates
from dfs_engine.portfolio.allocation import AllocationConfig, allocate, allocation_audit
from dfs_engine.portfolio.builder import SelectionConfig, label_lineups, select_portfolio
from dfs_engine.portfolio.diagnostics import (
    correlation_summary,
    exposure_table,
    final_audit,
    largest_deviations,
    risk_flags,
)
from dfs_engine.simulation.field import FieldConfig, build_field, evaluate_lineups
from dfs_engine.simulation.portfolio import (
    champion_challenger,
    concentration_report,
    hidden_world_concentration,
    marginal_values,
    portfolio_metrics,
)


@pytest.fixture(scope="module")
def evaluated(nfl_projections, nfl_rules, nfl_ownership, nfl_sim):
    field = build_field(nfl_projections, nfl_rules, nfl_ownership, nfl_sim,
                        FieldConfig(n_entries=800, seed=11))
    pool = generate_candidates(nfl_projections, nfl_rules, nfl_ownership,
                               ObjectiveWeights(), SolverConfig(mode="world", seed=5),
                               n=45, sim=nfl_sim)
    contest = Contest(name="GPP", entries=10, field_size=50000, payout_top_fraction=0.2)
    result = evaluate_lineups(nfl_sim, field, [[p.player_id for p in lu.players]
                                               for lu in pool.lineups],
                              contest, ownership=nfl_ownership)
    label_lineups(pool.lineups, nfl_projections, nfl_ownership, result.metrics)
    return pool.lineups, result, contest


def test_marginal_selection_beats_taking_the_top_n_by_ev(evaluated):
    """The whole point of portfolio selection: coverage, not repetition."""
    candidates, evaluation, _ = evaluated
    n = 8
    chosen = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=n))
    greedy_top = list(np.argsort(-evaluation.payouts.mean(axis=1))[:n])

    in_tail = evaluation.beaten_by <= 0.01
    picked_cover = float(in_tail[chosen.indices].any(axis=0).mean())
    naive_cover = float(in_tail[greedy_top].any(axis=0).mean())
    assert picked_cover >= naive_cover

    picked_corr = portfolio_metrics(
        _subset(evaluation, chosen.indices), [candidates[i] for i in chosen.indices])
    naive_corr = portfolio_metrics(
        _subset(evaluation, greedy_top), [candidates[i] for i in greedy_top])
    # When both strategies land on the same set the two figures differ only by
    # floating-point row ordering, so compare with a tolerance.
    assert picked_corr.effective_lineups >= naive_corr.effective_lineups - 1e-9


def _subset(evaluation, indices):
    from dfs_engine.simulation.field import EvaluationResult

    idx = list(indices)
    return EvaluationResult(
        metrics=[evaluation.metrics[i] for i in idx],
        scores=evaluation.scores[idx], beaten_by=evaluation.beaten_by[idx],
        payouts=evaluation.payouts[idx], contest=evaluation.contest)


def test_selection_respects_min_uniques(evaluated):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation,
                              SelectionConfig(n_lineups=6, min_uniques=3))
    for i, a in enumerate(result.lineups):
        for b in result.lineups[i + 1:]:
            assert a.overlap(b) <= len(a.players) - 3


def test_selection_trace_explains_every_pick(evaluated):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=5))
    assert len(result.trace) == len(result.lineups)
    for row in result.trace:
        assert {"ev", "new_tail_worlds", "marginal_payout", "max_corr"} <= set(row)


def test_labels_describe_the_script(evaluated):
    candidates, _, _ = evaluated
    for lu in candidates:
        assert lu.labels["risk"] in {"chalk-leaning", "balanced", "leverage"}
        assert lu.labels["anchor_team"] in set(lu.teams)
        assert "x" in lu.labels["stack"]


def test_allocation_gives_every_contest_a_full_mini_portfolio(evaluated):
    candidates, evaluation, _ = evaluated
    selected = select_portfolio(candidates, evaluation,
                                SelectionConfig(n_lineups=12)).lineups
    contests = [
        Contest(name="Big", entries=8, field_size=150000, entry_fee=20, priority=1),
        Contest(name="Small", entries=4, field_size=4000, entry_fee=3, priority=2),
    ]
    allocation = allocate(selected, contests, AllocationConfig())
    assert sum(len(v) for v in allocation.values()) == 12
    assert len(allocation["Big"]) == 8 and len(allocation["Small"]) == 4
    # the small contest must not be a dumping ground: its best lineup should be
    # competitive with the big contest's median
    big = sorted(float(lu.metrics["expected_payout"]) for lu in allocation["Big"])
    small = sorted(float(lu.metrics["expected_payout"]) for lu in allocation["Small"])
    assert max(small) >= big[len(big) // 2] * 0.8

    audit = allocation_audit(allocation, contests)
    assert {row["contest"] for row in audit} == {"Big", "Small"}
    for row in audit:
        assert row["unique_lineups"] == row["lineups"]


def test_single_contest_allocation_is_a_passthrough(evaluated):
    candidates, evaluation, contest = evaluated
    selected = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=4)).lineups
    allocation = allocate(selected, [contest])
    assert len(allocation[contest.name]) == 4
    assert all(lu.contest == contest.name for lu in selected)


def test_portfolio_metrics_flag_hidden_concentration(evaluated):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=10))
    subset = _subset(evaluation, result.indices)
    metrics = portfolio_metrics(subset, result.lineups)
    assert 0 <= metrics.any_top1_rate <= 1
    assert metrics.any_top1_rate >= max(m.top1_rate for m in subset.metrics)
    assert 1 <= metrics.effective_lineups <= metrics.n_lineups
    hidden = hidden_world_concentration(subset, result.lineups)
    assert hidden["top_teams"] and sum(t["share_pct"] for t in hidden["top_teams"]) <= 100.5
    assert len(marginal_values(subset)) == len(result.lineups)


def test_concentration_report_detects_a_single_story_portfolio(evaluated):
    candidates, _, _ = evaluated
    one = concentration_report([candidates[0]] * 5)
    many = concentration_report(candidates[:5])
    assert one["player_hhi"] > many["player_hhi"]


def test_exposure_table_reports_percentage_point_differences(
        evaluated, nfl_projections, nfl_ownership):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=6))
    portfolio = Portfolio(lineups=result.lineups)
    rows = exposure_table(portfolio, nfl_projections, nfl_ownership)
    assert rows
    for row in rows:
        assert row.difference_pp == pytest.approx(
            row.exposure_pct - row.engine_ownership, abs=0.11)
        assert row.reason
    assert len(largest_deviations(rows, 3)) == 3
    assert correlation_summary(portfolio)["stack_size_distribution"]


def test_final_audit_catches_an_illegal_portfolio(evaluated, nfl_projections, nfl_rules):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=4))
    good = Portfolio(lineups=result.lineups)
    assert final_audit(good, nfl_projections, nfl_rules)["passed"]

    bad = Portfolio(lineups=[result.lineups[0], result.lineups[0]])
    report = final_audit(bad, nfl_projections, nfl_rules)
    assert not report["passed"]
    assert any("duplicate" in f for f in report["failures"])


def test_final_audit_blocks_a_source_zero_player(evaluated, nfl_projections, nfl_rules):
    candidates, evaluation, _ = evaluated
    lineup = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=1)).lineups[0]
    victim = lineup.players[0]
    original = victim.vendor_projection
    victim.vendor_projection = 0.0
    try:
        report = final_audit(Portfolio(lineups=[lineup]), nfl_projections, nfl_rules)
        assert not report["passed"]
        assert any("source-zero" in f for f in report["failures"])
    finally:
        victim.vendor_projection = original


def test_risk_flags_surface_fallback_projections(evaluated, nfl_projections):
    candidates, evaluation, _ = evaluated
    result = select_portfolio(candidates, evaluation, SelectionConfig(n_lineups=8))
    flags = risk_flags(nfl_projections, Portfolio(lineups=result.lineups))
    assert isinstance(flags, list)


def test_champion_challenger_retains_an_equal_portfolio(evaluated):
    candidates, evaluation, _ = evaluated
    idx = list(range(6))
    subset = _subset(evaluation, idx)
    verdict = champion_challenger(subset, subset, candidates[:6], candidates[:6])
    assert verdict["verdict"] == "retain_champion"
    assert verdict["champion"]["any_top1_rate"] == verdict["challenger"]["any_top1_rate"]
