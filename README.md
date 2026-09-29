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

When the user attaches a Sim Savant CSV and asks for market inputs / Savant prep, the job is **projection model v6**. Not lineups.

Read in this order:

1. `core/MARKET_INPUTS_RUN.md` — executable card
2. `core/PROJECTION_MODEL.md` — v6 lock
3. `core/VEGAS_CONSENSUS.md` — price to site points
4. `src/dfs_engine/projections/` — the Python scrape

```
Python scrape of a real sportsbook board
Scoring markets posted  -> Proj = de-vigged book number, in site points
Scoring markets missing -> Proj = Savant, unchanged
Savant 0                -> 0
```

Books drive, every sport. Savant is the fallback, not a vote. A missing price is not filled. Industry is a check. No Odds API. A page summary is not a source.

`Own` stays unchanged unless an ownership pass is requested. Savant zeros stay 0.

## Repository Map

- `core/PROJECTION_MODEL.md` — production model v6
- `core/MARKET_INPUTS_RUN.md` — executable card
- `core/VEGAS_CONSENSUS.md` — book conversion
- `src/dfs_engine/projections/` — Python scrape and blend
- `core/SAVANT_PREP.md` — Savant import contract
- `sports/mlb_market_inputs_projection_override.md` — MLB scoring, same v6 rule

This repository is the canonical DFS Engine brain. New chats should read the run card and `core/PROJECTION_MODEL.md` before a Market Inputs run.
