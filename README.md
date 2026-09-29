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

When the user attaches a Sim Savant CSV and asks for market inputs / Savant prep, the job is **projection model v2**, not lineups.

Model: `core/PROJECTION_MODEL.md`  
Executable card: `core/MARKET_INPUTS_RUN.md`  
Score: `core/PROJECTION_SCORE.md`  
Vegas retrieval: `core/VEGAS_BOARD_SWEEP.md`  
Savant contract: `core/SAVANT_PREP.md`

Industry means other DFS projection sites. Their median is one half. The de-vigged Vegas prop is the other half.  
`Proj = 0.50 × DFS-site median + 0.50 × Vegas prop` when both exist.  
`Own` stays unchanged unless an ownership pass is requested.  
Savant zeros stay 0. Savant is not in the blend. Showdown CPT = 1.5 × FLEX. Persist boards and the projection log in `history/`, not the import CSV.

## Repository Map

- `core/PROJECTION_MODEL.md` — production Market Inputs model v2
- `core/MARKET_INPUTS_RUN.md` — executable card
- `core/PROJECTION_SCORE.md` — absolute-error score and required log
- `core/VEGAS_BOARD_SWEEP.md` — board-first Vegas retrieval
- `core/SAVANT_PREP.md` — Savant import contract
- `sports/mlb_market_inputs_projection_override.md` — MLB Proj override, points at model v2
- `sports/nfl.md` — NFL board-to-DK conversion

This repository is the canonical DFS Engine brain. New chats should read the model file before a Market Inputs run.
