# DFS Engine

A persistent, versioned decision system for building and improving DFS lineups across sports — and the executable engine that implements it.

The markdown files in `core/` and `sports/` are the specification. The Python package in `src/dfs_engine/` is the implementation: it sweeps sportsbooks for player props, converts de-vigged odds into fantasy-point distributions, simulates correlated slate outcomes against a modelled field, and builds a diversified portfolio with a full audit trail.

## Mission

The DFS Engine is not a single projection model. It is a portfolio-construction framework that combines projections, ownership, contest context, slate structure, game-script analysis, leverage, correlation, simulation, and post-slate learning.

The goal is repeatable decision quality: ingest slate inputs, cross-check them against broader market information, build diversified but intentional portfolios, compare final exposures to source projections, and learn from results without overfitting.

## Operating Principles

1. Never treat one projection source as authoritative.
2. Separate player projection quality from portfolio construction quality.
3. Optimize for contest-specific expected value, not median lineup projection alone.
4. Use correlation and game-script logic where the sport supports it.
5. Respect uncertainty. Diversification should cover plausible slate outcomes, not randomize blindly.
6. Use native outcome simulation as an evidence layer, not an automatic decision-maker.
7. Always compare source projected ownership with DFS Engine final exposure.
8. Record durable lessons after slates; do not memorialize noise.
9. Prefer explicit rules, schemas, and versioned logic over chat-only memory.
10. Prefer fewer strong rules over many narrow rules; remove redundancy and avoid overfitting.

---

## Quickstart

```bash
pip install -e ".[dev]"

# Full pipeline on a synthetic slate: no network, no API key, ~25 seconds.
dfs-engine demo --sport nfl --out slates/demo
open slates/demo/report.html
```

The demo writes the complete delivery package:

| File | Contents |
|---|---|
| `lineups.csv` | Site-ready upload file, columns in roster-slot order |
| `lineups_detail.csv` | Per-lineup contest, salary, simulation metrics, script label |
| `exposures.csv` | Exposure vs expected ownership with percentage-point differences |
| `projections.csv` | Vendor prior, market projection, coverage grade, engine projection |
| `build.json` | Everything above, machine-readable |
| `audit.md` | The written build report (`schemas/LINEUP_OUTPUT.md` contract) |
| `report.html` | Self-contained dashboard |

> The demo slate is **synthetic**. It generates plausible latent player rates and
> posts book quotes around them, so the odds math is genuinely exercised — but
> the numbers are invented and every output is stamped as such.

## Running a real slate

```bash
# 1. Sweep the market. ODDS_API_KEY covers DraftKings, FanDuel, BetMGM, Caesars,
#    bet365, ESPN BET, Fanatics and others through one API; the DraftKings
#    source is key-less. Anything else you can export goes in as a CSV.
export ODDS_API_KEY=...
dfs-engine fetch-props --sport nfl --out slates/2026-09-22/markets.json \
    --csv exports/action_network.csv

dfs-engine inspect --markets slates/2026-09-22/markets.json -v

# 2. Build. --players is the site salary export; --vendor is the Savant/vendor
#    baseline (optional, used as the fallback prior and kept for the audit).
dfs-engine build --sport nfl --site dk \
    --players exports/DKSalaries.csv \
    --vendor exports/savant.csv \
    --markets slates/2026-09-22/markets.json \
    --contests examples/contests.json \
    --lineups 20 --worlds 50000 --candidates 300 \
    --out slates/2026-09-22/nfl
```

`dfs-engine project` runs the projection stage alone if you only want
market-derived numbers to take elsewhere. `dfs-engine scoring --sport nfl`
prints the site scoring rules in use — check them against the site before a real
build.

Sports: `nfl`, `ncaaf`, `nba`, `mlb`, `nhl`, `tennis`. Sites: `dk`, `fd`.

## How it works

### 1. Market sweep — `markets/`

