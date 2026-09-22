# MLB Market Inputs — Projection-Only Override

## Status

Authoritative override to `sports/mlb_market_inputs.md` for MLB market-input / Savant Prep / attached-file projection passes.

Iteration addendum: `sports/mlb_market_inputs_future_iteration.md`.

**User default (2026-09-22): no paid vendor file drops. Scrape public industry + public Vegas. Deliver the best available composite.**

## Standard

The output `Proj` is a **pure numeric composite**:

1. **Public industry layer** — scrape every reachable numeric projection/component page for this exact slate.
2. **Public Vegas layer** — board-first multi-book props + game markets; de-vig when possible.
3. **Sim Savant** — fallback only when both public layers are thin for a positive-Proj player.

No narrative in Proj. Own unchanged unless an ownership pass is requested.

Paid vendor CSVs are optional if the user later attaches them. They are not required to start or finish a pass.

## Trust Savant zeros — mandatory

If source `Proj` is `0`, leave `Proj = 0` unless the user says `unlock posted starters`.

## Required behavior

1. Split zeros vs positive-Proj pool.
2. Identify the exact slate window. Reject wrong-slate public tables.
3. Sweep public industry pages and public Vegas boards in parallel. Do not wait for file uploads.
4. Convert components with site scoring. Never mix Yahoo/FD/DK raw points.
5. Role facts only: posted order, opener/bulk/full start, PH/bench.
6. Preserve Name, DFS ID, Own, row order. Replace only researched `Proj`.
7. Report actual public source count, not a fictional 10.
8. Grade honestly. Public-scrape A- is an acceptable delivery grade when hitter vendor grids are unavailable.
9. Stop. No lineups.

## Grade gate

- Target remains A / A+ when public coverage supports it.
- Missing paywalled CSVs is **not** a delivery blocker.
- Report `Projection grade` and the public sources used.

## Core philosophy

**Scrape public industry projections + scrape sportsbook odds → blend into one composite.**
Trust Savant zeros. Do not stall for files the user will not attach.
