# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Estimator: `core/PROJECTION_MODEL.md` v4. Python pull. Industry leaders and the book board, blended.

**User default (2026-09-22): no paid vendor file drops. Scrape public books + public sites.**

**User default (2026-09-29, evening): pull both layers in Python. A full prop board is thousands of rows. Blend the industry median with the de-vigged book consensus into one Proj.**

## Standard

1. Run `python -m dfs_engine.projections --sport mlb --pull`. Record the raw row count.
2. Both present: mean of the industry median and the de-vigged book consensus, in DraftKings points.
3. One present: that one.
4. Neither: Savant, unchanged.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

## No invented props

A missing prop does not get filled from a team total. Team total × lineup slot is a slate check only.

## Trust Savant zeros

Source Proj = 0 stays 0 unless the user says `unlock posted starters`.

## Required behavior

Lock roles before the number. Reject the wrong slate. Convert to site scoring. Preserve Name, DFS ID, Own, row order. Report both / vegas-only / industry-only / savant / zeros. Stop. No lineups.
