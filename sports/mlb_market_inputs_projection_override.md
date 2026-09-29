# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Estimator: `core/PROJECTION_MODEL.md` v3. Vegas-driven. No 50/50. No Savant weight.

**User default (2026-09-22): no paid vendor file drops. Scrape public books + public sites.**

**User default (2026-09-29, correction): Proj is the multi-book de-vigged prop, converted to site points. Industry only if that player has no prop. Savant only if both are empty, and then unchanged.**

## Standard

1. Prop boards across books. Convert American odds to probability. Remove the vig. Median the books. Convert that expectation to DraftKings or FanDuel points. That is Proj.
2. No two-sided prop: DFS-site median.
3. No site number either: Savant, unchanged.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

## No invented props

A missing prop does not get filled from a team total. Team total × lineup slot is a slate check only.

## Trust Savant zeros

Source Proj = 0 stays 0 unless the user says `unlock posted starters`.

## Required behavior

Lock roles before the number. Reject the wrong slate. Convert to site scoring. Preserve Name, DFS ID, Own, row order. Report how many names were VEGAS, how many INDUSTRY, how many SAVANT. Stop. No lineups.
