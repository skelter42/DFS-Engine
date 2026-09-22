"""DFS Engine: market-derived projections, correlated simulation, portfolio construction.

Pipeline:

    sportsbook sweep -> de-vig + multi-book consensus -> stat distributions
    -> site scoring -> coverage-graded engine projections -> expected ownership
    -> correlated slate simulation -> field model -> candidate lineups
    -> marginal-value portfolio selection -> contest allocation -> audit

The markdown files in ``core/`` and ``sports/`` are the specification this
package implements; where a rule is quoted in a docstring, that file is the
authority.
"""

__version__ = "0.2.0"

from .models import Contest, Lineup, MarketSnapshot, Player, PlayerProjection, Portfolio

__all__ = ["Contest", "Lineup", "MarketSnapshot", "Player", "PlayerProjection",
           "Portfolio", "__version__"]
