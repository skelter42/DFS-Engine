# MLB Market Inputs — Projection-Only Override

## Status

This file is an authoritative override to `sports/mlb_market_inputs.md` for future MLB market-input / Savant Prep passes.

## User workflow decision

Sim Savant allows ownership to be changed separately, so the DFS Engine market-input pass focuses its research and refinement effort on **projections only** by default.

The output `Proj` is a **composite projection** (multi-book Vegas + multiple industry leaders). The original Sim Savant projection is used only as the final fallback when external coverage is genuinely insufficient.

## Required behavior

1. `@GitHub market inputs mlb` / `Savant Prep` / any attached projection file must exhaust sportsbook and multi-industry information for `Proj` before delivery.
2. Build the composite in this order:
   - Direct player props and prices across multiple books (primary)
   - Game/team markets and context
   - Multiple independent industry projection systems (THE BAT, RotoGrinders, Daily Fantasy Fuel, FantasyPros, LineStar, etc.)
   - Original Sim Savant projection only as final fallback
3. Preserve the original Sim Savant `Own` values unchanged in the returned import CSV unless the user explicitly requests an ownership pass or ownership audit.
4. Do not spend the normal market-input research budget trying to estimate or replace ownership by default.
5. The final CSV retains the standard import schema `Name, DFS ID, Proj, Own` for compatibility; `Own` is pass-through data by default.
6. Track projection provenance: `VEGAS_DIRECT`, `VEGAS_SUPPORTED`, `INDUSTRY_BLEND`, `SAVANT_FALLBACK`.
7. Report projection-source coverage and material Savant-vs-composite projection differences.

## AI grade gate

The mandatory A-or-better gate applies to **projection quality** for the standard MLB market-input pass.

Required report:

- `Projection grade: <grade>`
- `Overall projection-input grade: <grade>`
- main reasons for the grade
- remaining projection fallback/uncertainty

A standard projection-only pass is final only at `A` or `A+`. Anything below `A` requires more sportsbook/market and industry research unless the user explicitly accepts the lower grade.

Ownership does **not** reduce the standard pass grade because ownership is no longer part of this workflow by default. If the user explicitly requests an ownership pass, then ownership receives its own evidence sweep and grade.

## Core philosophy

**Multi-book Vegas + multi-industry consensus create the fantasy-point expectation. Sim Savant receives the improved composite projections and handles ownership separately unless the user asks otherwise.**

Never alter projections to manufacture leverage or force a preferred lineup outcome. Composite projections must remain objective and independent from portfolio construction.