Multiple sources feed one snapshot: `TheOddsApiSource` (many books in one call),
`DraftKingsSource` (key-less, deep alternate ladders), and `CsvPropSource`
(any aggregator you can export). Sources fail independently — a book that errors
is recorded in `snapshot.errors` and lowers the reported coverage; it never
becomes a guess. The same book arriving by two paths is de-duplicated.

Book labels (`player_pass_yds`, `"Passing Yards"`, `"Pts + Reb + Ast"`) all
normalise to one canonical stat vocabulary.

### 2. Odds → distributions — `odds/`

A prop is a probability statement about a distribution, not a point estimate.
`Over 5.5 K @ -120` says `P(K ≥ 6) = 0.55` once the juice is removed.

- **De-vig**: multiplicative, additive, power, or Shin.
- **Consensus**: median across books per line, with cross-book dispersion kept as
  a confidence input. One outlier book cannot move the number.
- **Inversion**: counts fit Poisson/negative-binomial, yardage fits lognormal.
  With three or more ladder lines the *shape* is identifiable, so mean and
  dispersion are fitted jointly by weighted least squares in probability space.

### 3. Projections — `projections/`

Components are sampled **jointly** through a Gaussian copula — a receiver's
yards, catches and touchdowns move together — then scored with the site's rules
*including threshold bonuses*. A DK 100-yard bonus is a tail probability; you
cannot recover its expectation from `E[yards]`. The output per player is an
empirical fantasy-point distribution, which is also the marginal the simulator
draws from. Ceiling and floor are measured, not assumed.

Overlapping markets are reconciled rather than added: hits, total bases and home
runs describe one hit-type distribution and are solved together.

Each player gets a coverage grade (A Vegas-rich → D fallback-heavy) from market
breadth, book depth, two-sided pricing and cross-book agreement. The engine
projection is the market projection shrunk toward the vendor prior by exactly as
much as the coverage deserves — no fixed blend. With no usable market, the prior
carries and the player is labelled fallback-driven.

### 4. Ownership — `projections/ownership.py`

Supplied industry numbers are the preferred anchor. Where they are missing, a
behavioural field model fills slots by softmax over what the field can see, so
slate ownership automatically sums to `100% × roster size` — the constraint real
ownership obeys. Ownership is never adjusted to manufacture leverage; exposure
is the decision variable.

### 5. Simulation — `simulation/`

One shared runtime; sports supply dependence structure only. A world is one
coherent version of the whole slate. Marginals come from the market-implied
distributions above — skewed, zero-heavy, bonus-aware — not `projection + normal
noise`.

Dependence is a linear factor model over latent game/team/role factors, so any
pair's correlation is the dot product of their loadings: inspectable and
testable. `tests/test_simulation.py` asserts the realised correlations land in
historically plausible ranges (QB–WR1 0.20–0.55, QB–opposing DST −0.60 to −0.15,
MLB pitcher vs the lineup he faces below −0.15). Same-team receivers *compete*
through per-receiver share factors, because a single shared "competition" factor
would wrongly make the losers correlate with each other.

A field of opposing entries is sampled from the ownership model, with the
stacking behaviour real entrants show, and candidate lineups are ranked inside
every world. Tail resolution is bounded by the sampled field size, so
`first_place_proxy` is labelled a proxy rather than dressed up as a win rate.

### 6. Lineups and portfolio — `optimize/`, `portfolio/`

Candidate generation samples a simulated world and solves the lineup that wins
**that** world, so the pool is a set of coherent slate stories rather than N
perturbations of the same median lineup. Hard constraints are limited to roster
legality, contest rules, confirmed inactives and the source-zero eligibility
gate.

Selection is greedy on *marginal* portfolio value — new tail worlds covered,
payout added where the portfolio is weak, minus correlation with what is already
in. Every pick is traced. The report includes the diagnostic that matters most:
**effective independent lineups**, which collapses toward 1 when twenty
different-looking rosters are all betting on the same world.

