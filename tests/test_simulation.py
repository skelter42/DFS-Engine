import numpy as np
import pytest

from dfs_engine.models import Contest
from dfs_engine.projections.engine import ProjectionConfig, project_slate
from dfs_engine.simulation.adapters import get_adapter
from dfs_engine.simulation.core import SimConfig, relative_std_error, simulate_slate
from dfs_engine.simulation.field import FieldConfig, PayoutCurve, build_field, evaluate_lineups


def _best(projections, team, position, rank=0):
    pool = sorted((p for p in projections.values()
                   if p.player.team == team and p.player.positions[0] == position),
                  key=lambda p: -p.engine_projection)
    return pool[rank].player.player_id if len(pool) > rank else None


def test_simulation_is_reproducible(nfl_projections, nfl_slate):
    cfg = SimConfig(n_worlds=800, seed=123)
    a = simulate_slate(nfl_projections, get_adapter("nfl"), nfl_slate.snapshot, cfg)
    b = simulate_slate(nfl_projections, get_adapter("nfl"), nfl_slate.snapshot, cfg)
    assert np.array_equal(a.scores, b.scores)
    c = simulate_slate(nfl_projections, get_adapter("nfl"), nfl_slate.snapshot,
                       SimConfig(n_worlds=800, seed=124))
    assert not np.array_equal(a.scores, c.scores)


def test_simulated_marginals_match_the_projections(nfl_projections, nfl_sim):
    for pid, proj in list(nfl_projections.items())[:40]:
        if proj.engine_projection < 3:
            continue
        simulated = float(nfl_sim.column(pid).mean())
        assert simulated == pytest.approx(proj.engine_projection, rel=0.06), proj.player.name


def test_nfl_correlations_land_in_historically_plausible_ranges(nfl_projections, nfl_sim):
    team = nfl_projections[next(iter(nfl_projections))].player.team
    qb = _best(nfl_projections, team, "QB")
    opponent = nfl_projections[qb].player.opponent
    checks = [
        ("QB-WR1", _best(nfl_projections, team, "WR", 0), 0.20, 0.55),
        ("QB-TE1", _best(nfl_projections, team, "TE", 0), 0.15, 0.50),
        ("WR1-WR2 via QB", _best(nfl_projections, team, "WR", 1), 0.20, 0.55),
        ("QB-opposing WR1", _best(nfl_projections, opponent, "WR", 0), -0.05, 0.25),
        ("QB-opposing DST", _best(nfl_projections, opponent, "DST", 0), -0.60, -0.15),
    ]
    for label, other, lo, hi in checks:
        if other is None:
            continue
        rho = nfl_sim.empirical_correlation(qb, other)
        assert lo <= rho <= hi, f"{label} correlation {rho:.3f} outside [{lo}, {hi}]"


def test_same_team_receivers_compete_rather_than_move_together(nfl_projections, nfl_sim):
    team = nfl_projections[next(iter(nfl_projections))].player.team
    wr1, wr2 = _best(nfl_projections, team, "WR", 0), _best(nfl_projections, team, "WR", 1)
    qb = _best(nfl_projections, team, "QB")
    assert nfl_sim.empirical_correlation(wr1, wr2) < nfl_sim.empirical_correlation(qb, wr1)


def test_mlb_pitcher_is_negatively_correlated_with_the_lineup_he_faces(mlb_slate):
    projections = project_slate(mlb_slate.players, mlb_slate.snapshot,
                                ProjectionConfig(n_samples=1024))
    sim = simulate_slate(projections, get_adapter("mlb"), mlb_slate.snapshot,
                         SimConfig(n_worlds=4000, seed=5))
    pitcher = next(p for p in projections.values() if p.player.roster_role == "pitcher")
    opposing = [p for p in projections.values()
                if p.player.team == pitcher.player.opponent
                and p.player.roster_role == "hitter"]
    teammates = [p for p in projections.values()
                 if p.player.team == pitcher.player.team
                 and p.player.roster_role == "hitter"]
    vs_opp = np.mean([sim.empirical_correlation(pitcher.player.player_id,
                                                p.player.player_id) for p in opposing])
    hitter_pair = sim.empirical_correlation(opposing[0].player.player_id,
                                            opposing[1].player.player_id)
    assert vs_opp < -0.15
    assert hitter_pair > 0.2          # a team's offense happens together
    assert len(teammates) >= 5


def test_implied_and_empirical_correlations_agree(nfl_sim, nfl_projections):
    ids = [p for p in list(nfl_projections)[:14]]
    diffs = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if nfl_sim.column(a).std() < 1e-6 or nfl_sim.column(b).std() < 1e-6:
                continue
            diffs.append(abs(nfl_sim.implied_correlation(a, b)
                             - nfl_sim.empirical_correlation(a, b)))
    assert float(np.mean(diffs)) < 0.05


def test_field_entries_are_legal_and_ownership_weighted(nfl_projections, nfl_rules,
                                                        nfl_ownership, nfl_sim):
    field = build_field(nfl_projections, nfl_rules, nfl_ownership, nfl_sim,
                        FieldConfig(n_entries=400, seed=3))
    assert field.size == 400
    ids = nfl_sim.player_ids
    for row in field.entries[:60]:
        players = [nfl_projections[ids[i]].player for i in row]
        assert len({p.player_id for p in players}) == nfl_rules.size
        assert sum(p.salary for p in players) <= nfl_rules.salary_cap
        assert len({p.team for p in players}) >= nfl_rules.min_teams
    # high-ownership players really do appear more often
    counts = np.bincount(field.entries.reshape(-1), minlength=len(ids))
    top = max(range(len(ids)), key=lambda i: nfl_ownership.get(ids[i], 0))
    bottom = min(range(len(ids)), key=lambda i: nfl_ownership.get(ids[i], 0))
    assert counts[top] > counts[bottom]


def test_lineup_evaluation_orders_a_strong_lineup_above_a_weak_one(
        nfl_projections, nfl_rules, nfl_ownership, nfl_sim):
    field = build_field(nfl_projections, nfl_rules, nfl_ownership, nfl_sim,
                        FieldConfig(n_entries=600, seed=4))
    ids = nfl_sim.player_ids
    strong = [ids[i] for i in field.entries[0]]
    weak_pool = sorted(nfl_projections.values(), key=lambda p: p.engine_projection)
    # build a legal-but-terrible lineup from the same slots as a real field entry
    weak = list(strong)
    cheap = [p.player.player_id for p in weak_pool[:40]]
    contest = Contest(name="t", field_size=20000, payout_top_fraction=0.2)
    result = evaluate_lineups(nfl_sim, field, [strong, weak], contest,
                              ownership=nfl_ownership)
    assert len(result.metrics) == 2
    m = result.metrics[0]
    assert 0 <= m.top1_rate <= 1 and 0 <= m.cash_rate <= 1
    assert m.p99 > m.median > 0
    assert result.payouts.shape == (2, nfl_sim.n_worlds)
    assert len(cheap) == 40


def test_payout_curve_pays_the_top_and_zero_below_the_cash_line():
    curve = PayoutCurve(paid_fraction=0.2)
    ranks = np.array([1, 2, 100, 5000])
    pay = curve.payout_for_rank(ranks, field_size=10000)
    assert pay[0] > pay[1] > pay[2]
    assert pay[3] == 0.0


def test_tail_precision_is_reported_honestly():
    assert relative_std_error(0.001, 20000) > relative_std_error(0.001, 200000)
