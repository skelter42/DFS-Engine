# DFS Engine

A persistent, versioned decision system for building and improving DFS lineups across sports.

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

## Market Inputs (Savant import)

When the user attaches a Sim Savant CSV and asks for market inputs / Savant prep, the job is **projection model v3**. Not lineups. Not a 50/50 blend.

Read in this order:

1. `core/MARKET_INPUTS_RUN.md` — executable card
2. `core/VEGAS_CONSENSUS.md` — how to build the number
3. `core/PROJECTION_MODEL.md` — v3 lock

Do not follow a 50/50 blend, an industry-median-plus-band, or a Savant weight. Those are retired.

```
Props exist  -> Proj = multi-book de-vigged consensus, in site points
No props     -> Proj = DFS-site median
Neither      -> Proj = Savant, unchanged
```

Books: DraftKings, FanDuel, BetMGM, plus any other book on the board. +150 is 40%. Strip the vig inside each book. Median the books. Convert that percentage into site points. That is the upload.

`Own` stays unchanged unless an ownership pass is requested. Savant zeros stay 0. Savant is the last priority.

## Repository Map

- `core/VEGAS_CONSENSUS.md` — operating framework. Read this.
- `core/PROJECTION_MODEL.md` — production model v3
- `core/MARKET_INPUTS_RUN.md` — executable card
- `core/VEGAS_BOARD_SWEEP.md` — board-first retrieval
- `core/SAVANT_PREP.md` — Savant import contract
- `sports/mlb_market_inputs_projection_override.md` — MLB override, points at v3

This repository is the canonical DFS Engine brain. New chats should read the run card and `core/VEGAS_CONSENSUS.md` before a Market Inputs run.
