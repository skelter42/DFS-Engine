# DFS Engine

A persistent, versioned decision system for building and improving DFS decisions across sports.

## Mission

The DFS Engine separates projection quality from portfolio-construction quality. Its broader research framework covers ownership, contest context, slate structure, game scripts, leverage, correlation, simulation, and post-slate learning. Market Inputs is a distinct, projection-only workflow; it does not build lineups.

The goal is repeatable decision quality: preserve source data, use current market evidence, cover plausible slate outcomes, and learn without overfitting to one slate.

## Operating Principles

1. For Market Inputs, posted sportsbook scoring markets drive the projection when the required prices are available; Savant is the fallback, not a co-equal vote.
2. Separate player projection quality from portfolio construction quality.
3. Evaluate portfolio decisions in the context of contest type, payout structure, and slate uncertainty.
4. Use correlation and game-script logic where the sport supports it.
5. Diversify across plausible outcomes without randomizing blindly or imposing unsupported constraints.
6. Use native outcome simulation as an evidence layer, not an automatic decision-maker.
7. Compare source projected ownership with final portfolio exposure when an ownership/exposure audit is requested.
8. Record durable lessons after slates; do not memorialize noise.
9. Prefer explicit rules, schemas, and versioned logic over chat-only memory.
10. Prefer fewer strong rules over many narrow rules; remove redundancy and avoid overfitting.

## Market Inputs (Savant import)

When a Sim Savant CSV is attached and the user asks for Market Inputs / Savant prep, the job is **projection model v6**. It is not a lineup-building task.

Read `CURRENT.md` first. Then read **only** these three operational files, in this order:

1. `core/MARKET_INPUTS_RUN.md` — executable run card
2. `core/PROJECTION_MODEL.md` — v6 projection contract
3. `core/VEGAS_CONSENSUS.md` — price-to-site-points conversion

`CURRENT.md` is authoritative if any other repository file disagrees.

```
Python scrape of a real sportsbook board
Qualifying scoring markets posted  -> Proj = de-vigged book number, in site points
Required scoring markets missing   -> Proj = original Savant, unchanged
Savant 0                            -> 0
```

Books drive; Savant is the fallback. A missing price is not filled with a rate, season average, or industry projection. Industry is a reasonableness check only. Do not use the Odds API or summarized page fetches as price sources.

Preserve Name, DFS ID, row order, Own, and all other original columns. Change only Proj where the posted-market requirements qualify. Produce the import CSV and the row-by-row price reconciliation, then stop. Do not build lineups unless explicitly asked.

Do not add other files to the Market Inputs read sequence unless `CURRENT.md` is deliberately revised.

## Repository Map

- `CURRENT.md` — authoritative pointer and conflict-resolution rule for the active process
- `core/MARKET_INPUTS_RUN.md` — Market Inputs run card
- `core/PROJECTION_MODEL.md` — projection model v6
- `core/VEGAS_CONSENSUS.md` — sportsbook price conversion
- `src/dfs_engine/projections/` — supporting Python projection helpers; not a replacement for the documented operational workflow
- `config/` — routing and engine configuration, which must remain consistent with the current process

Other sport, portfolio, learning, and reference documents may support separate tasks, but they are not part of the Market Inputs read sequence unless `CURRENT.md` is updated to include them.
