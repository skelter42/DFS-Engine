import pytest

from dfs_engine.data.synthetic import build_demo_slate
from dfs_engine.optimize.rules import get_rules
from dfs_engine.projections.engine import ProjectionConfig, project_slate
from dfs_engine.projections.ownership import blend_ownership
from dfs_engine.simulation.adapters import get_adapter
from dfs_engine.simulation.core import SimConfig, simulate_slate


@pytest.fixture(scope="session")
def nfl_slate():
    return build_demo_slate("nfl", seed=7)


@pytest.fixture(scope="session")
def mlb_slate():
    return build_demo_slate("mlb", seed=11)


@pytest.fixture(scope="session")
def nfl_projections(nfl_slate):
    return project_slate(nfl_slate.players, nfl_slate.snapshot,
                         ProjectionConfig(site="dk", n_samples=2048))


@pytest.fixture(scope="session")
def nfl_rules():
    return get_rules("dk", "nfl")


@pytest.fixture(scope="session")
def nfl_ownership(nfl_projections, nfl_rules, nfl_slate):
    return blend_ownership(nfl_projections, nfl_rules, nfl_slate.snapshot).ownership


@pytest.fixture(scope="session")
def nfl_sim(nfl_projections, nfl_slate):
    return simulate_slate(nfl_projections, get_adapter("nfl"), nfl_slate.snapshot,
                          SimConfig(n_worlds=6000, seed=99))
