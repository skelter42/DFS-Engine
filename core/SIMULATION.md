# Cross-Sport Simulation Layer

## Purpose

The DFS Engine should use Monte Carlo simulation as a native cross-sport decision layer. The purpose is not to replace projections, ownership, game theory, or portfolio judgment. The purpose is to model the distribution of plausible slate outcomes so the Engine can estimate ceiling paths, failure paths, first-place equity, leverage, and portfolio overlap more realistically than median projections alone.

## Core Principle

Do not simulate every player independently with `projection + random normal noise`.

DFS outcomes are non-normal, role-dependent, game-dependent, and correlated. Each sport must define its own scoring distribution, volatility assumptions, and correlation structure.

The shared simulation layer should provide a common framework while sport modules provide the actual variance and dependency rules.

## Required Inputs

When available, simulations should use:

- baseline fantasy projection
- salary and roster position
- projected ownership
- empirical or estimated standard deviation / volatility
- ceiling and floor information
- role / usage / opportunity
- team and opponent
- game environment
- betting market information
- injury / lineup / depth-chart uncertainty
- sport-specific correlation factors

If empirical standard deviation is unavailable, the Engine may use an archetype-based estimate, but it must label the estimate as modeled rather than observed.

## Distribution Rules

Use empirical historical scoring distributions whenever enough data exists.

Do not assume normality by default. DFS scoring commonly has skew, zero-inflation, fat tails, role-based ceilings, and asymmetric downside.

Preferred order:

1. empirical player or role/archetype distribution
2. fitted sport-specific distribution
3. calibrated mean/SD approximation
4. generic normal approximation only as a temporary fallback

Simulation calibration should be backtested against actual fantasy-score distributions and top-percentile outcomes.

## Correlation Rules

Each simulation must preserve meaningful dependencies rather than sampling players independently.

Examples include:

- teammates benefiting from the same high-scoring game environment
- opposing players benefiting from shootout or pace scenarios
- pitchers negatively correlated with opposing hitters
- quarterbacks positively correlated with pass catchers
- running backs correlated with favorite / positive game scripts
- NBA teammates affected by usage and minutes redistribution
- NHL skaters correlated by line and power-play unit
- tennis opponents being strongly negatively correlated

Correlation assumptions must be sport-specific and should be calibrated from historical data where practical.

## Slate-Level Simulation

The preferred unit is the full slate, not isolated player simulations.

A single simulated world should represent one internally coherent version of what happens across all games. Every player's fantasy score in that iteration should reflect the same underlying game environments and role outcomes.

Default target for serious GPP analysis: 50,000 to 200,000 slate iterations when computationally practical.

Lower iteration counts may be used for rapid pre-build exploration, but final model comparisons should use enough trials for stable tail estimates.

## Lineup Evaluation Metrics

For every candidate lineup, calculate as available:

- mean simulated score
- median simulated score
- 90th / 95th / 99th percentile score
- boom probability
- top 20% rate
- top 10% rate
- top 1% rate
- top 0.1% rate
- first-place / tournament-win proxy
- probability of beating a target score
- expected ownership
- expected duplication or duplication proxy
- leverage-adjusted tournament value

The Engine should not optimize on one metric alone.

For large-field GPPs, top-tail and first-place-equity metrics should receive materially more weight than cash rate or median score.

## Field Simulation

When projected ownership and contest size are available, the Engine should simulate or approximate the opposing field.

Field simulation should account for:

- ownership
- roster constraints
- common stack / correlation structures
- salary usage
- popular value combinations
- likely optimizer behavior
- duplication

The goal is to estimate relative finish probability, not merely absolute lineup fantasy score.

If a full field model is unavailable, use ownership and duplication proxies while clearly labeling them as approximations.

## Portfolio Simulation

Evaluate the lineup set as a portfolio, not just one lineup at a time.

Measure:

- aggregate first-place equity
- frequency at least one lineup reaches top 1%, top 0.1%, or first-place proxy
- overlap between lineups' winning scenarios
- player concentration
- team/game concentration
- script concentration
- duplicated outcome exposure

A portfolio of different-looking lineups can still be overexposed to the same underlying simulated world. Penalize excessive hidden correlation unless it reflects an intentional high-conviction thesis.

## Sport-Specific Variance Examples

### MLB
- hitter distributions are highly right-skewed and zero-heavy
- power hitters generally carry larger ceiling variance
- team offense must be correlated
- pitcher and opposing hitters must be negatively correlated
- pitcher strikeout ceiling and blow-up risk require asymmetric distributions

### NFL / NCAAF
- QB-pass catcher positive correlation
- opposing passing-game bring-back correlation
- RB / defense / positive-game-script relationships
- touchdown variance
- role and snap uncertainty

### NBA
- minutes and usage drive most variance
- injury news creates correlated usage redistribution
- overtime and game environment affect multiple players together
- teammate correlations can be positive or negative depending on role

### NHL
- line and power-play correlation
- goalie vs opposing skaters negative correlation
- goal scoring is highly discrete and volatile

### Tennis
- opponent outcomes are strongly negatively correlated
- win probability, set length, aces, breaks, and straight-set outcomes create different ceiling distributions

## Learning and Calibration

Post-slate, store simulation calibration findings separately from slate-specific results.

Track whether predicted percentile probabilities match realized frequencies over many slates. Examples:

- players estimated to reach their 90th percentile 10% of the time should do so approximately 10% over a sufficiently large sample
- lineups assigned higher top-1% probability should outperform lower-rated lineups in aggregate
- simulated correlation structures should resemble observed scoring relationships

Do not change standard deviation, correlation, or distribution rules because of one slate. Promote changes only when backtesting or repeated evidence supports them.

## Decision Hierarchy

Simulation is evidence, not authority.

The Engine should combine simulation results with:

- projection quality
- ownership
- game theory
- correlation
- news and role certainty
- market context
- duplication
- contest structure
- portfolio diversification

A lineup may be rejected despite a strong simulation score if the model is relying on fragile assumptions, stale news, excessive duplication, or a poorly represented game script.

The objective is not to find the lineup with the highest simulated median. The objective is to build the portfolio with the strongest long-run tournament-winning equity.