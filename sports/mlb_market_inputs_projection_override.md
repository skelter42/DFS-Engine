# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

## Standard

The output `Proj` is a **composite projection** that must meet the A+ bar defined in `core/MARKET_PROJECTIONS.md`:

1. **Industry layer** — blend as many independent numeric projection sources as are realistically available (target **10+** on a normal MLB main slate).
2. **Vegas layer** — multi-book player props + game markets, used as primary expectation and as sanity check / reconciliation against the industry blend.
3. **Sim Savant** — final fallback only when both layers are thin.

Ownership (`Own`) is left unchanged unless the user explicitly requests an ownership pass.

## Required behavior

1. Exhaust industry sources and sportsbook markets for `Proj` before delivery.
2. Industry: pursue THE BAT / THE BAT X, RotoGrinders, Daily Fantasy Fuel, FantasyPros, LineStar, Stokastic/Awesemo, RotoWire, NumberFire, Sabersim, and any other current numeric MLB DFS projection systems. Do not stop at one or two sources.
3. Vegas: multi-book props (K, outs, ER, hits/walks, win for pitchers; hits, TB, HR, RBI, runs, walks, H+R+RBI, SB for hitters) + game totals / ML / team totals. De-vig and consensus across books.
4. Form the composite from both layers; reconcile player totals to the game environment.
5. Preserve Name, DFS ID, Own, and row order. Replace only `Proj`.
6. Track provenance: `VEGAS_DIRECT`, `VEGAS_SUPPORTED`, `INDUSTRY_BLEND`, `SAVANT_FALLBACK`, plus industry source count.
7. Report grade, industry source count, Vegas coverage, and largest composite vs original Savant deltas.

## Grade gate

- `Projection grade: <grade>`
- `Overall projection-input grade: <grade>`
- Target: **A or A+**
- Below A → more industry and/or Vegas research required unless user accepts lower grade.

## Core philosophy

**Broad industry consensus + multi-book Vegas create the fantasy-point expectation. Sim Savant receives the composite and handles ownership separately unless asked otherwise.**

Never alter projections to manufacture leverage. Keep the composite objective and independent from lineup construction.