Multi-contest allocation deals each contest from within every script family in
priority order, so no contest becomes a leftover bin.

### 7. Delivery — `report/`

Exposure vs expected ownership with percentage-point differences and a reason
per row, stack summary, hidden concentration in the worlds where the portfolio
wins, per-contest allocation audit, risk flags, and a final QA gate (cap, roster
size, duplicates, source-zero players, inactives, team minimums).

## Repository map

### Brain (specification)

- `core/ENGINE.md` — master slate workflow and portfolio rules
- `core/MARKET_INPUTS.md` — the sportsbook/industry sweep standard
- `core/MARKET_PROJECTIONS.md` — Vegas-first projection hierarchy
- `core/SIMULATION.md` — outcome-distribution and Monte Carlo policy
- `core/SIMULATION_IMPLEMENTATION.md` — simulation architecture contract
- `core/AGENTS.md`, `core/PROCESS_GOVERNANCE.md`, `core/LEARNING.md`
- `sports/*.md` — sport-specific construction logic
- `schemas/LINEUP_OUTPUT.md` — delivery contract
- `learning/REGISTRY.md`, `history/CONTEST_HISTORY.md`

### Engine (implementation)

```
src/dfs_engine/
  cli.py            command line entry point
  pipeline.py       the canonical slate workflow, wired end to end
  models.py         Player, PropMarket, MarketSnapshot, PlayerProjection, Lineup, Portfolio
  ingest.py         site salary exports and vendor baselines
  odds/             American odds, de-vig, consensus, distribution inversion
  markets/          sportsbook sources, catalog, aggregation, coverage reporting
  projections/      component inference, site scoring, engine projections, ownership
  simulation/       shared runtime, sport adapters, field model, portfolio metrics
  optimize/         site roster rules, MILP solver, candidate generation
  portfolio/        selection, multi-contest allocation, exposure diagnostics
  report/           upload files, audit markdown, HTML dashboard
  data/synthetic.py labelled synthetic slates for demos and tests
```

## Standard Output Contract

Every lineup build should include:

- slate thesis and major game environments
- key leverage points and fragility risks
- final lineup portfolio
- stack/correlation summary where applicable
- source projected ownership vs DFS Engine exposure, side by side, with percentage-point difference
- concise explanation of the largest exposure deviations
- pre-lock/final status and unresolved uncertainty

## Limits worth knowing

- **Scoring rules and roster rules are encoded, not fetched.** Sites change them.
  `dfs-engine scoring` prints what the engine is using; verify before a real build.
- **Sportsbook endpoints drift.** Parsers are defensive and report what they
  cannot read, but the DraftKings source in particular tracks a public endpoint
  that DraftKings reshapes periodically.
- **The field model is a model.** Duplication and first-place rates are proxies
  scaled from a sampled field, and they are labelled as proxies throughout.
- **Correlation loadings are hand-specified priors**, tuned to plausible ranges
  rather than fitted to historical scoring data. `core/SIMULATION.md` asks for
  calibration against realised outcomes over repeated slates; that backtest is
  the highest-value next piece of work.
- **This is the mathematical layer.** `core/ENGINE.md` requires an explicit
  strategic review of the portfolio before entry — confirm the exposures express
  intended slate theses rather than optimizer repetition.

## Development

```bash
pip install -e ".[dev]"
pytest -q                    # 86 tests, ~50s
```

Tests cover odds math against known identities, distribution fits against
synthetic truth, projection recovery (fantasy-point error under 10% MAE with no
systematic bias), simulation determinism and correlation targets, roster
legality across sports, portfolio selection beating naive top-N, and the full
build being byte-reproducible for a given seed.

This repository is the canonical DFS Engine brain. New chats should read the relevant files before making slate-specific decisions, and durable improvements should be written back here. The process manager should decide whether new ideas belong in core logic, a sport module, the learning registry, or nowhere, and should actively prevent duplicate or overfit logic from accumulating.
