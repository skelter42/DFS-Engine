# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Estimator: `core/PROJECTION_MODEL.md` v2. Do not use a band. Do not use a Savant weight.

**User default (2026-09-22): no paid vendor file drops. Scrape public DFS sites + public Vegas.**

**User default (2026-09-23): both layers on the same player. Grade the active pool, not the raw file.**

**User default (2026-09-29): Proj = 0.50 × DFS-site median + 0.50 × Vegas prop when both exist.**

## Standard

1. DFS projection sites for this slate. Tier A votes if three or more exist. Median of those votes.
2. Vegas prop, de-vigged and converted once. One number, not one per book.
3. Both exist: half and half. Sites only: site median. Prop only: Vegas number. Neither: Savant fallback.
4. Savant does not enter the blend.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

## No-prop hitters

A missing hitter prop does not invent the Vegas half. Team total × lineup slot is a slate check only, not site points. The locked shares are 1: 0.13, 2: 0.12, 3: 0.12, 4: 0.11, 5: 0.11, 6: 0.11, 7: 0.10, 8: 0.10, 9: 0.10.

## Trust Savant zeros

Source `Proj = 0` stays 0 unless the user says `unlock posted starters`.

## Coverage

Active pool is starting pitchers plus posted 1–9. Target 0% Savant fallback on that pool. Reliever fallback is reported second.

## Required behavior

Lock roles before the blend. Reject the wrong slate. Convert to site scoring. Preserve Name, DFS ID, Own, row order. Report source count and how many names had both halves. Stop. No lineups.
