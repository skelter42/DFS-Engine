import pytest

from dfs_engine.optimize.rules import DK_MLB_CLASSIC, DK_TENNIS_CLASSIC, get_rules, showdown
from dfs_engine.optimize.solver import (
    ObjectiveWeights,
    SolverConfig,
    build_objective,
    generate_candidates,
    solve_lineup,
)
from dfs_engine.projections.engine import ProjectionConfig, project_slate


def _objective(projections, ownership):
    return build_objective(list(projections.values()), ObjectiveWeights(), ownership,
                           SolverConfig(mode="chalk"))


def test_solved_lineup_is_legal(nfl_projections, nfl_rules, nfl_ownership):
    result = solve_lineup(list(nfl_projections.values()), nfl_rules,
                          _objective(nfl_projections, nfl_ownership), SolverConfig())
    lineup = result.lineup
    assert lineup is not None, result.status
    assert len(lineup.players) == nfl_rules.size
    assert lineup.salary <= nfl_rules.salary_cap
    assert len({p.player_id for p in lineup.players}) == nfl_rules.size
    assert len(set(lineup.teams)) >= nfl_rules.min_teams
    assert sorted(lineup.slots) == sorted(nfl_rules.slot_names)
    for player, slot in zip(lineup.players, lineup.slots):
        eligible = next(s for s in nfl_rules.slots if s.name == slot).eligible
        assert any(pos in eligible for pos in player.positions)


def test_uniqueness_constraint_is_enforced(nfl_projections, nfl_rules, nfl_ownership):
    objective = _objective(nfl_projections, nfl_ownership)
    first = solve_lineup(list(nfl_projections.values()), nfl_rules, objective,
                         SolverConfig()).lineup
    second = solve_lineup(list(nfl_projections.values()), nfl_rules, objective,
                          SolverConfig(min_uniques=4), previous=[first]).lineup
    assert second is not None
    assert first.overlap(second) <= nfl_rules.size - 4


def test_banned_and_locked_players_are_respected(nfl_projections, nfl_rules,
                                                 nfl_ownership):
    objective = _objective(nfl_projections, nfl_ownership)
    baseline = solve_lineup(list(nfl_projections.values()), nfl_rules, objective,
                            SolverConfig()).lineup
    banned = baseline.players[0].player_id
    locked = min(nfl_projections.values(), key=lambda p: p.engine_projection)
    result = solve_lineup(list(nfl_projections.values()), nfl_rules, objective,
                          SolverConfig(banned=(banned,),
                                       locked=(locked.player.player_id,))).lineup
    assert banned not in {p.player_id for p in result.players}
    assert locked.player.player_id in {p.player_id for p in result.players}


def test_mlb_team_cap_is_enforced(mlb_slate):
    projections = project_slate(mlb_slate.players, mlb_slate.snapshot,
                                ProjectionConfig(n_samples=512))
    ownership = {pid: 10.0 for pid in projections}
    objective = build_objective(list(projections.values()), ObjectiveWeights(), ownership,
                                SolverConfig(mode="chalk"))
    lineup = solve_lineup(list(projections.values()), DK_MLB_CLASSIC, objective,
                          SolverConfig()).lineup
    assert lineup is not None
    hitters: dict[str, int] = {}
    for player in lineup.players:
        if "P" not in player.positions:
            hitters[player.team] = hitters.get(player.team, 0) + 1
    assert max(hitters.values()) <= DK_MLB_CLASSIC.max_per_team


def test_tennis_rules_forbid_rostering_both_sides_of_a_match():
    assert DK_TENNIS_CLASSIC.forbid_same_game_opponents
    assert DK_TENNIS_CLASSIC.size == 6


def test_showdown_captain_costs_and_scores_more():
    rules = showdown("dk", "nfl")
    captain = rules.slots[0]
    assert captain.name == "CPT" and captain.multiplier == 1.5
    assert rules.size == 6


def test_world_mode_produces_a_more_varied_candidate_pool(
        nfl_projections, nfl_rules, nfl_ownership, nfl_sim):
    common = dict(projections=nfl_projections, rules=nfl_rules, ownership=nfl_ownership,
                  weights=ObjectiveWeights(), n=12)
    world = generate_candidates(config=SolverConfig(mode="world", seed=1), sim=nfl_sim,
                                **common)
    noise = generate_candidates(config=SolverConfig(mode="noise", randomness=0.08, seed=1),
                                **common)
    world_players = {p.player_id for lu in world.lineups for p in lu.players}
    noise_players = {p.player_id for lu in noise.lineups for p in lu.players}
    assert len(world.lineups) == 12
    assert len(world_players) > len(noise_players)


def test_candidates_are_unique(nfl_projections, nfl_rules, nfl_ownership, nfl_sim):
    pool = generate_candidates(nfl_projections, nfl_rules, nfl_ownership,
                               ObjectiveWeights(), SolverConfig(mode="world", seed=2),
                               n=15, sim=nfl_sim)
    signatures = [lu.signature() for lu in pool.lineups]
    assert len(set(signatures)) == len(signatures)


def test_unknown_site_rules_raise_rather_than_guess():
    with pytest.raises(KeyError):
        get_rules("dk", "cricket")


def test_lineup_legality_checker_catches_violations(nfl_projections, nfl_rules,
                                                    nfl_ownership):
    from dfs_engine.models import Lineup
    from dfs_engine.optimize.rules import lineup_is_legal

    lineup = solve_lineup(list(nfl_projections.values()), nfl_rules,
                          _objective(nfl_projections, nfl_ownership),
                          SolverConfig()).lineup
    assert lineup_is_legal(lineup, nfl_rules) == (True, "")

    short = Lineup(players=lineup.players[:-1], slots=lineup.slots[:-1],
                   salary=lineup.salary)
    assert lineup_is_legal(short, nfl_rules)[0] is False

    doubled = Lineup(players=lineup.players[:-1] + (lineup.players[0],),
                     slots=lineup.slots, salary=lineup.salary)
    assert "twice" in lineup_is_legal(doubled, nfl_rules)[1]

    expensive = Lineup(players=lineup.players, slots=lineup.slots, salary=99_999)
    assert "cap" in lineup_is_legal(expensive, nfl_rules)[1]


def test_showdown_build_applies_the_captain_multiplier(nfl_slate):
    from dfs_engine.models import Contest
    from dfs_engine.pipeline import BuildRequest, run_build

    game = nfl_slate.snapshot.games[0]
    players = [p for p in nfl_slate.players if p.team in game.teams]
    request = BuildRequest(sport="nfl", players=players, snapshot=nfl_slate.snapshot,
                           variant="showdown", n_lineups=3, n_candidates=8,
                           n_worlds=800, field_entries=150, synthetic=True,
                           contests=[Contest(name="SD", entries=3, field_size=5000)])
    result = run_build(request)
    assert len(result.portfolio.lineups) == 3
    for lu in result.portfolio.lineups:
        assert lu.slots[0] == "CPT"
        assert len(lu.players) == 6
        captain_cost = lu.players[0].salary * 1.5
        assert lu.salary >= captain_cost
        assert lu.salary <= result.rules.salary_cap
