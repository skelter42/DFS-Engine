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

When the user attaches a Sim Savant CSV and asks for market inputs / Savant prep, the job is **projection model v4**. Not lineups.

Read in this order:

1. `core/MARKET_INPUTS_RUN.md` — executable card
2. `core/PROJECTION_MODEL.md` — v4 lock
3. `src/dfs_engine/projections/` — the Python pull

Do not follow a Vegas-only card. Do not follow a summarized page fetch. Those are retired.

```
Python pull of industry sites + book props
Both present   -> Proj = mean(industry median, de-vigged book consensus in site points)
One present    -> Proj = that one
Neither        -> Proj = Savant, unchanged
```

The pull is Python. A full prop board is thousands of rows. Record the count. Under 100 prop rows is a failed pull.

`Own` stays unchanged unless an ownership pass is requested. Savant zeros stay 0. Savant is the last priority, not a third equal vote.

## Repository Map

- `core/PROJECTION_MODEL.md` — production model v4
- `core/MARKET_INPUTS_RUN.md` — executable card
- `core/VEGAS_CONSENSUS.md` — book-layer conversion
- `src/dfs_engine/projections/` — Python pull and blend
- `core/SAVANT_PREP.md` — Savant import contract
- `sports/mlb_market_inputs_projection_override.md` — MLB override, points at v4

This repository is the canonical DFS Engine brain. New chats should read the run card and `core/PROJECTION_MODEL.md` before a Market Inputs run.
