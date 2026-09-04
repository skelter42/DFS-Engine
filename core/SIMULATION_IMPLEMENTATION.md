# Native Simulation Implementation Contract

## Purpose

This file defines how the DFS Engine should implement native simulation in code without duplicating simulation logic across sports. The conceptual and statistical policy remains authoritative in `core/SIMULATION.md`.

This file is implementation architecture only. Sport files define distributions/correlations as adapters; they do not own separate simulation engines.

## Single Shared Simulator

The repository should converge on one shared simulation runtime with four layers:

1. Slate state builder
2. Sport adapter
3. Field/lineup evaluator
4. Portfolio evaluator

Do not create independent MLB, NFL, NBA, NHL, NCAAF, or tennis simulation programs that each reinvent ingestion, iteration control, lineup scoring, field modeling, and portfolio analysis.

## Required Runtime Inputs

The shared simulator should accept a normalized slate dataset containing, where available:

- player ID / name / team / opponent / position / salary
- DFS Engine projection
- fallback/source projection
- expected ownership
- sharp-field ownership or construction tendencies when available
- market coverage/confidence
- empirical or calibrated distribution parameters
- role/usage inputs
- team/game environment
- sport-specific correlation metadata
- roster/site rules
- candidate lineups
- contest size/profile when field simulation is requested

Missing calibrated variance/correlation inputs must be labeled. Do not fabricate them merely to make the simulator run.

## Sport Adapter Contract

Each sport adapter supplies only sport-specific mechanics:

- player/role distribution family or empirical sampling rule
- volatility parameters or calibrated archetypes
- team/game latent factors
- teammate/opponent dependency rules
- role uncertainty handling
- fantasy scoring transformations if simulating underlying stats

Examples:
- MLB: correlated team run environments, hitter event skew/zero inflation, pitcher strikeout/run-prevention/blow-up behavior, pitcher-vs-opposing-hitter negative dependency
- NFL/NCAAF: game scoring/pass/run environments, QB-pass catcher dependency, touchdown/role uncertainty
- NBA: minutes/usage/injury redistribution, pace/game environment
- NHL: goal/shot/line/power-play correlation, goalie-opponent dependency
- Tennis: match winner/set length/ace-break dynamics and opponent negative correlation

## Simulation Modes

Every build must report one of these modes:

### Native Monte Carlo
The shared runtime executed calibrated correlated slate worlds.

### External Simulation
Trusted simulation outputs were supplied by a vendor/source and ingested. The Engine may reweight or interpret them but must identify the external source.

### Scenario Fallback
No defensible calibrated simulation was available. GPT/game-script reasoning may still construct plausible scenarios, but the build must not call this Monte Carlo simulation or invent percentile/top-1% probabilities.

## Iteration Guidance

Follow `core/SIMULATION.md` for iteration targets. Serious final GPP analysis should prefer enough iterations for stable tail estimates. Iteration count should be stored in the output metadata.

## Field Model Integration

Field simulation should consume the Ownership & Field Agent outputs, including conditional ownership and construction archetypes. It should not independently recreate a second ownership model.

If full field generation is unavailable, use a clearly labeled duplication/ownership proxy.

## Candidate and Portfolio Evaluation

The simulator should score candidate lineups across the same slate worlds and compute, as available:

- mean/median score
- upper percentiles
- top-20%, top-10%, top-1%, top-0.1% proxies
- first-place proxy when field modeling supports it
- duplication-adjusted or leverage-adjusted tournament metrics

Portfolio evaluation should additionally measure:

- probability at least one lineup reaches target tail thresholds
- aggregate first-place proxy
- overlap in winning worlds
- hidden concentration by latent game/script outcome
- marginal value of each lineup to the portfolio

## GPT Boundary

GPT receives simulation outputs and may:

- challenge fragile assumptions
- interpret leverage and game-script meaning
- reject duplicated or overly concentrated portfolios
- preserve multiple credible paths to first

GPT must not:

- invent SDs/correlations
- claim unrun Monte Carlo trials
- fabricate percentile/top-tail probabilities
- replace missing executable simulation with narrative and label it as simulation

## Code Placement

When executable code is added, prefer a structure such as:

- `src/dfs_engine/simulation/core.py` — iteration engine and shared state
- `src/dfs_engine/simulation/field.py` — field generation/evaluation
- `src/dfs_engine/simulation/portfolio.py` — lineup/portfolio metrics
- `src/dfs_engine/simulation/adapters/mlb.py`
- `src/dfs_engine/simulation/adapters/nfl.py`
- etc.

Exact filenames may evolve, but ownership must remain centralized.

## Validation

Before native simulation is considered production-ready:

- deterministic seed/reproducibility tests
- roster/score consistency tests
- distribution calibration tests
- correlation sanity tests
- tail-stability tests across iteration counts
- post-slate calibration against realized outcomes over repeated slates

## Non-Duplication Rule

If a simulation rule is cross-sport, it belongs in `core/SIMULATION.md` or this implementation contract. If it is sport-specific, it belongs in the sport adapter/module. Do not duplicate the same rule in `ENGINE.md`, `AGENTS.md`, and sport files except for a brief pointer needed to define stage ownership.
