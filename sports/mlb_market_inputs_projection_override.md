# MLB Market Inputs — Projection-Only Override

## Status

This file is an authoritative override to `sports/mlb_market_inputs.md` for future MLB market-input / Savant Prep passes.

## User workflow decision

Sim Savant allows ownership to be changed separately, so the DFS Engine market-input pass should now focus its research and refinement effort on **projections only**.

## Required behavior

1. `@GitHub market inputs mlb` / `Savant Prep` must exhaust sportsbook and market information for `Proj` before delivery.
2. Prioritize direct player props and prices, then game/team markets and context, then independent projection systems, with original Sim Savant projection as final fallback.
3. Preserve the original Sim Savant `Own` values unchanged in the returned import CSV unless the user explicitly requests an ownership pass or ownership audit.
4. Do not spend the normal market-input research budget trying to estimate or replace ownership by default.
5. The final CSV should retain the standard import schema `Name, DFS ID, Proj, Own` for compatibility; `Own` is pass-through data by default.
6. Continue tracking projection provenance: `VEGAS_DIRECT`, `VEGAS_SUPPORTED`, `INDUSTRY_BLEND`, `SAVANT_FALLBACK`.
7. Continue reporting projection-source coverage and material Savant-vs-market projection differences.

## AI grade gate

The mandatory A-or-better gate now applies to **projection quality** for the standard MLB market-input pass.

Required report:

- `Projection grade: <grade>`
- `Overall projection-input grade: <grade>`
- main reasons for the grade
- remaining projection fallback/uncertainty

A standard projection-only pass is final only at `A` or `A+`. Anything below `A` requires more sportsbook/market research and reconciliation unless the user explicitly accepts the lower grade.

Ownership does **not** reduce the standard pass grade because ownership is no longer part of this workflow by default. If the user explicitly requests an ownership pass, then ownership should receive its own evidence sweep and grade.

## Core philosophy

**Vegas/props create the fantasy-point expectation. Sim Savant receives the improved projections and handles ownership separately unless the user asks otherwise.**

Never alter projections to manufacture leverage or force a preferred lineup outcome. Market projections must remain objective and independent from portfolio construction.
